import csv
import os
import time

import json
from openai import ask_model

LINKS_CSV = 'all_links.csv'
ARTICLES_DIR = 'all_articles'
OUTPUT_CSV = 'enriched.csv'

# Comprehensive system prompt for enrichment
SYSTEM_PROMPT = '''
You are an expert knowledge extraction agent for the Atman project, building a structured knowledge graph of Hinduism from Wikipedia articles. For each article, extract and return the following fields in JSON:

- entities: List of key people, places, texts, concepts, events, and symbols mentioned.
- topic: Main subject(s) of the article.
- summary: A concise, neutral summary (100–150 words) of the article’s core content.
- type: One of DEITY, TEXT, CONCEPT, CHARACTER, PLACE, EVENT, SYMBOL (choose the best fit).
- aliases: Alternative names, epithets, or redirects for the main subject.
- tags: Relevant keywords or categories.
- relationships: List of structured edges (from, to, rel, source) as described in the Atman blueprint, including AVATAR_OF, INCARNATION_OF, PAST_LIFE_OF, REINCARNATION_OF, DESCENDANT_OF, CHILD_OF, CONSORT_OF, SIBLING_OF, APPEARS_IN, CONTAINED_IN, SYMBOLIZES, WIELDS, RESIDES_IN, FOUGHT_AGAINST, ASSOCIATED_WITH, MEMBER_OF, MENTOR_OF, DEVOTEE_OF, etc.
- sources: Attribution info (Wikipedia URL, oldid, license).
- media: List of notable images or audio files (with captions, license, author, source URL).

Instructions:
- Use only information present in the article text.
- Prefer structured facts from infoboxes and lead sections.
- Return all fields as a single JSON object.
- Be precise, neutral, and avoid speculation.
- If a field is not present, return an empty list or null.
'''


# Actual LLM call using ask_model from openai.py
def call_llm(text):
    prompt = SYSTEM_PROMPT + "\n\n" + text
    response = ask_model(prompt)
    if response:
        # Strip markdown code block markers if present
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
            return {}
    else:
        print("No response from LLM.")
        return {}

def main():
    with open(LINKS_CSV, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        base_fieldnames = reader.fieldnames if reader.fieldnames else []
        enrichment_fields = ['entities', 'topic', 'summary', 'sources', 'aliases', 'tags', 'relationships', 'type', 'media']
        fieldnames = base_fieldnames + [f for f in enrichment_fields if f not in base_fieldnames]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            title = row['title']
            filename = os.path.join(ARTICLES_DIR, f"{title.replace('/', '_')}_clean.txt")
            if not os.path.exists(filename):
                print(f"Warning: Article file not found for {title}")
                continue
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
            # Call LLM to enrich
            enrichment = call_llm(text)
            out_row = row.copy()
            out_row.update(enrichment)
            # Convert any list/dict fields to string for CSV compatibility
            for k, v in out_row.items():
                if isinstance(v, (list, dict)):
                    out_row[k] = str(v)
            writer.writerow(out_row)
            time.sleep(1)  # Polite delay for API rate limits

if __name__ == "__main__":
    main()
