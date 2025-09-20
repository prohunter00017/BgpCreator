#!/usr/bin/env python3
"""
ArcadeForge - Static Game Site Generator
Main entry point for generating game websites
"""

import argparse
import sys
import os
from core.generator_refactored import SiteGenerator
from core.performance_logger import log_error, print_build_summary

def main():
    """Main entry point for the site generator"""
    parser = argparse.ArgumentParser(description='Generate static game websites')
    parser.add_argument('--site', required=True, help='Site to generate (e.g., slitheriofree.net)')
    parser.add_argument('--force', action='store_true', help='Force regenerate all files')
    parser.add_argument('--output-dir', help='Output directory (optional)')
    parser.add_argument('--site-url', help='Site URL (optional)')
    
    args = parser.parse_args()
    
    try:
        # Create generator instance
        generator = SiteGenerator(
            site=args.site,
            output_dir=args.output_dir,
            site_url=args.site_url,
            force=args.force
        )
        
        # Generate the site
        generator.generate_site()
        
        # Print build summary
        print_build_summary()
        
    except Exception as e:
        log_error("Main", f"Site generation failed: {str(e)}", "❌")
        sys.exit(1)

if __name__ == "__main__":
    main()