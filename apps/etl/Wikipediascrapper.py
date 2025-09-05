#!/usr/bin/env python3
"""
Multiprocessing version of Wikipedia scraper for faster crawling.
- Uses multiprocessing.Pool to parallelize article scraping
- Maintains depth-limited recursion and deduplication
- Writes clean text and links for each article
"""

import requests
from bs4 import BeautifulSoup
import os
import csv
from datetime import datetime
import time
from multiprocessing import Pool, Manager, cpu_count

ARTICLES_DIR = 'new_articles_1'
LINKS_CSV = 'new_links_1.csv'
WIKIPEDIA_BASE = 'https://en.wikipedia.org'
MAX_DEPTH = 2
BATCH_SIZE = 16  # Number of concurrent processes (tune as needed)

# Utility functions

def clean_filename(title):
    return "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in title).rstrip()

def already_scraped(url, catalog_dict):
    return url in catalog_dict

def load_catalog():
    catalog_dict = {}
    if os.path.exists(LINKS_CSV):
        with open(LINKS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                catalog_dict[row['url']] = True
    return catalog_dict

def save_to_catalog(title, url, lock, catalog_dict):
    file_exists = os.path.exists(LINKS_CSV)
    serial_no = 1
    if file_exists:
        with open(LINKS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) > 1:
                serial_no = len(rows)
    with lock:
        if url not in catalog_dict:
            with open(LINKS_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Serial no', 'title', 'url', 'timestamp'])
                writer.writerow([serial_no, title, url, datetime.now().isoformat()])
            catalog_dict[url] = True

def scrape_article(args):
    url, catalog_dict, lock = args
    if already_scraped(url, catalog_dict):
        return url, []
    print(f"Scraping: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"Request failed for {url}: {e}")
        return url, []
    if resp.status_code != 200:
        print(f"Failed to fetch {url} (status {resp.status_code})")
        return url, []
    soup = BeautifulSoup(resp.content, 'lxml')
    title_tag = soup.find('h1', id='firstHeading')
    if not title_tag:
        print(f"No title found for {url}")
        return url, []
    title = title_tag.text.strip()
    content_div = soup.find('div', id='mw-content-text')
    if not content_div:
        print(f"No content found for {url}")
        return url, []
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
    save_to_catalog(title, url, lock, catalog_dict)
    return url, list(links)

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python Wikipediascrapper.py <Wikipedia Article URL>")
        sys.exit(1)
    seed_url = sys.argv[1]
    manager = Manager()
    lock = manager.Lock()
    catalog_dict = manager.dict(load_catalog())
    max_depth = MAX_DEPTH
    pool = Pool(processes=BATCH_SIZE)
    # Start with the seed URL at depth 0
    current_level = [seed_url]
    for depth in range(max_depth + 1):
        print(f"\n--- Depth {depth} ---")
        # Prepare batch for this depth
        batch = []
        for url in current_level:
            if not already_scraped(url, catalog_dict):
                batch.append((url, catalog_dict, lock))
        if not batch:
            print("No new URLs to scrape at this depth.")
            break
        # Scrape all URLs at this depth in parallel
        results = pool.map(scrape_article, batch)
        # Collect links for next depth
        next_level = set()
        for url, new_links in results:
            for link in new_links:
                if not already_scraped(link, catalog_dict):
                    next_level.add(link)
        current_level = list(next_level)
        time.sleep(1)  # Polite delay
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
