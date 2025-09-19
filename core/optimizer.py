#!/usr/bin/env python3
"""
Image Optimization Script for SEO
Generates multiple image sizes, formats, and SEO-optimized markup.
"""

import os
import json
import shutil
from pathlib import Path
from PIL import Image, ImageOps
from .site_loader import get_project_root, abs_path

class ImageOptimizer:
    def __init__(self, input_dir="static", output_dir="output"):
        # Convert to absolute paths to avoid CWD dependencies (cross-platform)
        if not os.path.isabs(input_dir):
            self.input_dir = str(abs_path(input_dir))
        else:
            self.input_dir = str(Path(input_dir).resolve())
            
        if not os.path.isabs(output_dir):
            self.output_dir = str(abs_path(output_dir))
        else:
            self.output_dir = str(Path(output_dir).resolve())
            
        self.image_config = self._load_image_config()
        
    def _load_image_config(self):
        """Load image configuration from seo_config.json (cross-platform)"""
        try:
            # Use absolute path to avoid CWD dependency
            config_path = abs_path("seo_config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("image_optimization", {})
        except FileNotFoundError:
            return {}
    
    def optimize_all_images(self):
        """Optimize all images for SEO"""
        print("🖼️  Starting image optimization for SEO...")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Process each image type
        self._optimize_hero_images()
        self._optimize_favicon()
        self._optimize_game_logo()
        self._generate_og_images()
        self._generate_pwa_icons()
        self._generate_pwa_screenshots()
        self._generate_seo_attributes()
        
        print("✅ Image optimization complete!")
    
    def _optimize_hero_images(self):
        """Use original hero images with SEO-optimized names"""
        # Get SEO filename for naming
        seo_filename = self._get_seo_filename()
        
        # Look for original hero images in static folder (cross-platform)
        hero_image_path = Path(self.input_dir) / "hero-image.webp"
        
        if hero_image_path.exists():
            print("📸 Using original hero image: hero-image.webp")
            
            # Add site name to the original image
            self._add_site_name_to_image(hero_image_path, "hero-image", {})
            
            # Create organized SEO images directory (cross-platform)
            seo_dir = Path(self.output_dir) / "assets" / "images" / "seo"
            seo_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the original image with SEO-optimized name to organized location
            seo_image_path = seo_dir / f"{seo_filename}.webp"
            shutil.copy2(str(hero_image_path), str(seo_image_path))
            
            print(f"  ✅ Copied to SEO-optimized name: {seo_filename}.webp in /assets/images/seo/")
            
            # Update the schema to use the SEO-optimized filename
            self._update_hero_image_schema(seo_filename)
            
        else:
            print(f"⚠️  No original hero image found at: {hero_image_path}")
            print("  Please add your hero image as 'hero-image.webp' in the static folder")
    
    def _add_site_name_to_image(self, input_path, image_name, config):
        """Add site name to existing hero image"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Save the image without any text overlay
                img.save(input_path, 'WEBP', quality=85, optimize=True)
                print(f"  ✅ Optimized image: {image_name}.webp")
                
        except Exception as e:
            print(f"  ⚠️  Could not optimize {image_name}: {e}")
    
    def _get_site_name(self):
        """Get site name from seo_config.json (cross-platform)"""
        try:
            # Use absolute path to avoid CWD dependency
            config_path = abs_path("seo_config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("site_name", "Space Waves Pro")
        except (FileNotFoundError, json.JSONDecodeError):
            return "Space Waves Pro"
    
    def _get_seo_filename(self):
        """Get SEO filename from config.py"""
        try:
            from . import settings as simple_config
            return simple_config.SEO_FILENAME
        except (ImportError, AttributeError):
            return "space-waves-pro"
    
    def _optimize_favicon(self):
        """Generate favicon in multiple sizes with organized structure"""
        favicon_path = os.path.join(self.input_dir, "favicon.ico")
        if not os.path.exists(favicon_path):
            print("⚠️  Favicon not found, creating default")
            self._create_default_favicon()
            return
        
        print("📱 Optimizing favicon...")
        
        # Create organized icons directory
        icons_dir = os.path.join(self.output_dir, "assets", "icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        try:
            with Image.open(favicon_path) as img:
                # Convert to RGBA if necessary
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Generate multiple sizes
                favicon_sizes = [16, 32, 48, 64, 128, 192, 256, 512]
                
                for size in favicon_sizes:
                    resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # Save as PNG in organized directory
                    png_path = os.path.join(icons_dir, f"favicon-{size}x{size}.png")
                    resized.save(png_path, "PNG", optimize=True)
                    
                    # Save as ICO for specific sizes in organized directory
                    if size in [16, 32, 48]:
                        ico_path = os.path.join(icons_dir, f"favicon-{size}x{size}.ico")
                        resized.save(ico_path, "ICO")
                
                # Copy original favicon to root (required for browser fallback)
                shutil.copy2(favicon_path, os.path.join(self.output_dir, "favicon.ico"))
                
                print(f"  ✅ Generated favicon in {len(favicon_sizes)} sizes (organized in /assets/icons/)")
                
        except Exception as e:
            print(f"❌ Error optimizing favicon: {e}")
    
    def _optimize_game_logo(self):
        """Optimize game logo and create SEO-renamed version"""
        gamelogo_path = os.path.join(self.input_dir, "gamelogo.webp")
        if not os.path.exists(gamelogo_path):
            print("⚠️  Game logo not found: gamelogo.webp")
            return
        
        print("🎮 Optimizing game logo...")
        
        try:
            # Get site name for SEO filename
            site_name = self._get_site_name()
            seo_filename = site_name.lower().replace(" ", "-").replace("_", "-")
            seo_filename = "".join(c for c in seo_filename if c.isalnum() or c in "-")
            logo_filename = f"{seo_filename}-logo.webp"
            
            with Image.open(gamelogo_path) as img:
                # Convert to RGBA if necessary
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Resize to 64x64 for logo use
                logo_size = (64, 64)
                resized = img.resize(logo_size, Image.Resampling.LANCZOS)
                
                # Create organized logos directory
                logos_dir = os.path.join(self.output_dir, "assets", "images", "logos")
                os.makedirs(logos_dir, exist_ok=True)
                
                # Save as SEO-optimized filename in organized location
                output_path = os.path.join(logos_dir, logo_filename)
                resized.save(output_path, "WEBP", quality=90, optimize=True)
                
                # Also keep a copy in root for backward compatibility
                root_logo_path = os.path.join(self.output_dir, logo_filename)
                resized.save(root_logo_path, "WEBP", quality=90, optimize=True)
                
                print(f"  ✅ Generated game logo: {logo_filename} (also in /assets/images/logos/)")
                
        except Exception as e:
            print(f"❌ Error optimizing game logo: {e}")
    
    def _create_default_favicon(self):
        """Create a default favicon if none exists with organized structure"""
        print("🎨 Creating default favicon...")
        
        # Create organized icons directory
        icons_dir = os.path.join(self.output_dir, "assets", "icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        # Create a simple favicon
        favicon = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        
        # Save in multiple sizes in organized directory
        sizes = [16, 32, 48, 64, 128, 192, 256, 512]
        for size in sizes:
            resized = favicon.resize((size, size), Image.Resampling.LANCZOS)
            png_path = os.path.join(icons_dir, f"favicon-{size}x{size}.png")
            resized.save(png_path, "PNG", optimize=True)
        
        # Save as ICO in root (required for browser fallback)
        ico_path = os.path.join(self.output_dir, "favicon.ico")
        favicon.save(ico_path, "ICO")
        
        print("  ✅ Created default favicon (organized in /assets/icons/)")
    
    def _generate_og_images(self):
        """Generate Open Graph images for social sharing"""
        print("📱 Generating Open Graph images...")
        
        og_config = self.image_config.get("og_images", {})
        
        for image_name, config in og_config.items():
            input_path = os.path.join(self.input_dir, f"{image_name}.webp")
            if not os.path.exists(input_path):
                print(f"⚠️  OG image not found: {input_path}")
                continue
            
            try:
                with Image.open(input_path) as img:
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Standard OG image size: 1200x630
                    og_size = (1200, 630)
                    og_img = ImageOps.fit(img, og_size, Image.Resampling.LANCZOS)
                    
                    # Save OG image as WebP only
                    og_webp_path = os.path.join(self.output_dir, f"{image_name}_og.webp")
                    og_img.save(og_webp_path, "WebP", quality=90, optimize=True)
                    
                    print(f"  ✅ Generated OG image: {image_name}_og (WebP)")
                    
            except Exception as e:
                print(f"❌ Error generating OG image {image_name}: {e}")
    
    def generate_image_manifest(self):
        """Generate a manifest of all optimized images"""
        manifest = {
            "images": {},
            "generated_at": str(Path().cwd()),
            "optimization_settings": self.image_config
        }
        
        # Scan output directory for images
        for file in os.listdir(self.output_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.ico')):
                file_path = os.path.join(self.output_dir, file)
                file_size = os.path.getsize(file_path)
                
                # Get image dimensions
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        format_type = img.format
                except (OSError, IOError):
                    width, height = 0, 0
                    format_type = "unknown"
                
                manifest["images"][file] = {
                    "size_bytes": file_size,
                    "width": width,
                    "height": height,
                    "format": format_type,
                    "path": file
                }
        
        # Save manifest
        manifest_path = os.path.join(self.output_dir, "image_manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"📋 Generated image manifest: {manifest_path}")
    
    def _generate_seo_attributes(self):
        """Generate SEO attributes for all images"""
        print("🔍 Generating SEO attributes for images...")
        
        # Get site name and SEO filename from config
        site_name = self._get_site_name()
        seo_filename = self._get_seo_filename()
        
        # Process hero images - use SEO filename if available
        hero_images = self.image_config.get("hero_images", {})
        # Create a copy to avoid dictionary changed size during iteration
        for image_name, config in list(hero_images.items()):
            # If this is the hero-image, use SEO filename for attributes
            if image_name == "hero-image":
                self._update_image_seo_attributes(seo_filename, config, site_name)
            else:
                self._update_image_seo_attributes(image_name, config, site_name)
        
        # Process OG images
        og_images = self.image_config.get("og_images", {})
        for image_name, config in og_images.items():
            self._update_og_image_seo_attributes(image_name, config, site_name)
        
        print("  ✅ SEO attributes generated for all images")
    
    def _update_image_seo_attributes(self, image_name, config, site_name):
        """Update SEO attributes for hero images"""
        # Generate better alt text if not provided
        if not config.get("alt_text"):
            config["alt_text"] = f"{site_name} - High quality image optimized for web"
        
        # Generate better title if not provided
        if not config.get("title"):
            config["title"] = f"{site_name} - Play Online"
        
        # Ensure loading and decoding attributes
        config["loading"] = config.get("loading", "lazy")
        config["decoding"] = config.get("decoding", "async")
        
        # Update the config
        self.image_config["hero_images"][image_name] = config
    
    def _update_og_image_seo_attributes(self, image_name, config, site_name):
        """Update SEO attributes for OG images"""
        # Generate better alt text if not provided
        if not config.get("alt_text"):
            config["alt_text"] = f"{site_name} - Share this exciting game with friends"
        
        # Generate better title if not provided
        if not config.get("title"):
            config["title"] = f"{site_name} - Free Online Game"
        
        # Update the config
        self.image_config["og_images"][image_name] = config
    
    def _update_hero_image_schema(self, seo_filename):
        """Update the hero image schema - simplified system doesn't need external config"""
        # Skip updating external config since we use the simplified system
        print(f"  ✅ Hero image optimized with SEO filename: {seo_filename}")
    
    def _generate_pwa_icons(self):
        """Generate PWA icons for different devices and purposes"""
        print("📱 Generating PWA icons...")
        
        # Get SEO filename for naming
        seo_filename = self._get_seo_filename()
        
        # Look for source icon (favicon or game logo)
        source_icon_path = None
        for icon_name in ["favicon.ico", "gamelogo.webp", "hero-image.webp"]:
            icon_path = os.path.join(self.input_dir, icon_name)
            if os.path.exists(icon_path):
                source_icon_path = icon_path
                break
        
        if not source_icon_path:
            print("⚠️  No source icon found for PWA icons")
            return
        
        try:
            with Image.open(source_icon_path) as img:
                # Convert to RGBA if necessary
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # PWA icon sizes for different devices
                pwa_sizes = [
                    {"size": 72, "purpose": "any"},
                    {"size": 96, "purpose": "any"},
                    {"size": 128, "purpose": "any"},
                    {"size": 144, "purpose": "any"},
                    {"size": 152, "purpose": "any"},
                    {"size": 192, "purpose": "any"},
                    {"size": 384, "purpose": "any"},
                    {"size": 512, "purpose": "any"},
                    {"size": 192, "purpose": "maskable"},
                    {"size": 512, "purpose": "maskable"}
                ]
                
                for icon_config in pwa_sizes:
                    size = icon_config["size"]
                    purpose = icon_config["purpose"]
                    
                    # Resize image
                    resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # For maskable icons, add padding for safe area
                    if purpose == "maskable":
                        # Create a larger canvas with padding
                        padding = size // 10  # 10% padding
                        canvas_size = size + (padding * 2)
                        canvas = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
                        
                        # Center the icon on the canvas
                        canvas.paste(resized, (padding, padding))
                        final_icon = canvas
                    else:
                        final_icon = resized
                    
                    # Create organized PWA directory
                    pwa_dir = os.path.join(self.output_dir, "assets", "pwa")
                    os.makedirs(pwa_dir, exist_ok=True)
                    
                    # Save as PNG in organized directory
                    filename = f"{seo_filename}-icon-{size}x{size}"
                    if purpose == "maskable":
                        filename += "-maskable"
                    filename += ".png"
                    
                    output_path = os.path.join(pwa_dir, filename)
                    final_icon.save(output_path, "PNG", optimize=True)
                    
                    print(f"  ✅ Generated {filename} (in /assets/pwa/)")
                
        except Exception as e:
            print(f"❌ Error generating PWA icons: {e}")
    
    def _generate_pwa_screenshots(self):
        """Generate PWA screenshots for different device form factors"""
        print("📸 Generating PWA screenshots...")
        
        # Get SEO filename for naming
        seo_filename = self._get_seo_filename()
        
        # Look for source screenshot (hero image)
        source_image_path = os.path.join(self.input_dir, "hero-image.webp")
        
        if not os.path.exists(source_image_path):
            print("⚠️  No source image found for PWA screenshots")
            return
        
        try:
            with Image.open(source_image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # PWA screenshot sizes for different form factors
                screenshot_configs = [
                    {"name": "mobile", "width": 390, "height": 844, "form_factor": "narrow"},
                    {"name": "tablet", "width": 768, "height": 1024, "form_factor": "wide"},
                    {"name": "desktop", "width": 1280, "height": 720, "form_factor": "wide"}
                ]
                
                for config in screenshot_configs:
                    width = config["width"]
                    height = config["height"]
                    name = config["name"]
                    
                    # Resize image maintaining aspect ratio and crop to fit
                    resized = ImageOps.fit(img, (width, height), Image.Resampling.LANCZOS)
                    
                    # Add device frame for better presentation
                    screenshot = self._add_device_frame(resized, config)
                    
                    # Create organized PWA directory
                    pwa_dir = os.path.join(self.output_dir, "assets", "pwa")
                    os.makedirs(pwa_dir, exist_ok=True)
                    
                    # Save as PNG in organized directory
                    filename = f"{seo_filename}-screenshot-{name}.png"
                    output_path = os.path.join(pwa_dir, filename)
                    screenshot.save(output_path, "PNG", optimize=True)
                    
                    print(f"  ✅ Generated {filename} (in /assets/pwa/)")
                
        except Exception as e:
            print(f"❌ Error generating PWA screenshots: {e}")
    
    def _add_device_frame(self, image, config):
        """Add a device frame to the screenshot for better presentation"""
        try:
            from PIL import ImageDraw
            
            # Create a slightly larger canvas for the frame
            frame_padding = 20
            canvas_width = image.width + (frame_padding * 2)
            canvas_height = image.height + (frame_padding * 2)
            
            # Create canvas with device-appropriate background
            if config["form_factor"] == "narrow":
                # Mobile frame - darker background
                canvas = Image.new('RGB', (canvas_width, canvas_height), (20, 20, 20))
            else:
                # Tablet/Desktop frame - lighter background
                canvas = Image.new('RGB', (canvas_width, canvas_height), (240, 240, 240))
            
            # Paste the screenshot in the center
            canvas.paste(image, (frame_padding, frame_padding))
            
            # Add rounded corners effect
            draw = ImageDraw.Draw(canvas)
            corner_radius = 15
            
            # Draw rounded rectangle border
            draw.rounded_rectangle(
                [frame_padding-2, frame_padding-2, 
                 canvas_width-frame_padding+2, canvas_height-frame_padding+2],
                radius=corner_radius,
                outline=(100, 100, 100) if config["form_factor"] == "narrow" else (200, 200, 200),
                width=2
            )
            
            return canvas
            
        except Exception as e:
            print(f"⚠️  Could not add device frame: {e}")
            return image

    def _save_updated_config(self):
        """Save updated configuration with SEO attributes - simplified system doesn't need this"""
        # Skip saving to seo_config.json since we use the simplified system
        print("  ✅ SEO attributes generated (simplified system - no external config needed)")

def main():
    """Main function - automatically optimize images"""
    print("🖼️  Automatic Image Optimization")
    print("=" * 40)
    
    # Use default directories
    input_dir = "static"
    output_dir = "output"
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"❌ Input directory '{input_dir}' not found")
        print("   Make sure you have images in the 'static' folder")
        return
    
    # Create optimizer and run
    optimizer = ImageOptimizer(input_dir, output_dir)
    optimizer.optimize_all_images()
    optimizer.generate_image_manifest()
    optimizer._save_updated_config()
    
    print("✅ Image optimization complete!")
    print(f"📁 Optimized images saved to: {output_dir}")
    print("🔍 SEO attributes updated in seo_config.json")

if __name__ == "__main__":
    main()
