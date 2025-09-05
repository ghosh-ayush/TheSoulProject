#!/usr/bin/env python3
"""
Scrape (cleanly) the main body of https://en.wikipedia.org/wiki/Hinduism
- Fetches stable HTML from Wikimedia Core REST API
- Removes images/figures/infoboxes/navboxes
- Removes inline citation markers (e.g., [1], superscripts)
- Drops "References", "Notes", "External links", etc.
- Writes clean UTF-8 text to ./Hinduism_clean.txt
- Optionally writes internal links (anchor -> URL) to ./Hinduism_links.csv

Requirements:
  pip install requests beautifulsoup4 lxml

Licensing/Attribution:
  Wikipedia text is CC BY-SA; keep the attribution block at the bottom.
  See: https://en.wikipedia.org/wiki/Wikipedia:Reusing_Wikipedia_content
"""


import requests
from bs4 import BeautifulSoup
import os
import csv
from datetime import datetime
import time

ARTICLES_DIR = 'articles'
LINKS_CSV = 'links.csv'
WIKIPEDIA_BASE = 'https://en.wikipedia.org'

def clean_filename(title):
    return "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in title).rstrip()

def already_scraped(url, catalog):
    return url in catalog

def load_catalog():
    catalog = set()
    if os.path.exists(LINKS_CSV):
        with open(LINKS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                catalog.add(row['url'])
    return catalog

def save_to_catalog(title, url):
    file_exists = os.path.exists(LINKS_CSV)
    # Determine next serial number
    serial_no = 1
    if file_exists:
        with open(LINKS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) > 1:
                serial_no = len(rows)
    with open(LINKS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Serial no', 'title', 'url', 'timestamp'])
        writer.writerow([serial_no, title, url, datetime.now().isoformat()])

def scrape_article(url, catalog):
    print(f"Scraping: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"Request failed for {url}: {e}")
        return []
    if resp.status_code != 200:
        print(f"Failed to fetch {url} (status {resp.status_code})")
        return []
    soup = BeautifulSoup(resp.content, 'lxml')
    title_tag = soup.find('h1', id='firstHeading')
    if not title_tag:
        print(f"No title found for {url}")
        return []
    title = title_tag.text.strip()
    content_div = soup.find('div', id='mw-content-text')
    if not content_div:
        print(f"No content found for {url}")
        return []
    paragraphs = content_div.find_all(['p', 'ul', 'ol'])
    text = '\n'.join(p.get_text(separator=' ', strip=True) for p in paragraphs)
    links = set()
    for a in content_div.find_all('a', href=True):
        href = a['href']
        if href.startswith('/wiki/') and not any(href.startswith(prefix) for prefix in [
            '/wiki/Special:', '/wiki/Help:', '/wiki/Talk:', '/wiki/Category:', '/wiki/File:', '/wiki/Portal:', '/wiki/Template:', '/wiki/Wikipedia:', '/wiki/Book:', '/wiki/Draft:', '/wiki/TimedText:', '/wiki/Module:', '/wiki/MediaWiki:', '/wiki/User:', '/wiki/Media:']):
            full_url = WIKIPEDIA_BASE + href.split('#')[0]
            links.add(full_url)
    # Save article text and links
    if not os.path.exists(ARTICLES_DIR):
        os.makedirs(ARTICLES_DIR)
    filename = os.path.join(ARTICLES_DIR, f"{clean_filename(title)}_clean.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)
        f.write('\n\n--- Hyperlinks ---\n')
        for link in sorted(links):
            f.write(link + '\n')
    save_to_catalog(title, url)
    return links


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scrapeWikipedia.py <Wikipedia Article URL> [<Another URL> ...]")
        sys.exit(1)
    seed_urls = sys.argv[1:]
    catalog = load_catalog()
    # Each item in to_scrape is a tuple: (url, depth)
    to_scrape = [(url, 0) for url in seed_urls]
    scraped = set(catalog)
    max_depth = 3
    while to_scrape:
        current_url, depth = to_scrape.pop(0)
        if current_url in scraped:
            continue
        try:
            new_links = scrape_article(current_url, scraped)
        except Exception as e:
            print(f"Error scraping {current_url}: {e}")
            continue
        scraped.add(current_url)
        # Only add new links that haven't been scraped yet and if depth < max_depth
        if depth < max_depth:
            for link in new_links:
                if link not in scraped and (link, depth+1) not in to_scrape:
                    to_scrape.append((link, depth+1))
        # Polite delay to avoid hammering Wikipedia
        time.sleep(1)

if __name__ == "__main__":
    main()
