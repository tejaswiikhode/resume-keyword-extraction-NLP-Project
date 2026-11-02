# Lab experiments 5 and 9: N-grams and TF-IDF keyword ranking.
# POS based noun phrases and a short skills list add readable keyword candidates.

from pathlib import Path
import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from linguistic import analyze_resume
from preprocess import TOKENIZER

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
CLEAN_FILE = PROJECT_FOLDER / "data" / "resumes_clean.csv"

# A small editable list of common resume skills and technologies.
COMMON_SKILLS = [
    "python", "java", "javascript", "c++", "c#", ".net", "sql", "mysql",
    "postgresql", "pandas", "numpy", "scikit-learn", "machine learning",
    "deep learning", "natural language processing", "nlp", "tensorflow",
    "pytorch", "keras", "aws", "azure", "docker", "kubernetes", "git",
    "linux", "hadoop", "spark", "tableau", "power bi", "excel", "html",
    "css", "react", "angular", "node.js", "flask", "django", "data analysis",
    "data science", "statistics", "regression", "svm", "random forest",
    "decision tree", "kafka", "elasticsearch", "matplotlib", "mongodb",
]


def fit_keyword_model(data=None):
    """Learn unigram, bigram, and trigram TF-IDF scores from unique resumes."""
    if data is None:
        data = pd.read_csv(CLEAN_FILE)

    vectorizer = TfidfVectorizer(
        tokenizer=TOKENIZER.tokenize,
        token_pattern=None,
        lowercase=True,
        ngram_range=(1, 3),
        max_df=0.95,
    )
    resume_matrix = vectorizer.fit_transform(data["Cleaned_Resume"].fillna(""))
    return vectorizer, resume_matrix


def find_common_skills(text):
    """Find whole skill names, avoiding matches such as Java inside JavaScript."""
    found_skills = []
    lowered_text = str(text).lower()

    for skill in COMMON_SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, lowered_text):
            found_skills.append(skill)

    return found_skills


def extract_keyword_report(text, vectorizer, top_count=10):
    """Return TF-IDF keywords, short noun phrases, and common skill matches."""
    cleaned_text = str(text)
    row = vectorizer.transform([cleaned_text])
    feature_names = vectorizer.get_feature_names_out()
    scores = row.toarray()[0]
    ranked_indexes = scores.argsort()[::-1]

    tfidf_keywords = [
        feature_names[index]
        for index in ranked_indexes
        if scores[index] > 0
    ][:top_count]

    # Keep useful two or three word pieces from POS based noun chunks.
    _, chunks = analyze_resume(cleaned_text)
    phrase_candidates = set()
    for chunk in chunks:
        words = TOKENIZER.tokenize(chunk.lower())
        for phrase_size in (2, 3):
            for start in range(len(words) - phrase_size + 1):
                phrase_candidates.add(" ".join(words[start:start + phrase_size]))

    phrase_scores = []
    for phrase in phrase_candidates:
        feature_index = vectorizer.vocabulary_.get(phrase)
        if feature_index is not None and scores[feature_index] > 0:
            phrase_scores.append((phrase, scores[feature_index]))
    phrase_scores.sort(key=lambda item: item[1], reverse=True)
    noun_phrases = [phrase for phrase, score in phrase_scores[:8]]

    return {
        "tfidf_keywords": tfidf_keywords,
        "noun_phrases": noun_phrases,
        "common_skills": find_common_skills(cleaned_text),
    }


def show_sample_output(number_of_resumes=3):
    """Rank keywords for a few cleaned resumes and print the result."""
    data = pd.read_csv(CLEAN_FILE)
    vectorizer, resume_matrix = fit_keyword_model(data)
    print(f"TF-IDF matrix shape: {resume_matrix.shape}")

    for row_number, row in data.head(number_of_resumes).iterrows():
        report = extract_keyword_report(row["Cleaned_Resume"], vectorizer)
        print(f"\nResume {row_number + 1} ({row['Category']})")
        print("TF-IDF keywords:", report["tfidf_keywords"])
        print("Noun phrases:", report["noun_phrases"])
        print("Common skills:", report["common_skills"])


if __name__ == "__main__":
    show_sample_output()
