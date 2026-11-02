# Lab experiment 10: text EDA, category charts, and word clouds.
# Charts use original category counts and unique resumes for text summaries.

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
ORIGINAL_FILE = PROJECT_FOLDER / "data" / "UpdatedResumeDataSet.csv"
CLEAN_FILE = PROJECT_FOLDER / "data" / "resumes_clean.csv"
FIGURE_FOLDER = PROJECT_FOLDER / "outputs" / "figures"


def make_figures():
    """Save category, resume-length, and word-cloud figures."""
    FIGURE_FOLDER.mkdir(parents=True, exist_ok=True)
    original_data = pd.read_csv(ORIGINAL_FILE)
    clean_data = pd.read_csv(CLEAN_FILE)

    # Keep original rows for category counts so duplicate removal does not change them.
    top_categories = original_data["Category"].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    top_categories.sort_values().plot(kind="barh", color="steelblue")
    plt.title("Top 10 Resume Categories (Original Dataset)")
    plt.xlabel("Number of resumes")
    plt.tight_layout()
    category_path = FIGURE_FOLDER / "top_categories.png"
    plt.savefig(category_path, dpi=150)
    plt.close()

    clean_data["Word_Count"] = clean_data["Cleaned_Resume"].fillna("").str.split().str.len()
    plt.figure(figsize=(9, 5))
    plt.hist(clean_data["Word_Count"], bins=20, color="coral", edgecolor="white")
    plt.title("Resume Lengths After Duplicate Removal")
    plt.xlabel("Words per resume")
    plt.ylabel("Number of resumes")
    plt.tight_layout()
    length_path = FIGURE_FOLDER / "resume_lengths.png"
    plt.savefig(length_path, dpi=150)
    plt.close()

    all_text = " ".join(clean_data["Cleaned_Resume"].fillna(""))
    all_cloud = WordCloud(
        width=1200,
        height=700,
        background_color="white",
        max_words=150,
        collocations=False,
    ).generate(all_text)
    plt.figure(figsize=(12, 7))
    plt.imshow(all_cloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Common Resume Terms (Unique Resumes)")
    all_cloud_path = FIGURE_FOLDER / "all_resumes_wordcloud.png"
    plt.savefig(all_cloud_path, dpi=150, bbox_inches="tight")
    plt.close()

    # Save a separate word cloud for each of the three largest original categories.
    category_cloud_paths = []
    for category in top_categories.index[:3]:
        category_text = " ".join(
            clean_data.loc[clean_data["Category"] == category, "Cleaned_Resume"].fillna("")
        )
        if not category_text.strip():
            continue

        cloud = WordCloud(
            width=1000,
            height=600,
            background_color="white",
            max_words=100,
            collocations=False,
        ).generate(category_text)
        plt.figure(figsize=(10, 6))
        plt.imshow(cloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Resume Keywords: {category}")
        safe_name = "_".join(str(category).lower().split())
        cloud_path = FIGURE_FOLDER / f"{safe_name}_wordcloud.png"
        plt.savefig(cloud_path, dpi=150, bbox_inches="tight")
        plt.close()
        category_cloud_paths.append(cloud_path)

    print("Top categories from original data:")
    print(top_categories.head(5).to_string())
    print(f"Unique resumes used for word clouds: {len(clean_data)}")
    print("Saved figures:")
    for figure_path in [category_path, length_path, all_cloud_path] + category_cloud_paths:
        print(f"- {figure_path}")


if __name__ == "__main__":
    make_figures()
