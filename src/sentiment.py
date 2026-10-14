"""
sentiment.py -- Sentiment Analysis & Rating Alignment Pipeline
Uses NLTK VADER to score customer reviews for Ethiopian banking apps.
Compares star ratings (1-5) against text sentiment to detect discrepancies.
Saves enriched results to data/processed/reviews_with_sentiment.csv
"""

import os
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure VADER lexicon is downloaded
nltk.download("vader_lexicon", quiet=True)


def get_vader_sentiment(text: str, sia: SentimentIntensityAnalyzer) -> tuple:
    """
    Compute VADER compound sentiment score and assign category.
    Returns: (compound_score, sentiment_label)
    """
    if not isinstance(text, str) or not text.strip():
        return 0.0, "Neutral"

    scores = sia.polarity_scores(text)
    compound = round(scores["compound"], 4)

    # Standard VADER classification thresholds
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return compound, label


def check_alignment(rating: int, sentiment_label: str) -> tuple:
    """
    Compare star rating against text sentiment.
    Returns: (is_aligned: bool, discrepancy_reason: str)
    """
    # Expected mappings:
    # 4-5 stars -> Positive
    # 3 stars   -> Neutral
    # 1-2 stars -> Negative

    if rating in [4, 5] and sentiment_label == "Positive":
        return True, "Aligned"
    elif rating == 3 and sentiment_label == "Neutral":
        return True, "Aligned"
    elif rating in [1, 2] and sentiment_label == "Negative":
        return True, "Aligned"

    # Discrepancies:
    if rating in [4, 5] and sentiment_label == "Negative":
        return False, "High Rating / Negative Sentiment"
    elif rating in [1, 2] and sentiment_label == "Positive":
        return False, "Low Rating / Positive Sentiment"
    else:
        return False, f"{rating}-Star / {sentiment_label}"


def run_sentiment_pipeline(
    input_path: str = "data/processed/reviews_cleaned.csv",
    output_path: str = "data/processed/reviews_with_sentiment.csv",
) -> pd.DataFrame:
    """Run end-to-end sentiment analysis and rating alignment."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at {input_path}")

    print(f"Loading cleaned reviews from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Total reviews to analyze: {len(df)}")

    # Initialize VADER analyzer
    sia = SentimentIntensityAnalyzer()

    # Step 1: Compute Sentiment Score and Label
    print("\n[1/3] Computing VADER sentiment scores...")
    sentiments = df["cleaned_review"].apply(lambda t: get_vader_sentiment(t, sia))
    df["sentiment_score"] = sentiments.apply(lambda x: x[0])
    df["sentiment_label"] = sentiments.apply(lambda x: x[1])

    # Step 2: Compute Rating Alignment
    print("[2/3] Analyzing rating vs. sentiment alignment...")
    alignments = df.apply(lambda row: check_alignment(row["rating"], row["sentiment_label"]), axis=1)
    df["is_aligned"] = alignments.apply(lambda x: x[0])
    df["alignment_status"] = alignments.apply(lambda x: x[1])

    # Step 3: Save Enriched Dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[3/3] Enriched dataset saved to: {output_path}")

    # Summary Analytics for Omega Consultancy
    print("\n" + "=" * 50)
    print("           SENTIMENT ANALYSIS REPORT")
    print("=" * 50)

    print("\n1. Overall Sentiment Breakdown:")
    print(df["sentiment_label"].value_counts(normalize=True).mul(100).round(1).astype(str) + "%")

    print("\n2. Average Sentiment Score by Bank:")
    avg_by_bank = df.groupby("bank")["sentiment_score"].mean().round(3)
    print(avg_by_bank)

    print("\n3. Rating Alignment Summary:")
    alignment_counts = df["alignment_status"].value_counts()
    print(alignment_counts)
    aligned_pct = (df["is_aligned"].mean() * 100).round(1)
    print(f"Overall Alignment Rate: {aligned_pct}%")

    print("\n4. Sample Discrepancies (High Rating but Negative Text):")
    sample_discrepancies = df[df["alignment_status"] == "High Rating / Negative Sentiment"]
    for idx, row in sample_discrepancies.head(3).iterrows():
        print(f"  - [{row['bank']}] ⭐ {row['rating']} stars | Score: {row['sentiment_score']}")
        print(f"    Text: \"{row['cleaned_review']}\"")

    return df


if __name__ == "__main__":
    df_results = run_sentiment_pipeline()
