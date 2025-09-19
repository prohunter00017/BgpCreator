# Overview

This is an Enhanced Static Site Generator built in Python that creates modern, SEO-optimized websites with organized structure and advanced features. The project consists of two main components: a comprehensive enhanced generator with modular architecture (in the `core/` directory) and a simplified game-focused site generator (ArcadeForge) for quick game website deployment. The system specializes in creating static websites for browser games with embedded content, multi-language support, and performance optimization.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes

## September 18, 2025 - Multi-Site Architecture & Complete Code Organization
- **Implemented Multi-Site Architecture**: Transformed single-site generator into scalable multi-site system supporting unlimited domains with organized structure
- **Domain-Specific Organization**: Content organized by domain in `/sites/domain.com/` structure with site-specific content, assets, and configuration
- **Advanced CLI Interface**: Added `--site domain.com`, `--all`, `--list`, and `--output` commands for flexible site management
- **Enhanced Security**: Implemented path traversal protection and input validation for site names
- **Template Inheritance System**: Jinja2 ChoiceLoader enables site-specific template overrides with shared template fallbacks
- **Backward Compatibility**: Legacy single-site mode preserved for existing workflows
- **Completed comprehensive code organization**: Reorganized scattered Python files from root directory into professional `core/` package structure
- **Implemented organized asset structure**: Transformed cluttered output (51 files in root) to clean, professional structure with only 17 essential files in root directory (67% reduction in clutter)
- **Enhanced PWA organization**: All PWA icons and screenshots moved to `/assets/pwa/` directory (10 icons + 3 screenshots)
- **Improved favicon management**: All favicon variations organized in `/assets/icons/` directory (11 different sizes)
- **SEO image optimization**: SEO-specific images organized in `/assets/images/seo/` and `/assets/images/logos/`
- **Fixed link resolution system**: Updated link resolution to handle new organized paths while maintaining backward compatibility
- **Code structure improvements**: Moved Python modules into organized package (`core/generator.py`, `core/settings.py`, `core/optimizer.py`, `core/config.py`)
- **Maintained performance**: Same generation speed (~4.9 seconds) with much cleaner, more professional code and output structure

# System Architecture

## Core Architecture Pattern
The enhanced generator follows a modular architecture with separation of concerns:
- **Core Modules**: Organized in `core/` directory with specialized components for different aspects of site generation
- **Template System**: Jinja2-based templating with inheritance and custom filters
- **Asset Pipeline**: Automated optimization and organization of static assets
- **Multi-Language Support**: Built-in internationalization with language-specific content routing

## Frontend Architecture
- **Template Inheritance**: Base templates with specialized templates for different content types (games, pages, error pages)
- **Responsive Design**: Mobile-first CSS with modern CSS variables and grid layouts
- **Asset Organization**: Structured `/assets/css/`, `/assets/js/`, `/assets/images/` directories
- **Performance Optimization**: Critical CSS inlining, lazy loading, and Progressive Web App features

## Content Management System
- **Markdown Support**: Content written in Markdown with YAML frontmatter for metadata
- **HTML Content**: Direct HTML content support for games and complex layouts
- **Metadata Handling**: JSON metadata embedded in HTML comments for game content
- **Content Processing**: Automatic conversion from Markdown to HTML with custom extensions

## Build System
- **Two-Tier Architecture**: Enhanced generator for complex sites, simplified ArcadeForge for quick game sites
- **Configuration Management**: Centralized configuration with simple Python config files
- **Asset Pipeline**: Image optimization with multiple formats (WebP, JPEG, PNG) and responsive sizing
- **Link Resolution**: Intelligent internal link resolution ensuring all navigation works correctly

## SEO and Performance Features
- **Schema.org Integration**: Structured data for games, FAQs, and breadcrumbs
- **Multi-Language SEO**: Language-specific sitemaps, hreflang tags, and localized URLs
- **Image Optimization**: Multiple formats and sizes with proper alt text and lazy loading
- **HTML/CSS/JS Minification**: Automated optimization for faster loading
- **Critical CSS**: Above-the-fold styles inlined for better Core Web Vitals

## Game Integration Architecture
- **Embedded Game Support**: iframe-based game embedding with full-screen capabilities
- **Game Metadata System**: JSON metadata for game descriptions, controls, and features
- **Interactive Elements**: JavaScript-enhanced game controls and user interactions
- **Responsive Game Display**: Adaptive sizing for different screen sizes and orientations

# External Dependencies

## Core Python Libraries
- **Jinja2**: Template engine for HTML generation and template inheritance
- **Pillow (PIL)**: Image processing and optimization (optional dependency)
- **Markdown**: Markdown to HTML conversion with extensions (optional)
- **BeautifulSoup4**: HTML parsing and manipulation for link resolution
- **Streamlit**: Web interface for the enhanced generator configuration

## Frontend Dependencies
- **Bootstrap Icons**: Icon library for UI elements
- **Google Fonts**: Web typography (Inter font family)
- **Modern CSS**: CSS Grid, Flexbox, and CSS custom properties for responsive design

## Build and Optimization Tools
- **Built-in Minification**: Custom Python-based CSS/JS/HTML minification
- **Image Optimization**: Multi-format image generation (WebP, JPEG, PNG)
- **Asset Bundling**: Automated asset copying and organization

## Analytics and SEO
- **Google Analytics**: Integration for website traffic tracking
- **Schema.org**: Structured data markup for search engines
- **Sitemap Generation**: Automated XML sitemap creation
- **Robots.txt**: Search engine crawler configuration

## Development Tools
- **File System Utilities**: Safe file operations and directory management
- **Error Handling**: Comprehensive error handling and logging
- **Multi-Language Processing**: Internationalization support without external translation APIs