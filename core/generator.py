#!/usr/bin/env python3
"""
ARCADEFORGE SITE GENERATOR
==========================

This is the main site generator. It reads your content and creates a complete website.

EASY USAGE:
- Run: python generate_site.py (uses your config.py settings)
- Or: python build.py (even simpler!)

WHAT IT DOES:
- Reads game content from content_html/games/
- Applies your templates from templates/
- Copies static files (images, CSS, etc.)
- Creates SEO-optimized HTML files
- Generates sitemap.xml and robots.txt

You usually don't need to edit this file - just run it!
"""

import os
import shutil
import argparse
import re
import json
import hashlib
import random
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape, ChoiceLoader
from .site_loader import load_site_settings, get_site_paths, get_site_output_dir

# Import site configuration
from .config import SiteConfig

# Try to import simple config if available
HAS_SIMPLE_CONFIG = False
simple_config = None
try:
    from . import settings as simple_config
    HAS_SIMPLE_CONFIG = True
except ImportError:
    pass

class SiteGenerator:
    def __init__(self, template_dir="templates", output_dir=None, site_url=None, language=None, site=None):
        # Store site parameter for multi-site support
        self.site = site
        
        # Load site-specific settings and paths
        self.site_settings = load_site_settings(site)
        self.site_paths = get_site_paths(site)
        
        # Set up directories using new path resolution
        project_root = self.site_paths["project_root"]
        self.template_dir = template_dir if os.path.isabs(template_dir) else os.path.join(project_root, template_dir)
        self.output_dir = get_site_output_dir(site, output_dir)
        self.content_dir = self.site_paths["content_dir"]
        self.static_dir = self.site_paths["static_dir"]
        
        # English only - simplified language detection
        self.language = "en-US"
        
        # Override site_url from site-specific settings if not provided
        if not site_url and hasattr(self.site_settings, 'SITE_URL'):
            site_url = self.site_settings.SITE_URL
        
        # Create config with site-specific settings  
        self.config = SiteConfig(language_code=self.language)
        # Pass static directory to config for proper FAQ schema loading
        self.config.static_dir = self.static_dir
        
        # Update site URL if provided
        if site_url:
            self.config.update_site_url(site_url)
        else:
            print(f"🌐 Using site URL from config: {self.config.site_url}")
        
        print(f"🌐 Using language: {self.language}")
        if site:
            print(f"🏢 Site: {site}")
            print(f"📁 Content: {self.content_dir}")
            print(f"📁 Static: {self.static_dir}")
            print(f"📁 Output: {self.output_dir}")
        
        # Setup Jinja2 environment with choice loader for template overrides
        template_loaders = []
        
        # If site is specified, check for site-specific templates first
        if site:
            site_template_dir = os.path.join(self.site_paths["site_root"], "templates")
            if os.path.exists(site_template_dir):
                template_loaders.append(FileSystemLoader(site_template_dir))
                print(f"📄 Site-specific templates found: {site_template_dir}")
        
        # Always include shared templates as fallback
        template_loaders.append(FileSystemLoader(self.template_dir))
        
        self.env = Environment(
            loader=ChoiceLoader(template_loaders) if len(template_loaders) > 1 else template_loaders[0],
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def generate_site(self):
        """Generate the complete website with progress tracking"""
        print("🚀 Generating website from template...")
        start_time = datetime.now()
        
        try:
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)
            print("📁 Output directory ready")
            
            # Optimize images for SEO
            print("🖼️  Starting image optimization...")
            self._optimize_images()
            
            # Copy static files
            print("📄 Copying static files...")
            self._copy_static_files()
            
            # Scan games content first to make games available for sidebar
            print("🎮 Scanning games content...")
            games = self._scan_games_content()
            # Save games for sidebar widget and sitemap generation
            self._games = games
            
            # Generate pages based on language config
            pages = self._get_pages_from_config()
            print(f"📝 Generating {len(pages)} pages...")
            
            for i, (page_key, template_name) in enumerate(pages, 1):
                print(f"  [{i}/{len(pages)}] Processing {page_key}...")
                self._generate_page(page_key, template_name)

            # Generate game pages and listing
            if games:
                print(f"🕹️  Found {len(games)} game(s)")
                self._generate_game_pages(games)
                self._generate_games_listing(games)
            else:
                print("ℹ️  No games found in content_html/games")
            
            # Calculate generation time
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            print(f"\n✅ Website generated successfully in '{self.output_dir}' directory!")
            print(f"⏱️  Generation completed in {generation_time:.2f} seconds")
            print("\n📋 Next steps:")
            print("1. Images have been optimized for SEO with multiple sizes")
            print("2. Favicon generated in multiple sizes for all devices")
            print("3. Test the website locally")
            print("4. Deploy to your web server")
            
        except Exception as e:
            print(f"❌ Fatal error during website generation: {e}")
            raise

    def _scan_games_content(self):
        """Scan content_html/games/*.html and extract minimal metadata.

        Returns list of dicts: {slug, title, content_html, embed_url, hero_image}
        """
        # Use site-specific content directory
        games_dir = os.path.join(self.content_dir, "games")
        games = []
        if not os.path.isdir(games_dir):
            return games
        for fname in sorted(os.listdir(games_dir)):
            if not fname.lower().endswith(".html"):
                continue
            slug = os.path.splitext(fname)[0]
            path = os.path.join(games_dir, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    raw = f.read()
                # Extract title from first <h1> if present
                title = None
                m = re.search(r"<h1[^>]*>(.*?)</h1>", raw, flags=re.IGNORECASE|re.DOTALL)
                if m:
                    title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                if not title:
                    title = slug.replace('-', ' ').replace('_', ' ').title()
                # Parse optional meta comments
                embed_url = None
                hero_image = None
                m2 = re.search(r"<!--\s*embed:\s*(.*?)\s*-->", raw, flags=re.IGNORECASE)
                if m2:
                    embed_url = m2.group(1).strip()
                m3 = re.search(r"<!--\s*hero:\s*(.*?)\s*-->", raw, flags=re.IGNORECASE)
                if m3:
                    hero_image = m3.group(1).strip()

                # JSON metadata block: <!-- meta: { ... } -->
                meta = {}
                try:
                    m_meta = re.search(r"<!--\s*meta:\s*(\{[\s\S]*?\})\s*-->", raw, flags=re.IGNORECASE)
                    if m_meta:
                        meta = json.loads(m_meta.group(1))
                except Exception as e:
                    print(f"⚠️  Ignoring invalid meta JSON in {fname}: {e}")

                games.append({
                    "slug": slug,
                    "title": meta.get("title") or title,
                    "content_html": raw,
                    "embed_url": meta.get("embed") or embed_url or self.config.seo_config.get("game_embed", {}).get("url", "about:blank"),
                    "hero_image": meta.get("hero") or hero_image or self.config.get_dynamic_hero_image(),
                    "description": meta.get("description"),
                    "meta": meta
                })
            except Exception as e:
                print(f"⚠️  Failed parsing game file {fname}: {e}")
        return games

    def _get_sidebar_title(self):
        """Get sidebar title - English only"""
        return "More Games"
    
    def _get_all_games_for_widget(self, games, exclude_slug=None):
        """Get all games for the icon widget
        
        Args:
            games: List of all games
            exclude_slug: Game slug to exclude (optional, for current game page)
            
        Returns:
            List of all games formatted for the widget (up to 60 games)
        """
        if not games or not isinstance(games, list):
            return []
            
        # Filter out the current game if specified and ensure valid games
        available_games = [g for g in games if isinstance(g, dict) and g.get("slug") and g.get("title")]
        if exclude_slug:
            available_games = [g for g in available_games if g["slug"] != exclude_slug]
        
        # Return up to 60 games
        result = []
        for g in available_games[:60]:
            if not g.get('slug') or not g.get('title'):
                continue
            # Get logo path - it's already in the format "img/filename.webp"
            logo = g.get('meta', {}).get('logo')
            if logo:
                # Remove the "img/" prefix if present since it's already in assets/images/
                if logo.startswith('img/'):
                    image_path = f"/assets/images/{logo[4:]}"
                else:
                    image_path = f"/assets/images/{logo}"
            else:
                # Fallback to hero image
                hero = g.get('hero_image', '')
                if hero.startswith('img/'):
                    image_path = f"/assets/images/{hero[4:]}"
                else:
                    image_path = f"/assets/images/{hero if hero else 'gamelogo.webp'}"
            
            result.append({
                "title": g.get("title", "Untitled Game"),
                "url": self._get_page_url(g.get('slug', ''), is_game_page=True),
                "image": image_path
            })
        return result
    
    def _get_random_games_for_widget(self, games, exclude_slug=None):
        """Get a random selection of games for the widget
        
        Args:
            games: List of all games
            exclude_slug: Game slug to exclude (optional, for current game page)
            
        Returns:
            List of randomly selected games for the widget (always randomized)
        """
        if not games or not isinstance(games, list):
            return []
            
        # Filter out the current game if specified and ensure valid games
        available_games = [g for g in games if isinstance(g, dict) and g.get("slug") and g.get("title")]
        if exclude_slug:
            available_games = [g for g in available_games if g["slug"] != exclude_slug]
        
        # Always randomize the order, regardless of count
        if len(available_games) == 0:
            return []
        
        # Select up to 12 games randomly (or all if fewer than 12)
        try:
            random_games = random.sample(available_games, min(12, len(available_games)))
        except (ValueError, TypeError):
            # Fallback if sampling fails
            random_games = available_games[:12]
        
        return [{
            "title": g.get("title", "Untitled Game"),
            "url": self._get_page_url(g.get('slug', ''), is_game_page=True),
            "image": f"/assets/images/{(g.get('meta', {}).get('logo') or g.get('hero_image', 'placeholder.webp'))}" 
        } for g in random_games if g.get('slug') and g.get('title')]

    def _generate_game_pages(self, games):
        """Generate per-game pages using templates/index.html layout."""
        try:
            template = self.env.get_template("index.html")
        except Exception as e:
            print(f"⚠️  Missing template index.html for game pages: {e}")
            return

        for game in games:
            try:
                page_key = game["slug"]
                breadcrumbs = [
                    {"title": "Home", "url": "/"},
                    {"title": "Games", "url": "/games.html"},
                    {"title": game["title"], "url": None}
                ]
                # Auto-generate SoftwareApplication schema from meta
                # Use logo for the main image field, fallback to hero if logo not available
                meta = game.get("meta", {})
                logo = meta.get("logo")
                if logo:
                    img_url = logo if (logo.startswith('http://') or logo.startswith('https://')) else f"{self.config.site_url}{logo}"
                else:
                    hero = game.get("hero_image")
                    img_url = hero if (hero.startswith('http://') or hero.startswith('https://')) else f"{self.config.site_url}{hero}"
                # Deterministic aggregate rating per game (overridable via meta)
                # Localize title/description from meta if provided (title_de, description_fr, etc.)
                lang_full = (self.config.language or "en").lower()
                lang_short = lang_full.split('-')[0]
                localized_title = meta.get(f"title_{lang_short}") or meta.get(f"title_{lang_full}") or game["title"]
                localized_description = meta.get(f"description_{lang_short}") or meta.get(f"description_{lang_full}") or game.get("description") or ""
                try:
                    h = int(hashlib.sha256(page_key.encode('utf-8')).hexdigest()[:8], 16)
                except Exception:
                    h = sum(ord(c) for c in page_key)
                # ratingValue between 3.0 and 4.9
                auto_rating_value = round(3.0 + ((h % 200) / 100.0), 1)
                if auto_rating_value > 5.0:
                    auto_rating_value = 5.0
                # ratingCount between 250 and 5250
                auto_rating_count = 250 + (h % 5001)
                rating_value = str(meta.get("ratingValue", auto_rating_value))
                rating_count = str(meta.get("ratingCount", auto_rating_count))
                # Localize currency based on site language
                lang = (self.config.language or "en").lower()
                currency_map = {
                    "en": "USD"
                }
                price_currency = currency_map.get(lang, "USD")

                # Use custom game schema with unique ratings
                custom_rating = {
                    "ratingValue": float(rating_value),
                    "ratingCount": int(rating_count)
                }
                software_schema = self.config.get_game_software_application_schema(
                    game_title=localized_title,
                    game_slug=page_key,
                    game_description=localized_description,
                    game_rating=custom_rating
                )
                context = {**self.config.get_base_context(),
                           "page_title": localized_title,
                           "page_description": localized_description or self.config._generate_automatic_description("about", localized_title),
                           "canonical_url": f"{self.config.site_url.rstrip('/')}{self._get_page_url(page_key, is_game_page=True)}",
                           "current_page": page_key,
                           "breadcrumbs": breadcrumbs,
                           # Keep generated SoftwareApplication and auto BreadcrumbList for games
                           "website_schema": None,
                           "faq_schema": None,
                           "software_application_schema": software_schema,
                           "breadcrumb_schema": self.config.get_breadcrumb_schema(breadcrumbs),
                           # index.html expectations
                           "game_name": localized_title,
                           "game_embed": {"url": game["embed_url"]},
                           "game_url": game["embed_url"],  # Add game_url for the play button
                           "hero_image": game["hero_image"],
                           "hero_seo_attributes": self.config.get_image_seo_attributes(game["hero_image"]),
                           "custom_html_content": game["content_html"],
                           # Add games data for sidebar widget (prefer logo over hero)
                           "games": self._get_random_games_for_widget(games, page_key),
                           "all_games": self._get_all_games_for_widget(games, page_key),
                           "sidebar_title": self._get_sidebar_title()
                           }
                # Update context with asset mappings for organized paths
                context = self._update_template_context_for_assets(context)
                
                html_content = template.render(**context)
                
                # Resolve asset links in rendered content
                html_content = self._resolve_asset_links(html_content)
                
                # Use organized output path for game pages
                output_file, subdir = self._get_page_output_path(page_key, is_game_page=True)
                temp_file = f"{output_file}.tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                os.rename(temp_file, output_file)
                
                # Show organized path in output  
                display_path = f"{subdir}/{page_key}.html" if subdir else f"{page_key}.html"
                print(f"📄 Generated game page {display_path}")
            except Exception as e:
                print(f"⚠️  Error generating game page {game.get('slug')}: {e}")

    def _generate_games_listing(self, games):
        """Generate games.html page listing all games in a grid."""
        try:
            template = self.env.get_template("games_list.html")
        except Exception:
            # Fallback: use page.html with simple links
            try:
                template = self.env.get_template("page.html")
            except Exception as e:
                print(f"⚠️  Missing games_list.html and page.html templates: {e}")
                return

        try:
            breadcrumbs = [{"title": "Home", "url": "/"}, {"title": "Games", "url": None}]
            context = {**self.config.get_base_context(),
                       "page_title": "Games",
                       "page_description": "Browse all games.",
                       "canonical_url": f"{self.config.site_url}games.html",
                       "current_page": "games",
                       "breadcrumbs": breadcrumbs,
                       "breadcrumb_schema": self.config.get_breadcrumb_schema(breadcrumbs),
                       "games": [{
                           "title": g["title"],
                           "url": self._get_page_url(g['slug'], is_game_page=True),
                           "image": (g.get("meta", {}).get("logo") or g["hero_image"]) 
                       } for g in games]
                       ,
                       "sidebar_title": self._get_sidebar_title()
                       }
            # Update context with asset mappings for organized paths
            context = self._update_template_context_for_assets(context)
            
            html_content = template.render(**context)
            
            # Resolve asset links in rendered content
            html_content = self._resolve_asset_links(html_content)
            
            output_file = os.path.join(self.output_dir, "games.html")
            temp_file = f"{output_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            os.rename(temp_file, output_file)
            print("📄 Generated games.html listing")
        except Exception as e:
            print(f"⚠️  Error generating games.html: {e}")
    
    def _get_pages_from_config(self):
        """Get English pages configuration"""
        
        # English only - simplified configuration
        return [
            ("index", "index.html"),
            ("about-us", "page.html"),
            ("contact", "page.html"),
            ("privacy-policy", "page.html"),
            ("terms-of-service", "page.html"),
            ("cookies-policy", "page.html"),
            ("dmca", "page.html"),
            ("parents-information", "page.html"),
        ]
    
    def _get_simple_config_page_data(self, page_key):
        """Get page data from simple config.py"""
        try:
            # Get content from simple config
            title = page_key.replace('-', ' ').title()
            description = ""
            keywords = ""
            
            # Load actual HTML content from site-specific content directory
            content_rel = f"{self._get_content_file_mapping().get(page_key, page_key)}.html"
            content_file = os.path.join(self.content_dir, content_rel)
            html_content = ""
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except FileNotFoundError:
                print(f"⚠️  Warning: Content file not found: {content_file}")
                html_content = f"<p>Content not found for {page_key}</p>"
            except Exception as content_error:
                print(f"⚠️  Warning: Could not read content file {content_file}: {content_error}")
                html_content = f"<p>Error loading content for {page_key}</p>"

            # Ensure no None values that could cause JSON serialization issues
            return {
                "page_title": str(title),
                "page_description": str(description),
                "meta_keywords": str(keywords),
                "og_title": f"{title} - {getattr(simple_config, 'SITE_NAME', 'Site')}",
                "twitter_title": f"{title} - {getattr(simple_config, 'SITE_NAME', 'Site')}",
                "custom_html_content": html_content
            }
        except Exception as e:
            print(f"⚠️  Warning: Could not load simple config page data for {page_key}: {e}")
            # Return fallback data to prevent JSON serialization errors
            return {
                "page_title": page_key.title(),
                "page_description": "",
                "meta_keywords": "",
                "og_title": f"{page_key.title()} - Slither Io",
                "twitter_title": f"{page_key.title()} - Slither Io",
                "custom_html_content": f"<p>Error loading content for {page_key}</p>"
            }
    
    def _get_content_file_mapping(self):
        """Map page keys to content file names"""
        mappings = {
            "ueber-uns": "about-us",
            "kontakt": "contact", 
            "datenschutz": "privacy-policy",
            "nutzungsbedingungen": "terms-of-service",
            "cookies": "cookies",
            "cookies-policy": "cookies",
            "eltern-information": "parents-information",
            "parents-information": "parents-information",
            "information-parents": "parents-information",
            "a-propos": "about-us",
            "confidentialite": "privacy-policy",
            "conditions-utilisation": "terms-of-service",
            "politique-cookies": "cookies",
            "over-ons": "about-us",
            "privacy": "privacy-policy", 
            "privacy-policy": "privacy-policy",
            "privacybeleid": "privacy-policy",
            "gebruiksvoorwaarden": "terms-of-service",
            "cookie-beleid": "cookies",
            "ouder-informatie": "parents-information",
            "about-us": "about-us",
            "contact": "contact",
            "privacy-policy": "privacy-policy",
            "terms-of-service": "terms-of-service",
            "dmca": "dmca"
        }
        return mappings
    
    def _copy_static_files(self):
        """Copy static files to organized output directory structure"""
        static_dir = self.static_dir
        if not os.path.exists(static_dir):
            print("⚠️  Static directory not found")
            return
            
        # Create organized asset directories
        assets_dir = os.path.join(self.output_dir, "assets")
        asset_subdirs = {
            "css": os.path.join(assets_dir, "css"),
            "js": os.path.join(assets_dir, "js"), 
            "images": os.path.join(assets_dir, "images"),
            "fonts": os.path.join(assets_dir, "fonts"),
            "media": os.path.join(assets_dir, "media")
        }
        
        # Create all asset directories
        for subdir in asset_subdirs.values():
            os.makedirs(subdir, exist_ok=True)
        
        # File type mappings to asset directories
        file_type_mapping = {
            # CSS files
            '.css': 'css',
            # JavaScript files  
            '.js': 'js',
            # Image files
            '.jpg': 'images', '.jpeg': 'images', '.png': 'images', 
            '.gif': 'images', '.webp': 'images', '.svg': 'images',
            '.ico': 'images', '.bmp': 'images', '.tiff': 'images',
            # Font files
            '.woff': 'fonts', '.woff2': 'fonts', '.ttf': 'fonts',
            '.otf': 'fonts', '.eot': 'fonts',
            # Media files
            '.mp4': 'media', '.mp3': 'media', '.wav': 'media',
            '.ogg': 'media', '.avi': 'media', '.mov': 'media'
        }
        
        # Keep track of file mappings for link resolution
        self._asset_mappings = {}
        
        # Copy files to organized structure
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                src = os.path.join(root, file)
                rel_path = os.path.relpath(src, static_dir)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Determine destination based on file type
                if file_ext in file_type_mapping:
                    asset_type = file_type_mapping[file_ext]
                    dst = os.path.join(asset_subdirs[asset_type], file)
                    new_rel_path = f"assets/{asset_type}/{file}"
                else:
                    # Keep other files (like robots.txt, site.webmanifest) in root
                    dst = os.path.join(self.output_dir, rel_path)
                    new_rel_path = rel_path
                    
                    # Create destination directory if it doesn't exist
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                
                # Copy the file
                shutil.copy2(src, dst)
                
                # Store mapping for link resolution
                self._asset_mappings[rel_path] = new_rel_path
                
                print(f"📄 Copied {rel_path} → {new_rel_path}")
        
        print(f"✅ Organized {len(self._asset_mappings)} static files into /assets/ structure")
    
    def _resolve_asset_links(self, content):
        """Resolve and update asset links in content to use organized paths"""
        if not hasattr(self, '_asset_mappings'):
            return content
            
        # Common asset reference patterns to update
        import re
        
        # Update CSS references: href="styles.css" -> href="/assets/css/styles.css" (root-absolute)
        def replace_css_refs(match):
            filename = match.group(1)
            if filename in self._asset_mappings:
                organized_path = self._asset_mappings[filename]
                # Ensure root-absolute path
                if not organized_path.startswith('/'):
                    organized_path = '/' + organized_path
                return f'href="{organized_path}"'
            return match.group(0)
        
        content = re.sub(r'href="([^"]*\.css)"', replace_css_refs, content)
        
        # Update JavaScript references: src="script.js" -> src="/assets/js/script.js" (root-absolute)
        def replace_js_refs(match):
            filename = match.group(1)
            if filename in self._asset_mappings:
                organized_path = self._asset_mappings[filename]
                # Ensure root-absolute path
                if not organized_path.startswith('/'):
                    organized_path = '/' + organized_path
                return f'src="{organized_path}"'
            return match.group(0)
        
        content = re.sub(r'src="([^"]*\.js)"', replace_js_refs, content)
        
        # Update image references: src="image.png" -> src="/assets/images/image.png" (root-absolute)
        def replace_img_refs(match):
            filename = match.group(1)
            # Handle different image reference patterns
            if filename in self._asset_mappings:
                organized_path = self._asset_mappings[filename]
                # Ensure root-absolute path
                if not organized_path.startswith('/'):
                    organized_path = '/' + organized_path
                return f'src="{organized_path}"'
            # Handle images in subdirectories (like img/image.png)
            for original, new_path in self._asset_mappings.items():
                if original.endswith(filename):
                    # Ensure root-absolute path
                    if not new_path.startswith('/'):
                        new_path = '/' + new_path
                    return f'src="{new_path}"'
            return match.group(0)
        
        content = re.sub(r'src="([^"]*\.(jpg|jpeg|png|gif|webp|svg|ico))"', replace_img_refs, content, flags=re.IGNORECASE)
        
        # Update background image references in CSS: url(image.png) -> url(assets/images/image.png)
        def replace_css_bg_refs(match):
            filename = match.group(1)
            if filename in self._asset_mappings:
                return f'url({self._asset_mappings[filename]})'
            # Handle images in subdirectories
            for original, new_path in self._asset_mappings.items():
                if original.endswith(filename):
                    return f'url({new_path})'
            return match.group(0)
        
        content = re.sub(r'url\(([^)]*\.(jpg|jpeg|png|gif|webp|svg))\)', replace_css_bg_refs, content, flags=re.IGNORECASE)
        
        # Update favicon references with organized structure
        def replace_favicon_refs(match):
            filename = match.group(1)
            if filename in self._asset_mappings:
                return f'href="{self._asset_mappings[filename]}"'
            # Handle organized favicon paths for generated favicon variations
            if filename.startswith('favicon-') and filename.endswith(('.ico', '.png')):
                return f'href="assets/icons/{filename}"'
            return match.group(0)
        
        content = re.sub(r'href="([^"]*\.ico)"', replace_favicon_refs, content)
        content = re.sub(r'href="([^"]*favicon[^"]*\.png)"', replace_favicon_refs, content)
        
        # Update manifest references: href="site.webmanifest" -> href="/site.webmanifest" (root-absolute)
        def replace_manifest_refs(match):
            filename = match.group(1)
            if filename == "site.webmanifest":
                return 'href="/site.webmanifest"'
            return match.group(0)
        
        content = re.sub(r'href="([^"]*\.webmanifest)"', replace_manifest_refs, content)
        
        # Update PWA manifest and icon references (specific to PWA, not favicon)
        def replace_pwa_refs(match):
            full_match = match.group(0)
            filename = match.group(1)
            
            # Skip if already organized or is a favicon
            if ('assets/' in filename or 'favicon-' in filename):
                return full_match
                
            # Only handle actual PWA icons and screenshots (not favicon variations)
            seo_filename = getattr(self.config, 'seo_filename', 'slither-io')
            is_pwa_icon = filename.startswith(f"{seo_filename}-icon-") and filename.endswith('.png')
            is_pwa_screenshot = filename.startswith(f"{seo_filename}-screenshot-") and filename.endswith('.png')
            
            if is_pwa_icon or is_pwa_screenshot:
                new_path = f"assets/pwa/{filename}"
                return full_match.replace(filename, new_path)
            return full_match
        
        # More specific regex to avoid favicon conflicts
        content = re.sub(r'"([^"]*(?:slither-io-|screenshot-)[^"]*\.png)"', replace_pwa_refs, content)
        
        # Update SEO image references
        def replace_seo_refs(match):
            filename = match.group(1)
            # Handle SEO optimized images (like slither-io.webp)
            if filename.endswith('.webp') and not filename.startswith('assets/'):
                # Check if it's a root SEO image that should stay in root for compatibility
                seo_patterns = ['slither-io', 'space-waves-pro', 'hero-image']
                if any(pattern in filename for pattern in seo_patterns):
                    return match.group(0)  # Keep in root for backward compatibility
            return match.group(0)
        
        content = re.sub(r'src="([^"]*\.webp)"', replace_seo_refs, content)
        
        return content
    
    def _get_page_output_path(self, page_key, is_game_page=False):
        """Determine organized output path for a page based on its type"""
        
        # Define page categories for organized structure
        legal_pages = {
            'privacybeleid', 'gebruiksvoorwaarden', 'cookie-beleid', 'dmca', 'ouder-informatie',
            'datenschutz', 'nutzungsbedingungen', 'cookies', 'eltern-information',
            'privacy', 'privacy-policy', 'terms', 'terms-of-service', 'cookies-policy', 'cookie-policy', 'parents-information', 'parent-info',
            'confidentialite', 'conditions-utilisation', 'politique-cookies', 'information-parents'
        }
        
        content_pages = {
            'over-ons', 'contact', 'ueber-uns', 'kontakt', 'about-us', 'a-propos'
        }
        
        # Main navigation pages stay in root
        root_pages = {'index', 'games'}
        
        if page_key in root_pages:
            # Main navigation pages stay in root
            subdir = ""
            filename = f"{page_key}.html"
        elif is_game_page:
            # Individual game pages go in /games/ subdirectory
            subdir = "games"
            filename = f"{page_key}.html"
        elif page_key in legal_pages:
            # Legal/policy pages go in /legal/ subdirectory
            subdir = "legal" 
            filename = f"{page_key}.html"
        elif page_key in content_pages:
            # General content pages go in /pages/ subdirectory
            subdir = "pages"
            filename = f"{page_key}.html"
        else:
            # Fallback to /pages/ for unknown content
            subdir = "pages"
            filename = f"{page_key}.html"
        
        # Create the full output path
        if subdir:
            output_dir = os.path.join(self.output_dir, subdir)
            os.makedirs(output_dir, exist_ok=True)
            return os.path.join(output_dir, filename), subdir
        else:
            return os.path.join(self.output_dir, filename), ""
    
    def _get_page_url(self, page_key, is_game_page=False):
        """Generate the correct URL for a page based on its organized location"""
        
        # Define page categories (same as in _get_page_output_path)
        legal_pages = {
            'privacybeleid', 'gebruiksvoorwaarden', 'cookie-beleid', 'dmca', 'ouder-informatie',
            'datenschutz', 'nutzungsbedingungen', 'cookies', 'eltern-information',
            'privacy', 'privacy-policy', 'terms', 'terms-of-service', 'cookies-policy', 'cookie-policy', 'parents-information', 'parent-info',
            'confidentialite', 'conditions-utilisation', 'politique-cookies', 'information-parents'
        }
        
        content_pages = {
            'over-ons', 'contact', 'ueber-uns', 'kontakt', 'about-us', 'a-propos'
        }
        
        # Main navigation pages stay in root
        root_pages = {'index', 'games'}
        
        if page_key in root_pages:
            return f"/{page_key}.html"
        elif is_game_page:
            return f"/games/{page_key}.html"
        elif page_key in legal_pages:
            return f"/legal/{page_key}.html"
        elif page_key in content_pages:
            return f"/pages/{page_key}.html"
        else:
            # Fallback to /pages/ for unknown content
            return f"/pages/{page_key}.html"
    
    def _update_template_context_for_assets(self, context):
        """Update template context to include asset path mappings"""
        if hasattr(self, '_asset_mappings'):
            # Add asset helper function to template context
            def asset_url(filename):
                """Helper function to get correct asset URL"""
                # Direct mapping
                if filename in self._asset_mappings:
                    return self._asset_mappings[filename]
                # Search for file in mappings
                for original, new_path in self._asset_mappings.items():
                    if original.endswith(filename):
                        return new_path
                # Fallback to original filename
                return filename
            
            context['asset_url'] = asset_url
            context['assets'] = self._asset_mappings
        
        return context
    
    def _generate_page(self, page_key, template_name):
        """Generate a single page with optimized performance"""
        try:
            # Get page configuration - merge simple config with regular config
            page_config = self.config.get_page_config(page_key)
            
            if hasattr(self.site_settings, 'SITE_NAME'):
                # Override with simple config data
                simple_config_data = self._get_simple_config_page_data(page_key)
                page_config.update(simple_config_data)
            
            # Merge with base context
            context = {**self.config.get_base_context(), **page_config}
            
            # Override canonical URL with organized structure for non-root pages
            if page_key != "index":
                organized_url = self._get_page_url(page_key, is_game_page=False)
                context["canonical_url"] = f"{self.config.site_url.rstrip('/')}{organized_url}"
            
            # Add games data for sidebar widget (prefer logo over hero)
            if hasattr(self, '_games') and self._games:
                context['games'] = self._get_random_games_for_widget(self._games)
                context['all_games'] = self._get_all_games_for_widget(self._games)
                # Add localized sidebar title based on language
                context['sidebar_title'] = self._get_sidebar_title()
            else:
                context['games'] = []
                context['all_games'] = []
                context['sidebar_title'] = "More Games"
            
            # Cache SEO filename to avoid repeated lookups
            seo_filename = getattr(self.config, 'seo_filename', 'space-waves-pro')
            
            # Add image optimization context (only if needed)
            if page_key == "index" or any(key in page_config for key in ["hero_image", "responsive_images"]):
                context["favicon_links"] = self.config.get_favicon_links()
                context["responsive_images"] = self.config.get_responsive_images(seo_filename)
                context["image_seo_attributes"] = self.config.get_image_seo_attributes(seo_filename)
            
            # Add hero image context for index page only
            if page_key == "index":
                context["hero_image"] = self.config.get_dynamic_hero_image()
                context["hero_image_config"] = self.config.get_hero_image_config(seo_filename)
                context["hero_seo_attributes"] = self.config.get_image_seo_attributes(seo_filename)
            
            # Update context with asset mappings for organized paths
            context = self._update_template_context_for_assets(context)
            
            # Load and render template
            template = self.env.get_template(template_name)
            html_content = template.render(**context)
            
            # Resolve asset links in rendered content
            html_content = self._resolve_asset_links(html_content)
            
            # Write to organized output path with atomic operation
            output_file, subdir = self._get_page_output_path(page_key, is_game_page=False)
            temp_file = f"{output_file}.tmp"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Atomic rename to prevent partial files
            os.rename(temp_file, output_file)
            
            # Show organized path in output
            display_path = f"{subdir}/{page_key}.html" if subdir else f"{page_key}.html"
            print(f"📄 Generated {display_path}")
            
        except Exception as e:
            print(f"❌ Error generating {page_key}.html: {e}")
            # Clean up temp file if it exists
            temp_file = os.path.join(self.output_dir, f"{page_key}.html.tmp")
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def create_manifest(self):
        """Create a site.webmanifest file using template"""
        try:
            # Load manifest template
            manifest_template_path = os.path.join(os.path.dirname(__file__), "static", "site.webmanifest")
            
            if os.path.exists(manifest_template_path):
                with open(manifest_template_path, 'r', encoding='utf-8') as f:
                    manifest_template = f.read()
                
                # Get SEO filename for template variables
                seo_filename = getattr(self.config, 'seo_filename', 'space-waves-pro')
                short_name = self.config.site_name[:12] if len(self.config.site_name) > 12 else self.config.site_name
                
                # Clean description (remove redundant words)
                description = self.config.centralized_description.replace(" online", "").replace("kostenlos", "kostenlos")
                if description.endswith("!"):
                    description = description[:-1]
                
                # English-only shortcut texts
                shortcut_texts = {"play_now": "Play Now", "play": "Play", "start": f"Start {self.config.site_name} instantly"}
                
                # Replace template variables
                manifest_content = manifest_template.replace("{{ site_name }}", self.config.site_name)
                manifest_content = manifest_content.replace("{{ short_name }}", short_name)
                manifest_content = manifest_content.replace("{{ background_color }}", self.config.css_bg)
                manifest_content = manifest_content.replace("{{ theme_color }}", self.config.theme_color)
                manifest_content = manifest_content.replace("{{ seo_filename }}", seo_filename)
                manifest_content = manifest_content.replace("{{ description }}", description)
                manifest_content = manifest_content.replace("{{ language }}", self.config.language)
                manifest_content = manifest_content.replace("{{ play_now_text }}", shortcut_texts["play_now"])
                manifest_content = manifest_content.replace("{{ play_text }}", shortcut_texts["play"])
                manifest_content = manifest_content.replace("{{ start_game_text }}", shortcut_texts["start"])
                
                # Write manifest file
                manifest_file = os.path.join(self.output_dir, "site.webmanifest")
                with open(manifest_file, 'w', encoding='utf-8') as f:
                    f.write(manifest_content)
                
                print("📄 Generated site.webmanifest with device-specific icons and screenshots")
            else:
                # Fallback to simple manifest if template not found
                self._create_simple_manifest()
                
        except Exception as e:
            print(f"⚠️  Error creating manifest: {e}")
            self._create_simple_manifest()
    
    def _create_simple_manifest(self):
        """Create an optimized PWA manifest"""
        seo_filename = getattr(self.config, 'seo_filename', 'space-waves-pro')
        short_name = self.config.site_name[:12] if len(self.config.site_name) > 12 else self.config.site_name
        
        # Clean description (remove redundant words)
        description = self.config.centralized_description.replace(" online", "").replace("kostenlos", "kostenlos")
        if description.endswith("!"):
            description = description[:-1]
        
        manifest = {
            "id": "/?source=pwa",
            "name": self.config.site_name,
            "short_name": short_name,
            "description": description,
            "start_url": "/",
            "display": "standalone",
            "background_color": self.config.css_bg,
            "theme_color": self.config.theme_color,
            "orientation": "any",
            "scope": "/",
            "lang": self.config.language,
            "dir": "ltr",
            "categories": ["games", "entertainment"],
            "prefer_related_applications": False,
            "icons": [
                {"src": f"/{seo_filename}-icon-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                {"src": f"/{seo_filename}-icon-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                {"src": f"/{seo_filename}-icon-192x192-maskable.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
                {"src": f"/{seo_filename}-icon-512x512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
            ],
            "screenshots": [
                {"src": f"/{seo_filename}-screenshot-mobile.png", "sizes": "390x844", "type": "image/png", "form_factor": "narrow", "label": f"{self.config.site_name} mobile gameplay"},
                {"src": f"/{seo_filename}-screenshot-desktop.png", "sizes": "1280x720", "type": "image/png", "form_factor": "wide", "label": f"{self.config.site_name} desktop gameplay"}
            ],
            "shortcuts": [
                {
                    "name": "Jetzt spielen",
                    "short_name": "Spielen",
                    "description": f"Starte {self.config.site_name} sofort",
                    "url": "/",
                    "icons": [{"src": f"/{seo_filename}-icon-96x96.png", "sizes": "96x96", "type": "image/png"}]
                }
            ]
        }
        
        manifest_file = os.path.join(self.output_dir, "site.webmanifest")
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print("📄 Generated optimized site.webmanifest")
    
    def create_robots_txt(self):
        """Create a robots.txt file"""
        robots_content = f"""User-agent: *
Allow: /

# Disallow admin and private areas
Disallow: /admin/
Disallow: /private/
Disallow: /*.json$
Disallow: /*.py$
Disallow: /*.md$

# Allow important files
Allow: /favicon.ico
Allow: /robots.txt
Allow: /sitemap.xml
Allow: /site.webmanifest

# Crawl delay (optional)
Crawl-delay: 1

Sitemap: {self.config.site_url.replace('http://', 'https://')}sitemap.xml
"""
        
        robots_file = os.path.join(self.output_dir, "robots.txt")
        with open(robots_file, 'w', encoding='utf-8') as f:
            f.write(robots_content)
        
        print("📄 Generated robots.txt")
    
    def create_sitemap_xml(self):
        """Create a sitemap.xml file"""
        
        # Use the actual generated pages instead of config-based pages
        generated_pages = self._get_pages_from_config()
        
        # Create sitemap pages from actually generated pages
        pages = []
        
        # Homepage
        pages.append({
            "url": "",
            "priority": "1.0", 
            "changefreq": "daily",
            "lastmod": None
        })
        
        # Add all other generated pages with organized URLs
        for page_key, template_name in generated_pages:
            if page_key != "index":  # Skip index as it's already added as homepage
                organized_url = self._get_page_url(page_key, is_game_page=False)
                pages.append({
                    "url": organized_url,
                    "priority": "0.8" if page_key in ["about-us", "ueber-uns", "a-propos", "over-ons"] else "0.5",
                    "changefreq": "monthly" if page_key in ["about-us", "ueber-uns", "a-propos", "over-ons", "contact", "kontakt"] else "yearly",
                    "lastmod": None
                })
        
        # Add image sitemap (always include for SEO)
        include_images = True
        
        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
"""
        
        # Append all generated game pages with organized URLs
        try:
            for game in getattr(self, "_games", []) or []:
                slug = game.get("slug")
                if slug:
                    organized_url = self._get_page_url(slug, is_game_page=True)
                    pages.append({
                        "url": organized_url,
                        "priority": "0.7",
                        "changefreq": "weekly",
                        "lastmod": None
                    })
        except Exception:
            pass

        for page in pages:
            # Ensure URLs use https and proper format
            if page['url'] == "":
                # Use clean URL for homepage (no .html extension)
                full_url = f"{self.config.site_url.rstrip('/')}"
            else:
                full_url = f"{self.config.site_url.rstrip('/')}/{page['url'].lstrip('/')}"
            
            # Ensure URL uses https
            if full_url.startswith("http://"):
                full_url = full_url.replace("http://", "https://")
            
            sitemap_content += f"""  <url>
    <loc>{full_url}</loc>
    <changefreq>{page['changefreq']}</changefreq>
    <priority>{page['priority']}</priority>
"""
            
            # Add images for homepage
            if include_images and page['url'] == "":
                # Add hero image
                seo_filename = getattr(self.config, 'seo_filename', 'space-waves-pro')
                image_url = f"{self.config.site_url}{seo_filename}.webp"
                # Ensure image URL uses https
                if image_url.startswith("http://"):
                    image_url = image_url.replace("http://", "https://")
                sitemap_content += f"""    <image:image>
      <image:loc>{image_url}</image:loc>
      <image:title>{self.config.site_name} - Play Free</image:title>
      <image:caption>Play {self.config.site_name} for free!</image:caption>
    </image:image>
"""
            
            sitemap_content += "  </url>\n"
        
        sitemap_content += "</urlset>"
        
        sitemap_file = os.path.join(self.output_dir, "sitemap.xml")
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        print("📄 Generated sitemap.xml")
    
    def _optimize_images(self):
        """Optimize images for SEO"""
        try:
            from .optimizer import ImageOptimizer
            # Use site-specific static directory
            input_dir = self.static_dir
            optimizer = ImageOptimizer(input_dir, self.output_dir)
            optimizer.optimize_all_images()
            optimizer._save_updated_config()
        except ImportError:
            print("⚠️  Pillow not installed. Install with: pip install Pillow")
            print("   Skipping image optimization...")
        except Exception as e:
            print(f"⚠️  Image optimization failed: {e}")
            print("   Continuing without image optimization...")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate website from template')
    parser.add_argument('--site-url', '-u', 
                       help='Site URL (e.g., https://example.com or example.com). If not provided, uses URL from language config')
    parser.add_argument('--output-dir', '-o', 
                       default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--language', '-l',
                       default=None,
                       help='Language code (e.g., en-US, fr-FR, nl-NL, de-DE). If not provided, uses config.py setting or de-DE')
    
    args = parser.parse_args()
    
    generator = SiteGenerator(output_dir=args.output_dir, site_url=args.site_url, language=args.language)
    generator.generate_site()
    generator.create_manifest()
    generator.create_robots_txt()
    generator.create_sitemap_xml()

if __name__ == "__main__":
    main()

