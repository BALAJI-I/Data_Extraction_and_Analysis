
---

## ⚙️ Features

- ✅ Web scraping with `requests` and `BeautifulSoup`
- ✅ Retry mechanism for failed URLs (e.g., 429 errors)
- ✅ Text cleaning with NLTK stop words
- ✅ Custom sentiment analysis using positive/negative word dictionaries
- ✅ Readability metrics like FOG Index, Average Sentence Length, etc.
- ✅ Export to Excel using `pandas` and `xlsxwriter`

---

## 🧪 NLP Metrics Computed

| Metric                       | Description                                               |
|-----------------------------|-----------------------------------------------------------|
| Positive Score              | # of positive words from dictionary                       |
| Negative Score              | # of negative words from dictionary                       |
| Polarity Score              | (Pos - Neg) / (Pos + Neg)                                 |
| Subjectivity Score          | (Pos + Neg) / Total words                                 |
| Avg Sentence Length         | Words / Sentences                                         |
| % of Complex Words          | Complex words / Total words                               |
| FOG Index                   | 0.4 × (Avg Sentence Length + % Complex Words)             |
| Complex Word Count          | Words with >2 syllables                                   |
| Word Count                  | Total cleaned words                                       |
| Syllables per Word          | Total syllables / total words                             |
| Personal Pronouns           | Count of “I”, “we”, “us”, “my”, “ours” (excluding "US")   |
| Avg Word Length             | Total characters / total words                            |

---

## 🛠️ How to Run

1. ✅ Clone the repo:
   ```bash
   git clone https://github.com/yourusername/nlp-blackcoffer-assignment.git
   cd nlp-blackcoffer-assignment
