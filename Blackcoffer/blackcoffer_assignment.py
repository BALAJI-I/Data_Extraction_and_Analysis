import os
import re
import time
import pandas as pd
import requests
import nltk
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize
import syllapy


nltk.download('punkt')
nltk.download('stopwords')


stop_words = set()
stopword_folders = ["StopWords"]
for folder in stopword_folders:
    for filename in os.listdir(folder):
        with open(os.path.join(folder, filename), "r", encoding="utf-8", errors="ignore") as f:
            stop_words.update(f.read().split())

positive_words, negative_words = set(), set()
with open("MasterDictionary/positive-words.txt", "r", encoding="utf-8", errors="ignore") as pos_file:
    positive_words.update(pos_file.read().split())
with open("MasterDictionary/negative-words.txt", "r", encoding="utf-8", errors="ignore") as neg_file:
    negative_words.update(neg_file.read().split())


df = pd.read_excel("Input.xlsx")


os.makedirs("extracted_texts_2", exist_ok=True)

def extract_text(url, max_retries=3):
    """Extracts title and article text from a URL with retries and delays."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    }
    
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers, timeout=20) 
            if response.status_code == 429:
                wait_time = 5 + (retries * 5)
                print(f"Too many requests (429) for {url}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
                continue
            elif response.status_code != 200:
                print(f"Skipping {url}: HTTP {response.status_code}")
                return None, None

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("title").text.strip() if soup.find("title") else "No Title"
            paragraphs = soup.find_all("p")
            article_text = " ".join(p.text.strip() for p in paragraphs)

            return title, article_text
        except requests.exceptions.RequestException as e:
            print(f"Error extracting {url}: {e}")
            retries += 1
            time.sleep(5)

    return None, None  

def clean_text(text):
    """Removes stopwords and non-alphabetic words."""
    words = word_tokenize(text.lower())
    return [word for word in words if word.isalpha() and word not in stop_words]

def count_syllables(word):
    """Counts syllables in a word."""
    return max(1, syllapy.count(word))

def analyze_text(text):
    """Performs text analysis."""
    words = clean_text(text)
    sentences = sent_tokenize(text)
    
    word_count = len(words)
    complex_words = [w for w in words if count_syllables(w) > 2]
    syllable_count = sum(count_syllables(w) for w in words)
    personal_pronouns = len(re.findall(r'\b(I|we|my|ours|us|mine|me)\b', text, re.I)) - len(re.findall(r'\bUS\b', text))
    
    pos_score = sum(1 for w in words if w in positive_words)
    neg_score = sum(1 for w in words if w in negative_words)
    
    polarity_score = (pos_score - neg_score) / ((pos_score + neg_score) + 0.000001)
    subjectivity_score = (pos_score + neg_score) / (word_count + 0.000001)
    
    avg_sentence_length = word_count / len(sentences) if sentences else 0
    complex_word_pct = len(complex_words) / word_count if word_count else 0
    fog_index = 0.4 * (avg_sentence_length + complex_word_pct * 100)
    avg_word_length = sum(len(w) for w in words) / word_count if word_count else 0

    return {
        "POSITIVE SCORE": pos_score,
        "NEGATIVE SCORE": neg_score,
        "POLARITY SCORE": polarity_score,
        "SUBJECTIVITY SCORE": subjectivity_score,
        "AVG SENTENCE LENGTH": avg_sentence_length,
        "PERCENTAGE OF COMPLEX WORDS": complex_word_pct * 100,
        "FOG INDEX": fog_index,
        "AVG NUMBER OF WORDS PER SENTENCE": avg_sentence_length,
        "COMPLEX WORD COUNT": len(complex_words),
        "WORD COUNT": word_count,
        "SYLLABLE PER WORD": syllable_count / word_count if word_count else 0,
        "PERSONAL PRONOUNS": personal_pronouns,
        "AVG WORD LENGTH": avg_word_length
    }

output_data = []

for _, row in df.iterrows():
    url_id, url = row["URL_ID"], row["URL"]
    
    print(f"Processing: {url} ...")
    title, text = extract_text(url)

    if text:
        file_path = f"extracted_texts_2/{url_id}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"{title}\n{text}")

        metrics = analyze_text(text)
        output_data.append([url_id, f'=HYPERLINK("{url}")', title] + list(metrics.values()))

    time.sleep(2 + (5 * (os.urandom(1)[0] % 3)))  


output_columns = ["URL_ID", "URL", "TITLE", "POSITIVE SCORE", "NEGATIVE SCORE", "POLARITY SCORE", 
                  "SUBJECTIVITY SCORE", "AVG SENTENCE LENGTH", "PERCENTAGE OF COMPLEX WORDS", 
                  "FOG INDEX", "AVG NUMBER OF WORDS PER SENTENCE", "COMPLEX WORD COUNT", 
                  "WORD COUNT", "SYLLABLE PER WORD", "PERSONAL PRONOUNS", "AVG WORD LENGTH"]

output_df = pd.DataFrame(output_data, columns=output_columns)

output_file = "Output_1.xlsx"
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    output_df.to_excel(writer, index=False, sheet_name="Results")

print(f"Processing complete. Output saved to {output_file}")
