#!/usr/bin/env python3

import requests
import json
from datetime import datetime
from urllib.parse import urlparse
import sys
from collections import Counter
import argparse
from typing import Dict, List, Optional
import time
try:
    from colorama import init, Fore, Back, Style
    colorama_available = True
    init(autoreset=True)  # Initialize colorama
except ImportError:
    colorama_available = False
    print("For colored output, install colorama: pip install colorama")

def analyze_extensions(urls: List[str]) -> Counter:
    extensions = []
    for url in urls:
        path = urlparse(url).path
        if '.' in path:
            ext = path.split('.')[-1].lower()
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
        if colorama_available:
            print(f"{Fore.RED}Error: Please provide a valid domain{Style.RESET_ALL}")
        else:
            print("Error: Please provide a valid domain")
        return

    if not domain.startswith(('http://', 'https://')):
        domain = 'http://' + domain
    
    try:
        parsed_domain = urlparse(domain).netloc
        wayback_url = (f"https://web.archive.org/cdx/search/cdx?"
                      f"url={parsed_domain}/*&output=json&collapse=timestamp:4")
        
        if colorama_available:
            print(f"\n{Fore.CYAN}╔{'═' * 60}╗")
            print(f"{Fore.CYAN}║ {Fore.YELLOW}Searching archived URLs for {Fore.GREEN}{parsed_domain}{Fore.YELLOW}...{' ' * (28-len(parsed_domain))}{Fore.CYAN}║")
            print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}\n")
        else:
            print(f"\nSearching archived URLs for {parsed_domain}...\n")
        
        response = requests.get(wayback_url, timeout=30)
        response.raise_for_status()
        
        results = response.json()
        
        if not results or len(results) <= 1:
            if colorama_available:
                print(f"{Fore.RED}No archived URLs found for this domain.{Style.RESET_ALL}")
            else:
                print("No archived URLs found for this domain.")
            return
        
        headers = results[0]
        urls = results[1:]
        
        unique_urls = {}
        all_urls = []
        
        if colorama_available:
            print(f"\n{Fore.CYAN}Processing URLs...{Style.RESET_ALL}")
        else:
            print("\nProcessing URLs...")
        
        total_urls = len(urls)
        for i, url_data in enumerate(urls):
            url_dict = dict(zip(headers, url_data))
            original_url = url_dict['original']
            
            if i > 0 and i % 100 == 0:
                if colorama_available:
                    print(f"{Fore.CYAN}Processed {i}/{total_urls} URLs{Style.RESET_ALL}", end="\r")
                else:
                    print(f"Processed {i}/{total_urls} URLs", end="\r")
            
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
        
        print("\nAnalysis of file types found:")
        print("-" * 50)
        extension_counts = analyze_extensions(all_urls)
        
        if extension_counts:
            for ext, count in sorted(
                    extension_counts.items(), key=lambda x: (-x[1], x[0])):
                if colorama_available:
                    ext_color = Fore.GREEN if count > 10 else Fore.YELLOW if count > 5 else Fore.WHITE
                    print(f"{ext_color}*.{ext}: {Fore.CYAN}{count} files{Style.RESET_ALL}")
                else:
                    print(f"*.{ext}: {count} files")
        else:
            if colorama_available:
                print(f"{Fore.YELLOW}No files with recognizable extensions were found{Style.RESET_ALL}")
            else:
                print("No files with recognizable extensions were found")
        
        if colorama_available:
            print(f"\n{Fore.GREEN}Total unique URLs found: {Fore.WHITE}{len(unique_urls)}{Style.RESET_ALL}")
        else:
            print(f"\nTotal unique URLs found: {len(unique_urls)}")
        
        # Handle output
        if output_file:
            export_to_file(unique_urls, output_file)
            if colorama_available:
                print(f"\n{Fore.GREEN}Results exported to: {Fore.WHITE}{output_file}{Style.RESET_ALL}")
            else:
                print(f"\nResults exported to: {output_file}")
        else:
            if colorama_available:
                divider = f"{Fore.CYAN}{'-' * 100}{Style.RESET_ALL}"
            else:
                divider = "-" * 100
            print(divider)
            for url, data in unique_urls.items():
                if colorama_available:
                    print(f"{Fore.YELLOW}URL: {Fore.WHITE}{url}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}First capture: {Fore.WHITE}{data['date']}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Archive link: {Fore.CYAN}{data['archive_link']}{Style.RESET_ALL}")
                else:
                    print(f"URL: {url}")
                    print(f"First capture: {data['date']}")
                    print(f"Archive link: {data['archive_link']}")
                print(divider)
            
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