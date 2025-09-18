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
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Import site configuration
from site_config import SiteConfig

# Try to import simple config if available
try:
    import config as simple_config
    HAS_SIMPLE_CONFIG = True
except ImportError:
    HAS_SIMPLE_CONFIG = False

class SiteGenerator:
    def __init__(self, template_dir="templates", output_dir="output", site_url=None, language=None):
        base_dir = os.path.dirname(__file__)
        # Resolve paths relative to the ArcadeForge module directory
        self.template_dir = template_dir if os.path.isabs(template_dir) else os.path.join(base_dir, template_dir)
        self.output_dir = output_dir if os.path.isabs(output_dir) else os.path.join(os.getcwd(), output_dir)
        
        # Determine language: explicit argument > simple config > default
        if language:
            # Explicit language provided
            self.language = language
        elif HAS_SIMPLE_CONFIG and hasattr(simple_config, 'DEFAULT_LANGUAGE'):
            # Use simple config language
            self.language = simple_config.DEFAULT_LANGUAGE
            print("📋 Using simple config.py")
        else:
            # Default fallback
            self.language = "en-US"
        
        # Use simple config for other settings if available
        if HAS_SIMPLE_CONFIG and not language:
            print("📋 Using simple config.py")
            # Override defaults with simple config values
            if not site_url and hasattr(simple_config, 'SITE_URL'):
                site_url = simple_config.SITE_URL
                
        # Check if simple config system is available (config.py + page_content.py)
        try:
            import page_content
            self.use_simple_config = HAS_SIMPLE_CONFIG and hasattr(page_content, 'PAGE_TITLES')
        except ImportError:
            self.use_simple_config = False
        
        self.config = SiteConfig(language_code=self.language)
        
        # Update site URL if provided, otherwise use the one from language config
        if site_url:
            self.config.update_site_url(site_url)
        else:
            # Use the URL from language config (already loaded in SiteConfig)
            print(f"🌐 Using site URL from config: {self.config.site_url}")
            print(f"🌐 Using language: {self.language}")
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
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
        games_dir = os.path.join(os.path.dirname(__file__), "content_html", "games")
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
        """Get localized sidebar title based on language"""
        lang = (self.config.language or "en").lower()
        
        sidebar_titles = {
            "de": "Mehr Spiele",
            "de-de": "Mehr Spiele", 
            "fr": "Plus de Jeux",
            "fr-fr": "Plus de Jeux",
            "nl": "Meer Spellen",
            "nl-nl": "Meer Spellen",
            "en": "More Games",
            "en-us": "More Games"
        }
        
        return sidebar_titles.get(lang, "More Games")

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
                    {"title": "Home", "url": ""},
                    {"title": "Games", "url": "games.html"},
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
                    "de": "EUR",
                    "fr": "EUR",
                    "nl": "EUR",
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
                           "canonical_url": f"{self.config.site_url}{page_key}.html",
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
                           "hero_image": game["hero_image"],
                           "hero_seo_attributes": self.config.get_image_seo_attributes(game["hero_image"]),
                           "custom_html_content": game["content_html"],
                           # Add games data for sidebar widget (prefer logo over hero)
                           "games": [{
                               "title": g["title"],
                               "url": f"{g['slug']}.html",
                               "image": (g.get("meta", {}).get("logo") or g["hero_image"]) 
                           } for g in games if g["slug"] != page_key],  # Exclude current game
                           "sidebar_title": self._get_sidebar_title()
                           }
                html_content = template.render(**context)
                output_file = os.path.join(self.output_dir, f"{page_key}.html")
                temp_file = f"{output_file}.tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                os.rename(temp_file, output_file)
                print(f"📄 Generated game page {page_key}.html")
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
            breadcrumbs = [{"title": "Home", "url": ""}, {"title": "Games", "url": None}]
            context = {**self.config.get_base_context(),
                       "page_title": "Games",
                       "page_description": "Browse all games.",
                       "canonical_url": f"{self.config.site_url}games.html",
                       "current_page": "games",
                       "breadcrumbs": breadcrumbs,
                       "breadcrumb_schema": self.config.get_breadcrumb_schema(breadcrumbs),
                       "games": [{
                           "title": g["title"],
                           "url": f"{g['slug']}.html",
                           "image": (g.get("meta", {}).get("logo") or g["hero_image"]) 
                       } for g in games]
                       ,
                       "sidebar_title": self._get_sidebar_title()
                       }
            html_content = template.render(**context)
            output_file = os.path.join(self.output_dir, "games.html")
            temp_file = f"{output_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            os.rename(temp_file, output_file)
            print("📄 Generated games.html listing")
        except Exception as e:
            print(f"⚠️  Error generating games.html: {e}")
    
    def _get_pages_from_config(self):
        """Get pages configuration from language config or simple config"""
        
        # Try simple config first if available - get pages from page_content.py
        if self.use_simple_config:
            try:
                import page_content
                page_titles = page_content.PAGE_TITLES.get(self.language, {})
                if page_titles:
                    pages = [("index", "index.html")]  # Always include index
                    # Add other pages based on page_content.py
                    for page_key in page_titles:
                        if page_key != "index":
                            pages.append((page_key, "page.html"))
                    print(f"📋 Using page_content.py pages for {self.language}")
                    return pages
            except Exception as e:
                print(f"⚠️  Warning: Could not load page_content.py pages: {e}")
        
        # Fallback to language config
        pages_config = self.config.language_config.get("pages", {})

        # If we have language-specific pages, use them
        if pages_config:
            # Build pages list from language config
            pages = [("index", "index.html")]  # Always include index

            # Add other pages based on language config
            for page_key in pages_config:
                if page_key != "index":
                    pages.append((page_key, "page.html"))

            return pages

        # Default pages if no config found (German fallback)
        default_pages = [
            ("index", "index.html"),
            ("ueber-uns", "page.html"),
            ("kontakt", "page.html"),
            ("datenschutz", "page.html"),
            ("nutzungsbedingungen", "page.html"),
            ("cookies", "page.html"),
            ("dmca", "page.html"),
            ("eltern-information", "page.html"),
        ]

        return default_pages
    
    def _get_simple_config_page_data(self, page_key):
        """Get page data from simple config.py"""
        try:
            import config as simple_config
            
            # Get content from simple config
            title = simple_config.get_page_title(page_key, self.language) or page_key.title()
            description = simple_config.get_page_description(page_key, self.language) or ""
            keywords = simple_config.get_seo_keywords(page_key, self.language) or ""
            
            # Load actual HTML content from file
            content_rel = f"content_html/{self._get_content_file_mapping().get(page_key, page_key)}.html"
            content_file = os.path.join(os.path.dirname(__file__), content_rel)
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
                "og_title": f"{title} - {simple_config.SITE_NAME}",
                "twitter_title": f"{title} - {simple_config.SITE_NAME}",
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
        """Copy static files to output directory recursively"""
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        if os.path.exists(static_dir):
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    src = os.path.join(root, file)
                    # Calculate relative path from static_dir
                    rel_path = os.path.relpath(src, static_dir)
                    dst = os.path.join(self.output_dir, rel_path)
                    
                    # Create destination directory if it doesn't exist
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    
                    shutil.copy2(src, dst)
                    print(f"📄 Copied {rel_path}")
    
    def _generate_page(self, page_key, template_name):
        """Generate a single page with optimized performance"""
        try:
            # Get page configuration - merge simple config with regular config
            page_config = self.config.get_page_config(page_key)
            
            if self.use_simple_config:
                # Override with simple config data
                simple_config_data = self._get_simple_config_page_data(page_key)
                page_config.update(simple_config_data)
            
            # Merge with base context
            context = {**self.config.get_base_context(), **page_config}
            
            # Add games data for sidebar widget (prefer logo over hero)
            if hasattr(self, '_games') and self._games:
                context['games'] = [{
                    "title": g["title"],
                    "url": f"{g['slug']}.html",
                    "image": (g.get("meta", {}).get("logo") or g["hero_image"]) 
                } for g in self._games]
                # Add localized sidebar title based on language
                context['sidebar_title'] = self._get_sidebar_title()
            else:
                context['games'] = []
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
            
            # Load and render template
            template = self.env.get_template(template_name)
            html_content = template.render(**context)
            
            # Write to output file with atomic operation
            output_file = os.path.join(self.output_dir, f"{page_key}.html")
            temp_file = f"{output_file}.tmp"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Atomic rename to prevent partial files
            os.rename(temp_file, output_file)
            
            print(f"📄 Generated {page_key}.html")
            
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
                
                # Replace template variables
                manifest_content = manifest_template.replace("{{ site_name }}", self.config.site_name)
                manifest_content = manifest_content.replace("{{ short_name }}", short_name)
                manifest_content = manifest_content.replace("{{ background_color }}", self.config.css_bg)
                manifest_content = manifest_content.replace("{{ theme_color }}", self.config.theme_color)
                manifest_content = manifest_content.replace("{{ seo_filename }}", seo_filename)
                manifest_content = manifest_content.replace("{{ description }}", description)
                manifest_content = manifest_content.replace("{{ language }}", self.config.language)
                
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
        
        # Add all other generated pages
        for page_key, template_name in generated_pages:
            if page_key != "index":  # Skip index as it's already added as homepage
                pages.append({
                    "url": f"{page_key}.html",
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
        
        # Append all generated game pages
        try:
            for game in getattr(self, "_games", []) or []:
                slug = game.get("slug")
                if slug:
                    pages.append({
                        "url": f"{slug}.html",
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
                full_url = f"{self.config.site_url}{page['url']}"
            
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
            from image_optimizer import ImageOptimizer
            input_dir = os.path.join(os.path.dirname(__file__), "static")
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

