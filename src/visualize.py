"""
visualize.py -- Visual Analytics & Executive Presentation Pipeline
Generates presentation-grade figures for Omega Consultancy's banking report:
1. Sentiment distribution across CBE, BoA, and Dashen Bank
2. Rating vs. Sentiment alignment heatmap
3. Thematic complaint drivers (negative reviews by topic per bank)
4. Executive benchmark scorecard (Average Star Rating vs. Mean Sentiment Score)
Saves all charts into reports/figures/
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set global visual style
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]


def ensure_dir(path: str):
    """Ensure destination directory exists."""
    os.makedirs(path, exist_ok=True)


def plot_sentiment_by_bank(df: pd.DataFrame, output_dir: str):
    """Figure 1: Stacked bar chart of sentiment breakdown by bank."""
    crosstab = pd.crosstab(df["bank"], df["sentiment_label"], normalize="index")[
        ["Positive", "Neutral", "Negative"]
    ] * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2ecc71", "#f39c12", "#e74c3c"]  # Green, Amber, Red

    crosstab.plot(kind="barh", stacked=True, color=colors, ax=ax, edgecolor="none", alpha=0.9)

    ax.set_title("Customer Sentiment Distribution by Bank", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlabel("Percentage of Reviews (%)", fontsize=12)
    ax.set_ylabel("")
    ax.set_xlim(0, 100)
    ax.legend(title="Sentiment", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)

    # Annotate percentage numbers inside bars
    for n, c in enumerate(crosstab.index):
        cum_val = 0
        for col_idx, col in enumerate(crosstab.columns):
            val = crosstab.loc[c, col]
            if val > 6:
                ax.text(
                    cum_val + val / 2,
                    n,
                    f"{val:.1f}%",
                    va="center",
                    ha="center",
                    color="white",
                    fontweight="bold",
                    fontsize=10,
                )
            cum_val += val

    plt.tight_layout()
    path = os.path.join(output_dir, "01_sentiment_by_bank.png")
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"Saved: {path}")


def plot_rating_vs_sentiment(df: pd.DataFrame, output_dir: str):
    """Figure 2: Heatmap of Star Ratings vs. NLP Sentiment Label."""
    matrix = pd.crosstab(df["rating"], df["sentiment_label"])[["Positive", "Neutral", "Negative"]]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=True,
        linewidths=1,
        linecolor="#f0f0f0",
        ax=ax,
    )

    ax.set_title("Rating vs. Sentiment Alignment Heatmap", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("VADER Sentiment Label", fontsize=12, fontweight="bold")
    ax.set_ylabel("Google Play Star Rating", fontsize=12, fontweight="bold")

    plt.tight_layout()
    path = os.path.join(output_dir, "02_rating_vs_sentiment_alignment.png")
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"Saved: {path}")


def plot_complaints_by_topic(df: pd.DataFrame, output_dir: str):
    """Figure 3: Breakdown of negative complaint topics per bank."""
    neg_df = df[df["sentiment_label"] == "Negative"]
    topic_bank = pd.crosstab(neg_df["topic"], neg_df["bank"])

    fig, ax = plt.subplots(figsize=(11, 6))
    palette = ["#3498db", "#9b59b6", "#e67e22"]

    topic_bank.plot(kind="bar", ax=ax, color=palette, width=0.8, edgecolor="none", alpha=0.9)

    ax.set_title("Customer Pain Points & Complaints by Topic", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Thematic Topic", fontsize=12, fontweight="bold")
    ax.set_ylabel("Number of Negative Reviews", fontsize=12)
    ax.legend(title="Bank", loc="upper right", frameon=True)
    plt.xticks(rotation=20, ha="right")

    plt.tight_layout()
    path = os.path.join(output_dir, "03_complaints_by_topic.png")
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"Saved: {path}")


def plot_executive_scorecard(df: pd.DataFrame, output_dir: str):
    """Figure 4: Executive comparative benchmark (Star Rating & Sentiment Score)."""
    summary = df.groupby("bank").agg(
        avg_rating=("rating", "mean"),
        avg_sentiment=("sentiment_score", "mean")
    ).reset_index()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Star Rating Bar Chart
    colors_rating = ["#2980b9", "#27ae60", "#f39c12"]
    bars1 = ax1.bar(summary["bank"], summary["avg_rating"], color=colors_rating, alpha=0.85)
    ax1.set_title("Average Star Rating (1 to 5)", fontsize=13, fontweight="bold")
    ax1.set_ylim(0, 5)
    ax1.set_ylabel("Stars")
    ax1.set_xticklabels(summary["bank"], rotation=15, ha="right")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, f"{yval:.2f} ⭐", ha="center", va="bottom", fontweight="bold")

    # NLP Sentiment Bar Chart
    colors_sentiment = ["#16a085", "#2ecc71", "#e67e22"]
    bars2 = ax2.bar(summary["bank"], summary["avg_sentiment"], color=colors_sentiment, alpha=0.85)
    ax2.set_title("Average NLP Sentiment Score (-1 to +1)", fontsize=13, fontweight="bold")
    ax2.set_ylim(-0.1, 0.4)
    ax2.set_ylabel("Compound Score")
    ax2.set_xticklabels(summary["bank"], rotation=15, ha="right")
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"+{yval:.3f}", ha="center", va="bottom", fontweight="bold")

    plt.suptitle("Executive Fintech Benchmark: Ethiopian Mobile Banking", fontsize=16, fontweight="bold", y=1.03)
    plt.tight_layout()
    path = os.path.join(output_dir, "04_executive_benchmark_scorecard.png")
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def run_visualization_pipeline(
    input_path: str = "data/processed/reviews_with_topics.csv",
    output_dir: str = "reports/figures"
):
    """Run full visualization pipeline and export all charts."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input dataset not found at: {input_path}")

    ensure_dir(output_dir)
    print(f"Loading data from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Generating executive visualizations for {len(df)} reviews...")

    plot_sentiment_by_bank(df, output_dir)
    plot_rating_vs_sentiment(df, output_dir)
    plot_complaints_by_topic(df, output_dir)
    plot_executive_scorecard(df, output_dir)

    print(f"\nAll 4 executive figures saved to: {output_dir}/")


if __name__ == "__main__":
    run_visualization_pipeline()
