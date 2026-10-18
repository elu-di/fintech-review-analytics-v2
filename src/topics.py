"""
topics.py -- Topic Modeling and Thematic Analysis Pipeline
Categorizes customer reviews across 5 core banking themes:
1. App Stability & Performance
2. Account Access & Authentication
3. Transfers & Financial Transactions
4. UI / UX & Usability
5. Customer Support & Branch Service
Plus "General Experience" for non-specific feedback.
Saves enriched results to data/processed/reviews_with_topics.csv
"""

import os
import re
import pandas as pd

# Thematic dictionary mapping each business topic to its regex patterns
TOPIC_PATTERNS = {
    "App Stability & Performance": [
        r"\bcrash\w*", r"\bslow\b", r"\bfreez\w*", r"\bbug\w*",
        r"\bload\w*", r"\berror\w*", r"\bwork\w*", r"\bfail\w*",
        r"\bupdate\w*", r"\bfix\b", r"\bnot working\b", r"\bstopped\b"
    ],
    "Account Access & Authentication": [
        r"\blogin\b", r"\bpassword\w*", r"\bpin\b", r"\botp\b",
        r"\bregist\w*", r"\bsign\s?up\b", r"\bphone\s?number\b",
        r"\bverif\w*", r"\baccount\b", r"\baccess\b", r"\bfingerprint\b"
    ],
    "Transfers & Financial Transactions": [
        r"\btransfer\w*", r"\bmoney\b", r"\bsend\w*", r"\btransact\w*",
        r"\bdeduct\w*", r"\bdebit\w*", r"\bpay\w*", r"\bbirr\b",
        r"\bbalance\b", r"\btelebirr\b", r"\bcbe\s?birr\b", r"\bcard\b", r"\bvisa\b"
    ],
    "UI / UX & Usability": [
        r"\beasy\b", r"\buser\s?friendly\b", r"\binterface\b", r"\bsimple\b",
        r"\bsmooth\b", r"\bdesign\b", r"\bconvenient\b", r"\bfeature\w*",
        r"\buseful\b", r"\bnavigation\b", r"\blayout\b"
    ],
    "Customer Support & Branch Service": [
        r"\bsupport\b", r"\bbranch\w*", r"\bcall\b", r"\bcustomer\s?care\b",
        r"\bhelp\b", r"\boperator\b", r"\bcontact\b", r"\bstaff\b",
        r"\bresponse\b", r"\bservice\s?center\b"
    ]
}


def classify_topic(text: str) -> str:
    """
    Score review against topic patterns and return the dominant topic.
    If no topic keywords match, return 'General Experience'.
    """
    if not isinstance(text, str) or not text.strip():
        return "General Experience"

    text_lower = text.lower()
    topic_scores = {}

    for topic, patterns in TOPIC_PATTERNS.items():
        score = 0
        for pattern in patterns:
            # Count how many keyword matches exist for this topic
            matches = len(re.findall(pattern, text_lower))
            score += matches
        topic_scores[topic] = score

    # Find the topic with the highest score
    best_topic = max(topic_scores, key=topic_scores.get)
    max_score = topic_scores[best_topic]

    # If no keywords matched at all, classify as General Experience
    if max_score == 0:
        return "General Experience"

    return best_topic


def run_topic_pipeline(
    input_path: str = "data/processed/reviews_with_sentiment.csv",
    output_path: str = "data/processed/reviews_with_topics.csv",
) -> pd.DataFrame:
    """Run topic classification and print thematic business breakdown."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Sentiment dataset not found at {input_path}")

    print(f"Loading sentiment reviews from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Total reviews to categorize: {len(df)}")

    # Step 1: Assign dominant topic
    print("\n[1/2] Categorizing reviews into banking themes...")
    df["topic"] = df["cleaned_review"].apply(classify_topic)

    # Step 2: Save enriched dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[2/2] Saved dataset with topics to: {output_path}")

    # Step 3: Analytical Insights for Omega Consultancy
    print("\n" + "=" * 55)
    print("             THEMATIC ANALYSIS REPORT")
    print("=" * 55)

    print("\n1. Distribution of Topics across All Reviews:")
    topic_counts = df["topic"].value_counts()
    for topic, count in topic_counts.items():
        pct = (count / len(df)) * 100
        print(f"  - {topic:<35} {count:>4} ({pct:.1f}%)")

    print("\n2. Dominant Topics by Bank:")
    by_bank = pd.crosstab(df["bank"], df["topic"], normalize="index").mul(100).round(1)
    print(by_bank.to_string())

    print("\n3. Negative Reviews by Topic (The Biggest Pain Points):")
    neg_reviews = df[df["sentiment_label"] == "Negative"]
    neg_by_topic = neg_reviews["topic"].value_counts()
    for topic, count in neg_by_topic.items():
        pct = (count / len(neg_reviews)) * 100
        print(f"  - {topic:<35} {count:>3} complaints ({pct:.1f}%)")

    return df


if __name__ == "__main__":
    df_topics = run_topic_pipeline()
