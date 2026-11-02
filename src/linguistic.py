# Lab experiments 4, 6, and 7: morphology, POS tagging, and phrase chunking.
# This file finds simple noun-phrase candidates in a resume.

from pathlib import Path

import pandas as pd
from nltk import pos_tag
from nltk.chunk import RegexpParser

from preprocess import INPUT_FILE, OUTPUT_FILE, TOKENIZER

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
CLEAN_FILE = PROJECT_FOLDER / "data" / "resumes_clean.csv"

# Group adjectives and noun-like words into short phrases.
PHRASE_GRAMMAR = r"NP: {<JJ.*>*<NN.*|VBG.*>+}"
CHUNKER = RegexpParser(PHRASE_GRAMMAR)


def analyze_resume(text):
    """Return POS tags and noun-phrase chunks for one cleaned resume."""
    tokens = TOKENIZER.tokenize(str(text))
    tagged_words = pos_tag(tokens)
    chunk_tree = CHUNKER.parse(tagged_words)

    noun_phrases = []
    for subtree in chunk_tree.subtrees():
        if subtree.label() == "NP":
            phrase = " ".join(word for word, tag in subtree.leaves())
            if phrase not in noun_phrases:
                noun_phrases.append(phrase)

    return tagged_words, noun_phrases


def show_sample_output(number_of_resumes=3):
    """Run POS tagging and chunking on a few cleaned resumes."""
    data = pd.read_csv(CLEAN_FILE)
    for row_number, row in data.head(number_of_resumes).iterrows():
        tags, phrases = analyze_resume(row["Cleaned_Resume"])
        print(f"\nResume {row_number + 1} ({row['Category']})")
        print("POS sample:", tags[:12])
        print("Noun phrases:", phrases[:8])


if __name__ == "__main__":
    show_sample_output()
