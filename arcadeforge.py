#!/usr/bin/env python3
"""
ARCADEFORGE - Super Simple Site Generator
=========================================

This is the EASIEST way to use ArcadeForge! Just run this script.

USAGE:
    python arcadeforge.py             # Generate German site (default)
    python arcadeforge.py --english   # Generate English site  
    python arcadeforge.py --french    # Generate French site
    python arcadeforge.py --dutch     # Generate Dutch site
    python arcadeforge.py --all       # Generate all languages

EXAMPLES:
    python arcadeforge.py             # German in 'output' folder
    python arcadeforge.py --english   # English in 'output-english' folder
    python arcadeforge.py --all       # All languages in separate folders
"""

import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='ArcadeForge Site Generator - Super Simple!')
    
    # Language options
    parser.add_argument('--english', action='store_true', help='Generate English site')
    parser.add_argument('--french', action='store_true', help='Generate French site')  
    parser.add_argument('--dutch', action='store_true', help='Generate Dutch site')
    parser.add_argument('--german', action='store_true', help='Generate German site')
    parser.add_argument('--all', action='store_true', help='Generate all languages')
    
    # Output options
    parser.add_argument('--output', '-o', help='Custom output directory')
    parser.add_argument('--check', action='store_true', help='Check setup before building')
    
    args = parser.parse_args()
    
    # Check setup if requested
    if args.check:
        os.system("python check.py")
        return
    
    # Import the generator
    try:
        from generate_site import SiteGenerator
    except ImportError as e:
        print(f"❌ Error importing generator: {e}")
        print("💡 Make sure you're in the ArcadeForge directory!")
        return 1
    
    # Determine what to generate
    languages_to_generate = []
    
    if args.all:
        languages_to_generate = [
            ('de-DE', 'output-german'),
            ('en-US', 'output-english'), 
            ('fr-FR', 'output-french'),
            ('nl-NL', 'output-dutch')
        ]
    else:
        # Single language
        if args.english:
            lang, output_dir = 'en-US', args.output or 'output-english'
        elif args.french:
            lang, output_dir = 'fr-FR', args.output or 'output-french'
        elif args.dutch:
            lang, output_dir = 'nl-NL', args.output or 'output-dutch'
        elif args.german:
            lang, output_dir = 'de-DE', args.output or 'output-german'
        else:
            # Default: use config.py setting
            lang, output_dir = None, args.output or 'output'
        
        languages_to_generate = [(lang, output_dir)]
    
    # Generate each language
    success_count = 0
    for language, output_dir in languages_to_generate:
        try:
            print(f"\n🚀 Generating {language or 'default language'} → {output_dir}")
            print("=" * 60)
            
            # Create generator and build
            generator = SiteGenerator(output_dir=output_dir, language=language)
            generator.generate_site()
            generator.create_manifest()
            generator.create_robots_txt()
            generator.create_sitemap_xml()
            
            print(f"✅ {language or 'Default'} site ready in '{output_dir}/'")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to generate {language or 'default'}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if success_count == len(languages_to_generate):
        print(f"🎉 All {success_count} site(s) generated successfully!")
        print("\n🚀 Next steps:")
        for _, output_dir in languages_to_generate:
            print(f"   • Test: Open {output_dir}/index.html")
        print("   • Deploy: Upload the output folder(s) to your server")
    else:
        print(f"⚠️  {success_count}/{len(languages_to_generate)} sites generated successfully")
    
    return 0 if success_count == len(languages_to_generate) else 1

if __name__ == "__main__":
    sys.exit(main())
