# BgpCreator Developer Documentation

## Overview

**BgpCreator** (also known as ArcadeForge) is a sophisticated multi-site static site generator specifically designed for creating game websites. Built with Python and Jinja2 templating, it transforms content into professional, SEO-optimized websites with organized structure and modern features.

## Key Features

- **Multi-Site Support**: Generate multiple websites from a single codebase
- **Dark Theme Design**: Professional dark theme matching modern gaming aesthetics  
- **High Performance**: 46x faster incremental builds (0.07s vs original ~5s)
- **SEO Optimized**: Automatic structured data, meta tags, and sitemaps
- **Game Integration**: Seamless iframe game embedding with fullscreen support
- **Responsive Design**: Mobile-first design with progressive web app features
- **Asset Optimization**: Automatic image optimization and compression

## System Requirements

- Python 3.8+
- Pillow (PIL) for image processing
- Jinja2 for templating

## Project Structure

```
BgpCreator/
├── core/                           # Core system modules
│   ├── __init__.py                # Package initialization
│   ├── config.py                  # Configuration management
│   ├── generator_refactored.py    # Main site generator (46x faster)
│   ├── optimizer.py               # Asset optimization
│   └── site_loader.py             # Site loading utilities
├── templates/                      # Jinja2 templates
│   ├── base.html                  # Base template with dark theme
│   ├── index.html                 # Homepage template
│   ├── game-iframe.html           # Game iframe component
│   ├── article-content.html       # Article content template
│   └── games-widget.html          # Games widget template
├── sites/                         # Site-specific content
│   └── [domain.com]/              # Domain-specific organization
│       ├── content_html/          # HTML content files
│       │   └── games/             # Game content
│       ├── static/                # Static assets
│       └── settings.py            # Site configuration
├── output/                        # Generated websites
│   └── [domain.com]/              # Generated site output
│       ├── assets/                # Optimized assets
│       ├── games/                 # Game pages
│       └── index.html             # Generated homepage
└── main.py                        # Entry point
```

## Quick Start

### 1. Basic Usage

Generate a website for a specific domain:

```bash
cd BgpCreator
python main.py --site [domain.com]
```

### 2. Configuration

Edit `sites/[domain.com]/settings.py` to customize your site:

```python
# Basic site settings
SITE_NAME = "Your Game Site"
SITE_URL = "https://yourdomain.com/"
SITE_DOMAIN = "yourdomain.com"

# Game embed URL - where your game is hosted
GAME_EMBED_URL = "https://yourgame.io/"

# Homepage content
INDEX_TITLE = "Your Game Title"
INDEX_DESCRIPTION = "Your game description for SEO"
INDEX_SEO_KEYWORDS = "game, online, free, play"
```

### 3. Adding Game Content

Create game files in `sites/[domain.com]/content_html/games/`:

```html
<!--
{
  "title": "Game Title",
  "description": "Game description",
  "hero_image": "game-preview.webp",
  "embed": {"url": "https://gamehost.io/game"}
}
-->
<h2>Game Title</h2>
<p>Game content and description...</p>
```

## Architecture Deep Dive

### Multi-Site Architecture

The system supports multiple websites from a single codebase:

- **Domain-based organization**: `/sites/domain.com/` structure
- **Site-specific content**: Each domain has its own content, assets, and configuration
- **Shared templates**: Common templates with site-specific overrides
- **Independent generation**: Each site generates to `/output/domain.com/`

### Performance Optimizations

The system achieves 46x faster builds through:

- **Parallel processing**: 12-worker parallel image optimization
- **Incremental builds**: Only regenerates changed files
- **Build caching**: Tracks file changes to avoid redundant work
- **Asset optimization**: Efficient image compression and resizing

### Template System

Built on Jinja2 with template inheritance:

- **Base template**: `base.html` provides common structure
- **Component templates**: Reusable components like `game-iframe.html`
- **Site-specific overrides**: Templates can be customized per site
- **Context injection**: Dynamic data passed to templates

### Game Integration

Games are embedded using iframe with fullscreen support:

- **Data-driven URLs**: Game URLs from `data-game-url` attributes
- **Fullscreen mode**: JavaScript handles fullscreen toggle
- **Settings integration**: Game URLs from `settings.py`
- **Consistent behavior**: Same iframe implementation across all pages

## Development Guidelines

### Adding New Sites

1. Create site directory: `sites/newdomain.com/`
2. Copy settings template: `cp sites/slitheriofree.net/settings.py sites/newdomain.com/`
3. Update configuration in `settings.py`
4. Add content in `content_html/` directory
5. Generate: `python main.py --site newdomain.com`

### Customizing Templates

1. Templates are in `/templates/` directory
2. Use Jinja2 template inheritance from `base.html`
3. Override specific blocks for customization
4. Site-specific templates can be added to `/sites/domain.com/templates/`

### Asset Management

Assets are automatically optimized:

- **Images**: Converted to WebP, multiple sizes generated
- **Icons**: PWA icons and favicons generated automatically
- **CSS/JS**: Minified and optimized for production
- **Cache busting**: Version parameters added to prevent caching issues

### SEO Features

The system automatically generates:

- **Meta tags**: Title, description, keywords
- **Open Graph**: Social media sharing metadata
- **Twitter Cards**: Twitter-specific metadata
- **Structured data**: Schema.org JSON-LD for search engines
- **Sitemaps**: XML sitemaps for search engine indexing

## Configuration Reference

### Site Settings (`sites/[domain]/settings.py`)

```python
# Required settings
SITE_NAME = "Site Name"                    # Site title
SITE_URL = "https://example.com/"          # Full site URL
SITE_DOMAIN = "example.com"                # Domain name
GAME_EMBED_URL = "https://game.io/"        # Main game URL

# Content settings
INDEX_TITLE = "Homepage Title"             # Homepage title
INDEX_DESCRIPTION = "SEO description"      # Homepage description
INDEX_SEO_KEYWORDS = "keywords, here"      # SEO keywords

# Optional settings
GOOGLE_ANALYTICS_ID = "G-XXXXXXXXXX"       # Analytics tracking
SOCIAL_MEDIA = {...}                       # Social media links
FOUNDER_INFO = {...}                       # Company information
```

### Image Optimization

Images are automatically optimized in multiple sizes:

- **Mobile**: 480x270
- **Tablet**: 768x432  
- **Desktop**: 1200x675
- **Large**: 1920x1080

### Build Cache

The system uses intelligent caching:

- **File tracking**: Monitors changes to content, templates, config
- **Incremental builds**: Only regenerates changed content
- **Cache invalidation**: Automatic cache clearing when needed
- **Performance metrics**: Detailed build performance reporting

## API Reference

### Generator Class

Main site generation functionality:

```python
from core.generator_refactored import SiteGenerator

generator = SiteGenerator(site_domain="example.com")
generator.generate_site()
```

### Configuration Class

Site configuration management:

```python
from core.config import SiteConfig

config = SiteConfig(site_domain="example.com")
settings = config.get_all_settings()
```

## Troubleshooting

### Common Issues

1. **Build Errors**: Check file permissions and paths
2. **Template Errors**: Verify Jinja2 syntax and variable names
3. **Asset Issues**: Ensure images exist and are valid formats
4. **Performance**: Clear build cache if builds are slow

### Debug Mode

Enable detailed logging:

```bash
python main.py --site example.com --verbose
```

### Cache Management

Clear build cache:

```bash
rm -f output/[domain]/.internal/build_cache.json
```

## Performance Metrics

Current performance benchmarks:

- **Build Time**: 3.72s (full build)
- **Incremental**: 0.07s (changed files only)
- **File Processing**: 82 files processed per build
- **Image Optimization**: 2.2 files/sec with 12 workers
- **Memory Usage**: 54.7MB peak

## Contributing

### Code Style

- Python: Follow PEP 8 conventions
- Templates: Use 2-space indentation
- Comments: Document complex logic
- Testing: Test changes before commits

### Performance

- Profile changes with large sites
- Maintain sub-second incremental builds
- Use parallel processing where possible
- Monitor memory usage

## License

This project is proprietary software. All rights reserved.

## Support

For technical support or questions about this documentation, contact the development team.