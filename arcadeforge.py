#!/usr/bin/env python3
"""
ARCADEFORGE - Multi-Site Static Site Generator
===============================================

Quick and easy website generation for game sites with multi-site support.

Usage:
    python arcadeforge.py                    # Generate using legacy mode
    python arcadeforge.py --site domain.com  # Generate specific site
    python arcadeforge.py --all             # Generate all sites
    python arcadeforge.py --list            # List available sites
    
What it does:
- Generates complete websites from your content
- Supports multiple sites with domain-specific organization
- Optimizes images automatically  
- Creates SEO-optimized HTML
- Handles games and regular pages

Multi-Site Structure:
- /sites/domain.com/content_html/    # Site-specific content
- /sites/domain.com/static/          # Site-specific assets
- /sites/domain.com/settings.py     # Site-specific config
- /templates/                       # Shared templates
- /output/domain.com/               # Site-specific output
"""

import sys
import time
import argparse
from core.generator import SiteGenerator
from core.site_loader import list_available_sites, validate_site_name


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='ArcadeForge Multi-Site Static Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python arcadeforge.py                           # Legacy mode (single site)
  python arcadeforge.py --site slitheriofree.net # Generate specific site
  python arcadeforge.py --all                    # Generate all sites
  python arcadeforge.py --list                   # List available sites
  python arcadeforge.py --site domain.com --output custom/  # Custom output
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--site', 
                      help='Generate specific site (domain name)',
                      metavar='DOMAIN')
    group.add_argument('--all', 
                      action='store_true',
                      help='Generate all sites in /sites/ directory')
    group.add_argument('--list', 
                      action='store_true',
                      help='List all available sites')
    
    parser.add_argument('--output', 
                       help='Custom output directory (overrides default)',
                       metavar='DIR')
    
    return parser.parse_args()


def generate_single_site(site=None, output_dir=None):
    """Generate a single site"""
    if site:
        print(f"🚀 Generating {site} → output/{site}")
    else:
        print("🚀 Generating en-US → output")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Initialize the site generator
        generator = SiteGenerator(site=site, output_dir=output_dir)
        
        # Generate the website
        generator.generate_site()
        generator.create_manifest()
        generator.create_robots_txt()
        generator.create_sitemap_xml()
        
        # Calculate generation time
        end_time = time.time()
        generation_time = end_time - start_time
        
        if site:
            print(f"✅ {site} site ready in '{generator.output_dir}/'")
        else:
            print(f"✅ en-US site ready in 'output/'")
        
        return True, generation_time
        
    except Exception as e:
        print(f"❌ Error generating {site or 'legacy site'}: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def generate_all_sites():
    """Generate all available sites"""
    sites = list_available_sites()
    
    if not sites:
        print("⚠️  No sites found in /sites/ directory")
        print("   Create site folders like: /sites/domain.com/")
        return False
    
    print(f"🚀 Generating {len(sites)} site(s)")
    print("=" * 60)
    
    total_time = 0
    successful = 0
    failed = 0
    
    for site in sites:
        success, gen_time = generate_single_site(site)
        total_time += gen_time
        
        if success:
            successful += 1
        else:
            failed += 1
        
        print()  # Empty line between sites
    
    print("=" * 60)
    print(f"🎉 All {successful} site(s) generated successfully!")
    if failed > 0:
        print(f"⚠️  {failed} site(s) failed to generate")
    
    print(f"\n⏱️  Total generation time: {total_time:.2f} seconds")
    print(f"📊 Average per site: {total_time/len(sites):.2f} seconds")
    
    print("\n🚀 Next steps:")
    print("   • Test: Open output/<site>/index.html")
    print("   • Deploy: Upload the output folder(s) to your server")
    
    return failed == 0


def list_sites():
    """List all available sites"""
    sites = list_available_sites()
    
    if not sites:
        print("⚠️  No sites found in /sites/ directory")
        print("\n📋 To create a new site:")
        print("   1. Create folder: /sites/domain.com/")
        print("   2. Add content: /sites/domain.com/content_html/")
        print("   3. Add assets: /sites/domain.com/static/")
        print("   4. Add config: /sites/domain.com/settings.py")
        return
    
    print(f"📋 Available sites ({len(sites)}):")
    print("=" * 40)
    
    for site in sites:
        print(f"   🌐 {site}")
    
    print(f"\n💡 Usage:")
    print(f"   python arcadeforge.py --site {sites[0]}")
    print(f"   python arcadeforge.py --all")


def main():
    """Main entry point for ArcadeForge"""
    args = parse_arguments()
    
    try:
        if args.list:
            list_sites()
            return
        
        if args.site:
            # Validate site name
            if not validate_site_name(args.site):
                print(f"❌ Invalid site name: {args.site}")
                print("   Site names can only contain letters, numbers, dots, and hyphens")
                sys.exit(1)
            
            success, _ = generate_single_site(args.site, args.output)
            if not success:
                sys.exit(1)
        
        elif args.all:
            success = generate_all_sites()
            if not success:
                sys.exit(1)
        
        else:
            # Legacy mode - single site generation
            success, generation_time = generate_single_site(output_dir=args.output)
            if success:
                print(f"\n⏱️  Generation completed in {generation_time:.2f} seconds")
                print("\n📋 Next steps:")
                print("   • Test: Open output/index.html")
                print("   • Deploy: Upload the output folder(s) to your server")
            else:
                sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()