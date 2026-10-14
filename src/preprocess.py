"""
preprocess.py -- Data Cleaning and Preprocessing Pipeline
Cleans raw Play Store reviews for CBE, Bank of Abyssinia, and Dashen Bank.
- Drops null and empty reviews
- Deduplicates rows
- Standardizes dates to YYYY-MM-DD
- Normalizes review text (cleaning URLs, strange punctuation, extra spaces)
- Saves output to data/processed/reviews_cleaned.csv
"""

import os
import re
import pandas as pd


def clean_text(text: str) -> str:
    """Normalize and clean a single review string."""
    if not isinstance(text, str):
        return ""
    # Remove URLs if any
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    # Replace multiple newlines or spaces with a single space
    text = re.sub(r"\s+", " ", text)
    # Strip leading and trailing whitespace
    return text.strip()


def preprocess_reviews(
    input_path: str = "data/raw/reviews_raw.csv",
    output_path: str = "data/processed/reviews_cleaned.csv",
) -> pd.DataFrame:
    """End-to-end preprocessing pipeline for scraped reviews."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    print(f"Loading raw reviews from: {input_path}")
    df = pd.read_csv(input_path)
    initial_count = len(df)
    print(f"Initial raw rows: {initial_count}")

    # 1. Handle missing / null review text or ratings
    df = df.dropna(subset=["review", "rating"]).copy()
    print(f"Rows after dropping nulls in review/rating: {len(df)} (dropped {initial_count - len(df)})")

    # 2. Clean the review text and filter out reviews that become empty
    df["cleaned_review"] = df["review"].astype(str).apply(clean_text)
    # Keep only reviews with at least 2 characters of actual content
    df = df[df["cleaned_review"].str.len() >= 2].copy()
    print(f"Rows after removing empty/too-short reviews: {len(df)}")

    # 3. Remove duplicates (same bank and review text)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["bank", "cleaned_review"]).copy()
    print(f"Rows after deduplication: {len(df)} (dropped {before_dedup - len(df)} duplicates)")

    # 4. Standardize date format to YYYY-MM-DD
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # 5. Ensure rating is an integer between 1 and 5
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").astype(int)
    df = df[df["rating"].between(1, 5)].copy()

    # 6. Save processed dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nCleaned dataset saved successfully to: {output_path}")
    print(f"Final clean review count: {len(df)}")
    
    print("\nCleaned review breakdown by bank:")
    print(df["bank"].value_counts())
    
    print("\nRating distribution across all banks:")
    print(df["rating"].value_counts().sort_index())

    return df


if __name__ == "__main__":
    df_clean = preprocess_reviews()
    print("\nSample cleaned records:")
    print(df_clean[["bank", "rating", "date", "cleaned_review"]].head(3))
