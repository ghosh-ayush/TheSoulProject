import os
import shutil

def combine_and_dedup_articles(src_dirs, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    seen = set()
    for src in src_dirs:
        for fname in os.listdir(src):
            if fname not in seen:
                src_path = os.path.join(src, fname)
                dest_path = os.path.join(dest_dir, fname)
                shutil.copy2(src_path, dest_path)
                seen.add(fname)
    print(f"Combined and deduped articles into {dest_dir}. Total files: {len(seen)}")

def combine_and_dedup_csvs(csv_files, output_csv):
    import csv
    seen = set()
    rows = []
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row.get('title')
                if key and key not in seen:
                    rows.append(row)
                    seen.add(key)
    if rows:
        fieldnames = rows[0].keys()
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    print(f"Combined and deduped CSVs into {output_csv}. Total rows: {len(rows)}")

if __name__ == "__main__":
    # Combine article folders
    combine_and_dedup_articles(['new_articles', 'new_articles_1'], 'all_articles')
    # Combine CSVs
    combine_and_dedup_csvs(['new_links.csv', 'new_links_1.csv'], 'all_links.csv')
