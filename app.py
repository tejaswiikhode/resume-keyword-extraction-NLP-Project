# Lab experiments 2, 3, 5, and 9: cleaning, lemmatization, N-grams, and TF-IDF.
# This Streamlit app analyzes a pasted resume and an optional job description.

from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_FOLDER = Path(__file__).resolve().parent
SRC_FOLDER = PROJECT_FOLDER / "src"
CLEAN_FILE = PROJECT_FOLDER / "data" / "resumes_clean.csv"

# Let this root-level app reuse the existing lab stages in the src folder.
sys.path.insert(0, str(SRC_FOLDER))

from keywords import find_common_skills, fit_keyword_model
from preprocess import TOKENIZER, clean_text


@st.cache_data
def load_cleaned_resumes():
    """Load the deduplicated resume collection used to learn TF-IDF scores."""
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(
            "The cleaned dataset is missing. Run python src/preprocess.py first."
        )
    return pd.read_csv(CLEAN_FILE)


@st.cache_resource
def load_keyword_vectorizer():
    """Fit the keyword model once and reuse it while the app is open."""
    resumes = load_cleaned_resumes()
    vectorizer, matrix = fit_keyword_model(resumes)
    return vectorizer


def get_top_keywords(cleaned_resume, vectorizer, number_to_show=10):
    """Return each top keyword and its TF-IDF score for the pasted resume."""
    resume_vector = vectorizer.transform([cleaned_resume])
    scores = resume_vector.toarray()[0]
    terms = vectorizer.get_feature_names_out()
    sorted_indexes = scores.argsort()[::-1]

    keyword_rows = []
    for index in sorted_indexes:
        if scores[index] > 0:
            keyword_rows.append(
                {"Keyword": terms[index], "TF-IDF score": round(float(scores[index]), 3)}
            )
        if len(keyword_rows) == number_to_show:
            break

    return keyword_rows


def compare_with_job(cleaned_resume, job_description):
    """Return cosine similarity and common-skill matches for an optional job text."""
    cleaned_job = clean_text(job_description)
    vectorizer = load_keyword_vectorizer()
    vectors = vectorizer.transform([cleaned_resume, cleaned_job])
    percentage = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

    resume_skills = set(find_common_skills(cleaned_resume))
    job_skills = find_common_skills(cleaned_job)
    matched_skills = [skill for skill in job_skills if skill in resume_skills]
    missing_skills = [skill for skill in job_skills if skill not in resume_skills]

    return percentage, matched_skills, missing_skills


def analyze_resume(resume_text, job_description="", vectorizer=None):
    """Analyze pasted text and return skills, scored keywords, and optional match."""
    cleaned_resume = clean_text(resume_text)
    if vectorizer is None:
        vectorizer = load_keyword_vectorizer()

    result = {
        "skills": find_common_skills(cleaned_resume),
        "keywords": get_top_keywords(cleaned_resume, vectorizer),
        "match_percentage": None,
        "matched_skills": [],
        "missing_skills": [],
    }

    if job_description.strip():
        percentage, matched, missing = compare_with_job(cleaned_resume, job_description)
        result["match_percentage"] = percentage
        result["matched_skills"] = matched
        result["missing_skills"] = missing

    return result


def run_app():
    """Show the resume input form and its NLP results."""
    st.title("Resume Keyword Extraction")
    st.write("Paste a resume to extract common skills and rank its keywords.")
    st.caption("A job description is optional. The match percentage uses TF-IDF cosine similarity.")

    try:
        vectorizer = load_keyword_vectorizer()
    except FileNotFoundError as error:
        st.error(str(error))
        return

    with st.form("resume_form"):
        resume_text = st.text_area("Resume text", height=240)
        job_description = st.text_area("Job description (optional)", height=160)
        submitted = st.form_submit_button("Analyze resume")

    if submitted:
        if not resume_text.strip():
            st.warning("Paste resume text before analyzing.")
            return

        result = analyze_resume(resume_text, job_description, vectorizer)

        st.subheader("Extracted skills")
        if result["skills"]:
            st.write(", ".join(result["skills"]))
        else:
            st.write("No skills from the built-in list were found.")

        st.subheader("Top keywords")
        if result["keywords"]:
            st.dataframe(pd.DataFrame(result["keywords"]), hide_index=True, width="stretch")
        else:
            st.info("No resume words matched the dataset vocabulary used by TF-IDF.")

        if result["match_percentage"] is not None:
            st.subheader("Job description match")
            st.metric("Match percentage", f"{result['match_percentage']:.1f}%")
            left, right = st.columns(2)
            left.write("**Matched listed skills**")
            left.write(", ".join(result["matched_skills"]) or "No listed skills matched.")
            right.write("**Missing listed skills**")
            right.write(", ".join(result["missing_skills"]) or "No listed skills are missing.")

    with st.expander("Sample text to try"):
        st.markdown("**Resume**")
        st.code(SAMPLE_RESUME)
        st.markdown("**Job description**")
        st.code(SAMPLE_JOB)


SAMPLE_RESUME = (
    "Data analyst with 3 years of experience using Python, SQL, pandas, "
    "scikit-learn, machine learning, Tableau, and AWS. Built dashboards, "
    "cleaned customer data, and trained classification models."
)
SAMPLE_JOB = (
    "Seeking a data analyst skilled in Python, SQL, machine learning, Tableau, "
    "and AWS. Experience building dashboards and preparing customer data is preferred."
)


def show_sample_output():
    """Run the same analysis on the sample text and print its results."""
    resumes = pd.read_csv(CLEAN_FILE)
    vectorizer, matrix = fit_keyword_model(resumes)
    result = analyze_resume(SAMPLE_RESUME, SAMPLE_JOB, vectorizer)
    print(f"TF-IDF model: {matrix.shape[0]} resumes, {matrix.shape[1]} terms")
    print("Extracted skills:", result["skills"])
    print("Top keywords:", result["keywords"])
    print(f"Match percentage: {result['match_percentage']:.1f}%")
    print("Matched skills:", result["matched_skills"])
    print("Missing skills:", result["missing_skills"])


if __name__ == "__main__":
    if "--sample" in sys.argv:
        show_sample_output()
    else:
        run_app()
