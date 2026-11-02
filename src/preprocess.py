# Lab experiments 2 and 3: text cleaning, stopword removal, and lemmatization.
# This file creates one clean row for each unique resume.

from pathlib import Path
import re

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_FOLDER / "data" / "UpdatedResumeDataSet.csv"
OUTPUT_FILE = PROJECT_FOLDER / "data" / "resumes_clean.csv"

# Keep common technology names with punctuation as one token.
TOKENIZER = RegexpTokenizer(r"(?:\.[A-Za-z0-9]+|[A-Za-z0-9]+(?:[+#./-][A-Za-z0-9+#/-]+)*(?:[+#]+)?)")
LEMMATIZER = WordNetLemmatizer()


def clean_text(text):
    """Lowercase and normalize a resume, then remove stopwords and lemmatize."""
    text = str(text).replace("NaÃ¯ve", "Naive").replace("naÃ¯ve", "naive")
    text = text.replace("â  ¢", " ").replace("\ufffd", " ")
    text = re.sub(r"\s+", " ", text.lower()).strip()

    stop_words = set(stopwords.words("english"))
    tokens = TOKENIZER.tokenize(text)
    useful_tokens = []

    for token in tokens:
        # Keep words, numbers, and useful terms such as C++, C#, .NET, and scikit-learn.
        if any(character.isalnum() for character in token):
            lemma = LEMMATIZER.lemmatize(token)
            if lemma not in stop_words:
                useful_tokens.append(lemma)

    return " ".join(useful_tokens)


def prepare_dataset():
    """Remove duplicate resumes, clean each resume, and save a new CSV."""
    data = pd.read_csv(INPUT_FILE)
    original_count = len(data)

    # Keep the first copy of each exact resume; leave the original CSV untouched.
    data = data.drop_duplicates(subset="Resume", keep="first").copy()
    data["Cleaned_Resume"] = data["Resume"].apply(clean_text)
    data.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Original rows: {original_count}")
    print(f"Unique resumes saved: {len(data)}")
    print(f"Duplicate rows removed: {original_count - len(data)}")
    print(f"Saved: {OUTPUT_FILE}")
    print("Sample cleaned resumes:")
    for _, row in data.head(3).iterrows():
        print(f"- {row['Category']}: {row['Cleaned_Resume'][:180]}")

    return data


if __name__ == "__main__":
    prepare_dataset()
