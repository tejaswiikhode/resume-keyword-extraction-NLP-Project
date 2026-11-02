# Lab experiment 8: named entity recognition with spaCy.
# The general-purpose model gives extra context about people, places, and organizations.

from pathlib import Path

import pandas as pd
import spacy

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
CLEAN_FILE = PROJECT_FOLDER / "data" / "resumes_clean.csv"
MODEL_NAME = "en_core_web_sm"


def load_nlp_model():
    """Load the small English spaCy model used in the lab."""
    try:
        return spacy.load(MODEL_NAME)
    except OSError as error:
        raise OSError(
            "spaCy model en_core_web_sm is missing. Install it with: "
            "python -m spacy download en_core_web_sm"
        ) from error


NLP = load_nlp_model()


def extract_entities(text):
    """Return unique entity names and their spaCy labels."""
    document = NLP(str(text))
    entities = []

    for entity in document.ents:
        item = (entity.text, entity.label_)
        if item not in entities:
            entities.append(item)

    return entities


def show_sample_output(number_of_resumes=3):
    """Run NER on a few cleaned resumes and print the recognized entities."""
    data = pd.read_csv(CLEAN_FILE)
    for row_number, row in data.head(number_of_resumes).iterrows():
        print(f"\nResume {row_number + 1} ({row['Category']})")
        print("Entities:", extract_entities(row["Resume"])[:12])


if __name__ == "__main__":
    show_sample_output()
