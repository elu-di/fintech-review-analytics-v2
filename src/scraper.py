"""
scraper.py -- Google Play Store Review Scraper
Fetches reviews for CBE, BOA, and Dashen Bank apps.
Outputs columns: review | rating | date | bank | source
Saves raw dataset to data/raw/reviews_raw.csv
"""

import os
import pandas as pd
from google_play_scraper import reviews, Sort
from datetime import datetime

# BANK_APPS maps each bank label to its verified Play Store app ID(s).
BANK_APPS = {
    "Commercial Bank of Ethiopia": ["prod.cbe.birr"],
    "Bank of Abyssinia":           ["com.boa.boaMobileBanking", "com.boa.apollo"],
    "Dashen Bank":                 ["com.dashen.dashensuperapp"],
}


def scrape_reviews(app_id: str, bank_name: str, count: int = 500) -> pd.DataFrame:
    """Fetch up to count reviews for a single app."""
    print(f"  Scraping: {bank_name} | {app_id} | requesting {count} reviews...")
    try:
        result, _ = reviews(
            app_id,
            lang="en",
            country="us",
            sort=Sort.NEWEST,
            count=count,
        )
    except Exception as e:
        print(f"  WARNING: Failed to scrape {app_id} -- {e}")
        return pd.DataFrame()

    if not result:
        print(f"  WARNING: 0 reviews returned for {app_id}")
        return pd.DataFrame()

    rows = []
    for r in result:
        review_date = r["at"].strftime("%Y-%m-%d") if isinstance(r["at"], datetime) else str(r["at"])
        rows.append({
            "review": r["content"],
            "rating": r["score"],
            "date":   review_date,
            "bank":   bank_name,
            "source": "Google Play",
        })

    df = pd.DataFrame(rows)
    print(f"  Done: {len(df)} reviews for {bank_name} ({app_id})")
    return df


def scrape_all_banks(count_per_app: int = 500) -> pd.DataFrame:
    """Scrape all banks and return one combined DataFrame."""
    all_frames = []
    for bank_name, app_ids in BANK_APPS.items():
        print(f"\n[{bank_name}]")
        for app_id in app_ids:
            df = scrape_reviews(app_id, bank_name, count=count_per_app)
            if not df.empty:
                all_frames.append(df)

    if not all_frames:
        raise RuntimeError("No reviews collected! Check app IDs and internet connection.")

    combined = pd.concat(all_frames, ignore_index=True)
    print(f"\nTotal reviews collected: {len(combined)}")
    return combined


def save_raw_reviews(df: pd.DataFrame, output_path: str = "data/raw/reviews_raw.csv") -> str:
    """Save the scraped reviews to CSV in data/raw/."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Saved {len(df)} raw reviews to {output_path}")
    return output_path


if __name__ == "__main__":
    df = scrape_all_banks(count_per_app=500)
    print("\nSample scraped data:")
    print(df.head(3))
    print("\nReview distribution by bank:")
    print(df["bank"].value_counts())
    
    save_raw_reviews(df)
