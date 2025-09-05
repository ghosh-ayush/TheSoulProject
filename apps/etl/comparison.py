import csv

old_file = 'new_links.csv'
new_file = 'new_links_1.csv'

def load_urls(csv_file):
    urls = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.add(row['url'])
    return urls

def main():
    old_urls = load_urls(old_file)
    new_urls = load_urls(new_file)
    common = old_urls & new_urls
    print(f"Total URLs in {old_file}: {len(old_urls)}")
    print(f"Total URLs in {new_file}: {len(new_urls)}")
    print(f"Common URLs: {len(common)}")
    if old_urls:
        percent = (len(common) / len(old_urls)) * 100
        print(f"Common % (of old): {percent:.2f}%")


if __name__ == "__main__":
    main()
