import csv
import time
from openai import ask_model

INPUT_CSV = 'all_links.csv'
OUTPUT_CSV = 'filtered_links.csv'
BATCH_SIZE = 20000
SLEEP_TIME = 2

SYSTEM_PROMPT = '''
You are an expert knowledge filter for the Atman project, building a knowledge graph of Hinduism and Sanatana Dharma. Given a batch of Wikipedia article URLs and titles, return a list of those that are relevant to Hinduism, Sanatana Dharma, or its core concepts, texts, deities, places, events, or symbols. Only include articles that would be valid nodes in the Atman knowledge graph. Return the result as a JSON list of valid titles and URLs.
'''

def batch_filter_llm(rows):
    titles_urls = [f"{row['title']} | {row['url']}" for row in rows]
    prompt = SYSTEM_PROMPT + "\n\n" + "\n".join(titles_urls)
    response = ask_model(prompt)
    if response:
        resp_str = response.strip()
        if resp_str.startswith('```json'):
            resp_str = resp_str[len('```json'):].strip()
        if resp_str.startswith('```'):
            resp_str = resp_str[len('```'):].strip()
        if resp_str.endswith('```'):
            resp_str = resp_str[:-len('```')].strip()
        try:
            return json.loads(resp_str)
        except Exception as e:
            print(f"Error parsing LLM response: {e}\nRaw response: {response}")
            return []
    else:
        print("No response from LLM.")
        return []

if __name__ == "__main__":
    import json
    with open(INPUT_CSV, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        reader = list(csv.DictReader(infile))
        writer = csv.DictWriter(outfile, fieldnames=['title', 'url'])
        writer.writeheader()
        for i in range(0, len(reader), BATCH_SIZE):
            batch = reader[i:i+BATCH_SIZE]
            valid = batch_filter_llm(batch)
            for item in valid:
                # Expecting item to be dict with 'title' and 'url'
                if isinstance(item, dict) and 'title' in item and 'url' in item:
                    writer.writerow({'title': item['title'], 'url': item['url']})
            time.sleep(SLEEP_TIME)
    print(f"Filtered links written to {OUTPUT_CSV}")
