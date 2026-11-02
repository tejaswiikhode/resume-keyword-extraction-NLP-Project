# Project Context: Resume Keyword Extraction using NLP

## Project

Build a small, explainable NLP lab mini project that extracts useful keywords from resumes in `data/UpdatedResumeDataSet.csv` and presents results in a simple Streamlit interface. Use the existing lab experiments as the foundation. Keep the implementation beginner-friendly and use only NLTK, spaCy, scikit-learn, pandas, matplotlib, wordcloud, and Streamlit.

## Problem statement (from experiment 1)

Recruiters spend substantial time screening resumes, and manual review becomes difficult when many applications arrive.
Important skills and qualifications can be missed during that review.
Create an NLP system that extracts useful resume keywords and presents them in a structured way to help recruiters review candidates faster.

## Existing experiment techniques

| Experiment | Technique used |
| --- | --- |
| exp1 | Survey of NLP applications and formulation of the resume keyword extraction problem statement. |
| exp2 | Text preprocessing: word tokenization, filtration of punctuation/symbols/numbers/extra spaces, and English-script validation. |
| exp3 | Stopword removal, lemmatization, and stemming; compares original, normalized, and stemmed words. |
| exp4 | Morphological analysis and word generation using tokenization, POS tagging, and lemmatization. |
| exp5 | Unigram, bigram, and trigram generation and frequency analysis. |
| exp6 | POS tagging with NLTK on resume text. |
| exp7 | Shallow phrase chunking using POS tags and a regular-expression grammar (NP chunks). |
| exp8 | Named entity recognition using NLTK `ne_chunk` and spaCy's pretrained English model. |
| exp9 | TF-IDF vectorization and cosine similarity for comparing documents, including resume/job-text style comparisons. |
| exp10 | Text exploratory analysis: dataset/category and word-count summaries, word frequencies, and overall/category word clouds. |

The syllabus frames experiments 1-8 as a selected case study sequence, followed by text similarity (exp9), word-cloud EDA (exp10), and a mini project. This project follows that sequence.

## Dataset notes

- File: `data/UpdatedResumeDataSet.csv`; columns are `Category` and `Resume`.
- 962 rows and 25 categories; no missing category or resume values were found.
- Category counts: Advocate 20; Arts 36; Automation Testing 26; Blockchain 40; Business Analyst 28; Civil Engineer 24; Data Science 40; Database 33; DevOps Engineer 55; DotNet Developer 28; ETL Developer 40; Electrical Engineering 30; HR 44; Hadoop 42; Health and fitness 30; Java Developer 84; Mechanical Engineer 40; Network Security Engineer 25; Operations Manager 40; PMO 30; Python Developer 48; SAP Developer 24; Sales 40; Testing 70; Web Designing 45.
- Exact duplicate resume text appears often: 796 rows are repeats after the first occurrence; 958 rows belong to repeated-text groups, representing 162 repeated texts. There are 166 distinct resume texts in total. Repeated texts were not found under different categories.
- Likely encoding artifacts appear in the resumes, for example `NaÃ¯ve Bayes` and sequences resembling `â  ¢`; 728 rows contain likely artifacts. Preserve the source CSV. During cleaning, handle suspicious text carefully and avoid silently damaging valid technical terms or punctuation such as `C++`, `C#`, `.NET`, and `scikit-learn`.

## Simple project plan

1. **Load and inspect (exp1, exp10)** — Read the CSV with pandas. Show the row count, category counts, missing values, duplicate-resume summary, and a short sample resume. Keep the original file untouched.
2. **Clean text (exp2)** — Normalize whitespace and case, tokenize with NLTK, and filter obvious noise. Record encoding artifacts for review. Keep useful skill spelling and symbols where possible; avoid an overly broad “letters only” filter that would turn `C++` or `C#` into misleading text. Treat script validation as a check/report rather than deleting whole resumes automatically.
3. **Normalize words (exp3, exp4)** — Remove English stopwords and lemmatize tokens. Keep stemming as an optional comparison from the lab; use lemmatized words for the main keyword output because stems can be hard to explain as skills.
4. **Find phrase candidates (exp4, exp6, exp7)** — POS-tag cleaned text, inspect nouns/adjectives, and use a simple noun-phrase chunk grammar to collect multiword candidates such as “machine learning.”
5. **Add supporting NLP signals (exp5, exp8)** — Generate unigrams, bigrams, and trigrams. Run NLTK or spaCy NER as an additional signal for names, organizations, dates, and places. Treat NER as supporting information: general-purpose NER may not recognize every technology or skill correctly.
6. **Rank keywords (exp5, exp9)** — Use scikit-learn `TfidfVectorizer` to rank informative terms and phrases in each resume. Explain that higher TF-IDF means a term is frequent in that resume but less common across the comparison corpus. Use cosine similarity as an optional feature to compare a resume with a short job description.
7. **Explore results (exp10)** — Use pandas summaries and matplotlib charts for category counts and resume lengths; use WordCloud for an overall view and selected category views. Remove stopwords first and interpret clouds as visual summaries, not proof of keyword quality.
8. **Present (mini project)** — Build a small Streamlit page with a resume/category selector, extracted top keywords, phrase candidates, optional NER results, and optional job-description similarity. Add a brief note that the output assists human review and can miss or mislabel skills.
9. **Account for duplicates** — Report both original and unique-resume totals. Consider using unique resume texts for corpus-level TF-IDF and word-frequency summaries so repeated copies do not dominate corpus statistics; retain the original rows for reporting category counts.

## Viva explanation

Explain the pipeline as: clean the resume, normalize words, find candidate terms and phrases, rank them with TF-IDF, and show the results. POS/chunking and NER provide extra linguistic clues; cosine similarity is a separate optional comparison with job text. Each stage reuses techniques already practiced in experiments 2-10.
