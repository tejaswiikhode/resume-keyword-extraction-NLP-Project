# Lab experiment 9: TF-IDF and cosine similarity between two texts.
# The Streamlit page displays resume keywords and job-description matches.

from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from entities import extract_entities
from keywords import extract_keyword_report, find_common_skills, fit_keyword_model
from preprocess import TOKENIZER, clean_text

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
CLEAN_FILE = PROJECT_FOLDER / "data" / "resumes_clean.csv"


def match_resume_to_job(resume_text, job_description, number_of_keywords=15):
    """Compare a resume and job description, then list matched and missing terms."""
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_description)

    vectorizer = TfidfVectorizer(
        tokenizer=TOKENIZER.tokenize,
        token_pattern=None,
        lowercase=True,
        ngram_range=(1, 3),
    )
    matrix = vectorizer.fit_transform([resume_clean, job_clean])
    similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    features = vectorizer.get_feature_names_out()

    resume_scores = matrix[0].toarray()[0]
    job_scores = matrix[1].toarray()[0]
    resume_skills = find_common_skills(resume_clean)
    job_skills = find_common_skills(job_clean)
    skill_parts = {
        word
        for skill in resume_skills + job_skills
        for word in skill.split()
    }

    resume_terms = []
    for index in resume_scores.argsort()[::-1]:
        term = features[index]
        if (
            resume_scores[index] > 0
            and len(term.split()) == 1
            and term not in skill_parts
        ):
            resume_terms.append(term)
        if len(resume_terms) == number_of_keywords:
            break

    # Shorter terms make the missing-keyword list easier to explain.
    general_words = {"experience", "year", "month", "skill", "skills"}
    job_terms = []
    for index in job_scores.argsort()[::-1]:
        term = features[index]
        if (
            job_scores[index] > 0
            and len(term.split()) == 1
            and term not in general_words
            and term not in skill_parts
        ):
            job_terms.append(term)
        if len(job_terms) == number_of_keywords:
            break

    # Add skill names to the job's keyword list so the result is easier to explain.
    for skill in job_skills:
        if skill not in job_terms:
            job_terms.append(skill)

    resume_terms.extend(resume_skills)
    resume_term_set = set(resume_terms)
    matched = [term for term in job_terms if term in resume_term_set]
    missing = [term for term in job_terms if term not in resume_term_set]

    return {
        "similarity": float(similarity),
        "matched_keywords": matched,
        "missing_keywords": missing,
    }


@st.cache_data

def load_cleaned_data():
    """Load the deduplicated resume file for the app."""
    return pd.read_csv(CLEAN_FILE)


@st.cache_resource

def load_keyword_model():
    """Fit the TF-IDF keyword model once for the app session."""
    data = load_cleaned_data()
    return fit_keyword_model(data)[0]


def run_app():
    """Show the resume picker and matching results in Streamlit."""
    st.title("Resume Keyword Extraction")
    st.write("Choose a resume to see keywords, entities, and job-description similarity.")
    st.caption("Results assist human review. General-purpose NLP can miss or mislabel skills.")

    data = load_cleaned_data()
    categories = sorted(data["Category"].dropna().unique())
    selected_category = st.selectbox("Resume category", categories)
    category_rows = data[data["Category"] == selected_category].reset_index(drop=True)
    resume_number = st.selectbox(
        "Resume",
        range(len(category_rows)),
        format_func=lambda number: f"Resume {number + 1}",
    )
    resume = category_rows.iloc[resume_number]

    with st.expander("View resume text"):
        st.text(resume["Resume"])

    keyword_model = load_keyword_model()
    keyword_report = extract_keyword_report(resume["Cleaned_Resume"], keyword_model)
    first, second, third = st.columns(3)
    first.write("**TF-IDF keywords**")
    first.write(", ".join(keyword_report["tfidf_keywords"]))
    second.write("**Noun phrases**")
    second.write(", ".join(keyword_report["noun_phrases"]))
    third.write("**Common skills**")
    third.write(", ".join(keyword_report["common_skills"]))

    st.subheader("Named entities")
    st.write(extract_entities(resume["Resume"]) or "No entities recognized.")

    st.subheader("Compare with a job description")
    job_description = st.text_area("Paste the job description", height=180)
    if job_description.strip():
        result = match_resume_to_job(resume["Resume"], job_description)
        st.metric("Cosine similarity", f"{result['similarity']:.1%}")
        left, right = st.columns(2)
        left.write("**Matched keywords**")
        left.write(", ".join(result["matched_keywords"]) or "No exact keyword matches.")
        right.write("**Missing job keywords**")
        right.write(", ".join(result["missing_keywords"]) or "No missing keywords.")
        st.caption("Keyword matching is based on exact cleaned terms and phrases.")


def show_sample_output():
    """Compare three sample resumes with the same short job description."""
    data = pd.read_csv(CLEAN_FILE)
    job_description = (
        "Data analyst with Python, SQL, machine learning, Tableau, and AWS experience."
    )
    print("Sample job description:", job_description)

    for row_number, row in data.head(3).iterrows():
        result = match_resume_to_job(row["Resume"], job_description)
        print(f"\nResume {row_number + 1} ({row['Category']})")
        print(f"Cosine similarity: {result['similarity']:.3f}")
        print("Matched:", result["matched_keywords"])
        print("Missing:", result["missing_keywords"])


if __name__ == "__main__":
    if "--sample" in sys.argv:
        show_sample_output()
    else:
        run_app()
