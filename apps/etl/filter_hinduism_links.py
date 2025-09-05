import csv
from openai import ask_model

# Keywords for filtering relevance to Hinduism/Sanatana Dharma
KEYWORDS = [
    'hindu', 'sanatan', 'sanatana', 'dharma', 'ved', 'veda', 'upanishad', 'bhagavad', 'ramayana', 'mahabharata',
    'purana', 'smriti', 'shruti', 'brahman', 'atman', 'karma', 'moksha', 'yoga', 'bhakti', 'dhyana', 'puja', 'japa',
    'shiva', 'vishnu', 'krishna', 'rama', 'gita', 'vedic', 'indian philosophy', 'indus valley', 'sanskrit', 'ashrama',
    'sampradaya', 'shaktism', 'shaivism', 'vaishnavism', 'smarta', 'tantra', 'agni', 'indra', 'deva', 'devi', 'tridevi',
    'trimurti', 'brahma', 'lakshmi', 'parvati', 'saraswati', 'ganesha', 'kartikeya', 'hanuman', 'radha', 'sita', 'mahadevi',
    'avatar', 'dashavatara', 'navadurga', 'mahavidya', 'rudra', 'aditya', 'vasu', 'ashvin', 'tridasha', 'puranic', 'itihasa',
    'epic', 'chronology', 'genealogy', 'samkhya', 'nyaya', 'vaisheshika', 'mimamsa', 'vedanta', 'advaita', 'dvaita', 'vishishtadvaita',
    'achintya bheda abheda', 'shuddhadvaita', 'svabhavika bhedabheda', 'akshar purushottam', 'astika', 'nastika', 'charvaka',
    'jain', 'jainism', 'buddh', 'buddhism', 'guru', 'rishi', 'sant', 'sannyasa', 'varnashrama', 'caste', 'varna', 'mantra',
    'ritual', 'scripture', 'tradition', 'spiritual', 'philosophy', 'pramana', 'prarthana', 'murti', 'temple', 'matha', 'tirtha',
    'yatra', 'festival', 'diwali', 'holi', 'navaratri', 'durga puja', 'ramlila', 'vijayadashami', 'raksha bandhan', 'ganesh chaturthi',
    'vasant panchami', 'rama navami', 'janmashtami', 'onam', 'makar sankranti', 'kumbh mela', 'pongal', 'ugadi', 'vaisakhi', 'bihu',
    'puthandu', 'vishu', 'ratha yatra', 'bhajan', 'kirtan', 'yajna', 'homa', 'tarpana', 'vrata', 'prayaschitta', 'seva', 'sadhu',
    'yogi', 'yogini', 'asana', 'sadhana', 'hatha yoga', 'jnana yoga', 'bhakti yoga', 'karma yoga', 'raja yoga', 'kundalini yoga',
    'bharatanatyam', 'kathak', 'kathakali', 'kuchipudi', 'manipuri', 'mohiniyattam', 'odissi', 'sattriya', 'bhagavata mela', 'yakshagana',
    'dandiya raas', 'carnatic music', 'pandav lila', 'kalaripayattu', 'silambam', 'adimurai', 'samskara', 'garbhadhana', 'pumsavana',
    'simantonnayana', 'jatakarma', 'namakarana', 'nishkramana', 'annaprashana', 'chudakarana', 'karnavedha', 'vidyarambham', 'upanayana',
    'keshanta', 'ritushuddhi', 'samavartanam', 'vivaha', 'antyesti', 'saptarshi', 'vashistha', 'kashyapa', 'atri', 'jamadagni', 'gotama',
    'vishvamitra', 'bharadwaja', 'agastya', 'angiras', 'aruni', 'ashtavakra', 'jaimini', 'kanada', 'kapila', 'patanjali', 'panini',
    'prashastapada', 'raikva', 'satyakama jabala', 'valmiki', 'vyasa', 'yajnavalkya', 'abhinavagupta', 'adi shankara', 'akka mahadevi',
    'allama prabhu', 'alvars', 'basava', 'chaitanya', 'ramdas kathiababa', 'chakradhara', 'changadeva', 'dadu dayal', 'eknath',
    'gangesha upadhyaya', 'gaudapada', 'gorakshanatha', 'haridasa thakur', 'harivansh', 'jagannatha dasa', 'jayanta bhatta', 'jayatirtha',
    'jiva goswami', 'jnaneshwar', 'kabir', 'kanaka dasa', 'kumārila bhatta', 'madhusudana', 'madhva', 'matsyendranatha', 'morya gosavi',
    'namadeva', 'nimbarka', 'ramanuja', 'ramdas', 'ramakrishna', 'ramana maharshi', 'ravidas', 'sankara', 'surdas', 'tulsidas', 'vallabha',
    'vivekananda', 'dayananda', 'swami', 'paramahamsa', 'sant', 'guru', 'rishi', 'philosopher', 'sage', 'spiritual leader', 'indian saint',
    'indian mystic', 'indian monk', 'indian ascetic', 'indian reformer', 'indian poet', 'indian theologian', 'indian philosopher',
    'indian spiritual', 'indian tradition', 'indian scripture', 'indian festival', 'indian ritual', 'indian temple', 'indian mythology',
    'indian epic', 'indian purana', 'indian smriti', 'indian shruti', 'indian yoga', 'indian dharma', 'indian caste', 'indian varna',
    'indian mantra', 'indian puja', 'indian music', 'indian dance', 'indian art', 'indian literature', 'indian history', 'indian culture',
    'indian civilization', 'indian society', 'indian religion', 'indian god', 'indian goddess', 'indian deity', 'indian avatar', 'indian incarnation'
    'shabda', 'ranade', 'maharishi', 'mahesh yogi', 'atmatusti', 'shakti pitha', 'pitha', 'chandogya upanishad', 'shiva purana',
    'kashmir shaivism', 'iskcon', 'krishna consciousness', 'gotra', 'trailanga', 'vairagya', 'kapalika', 'diet in hinduism',
    'namakarana', 'nāmakaraṇa', 'matrika', 'matrikas', 'svara', 'third eye', 'samaveda', 'timeline of hindu texts', 'hindu studies',
    'prashna upanishad', 'yoga vasistha'
]

LINKS_CSV = 'links.csv'


def is_relevant(title, url):
    """
    Check if the title or url contains any Hinduism/Sanatana Dharma keywords.
    """
    title_lower = title.lower()
    url_lower = url.lower()
    for kw in KEYWORDS:
        if kw in title_lower or kw in url_lower:
            return True
    return False


def filter_links():
    relevant_rows = []
    import os
    import shutil
    # Ensure filtered directory exists
    if not os.path.exists('filtered'):
        os.makedirs('filtered')
    with open(LINKS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with open('filtered.csv', 'a', encoding='utf-8', newline='') as filtered_f:
            writer = csv.DictWriter(filtered_f, fieldnames=reader.fieldnames)
            for row in reader:
                title = row.get('title', '')
                url = row.get('url', '')
                if is_relevant(title, url):
                    relevant_rows.append(row)
                    writer.writerow(row)
                    src_txt = os.path.join('articles', f"{title.replace('/', '_')}_clean.txt")
                    dst_txt = os.path.join('filtered', f"{title.replace('/', '_')}_clean.txt")
                    if os.path.exists(src_txt):
                        shutil.copy2(src_txt, dst_txt)
    return relevant_rows


def send_to_ai(rows):
    import csv
    import time
    batch_size = 10
    keywords_str = ', '.join(KEYWORDS)
    system_prompt = (
        "You are an expert on Hinduism and Sanatana Dharma. "
        "Given a list of Wikipedia articles, and a list of keywords (not exclusive or complete), "
        "return a CSV with columns: Serial no,title,url,timestamp,valid. "
        "For each row, valid should be True if the article is relevant to Hinduism/Sanatan Dharma, otherwise False. "
        "Use the keywords as a guide, but use your own knowledge as well."
        "Final result structure: Serial no,title,url,timestamp,valid"
    )
    with open('ai_filtered.csv', 'a', encoding='utf-8', newline='') as out_f:
        writer = None
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            input_csv = 'Serial no,title,url,timestamp\n' + '\n'.join([
                f"{r.get('Serial no', r.get('serial no', r.get('serial_no', '')))},{r['title']},{r['url']},{r['timestamp']}" for r in batch
            ])
            user_prompt = (
                f"KEYWORDS: {keywords_str}\n" +
                f"{input_csv}\n" +
                "Return the same CSV with an extra column 'valid' (True/False) for each row."
            )
            prompt = system_prompt + "\n" + user_prompt
            # Retry logic for 429 errors
            max_retries = 5
            delay = 5
            for attempt in range(max_retries):
                answer = ask_model(prompt)
                if answer is None or (isinstance(answer, str) and '429' in answer):
                    print(f"429 Too Many Requests, retrying in {delay} seconds (attempt {attempt+1}/{max_retries})...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    break
            # Parse and write output
            if answer:
                lines = answer.strip().splitlines()
                if writer is None and lines:
                    header = lines[0].strip().split(',')
                    writer = csv.DictWriter(out_f, fieldnames=header)
                    writer.writeheader()
                for line in lines[1:]:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) == len(writer.fieldnames):
                        writer.writerow(dict(zip(writer.fieldnames, parts)))


if __name__ == "__main__":
    relevant_rows = filter_links()
    print(f"Found {len(relevant_rows)} potentially relevant articles.")
    #send_to_ai(relevant_rows)
