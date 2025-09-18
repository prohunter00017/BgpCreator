#!/usr/bin/env python3
"""
ARCADEFORGE SITE CONFIGURATION
==============================

This is the MAIN configuration file - edit this to customize your site!
All other config files will be generated from this one.
"""

# =============================================================================
# BASIC SITE SETTINGS (EDIT THESE!)
# =============================================================================

SITE_NAME = "Slither Io"
SITE_URL = "https://slitheriofree.net/"
SITE_DOMAIN = "slitheriofree.net"

# Game embed URL - where your game is hosted
GAME_EMBED_URL = "https://gulper.io/"

# Contact information
CONTACT_EMAIL = "support@slitheriofree.net"
CONTACT_PHONE = "+493012345678"

# Google Analytics ID (optional)
GOOGLE_ANALYTICS_ID = "G-FGRWDEFQY4"

# =============================================================================
# LANGUAGE SETTINGS - CHANGE THIS LINE TO SWITCH LANGUAGES!
# =============================================================================

DEFAULT_LANGUAGE = "nl-NL"  # Options: "de-DE", "en-US", "fr-FR", "nl-NL"

# =============================================================================
# INDEX PAGE CONTENT (THE ONLY CONTENT YOU NEED TO EDIT!)
# =============================================================================

# Homepage title (same for all languages - keep it simple)
INDEX_TITLE = "Slither Io"

# Homepage description - EDIT THIS for your game
INDEX_DESCRIPTION = "Spiele Slither Io online kostenlos! Steuere deine Schlange, wachse mit Pellets und besiege Gegner in diesem spannenden Mehrspieler io Spiel."

# Homepage SEO keywords - EDIT THIS for your game  
INDEX_SEO_KEYWORDS = "slither io, io spiele, kostenlos spielen, schlangen spiel, mehrspieler online, browser spiel, arcade spiel, online spiel kostenlos"

# =============================================================================
# SOCIAL MEDIA & SEO
# =============================================================================

# Social media links (optional - leave empty if not needed)
SOCIAL_MEDIA = {
    "facebook": "https://www.facebook.com/slitheriofree",
    "twitter": "https://twitter.com/slitheriofree",
    "youtube": "https://www.youtube.com/@slitheriofree",
    "app_store": "https://apps.apple.com/de/app/slither-io/id1091944550",
    "play_store": "https://play.google.com/store/apps/details?id=air.com.hypah.io.slither&hl=de&gl=DE"
}

# SEO filename (used for image names and URLs)
SEO_FILENAME = "slither-io"

# =============================================================================
# COMPANY/FOUNDER INFO (for structured data)
# =============================================================================

FOUNDER_INFO = {
    "name": "Game Creator",
    "job_title": "Creator",
    "twitter": "https://twitter.com/gamecreator",
    "linkedin": "https://www.linkedin.com/in/gamecreator"
}

COMPANY_ADDRESS = {
    "street": "Alexanderplatz 5",
    "city": "Berlin",
    "postal_code": "10117",
    "country": "DE"
}

# =============================================================================
# ADVANCED SETTINGS (usually don't need to change)
# =============================================================================

# Image optimization settings
IMAGE_SIZES = [
    {"name": "mobile", "width": 480, "height": 270},
    {"name": "tablet", "width": 768, "height": 432},
    {"name": "desktop", "width": 1200, "height": 675},
    {"name": "large", "width": 1920, "height": 1080}
]

# Site pages and their priorities for sitemap
SITE_PAGES = [
    {"url": "", "priority": "1.0", "changefreq": "daily"},  # Homepage
    {"url": "ueber-uns.html", "priority": "0.8", "changefreq": "monthly"},
    {"url": "kontakt.html", "priority": "0.7", "changefreq": "monthly"},
    {"url": "datenschutz.html", "priority": "0.5", "changefreq": "yearly"},
    {"url": "nutzungsbedingungen.html", "priority": "0.5", "changefreq": "yearly"},
    {"url": "cookies.html", "priority": "0.5", "changefreq": "yearly"},
    {"url": "dmca.html", "priority": "0.3", "changefreq": "yearly"},
    {"url": "eltern-information.html", "priority": "0.6", "changefreq": "monthly"}
]

# =============================================================================
# HELPER FUNCTIONS (don't edit these)
# =============================================================================

def get_page_title(page_key, language_code=None):
    """Get page title - index from config, others from page_content.py"""
    if page_key == "index":
        return INDEX_TITLE
    
    # Import static page content
    try:
        from page_content import get_page_title as get_static_title
        return get_static_title(page_key, language_code or DEFAULT_LANGUAGE)
    except ImportError:
        return page_key.title()

def get_page_description(page_key, language_code=None):
    """Get page description - index from config, others from page_content.py"""
    if page_key == "index":
        return INDEX_DESCRIPTION
    
    # Import static page content
    try:
        from page_content import get_page_description as get_static_description
        return get_static_description(page_key, language_code or DEFAULT_LANGUAGE)
    except ImportError:
        return ""

def get_seo_keywords(page_key, language_code=None):
    """Get SEO keywords - only index has keywords (keep it simple)"""
    if page_key == "index":
        return INDEX_SEO_KEYWORDS
    
    # No keywords for other pages - keep it simple
    return ""

def get_site_config():
    """Get all configuration as a dictionary"""
    return {
        "site_name": SITE_NAME,
        "site_url": SITE_URL,
        "site_domain": SITE_DOMAIN,
        "game_embed_url": GAME_EMBED_URL,
        "contact_email": CONTACT_EMAIL,
        "contact_phone": CONTACT_PHONE,
        "google_analytics_id": GOOGLE_ANALYTICS_ID,
        "default_language": DEFAULT_LANGUAGE,
        "index_title": INDEX_TITLE,
        "index_description": INDEX_DESCRIPTION,
        "index_seo_keywords": INDEX_SEO_KEYWORDS,
        "social_media": SOCIAL_MEDIA,
        "seo_filename": SEO_FILENAME,
        "founder_info": FOUNDER_INFO,
        "company_address": COMPANY_ADDRESS,
        "image_sizes": IMAGE_SIZES,
        "site_pages": SITE_PAGES
    }

if __name__ == "__main__":
    import json
    config = get_site_config()
    print(json.dumps(config, indent=2, ensure_ascii=False))
