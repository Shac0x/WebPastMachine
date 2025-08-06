#!/usr/bin/env python3

import requests
import json
from datetime import datetime
from urllib.parse import urlparse
import sys
from collections import Counter
import argparse
from typing import Dict, List, Optional

def analyze_extensions(urls: List[str]) -> Counter:
    extensions = []
    for url in urls:
        path = urlparse(url).path
        if '.' in path:
            ext = path.split('.')[-1].lower()
            # Only include valid extensions (alphanumeric and reasonable length)
            if ext.isalnum() and len(ext) < 6:
                extensions.append(ext)
    
    return Counter(extensions)

def export_to_file(urls_data: Dict, output_file: str) -> None:
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for url, data in urls_data.items():
                f.write(f"URL: {url}\n")
                f.write(f"First capture: {data['date']}\n")
                f.write(f"Archive link: {data['archive_link']}\n")
                f.write("-" * 100 + "\n")
    except IOError as e:
        print(f"Error writing to file: {e}")
        sys.exit(1)

def get_wayback_urls(domain: str, extension_filter: Optional[str] = None, 
                    output_file: Optional[str] = None) -> None:
    if not domain:
        print("Error: Please provide a valid domain")
        return

    # Ensure domain has proper format
    if not domain.startswith(('http://', 'https://')):
        domain = 'http://' + domain
    
    try:
        parsed_domain = urlparse(domain).netloc
        wayback_url = (f"https://web.archive.org/cdx/search/cdx?"
                      f"url={parsed_domain}/*&output=json&collapse=timestamp:4")
        
        print(f"Searching archived URLs for {parsed_domain}...")
        
        response = requests.get(wayback_url, timeout=30)
        response.raise_for_status()
        
        results = response.json()
        
        if not results or len(results) <= 1:
            print("No archived URLs found for this domain.")
            return
        
        headers = results[0]
        urls = results[1:]
        
        unique_urls = {}
        all_urls = []
        
        # Process URLs
        for url_data in urls:
            url_dict = dict(zip(headers, url_data))
            original_url = url_dict['original']
            
            # Apply extension filter if specified
            if extension_filter and not original_url.lower().endswith(
                    f'.{extension_filter.lower()}'):
                continue
            
            if original_url not in unique_urls:
                timestamp = url_dict['timestamp']
                date = datetime.strptime(
                    timestamp, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                archive_link = f"http://web.archive.org/web/{timestamp}/{original_url}"
                
                unique_urls[original_url] = {
                    'date': date,
                    'archive_link': archive_link,
                    'timestamp': timestamp
                }
                all_urls.append(original_url)
        
        # Show extension analysis
        print("\nAnalysis of file types found:")
        print("-" * 50)
        extension_counts = analyze_extensions(all_urls)
        
        if extension_counts:
            for ext, count in sorted(
                    extension_counts.items(), key=lambda x: (-x[1], x[0])):
                print(f"*.{ext}: {count} files")
        else:
            print("No files with recognizable extensions were found")
        
        print(f"\nTotal unique URLs found: {len(unique_urls)}")
        
        # Handle output
        if output_file:
            export_to_file(unique_urls, output_file)
            print(f"\nResults exported to: {output_file}")
        else:
            print("-" * 100)
            for url, data in unique_urls.items():
                print(f"URL: {url}")
                print(f"First capture: {data['date']}")
                print(f"Archive link: {data['archive_link']}")
                print("-" * 100)
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error processing server response")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main() -> None:
    parser = argparse.ArgumentParser(
        description='''
Wayback Machine URL Finder
-------------------------
This tool searches for all archived URLs in the Wayback Machine for a specific domain.
You can filter by file extension and export the results to a file.

Examples:
  python pastwebviewer.py example.com
  python pastwebviewer.py example.com -e pdf
  python pastwebviewer.py example.com -o results.txt
  python pastwebviewer.py example.com -e pdf -o pdfs.txt
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'domain',
        nargs='?',
        help='The domain to search (example: example.com)'
    )
    
    parser.add_argument(
        '-e', '--extension',
        help='Filter by file extension (example: pdf, jpg, html)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file to save results (example: results.txt)'
    )

    args = parser.parse_args()

    if not args.domain:
        parser.print_help()
        sys.exit(1)

    get_wayback_urls(args.domain, args.extension, args.output)

if __name__ == "__main__":
    main()