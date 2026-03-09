import pandas as pd
from datetime import datetime


def load_and_summarise(filepath: str) -> dict:
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    
    total_revenue = df["revenue"].sum()
    total_cost = df["cost"].sum()
    total_profit = total_revenue - total_cost
    profit_margin = (total_profit / total_revenue) * 100
    total_units = df["units_sold"].sum()
    total_returns = df["returns"].sum()
    return_rate = (total_returns / total_units) * 100
    date_range = f"{df['date'].min().strftime('%d %b %Y')} to {df['date'].max().strftime('%d %b %Y')}"
    
    product_summary = (
        df.groupby("product")
          .agg(
              revenue=("revenue", "sum"),
              units=("units_sold", "sum"),
              avg_order_value=("revenue", "mean"),
          )
          .round(2)
          .to_dict(orient="index")
    )
    
    region_summary = (
        df.groupby("region")
          .agg(
              revenue=("revenue", "sum"),
              units=("units_sold", "sum"),
          )
          .round(2)
          .to_dict(orient="index")
    )
    
    rep_summary = (
        df.groupby("salesperson")
          .agg(
              revenue=("revenue", "sum"),
              units=("units_sold", "sum"),
              transactions=("revenue", "count"),
          )
          .round(2)
          .to_dict(orient="index")
    )
    
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly_trend = (
        df.groupby("month")
          .agg(revenue=("revenue", "sum"), units=("units_sold", "sum"))
          .round(2)
          .to_dict(orient="index")
    )
    
    best_product = max(product_summary, key=lambda k: product_summary[k]["revenue"])
    worst_product = min(product_summary, key=lambda k: product_summary[k]["revenue"])
    best_region = max(region_summary, key=lambda k: region_summary[k]["revenue"])
    best_rep = max(rep_summary, key=lambda k: rep_summary[k]["revenue"])
    
    return {
        "date_range": date_range,
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "total_profit": round(total_profit, 2),
        "profit_margin_pct": round(profit_margin, 1),
        "total_units_sold": int(total_units),
        "return_rate_pct": round(return_rate, 1),
        "product_breakdown": product_summary,
        "regional_breakdown": region_summary,
        "rep_performance": rep_summary,
        "monthly_trend": monthly_trend,
        "highlights": {
            "best_product": best_product,
            "worst_product": worst_product,
            "best_region": best_region,
            "top_rep": best_rep,
        },
        "raw_df": df,
    }