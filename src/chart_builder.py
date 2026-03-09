import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import os


def _save_chart(fig, filename, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return filepath


def revenue_by_product_chart(df, output_dir):
    product_rev = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.bar(product_rev.index, product_rev.values, color=["#2563eb", "#7c3aed", "#db2777"])
    ax.set_title("Revenue by Product", fontsize=12, fontweight="bold")
    ax.set_ylabel("Revenue ($)")
    ax.set_xlabel("Product")
    for bar, val in zip(bars, product_rev.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f"${val:,.0f}", ha="center", va="bottom", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save_chart(fig, "chart_product_revenue.png", output_dir)


def monthly_trend_chart(df, output_dir):
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["revenue"].sum()
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(monthly.index, monthly.values, marker="o", color="#2563eb", linewidth=2)
    ax.fill_between(monthly.index, monthly.values, alpha=0.1, color="#2563eb")
    ax.set_title("Monthly Revenue Trend", fontsize=12, fontweight="bold")
    ax.set_ylabel("Revenue ($)")
    ax.set_xlabel("Month")
    for i, (month, val) in enumerate(monthly.items()):
        ax.annotate(f"${val:,.0f}", (month, val),
                    textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save_chart(fig, "chart_monthly_trend.png", output_dir)


def revenue_by_region_chart(df, output_dir):
    region_rev = df.groupby("region")["revenue"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(6, 3))
    colors = ["#f59e0b", "#10b981", "#3b82f6", "#8b5cf6"]
    bars = ax.barh(region_rev.index, region_rev.values, color=colors[:len(region_rev)])
    ax.set_title("Revenue by Region", fontsize=12, fontweight="bold")
    ax.set_xlabel("Revenue ($)")
    for bar, val in zip(bars, region_rev.values):
        ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
                f"${val:,.0f}", va="center", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save_chart(fig, "chart_region_revenue.png", output_dir)