#!/usr/bin/env python3
"""
Asset management module
Handles static files, CSS, JavaScript, and image copying with optimization
"""

import os
import shutil
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, List, Tuple
from threading import Lock
from .performance_logger import (
    logger, time_operation, log_info, log_success, log_warn, log_error,
    log_phase_start, log_phase_complete, update_stats
)


class AssetManager:
    """Manages static assets and file operations"""
    
    def __init__(self, static_dir: str, output_dir: str, max_workers: Optional[int] = None, build_cache=None):
        self.static_dir = static_dir
        self.output_dir = output_dir
        self.build_cache = build_cache  # For coordinating with ImageOptimizer
        # Configure max workers for parallel processing (default: min(32, cpu_count() + 4))
        cpu_count = os.cpu_count() or 4  # Fallback to 4 if cpu_count() returns None
        self.max_workers = max_workers if max_workers is not None else min(32, cpu_count + 4)
        # Thread-safe stats aggregation
        self._stats_lock = Lock()
    
    def copy_static_files(self, force: bool = False) -> None:
        """
        Copy all static files to output directory with organized structure and incremental support.
        Uses parallel processing for improved performance.
        
        Args:
            force: Force copy all files regardless of modification times
        """
        copy_timer = logger.start_timing("static_file_copying")
        log_phase_start("AssetManager", f"parallel file copying with {self.max_workers} workers", "📁")
        
        # Create organized asset directories
        assets_dir = os.path.join(self.output_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # Define asset mappings
        asset_mappings = {
            "css": ["*.css"],
            "js": ["*.js"],
            "images": ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.svg", "*.gif", "*.ico"],
            "fonts": ["*.woff", "*.woff2", "*.ttf", "*.otf", "*.eot"]
        }
        
        total_stats = {'copied': 0, 'skipped': 0, 'errors': 0}
        
        # Collect all file copy tasks
        copy_tasks = []
        
        # Add tasks for asset files
        for asset_type, patterns in asset_mappings.items():
            target_dir = os.path.join(assets_dir, asset_type)
            os.makedirs(target_dir, exist_ok=True)
            
            # Preserve directory structure for all asset types to prevent filename collisions
            preserve_structure = True
            
            for pattern in patterns:
                file_tasks = self._collect_file_tasks(pattern, target_dir, preserve_structure, force)
                copy_tasks.extend(file_tasks)
        
        # Add tasks for special files to root - explicit allowlist to prevent pollution/security issues
        # SECURITY: Only allow specific essential files in site root to prevent:
        # - Internal JSON configuration leaks (e.g., build metadata, cache files)
        # - Accidental overwrites of system-generated files
        # - Site root pollution with development/debugging files
        root_files_allowlist = [
            "favicon.ico",           # Browser icon
            "site.webmanifest",      # PWA manifest 
            "manifest.json",         # PWA manifest (alternative name)
            "app.webmanifest",       # PWA manifest (alternative name)
            "sw.js",                 # Service worker for PWA functionality
            "logo.png",              # Site logo
            "robots.txt",            # SEO robots file (may override system-generated)
            "sitemap.xml"            # SEO sitemap (may override system-generated)
        ]
        
        # System-generated files that might be overridden - show warnings
        system_generated_files = {"robots.txt", "sitemap.xml"}
        
        log_info("AssetManager", f"Processing root files with security allowlist ({len(root_files_allowlist)} files allowed)", "📁")
        
        # Track and log files that are being processed vs blocked
        processed_files = []
        
        for filename in root_files_allowlist:
            file_tasks = self._collect_file_tasks(filename, self.output_dir, False, force)
            if file_tasks:
                processed_files.extend([task[0] for task in file_tasks])
                if filename in system_generated_files:
                    log_warn("AssetManager", f"Static file '{filename}' will override system-generated file", "⚠️")
                else:
                    log_info("AssetManager", f"Root file allowed: {filename}", "✅")
            copy_tasks.extend(file_tasks)
        
        # Check for potentially blocked files that would have been copied by wildcards
        self._log_blocked_files()
        
        # Execute file copying in parallel
        if copy_tasks:
            log_info("AssetManager", f"Executing {len(copy_tasks)} file copy operations in parallel", "⚙️")
            stats = self._execute_parallel_copy(copy_tasks)
            total_stats.update(stats)
            
            # Update performance statistics
            copy_duration = logger.stop_timing(copy_timer)
            if copy_duration and copy_duration > 0:
                processing_rate = logger.calculate_processing_rate(total_stats['copied'], copy_duration)
                update_stats("static_file_copying",
                           files_processed=total_stats['copied'],
                           files_skipped=total_stats['skipped'],
                           files_error=total_stats['errors'],
                           processing_rate=processing_rate,
                           parallel_workers=self.max_workers,
                           memory_usage_mb=logger.get_memory_usage())
            else:
                copy_timer = None  # Don't stop timer again later
        
        # Copy img folder if exists (for backward compatibility)
        img_dir = os.path.join(self.static_dir, "img")
        if os.path.exists(img_dir):
            with time_operation("img_directory_copy"):
                log_info("AssetManager", "Copying img/ directory for backward compatibility", "📂")
                target_img_dir = os.path.join(assets_dir, "images")
                self._copy_directory(img_dir, target_img_dir)
                log_success("AssetManager", "img/ directory copied successfully", "📂")
        
        # Provide feedback about copy operation
        if copy_timer:
            copy_duration = logger.stop_timing(copy_timer)
        else:
            copy_duration = None
            
        if total_stats['copied'] > 0 or total_stats['errors'] > 0 or force:
            processing_rate = logger.calculate_processing_rate(total_stats['copied'], copy_duration) if copy_duration else 0
            log_phase_complete("AssetManager", "static file copying", copy_duration or 0, "📁",
                             files_processed=total_stats['copied'],
                             files_skipped=total_stats['skipped'],
                             processing_rate=processing_rate)
            if total_stats['errors'] > 0:
                log_warn("AssetManager", f"{total_stats['errors']} errors occurred during copying", "⚠️")
        else:
            log_info("AssetManager", "Static files: all up to date", "📁")
            update_stats("static_file_copying", cache_hits=1)
    
    def _collect_file_tasks(self, pattern: str, target_dir: str, 
                           preserve_path: bool = True, force: bool = False) -> List[Tuple[str, str, bool]]:
        """
        Collect file copy tasks for parallel execution.
        
        Args:
            pattern: File pattern (e.g., "*.css")
            target_dir: Target directory
            preserve_path: Whether to preserve subdirectory structure
            force: Force copy all files regardless of modification times
            
        Returns:
            List of tuples (source_path, target_path, force)
        """
        import glob
        
        tasks = []
        
        # Get all matching files
        pattern_path = os.path.join(self.static_dir, "**", pattern)
        files = glob.glob(pattern_path, recursive=True)
        
        for file_path in files:
            if os.path.isfile(file_path):
                # Check if this image has already been processed by ImageOptimizer
                if self._is_image_file(file_path) and self._is_image_already_processed(file_path):
                    log_info("AssetManager", f"Skipping already processed image: {os.path.relpath(file_path, self.static_dir)}", "⚡")
                    continue
                
                rel_path = os.path.relpath(file_path, self.static_dir)
                
                if preserve_path:
                    # Smart directory structure preservation for CSS/JS assets
                    # Avoid double-nesting by handling immediate css/ and js/ subdirectories specially
                    if rel_path.startswith(('css/', 'js/')):
                        # For files in css/ or js/ subdirectories, use the subdirectory path
                        # css/main.css -> main.css (relative to /assets/css/)
                        # css/components/main.css -> components/main.css (relative to /assets/css/)
                        asset_type = rel_path.split('/')[0]  # 'css' or 'js'
                        if target_dir.endswith(f'/assets/{asset_type}'):
                            # Remove the asset type prefix to avoid double-nesting
                            sub_path = rel_path[len(asset_type)+1:]  # Remove 'css/' or 'js/'
                            target_path = os.path.join(target_dir, sub_path)
                        else:
                            # Preserve full directory structure for other cases
                            target_path = os.path.join(target_dir, rel_path)
                    else:
                        # Preserve directory structure for files not in css/ or js/ subdirectories
                        target_path = os.path.join(target_dir, rel_path)
                else:
                    # Copy to root of target directory
                    target_path = os.path.join(target_dir, os.path.basename(file_path))
                
                # Check if copy is needed (for incremental builds)
                if force or self._needs_copy(file_path, target_path):
                    tasks.append((file_path, target_path, force))
        
        return tasks
    
    def _execute_parallel_copy(self, copy_tasks: List[Tuple[str, str, bool]]) -> Dict[str, int]:
        """
        Execute file copying tasks in parallel using ThreadPoolExecutor.
        
        Args:
            copy_tasks: List of (source_path, target_path, force) tuples
            
        Returns:
            Dictionary with copy statistics (copied, skipped, errors)
        """
        stats = {'copied': 0, 'skipped': 0, 'errors': 0}
        
        if not copy_tasks:
            return stats
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all copy tasks
            future_to_task = {executor.submit(self._copy_single_file, task): task 
                             for task in copy_tasks}
            
            # Process completed tasks
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    with self._stats_lock:
                        if result == 'copied':
                            stats['copied'] += 1
                        elif result == 'skipped':
                            stats['skipped'] += 1
                        elif result == 'error':
                            stats['errors'] += 1
                except Exception as e:
                    log_warn("AssetManager", f"Unexpected error in parallel copy task {task}: {e}", "⚠️")
                    with self._stats_lock:
                        stats['errors'] += 1
        
        return stats
    
    def _copy_single_file(self, task: Tuple[str, str, bool]) -> str:
        """
        Copy a single file (thread-safe method for parallel execution).
        
        Args:
            task: Tuple of (source_path, target_path, force)
            
        Returns:
            Result status: 'copied', 'skipped', or 'error'
        """
        source_path, target_path, force = task
        
        try:
            # Ensure destination directory exists (thread-safe)
            target_dir = os.path.dirname(target_path)
            if target_dir:
                os.makedirs(target_dir, exist_ok=True)
            
            # Double-check if copy is still needed (in case another thread processed it)
            if not force and not self._needs_copy(source_path, target_path):
                return 'skipped'
            
            shutil.copy2(source_path, target_path)
            return 'copied'
            
        except (OSError, IOError, shutil.SameFileError) as e:
            log_warn("AssetManager", f"Could not copy {source_path}: {e}", "⚠️")
            return 'error'
        except Exception as e:
            log_warn("AssetManager", f"Unexpected error copying {source_path}: {e}", "⚠️")
            return 'error'
    
    def _copy_files_by_pattern(self, pattern: str, target_dir: str, 
                              preserve_path: bool = True, force: bool = False) -> Dict[str, int]:
        """
        Legacy method - now redirects to parallel implementation for backwards compatibility.
        
        Args:
            pattern: File pattern (e.g., "*.css")
            target_dir: Target directory
            preserve_path: Whether to preserve subdirectory structure
            force: Force copy all files regardless of modification times
            
        Returns:
            Dictionary with copy statistics (copied, skipped, errors)
        """
        # Collect tasks and execute in parallel
        copy_tasks = self._collect_file_tasks(pattern, target_dir, preserve_path, force)
        return self._execute_parallel_copy(copy_tasks)
    
    def _copy_directory(self, src_dir: str, dest_dir: str) -> None:
        """
        Copy entire directory to destination.
        
        Args:
            src_dir: Source directory
            dest_dir: Destination directory
        """
        try:
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            shutil.copytree(src_dir, dest_dir)
        except (OSError, IOError, shutil.Error) as e:
            log_warn("AssetManager", f"Could not copy directory {src_dir}: {e}", "⚠️")
        except Exception as e:
            log_warn("AssetManager", f"Unexpected error copying directory {src_dir}: {e}", "⚠️")
    
    def copy_file(self, src: str, dest: str, force: bool = False) -> bool:
        """
        Copy a single file with incremental build support.
        
        Args:
            src: Source file path
            dest: Destination file path
            force: Force copy even if destination is newer
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if copy is needed (incremental build support)
            if not force and not self._needs_copy(src, dest):
                return True  # File is up to date
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(dest)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.copy2(src, dest)
            return True
        except (OSError, IOError, shutil.SameFileError) as e:
            log_warn("AssetManager", f"Could not copy {src} to {dest}: {e}", "⚠️")
            return False
        except Exception as e:
            log_warn("AssetManager", f"Unexpected error copying {src} to {dest}: {e}", "⚠️")
            return False
    
    def _needs_copy(self, src: str, dest: str) -> bool:
        """
        Check if a file needs to be copied based on modification times.
        
        Args:
            src: Source file path
            dest: Destination file path
            
        Returns:
            True if copy is needed, False otherwise
        """
        try:
            if not os.path.exists(dest):
                return True  # Destination doesn't exist, copy needed
            
            src_stat = os.stat(src)
            dest_stat = os.stat(dest)
            
            # Copy if source is newer than destination
            return src_stat.st_mtime > dest_stat.st_mtime
        except OSError:
            return True  # Error accessing files, assume copy needed
    
    def update_template_context_for_assets(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update template context with asset path mappings.
        
        Args:
            context: Template context dictionary
            
        Returns:
            Updated context with asset mappings
        """
        # Add asset path helpers
        context['asset_path'] = lambda path: f"/assets/{path}"
        context['image_path'] = lambda path: f"/assets/images/{path}"
        context['css_path'] = lambda path: f"/assets/css/{path}"
        context['js_path'] = lambda path: f"/assets/js/{path}"
        
        # Update existing paths if needed
        if 'og_image' in context and not context['og_image'].startswith('http'):
            if not context['og_image'].startswith('/'):
                context['og_image'] = f"/assets/images/{context['og_image']}"
        
        return context
    
    def optimize_assets(self) -> None:
        """
        Optimize assets - minify CSS/JS and improve performance.
        """
        with time_operation("asset_optimization"):
            log_phase_start("AssetManager", "asset optimization", "🔧")
            
            # Minify CSS files
            css_files = self._minify_css_files()
            
            # Minify JS files
            js_files = self._minify_js_files()
            
            total_files = css_files + js_files
            update_stats("asset_optimization", files_processed=total_files)
            
            log_success("AssetManager", f"Asset optimization completed - {total_files} files optimized", "✅")
    
    def _minify_css_files(self) -> int:
        """
        Basic CSS minification - remove comments, extra whitespace, and empty rules.
        
        Returns:
            Number of CSS files processed
        """
        css_dir = os.path.join(self.output_dir, "assets", "css")
        if not os.path.exists(css_dir):
            return 0
        
        css_files_processed = 0
        for root, dirs, files in os.walk(css_dir):
            for file in files:
                if file.endswith('.css'):
                    file_path = os.path.join(root, file)
                    try:
                        self._minify_css_file(file_path)
                        css_files_processed += 1
                        log_info("AssetManager", f"Minified CSS: {file}", "🎨")
                    except Exception as e:
                        log_warn("AssetManager", f"Could not minify CSS {file}: {e}", "⚠️")
        
        if css_files_processed > 0:
            log_success("AssetManager", f"Minified {css_files_processed} CSS files", "🎨")
        
        return css_files_processed
    
    def _minify_css_file(self, file_path: str) -> None:
        """
        Minify individual CSS file.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic CSS minification
        # Remove comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        # Remove whitespace around certain characters
        content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', content)
        # Remove trailing semicolons before }
        content = re.sub(r';\s*}', '}', content)
        # Remove empty rules
        content = re.sub(r'[^{}]*{\s*}', '', content)
        
        # Write minified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
    
    def _minify_js_files(self) -> int:
        """
        Basic JavaScript minification - remove comments and extra whitespace.
        
        Returns:
            Number of JS files processed
        """
        js_dir = os.path.join(self.output_dir, "assets", "js")
        if not os.path.exists(js_dir):
            return 0
        
        js_files_processed = 0
        for root, dirs, files in os.walk(js_dir):
            for file in files:
                if file.endswith('.js'):
                    file_path = os.path.join(root, file)
                    try:
                        self._minify_js_file(file_path)
                        js_files_processed += 1
                        log_info("AssetManager", f"Minified JS: {file}", "⚙️")
                    except Exception as e:
                        log_warn("AssetManager", f"Could not minify JS {file}: {e}", "⚠️")
        
        if js_files_processed > 0:
            log_success("AssetManager", f"Minified {js_files_processed} JS files", "⚙️")
        
        return js_files_processed
    
    def _minify_js_file(self, file_path: str) -> None:
        """
        Basic JavaScript minification.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic JS minification - be conservative to avoid breaking code
        # Remove single-line comments (but preserve URLs)
        content = re.sub(r'(?<!:)//.*$', '', content, flags=re.MULTILINE)
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Remove extra whitespace (but preserve line breaks in strings)
        content = re.sub(r'\n\s*\n', '\n', content)
        # Remove leading/trailing whitespace
        content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
        
        # Write minified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _is_image_file(self, file_path: str) -> bool:
        """
        Check if a file is an image based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is an image, False otherwise
        """
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.ico'}
        return os.path.splitext(file_path.lower())[1] in image_extensions
    
    def _log_blocked_files(self) -> None:
        """
        Log files that would have been copied by old wildcards but are now blocked.
        This provides transparency about security filtering.
        """
        import glob
        
        # Check for files that old wildcards would have caught
        old_wildcards = ["*.xml", "*.txt", "*.json"]
        blocked_files = []
        
        for pattern in old_wildcards:
            pattern_path = os.path.join(self.static_dir, "**", pattern)
            files = glob.glob(pattern_path, recursive=True)
            
            for file_path in files:
                if os.path.isfile(file_path):
                    filename = os.path.basename(file_path)
                    # Check if this file is NOT in our allowlist
                    root_files_allowlist = [
                        "favicon.ico", "site.webmanifest", "manifest.json", 
                        "app.webmanifest", "logo.png", "robots.txt", "sitemap.xml"
                    ]
                    if filename not in root_files_allowlist:
                        rel_path = os.path.relpath(file_path, self.static_dir)
                        blocked_files.append(rel_path)
        
        if blocked_files:
            log_warn("AssetManager", f"Security: Blocked {len(blocked_files)} file(s) from root (prevented pollution)", "🛡️")
            for blocked_file in blocked_files[:5]:  # Show first 5 blocked files
                log_info("AssetManager", f"Blocked: {blocked_file}", "🚫")
            if len(blocked_files) > 5:
                log_info("AssetManager", f"... and {len(blocked_files) - 5} more files blocked", "🚫")
        else:
            log_success("AssetManager", "Security: No potentially harmful files found to block", "✅")
    
    def _is_image_already_processed(self, file_path: str) -> bool:
        """
        Check if an image has already been processed by ImageOptimizer.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            True if image was already processed, False otherwise
        """
        if not self.build_cache:
            return False
        
        return self.build_cache.is_image_processed(file_path)