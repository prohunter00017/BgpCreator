#!/usr/bin/env python3
"""
MINIMAL SITE CONFIG
===================

This is a minimal replacement for the complex site_config.py
It only provides the essential functionality needed by generate_site.py
"""

import json
import os
from datetime import datetime

class SiteConfig:
    def __init__(self, language_code="en-US"):
        # Initialize cross-platform path handling
        self.static_dir = None
        # Import from the simple config if available
        try:
            from . import settings as simple_config
            self._site_name = simple_config.SITE_NAME
            self.site_url = simple_config.SITE_URL
            self.site_domain = simple_config.SITE_DOMAIN
            self.game_embed_url = simple_config.GAME_EMBED_URL
            self.google_analytics_id = simple_config.GOOGLE_ANALYTICS_ID
            self.seo_filename = simple_config.SEO_FILENAME
        except ImportError:
            # Fallback defaults
            self._site_name = "Slither Io"
            self.site_url = "https://slitheriofree.net/"
            self.site_domain = "slitheriofree.net"
            self.game_embed_url = "https://gulper.io/"
            self.google_analytics_id = "G-FGRWDEFQY4"
            self.seo_filename = "slither-io"
        
        self.language = language_code
        self.current_year = datetime.now().year
        self.support_email = f"support@{self.site_domain}"
        
        # Minimal required properties
        self.language_config = {}
        self.seo_config = {
            "site_name": self.site_name,
            "site_url": self.site_url,
            "site_domain": self.site_domain,
            "seo_filename": self.seo_filename,
            "google_analytics_id": self.google_analytics_id,
            "game_embed": {"url": self.game_embed_url},
            "image_optimization": {}
        }

    def get_page_config(self, page_key):
        """Get page configuration with appropriate schemas"""
        # Localized labels (duplicate minimal map to avoid circular deps)
        lang = (self.language or "en").lower()
        lang_short = lang.split('-')[0]
        nav_titles = {
            "de": {"home": "Home"},
            "en": {"home": "Home"},
            "fr": {"home": "Accueil"},
            "nl": {"home": "Home"},
        }.get(lang_short, {"home": "Home"})

        # Defaults
        page_title = page_key.title()
        canonical_url = f"{self.site_url}{page_key}.html"  # Will be overridden in _generate_page for organized structure
        breadcrumbs = [
            {"title": nav_titles["home"], "url": "/"},
            {"title": page_title, "url": None}
        ]

        # Special-case index page: use root canonical and Home label
        if page_key == "index":
            page_title = self.centralized_game_name
            canonical_url = self.site_url.rstrip('/')
            breadcrumbs = [
                {"title": nav_titles["home"], "url": "/"},
                {"title": nav_titles["home"], "url": None}
            ]

        config = {
            "page_title": page_title,
            "page_description": f"Learn more about {self.site_name}",
            "canonical_url": canonical_url,
            "current_page": page_key,
            "breadcrumbs": breadcrumbs,
            "custom_html_content": f"content_html/{page_key}.html"
        }
        
        # Add specific schemas based on page type
        if page_key == "index":
            # Index page gets: SoftwareApplication + FAQ schemas (WebSite now in base context)
            config.update({
                "software_application_schema": self.get_software_application_schema(),
                "faq_schema": self.get_faq_schema()
            })
        
        # All pages get breadcrumb schema
        config["breadcrumb_schema"] = self.get_breadcrumb_schema(config["breadcrumbs"])
        
        return config
    
    def get_base_context(self):
        """Get minimal base context for templates - Organization + WebSite schemas on ALL pages"""
        # English only navigation titles
        nav_titles = {"home": "Home", "games": "Games", "about": "About", "contact": "Contact", "privacy": "Privacy"}
        footer_titles = {"privacy": "Privacy Policy", "terms": "Terms of Service", "contact": "Contact", "dmca": "DMCA"}

        # Dark Theme CSS design tokens - matching escaperoad.io
        # Try to get from settings first, then use defaults
        try:
            from . import settings as simple_config
            css_bg = getattr(simple_config, "CSS_BG", "#000000")
            css_fg = getattr(simple_config, "CSS_FG", "#ffffff")
            css_muted = getattr(simple_config, "CSS_MUTED", "#999999")
            css_brand = getattr(simple_config, "CSS_BRAND", "#4a9eff")
            css_brand_2 = getattr(simple_config, "CSS_BRAND_2", "#357acc")
            css_surface = getattr(simple_config, "CSS_SURFACE", "#222222")
            css_radius = getattr(simple_config, "CSS_RADIUS", "8px")
            css_font_family = getattr(simple_config, "CSS_FONT_FAMILY", "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif")
            container_max_width = getattr(simple_config, "CONTAINER_MAX_WIDTH", "1400px")
        except ImportError:
            # Fallback to defaults if settings not available
            css_bg = "#000000"
            css_fg = "#ffffff"
            css_muted = "#999999"
            css_brand = "#4a9eff"
            css_brand_2 = "#357acc"
            css_surface = "#222222"
            css_radius = "8px"
            css_font_family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
            container_max_width = "1400px"

        return {
            "site_name": self.site_name,
            "site_url": self.site_url,
            "site_domain": self.site_domain,
            "support_email": self.support_email,
            "current_year": self.current_year,
            "language": self.language,
            "locale": self.language,
            "google_analytics_id": self.google_analytics_id,
            "game_embed": {"url": self.game_embed_url},
            "game_name": self.centralized_game_name,
            "navigation": [
                {"title": nav_titles["home"], "url": "/index.html", "key": "index"},
                {"title": nav_titles["games"], "url": "/games.html", "key": "games"},
                {"title": nav_titles["about"], "url": self._get_about_url(), "key": "about"},
                {"title": nav_titles["contact"], "url": self._get_contact_url(), "key": "contact"},
                {"title": nav_titles["privacy"], "url": self._get_privacy_url(), "key": "privacy"}
            ],
            "footer_links": [
                {"title": footer_titles["privacy"], "url": self._get_privacy_url()},
                {"title": footer_titles["terms"], "url": self._get_terms_url()},
                {"title": footer_titles["contact"], "url": self._get_contact_url()},
                {"title": footer_titles["dmca"], "url": "/legal/dmca.html"}
            ],
            "robots_content": "index,follow",
            "og_type": "website",
            "og_image": f"assets/images/seo/{self.seo_filename}.webp",
            "theme_color": "#0369a1",
            # CSS tokens for templates
            "css_bg": css_bg,
            "css_fg": css_fg,
            "css_muted": css_muted,
            "css_brand": css_brand,
            "css_brand_2": css_brand_2,
            "css_surface": css_surface,
            "css_radius": css_radius,
            "css_font_family": css_font_family,
            "container_max_width": container_max_width,
            # Organization + WebSite schemas on ALL pages
            "organization_schema": self.get_organization_schema(),
            "website_schema": self.get_website_schema()
        }
    
    def get_dynamic_hero_image(self):
        """Get hero image filename with correct path - use the same logic as image optimizer"""
        # The image optimizer uses seo_config fallback, so we need to match that
        # Until we fully migrate, use the fallback that image_optimizer.py uses
        try:
            from . import settings as simple_config
            return f"/assets/images/seo/{simple_config.SEO_FILENAME}.webp"
        except (ImportError, AttributeError):
            return "/assets/images/seo/space-waves-pro.webp"  # Match image optimizer fallback
    
    def _get_about_url(self):
        """Get About page URL - English only"""
        return "/pages/about-us.html"
    
    def _get_contact_url(self):
        """Get Contact page URL - English only"""
        return "/pages/contact.html"
    
    def _get_privacy_url(self):
        """Get Privacy page URL - English only"""
        return "/legal/privacy-policy.html"
    
    def _get_terms_url(self):
        """Get Terms page URL - English only"""
        return "/legal/terms-of-service.html"
    
    def update_site_url(self, new_url):
        """Update site URL"""
        if not new_url.startswith(('http://', 'https://')):
            new_url = f"https://{new_url}"
        self.site_url = new_url.rstrip('/') + '/'
        self.site_domain = self.site_url.split('://')[1].split('/')[0]
        self.support_email = f"support@{self.site_domain}"
        print(f"✅ Updated site URL to: {self.site_url}")
    
    # Additional properties needed by generate_site.py
    @property
    def centralized_description(self):
        try:
            from . import settings as simple_config
            return getattr(simple_config, 'INDEX_DESCRIPTION', f"Play {self.site_name} free online!")
        except (ImportError, AttributeError):
            return f"Play {self.site_name} free online!"
    
    @property 
    def centralized_game_name(self):
        try:
            from . import settings as simple_config
            return simple_config.INDEX_TITLE
        except (ImportError, AttributeError):
            return self.site_name
    
    @property
    def site_name(self):
        return self._site_name
    
    @site_name.setter
    def site_name(self, value):
        self._site_name = value
    
    @property
    def css_bg(self):
        return "#ffffff"
    
    @property
    def theme_color(self):
        return "#0369a1"
    
    def get_favicon_links(self):
        """Get favicon links with root-absolute paths"""
        return [
            {"rel": "icon", "type": "image/x-icon", "href": "/assets/images/favicon.ico"},
            {"rel": "icon", "type": "image/png", "sizes": "32x32", "href": "/assets/icons/favicon-32x32.png"}
        ]
    
    def get_breadcrumb_schema(self, breadcrumbs):
        """Get breadcrumb schema"""
        items = []
        for i, crumb in enumerate(breadcrumbs):
            item = {"@type": "ListItem", "position": i + 1, "name": crumb["title"]}
            if crumb.get("url") is not None:
                if crumb["url"] == "":
                    item["item"] = self.site_url.rstrip('/')
                else:
                    # Normalize URL concatenation to avoid double slashes
                    url = crumb['url']
                    item["item"] = f"{self.site_url.rstrip('/')}/{url.lstrip('/')}"
            items.append(item)
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList", 
            "itemListElement": items
        }
    
    def get_faq_schema(self):
        """Get FAQ schema for index page - load from static/faq.json"""
        try:
            # Use the static directory set by generator, fallback to site loader
            if hasattr(self, 'static_dir') and self.static_dir:
                static_dir = self.static_dir
            else:
                # Try to get static directory from site loader if available
                try:
                    from .site_loader import get_site_paths
                    # Use current site paths if available (this will be None for legacy mode)
                    site_paths = get_site_paths(getattr(self, '_current_site', None))
                    static_dir = site_paths['static_dir']
                except (ImportError, AttributeError, TypeError):
                    # Fallback to legacy path
                    project_root = os.path.dirname(os.path.dirname(__file__))
                    static_dir = os.path.join(project_root, "static")
            
            faq_file = os.path.join(static_dir, "faq.json")
            with open(faq_file, 'r', encoding='utf-8') as f:
                faq_schema = json.load(f)
            
            # Add @id field for consistency
            faq_schema["@id"] = f"{self.site_url}#faq"
            # Ensure language matches current site language
            faq_schema["inLanguage"] = (self.language or "en-US").split('-')[0]
            return faq_schema
        except FileNotFoundError:
            print(f"⚠️  Warning: FAQ file not found")
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Invalid JSON in FAQ file: {e}")
        except Exception as e:
            print(f"⚠️  Warning: Could not load FAQ schema: {e}")
            
        # Return minimal fallback FAQ schema for all exception cases
            return {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "How do I play Slither Io?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Control your snake with mouse movements and use boost to grow faster by eating pellets and avoiding other snakes."
                        }
                    }
                ]
            }
    
    def _generate_automatic_description(self, page_type, title):
        """Generate automatic description"""
        return f"Learn more about {title} - {self.site_name}"
    
    def get_organization_schema(self):
        """Get Organization schema for SEO"""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "@id": f"{self.site_url}#organization",
            "name": self.site_name,
            "url": self.site_url,
            "description": self.centralized_description,
            "email": self.support_email,
            "logo": {
                "@type": "ImageObject",
                "url": f"{self.site_url}logo.png",
                "width": 1024,
                "height": 1024
            },
            "sameAs": [
                f"{self.site_url.rstrip('/')}{self._get_about_url()}"
            ]
        }
    
    def get_website_schema(self):
        """Get WebSite schema for SEO"""
        return {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "@id": f"{self.site_url}#website",
            "name": self.site_name,
            "url": self.site_url,
            "description": self.centralized_description,
            "publisher": {
                "@id": f"{self.site_url}#organization"
            }
        }
    
    def get_software_application_schema(self):
        """Get SoftwareApplication schema for INDEX page only"""
        return {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "@id": f"{self.site_url}#software",
            "name": self.centralized_game_name,
            "url": self.site_url,
            "description": self.centralized_description,
            "applicationCategory": "GameApplication",
            "operatingSystem": "Web Browser",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.5",
                "bestRating": "5",
                "ratingCount": "1250",
                "worstRating": "1"
            }
        }
    
    def get_game_software_application_schema(self, game_title, game_slug, game_description=None, game_rating=None):
        """Get CUSTOM SoftwareApplication schema for individual GAME pages"""
        import hashlib
        
        # Generate unique ratings per game based on slug
        try:
            h = int(hashlib.sha256(game_slug.encode('utf-8')).hexdigest()[:8], 16)
        except Exception:
            h = sum(ord(c) for c in game_slug)
        
        # Rating between 3.5 and 4.9
        rating_value = round(3.5 + ((h % 150) / 100.0), 1)
        if rating_value > 4.9:
            rating_value = 4.9
            
        # Rating count between 150 and 3500
        rating_count = 150 + (h % 3351)
        
        # Use custom rating if provided
        if game_rating:
            rating_value = game_rating.get("ratingValue", rating_value)
            rating_count = game_rating.get("ratingCount", rating_count)
        
        return {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "@id": f"{self.site_url}{game_slug}.html#software",
            "name": game_title,
            "url": f"{self.site_url}{game_slug}.html",
            "description": game_description or f"Play {game_title} free online - {self.site_name}",
            "applicationCategory": "GameApplication",
            "operatingSystem": "Web Browser",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": str(rating_value),
                "bestRating": "5",
                "ratingCount": str(rating_count),
                "worstRating": "3"
            },
            "isPartOf": {
            "@type": "WebSite",
                "@id": f"{self.site_url}#website"
            }
        }
    
    
    def get_responsive_images(self, image_name):
        """Get responsive images (minimal implementation)"""
        return []
    
    def get_image_seo_attributes(self, image_name):
        """Get image SEO attributes"""
        return {
            "alt": f"{self.site_name} - Play Free Online",
            "title": f"{self.site_name}",
            "loading": "lazy",
            "decoding": "async"
        }
    
    def get_hero_image_config(self, image_name):
        """Get hero image config"""
        return {
            "alt_text": f"{self.site_name} - Play Free Online",
            "title": f"{self.site_name}",
            "loading": "eager",
            "decoding": "async"
        }
