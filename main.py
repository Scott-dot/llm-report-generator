import os
import sys
import time
from datetime import datetime

import config
from src.data_loader import load_and_summarise
from src.llm_analyst import generate_insights, parse_sections
from src.chart_builder import revenue_by_product_chart, monthly_trend_chart, revenue_by_region_chart
from src.report_builder import build_pdf


def main(csv_path: str = None):
    csv_path = csv_path or config.DEFAULT_CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(config.OUTPUT_DIR, f"sales_report_{timestamp}.pdf")
    chart_dir = os.path.join(config.OUTPUT_DIR, "charts")
    
    print("\n=== LLM Report Generator ===\n")
    
    print("[1/4] Loading and summarising data...")
    summary = load_and_summarise(csv_path)
    df = summary.pop("raw_df")
    print(f"  Loaded {len(df)} rows | {summary['date_range']}")
    print(f"  Revenue: ${summary['total_revenue']:,.0f} | Margin: {summary['profit_margin_pct']}%")
    
    print("\n[2/4] Generating LLM insights (this takes 15-60 seconds)...")
    start = time.time()
    raw_insights = generate_insights(summary)
    elapsed = time.time() - start
    print(f"  Done in {elapsed:.1f}s ({len(raw_insights)} chars generated)")
    
    sections = parse_sections(raw_insights)
    print(f"  Parsed sections: {[k for k, v in sections.items() if v]}")
    
    print("\n[3/4] Generating charts...")
    chart_paths = {
        "product": revenue_by_product_chart(df, chart_dir),
        "monthly": monthly_trend_chart(df, chart_dir),
        "region": revenue_by_region_chart(df, chart_dir),
    }
    print(f"  Generated {len(chart_paths)} charts")
    
    print("\n[4/4] Building PDF report...")
    build_pdf(summary, sections, chart_paths, output_path)
    
    print(f"\n✓ Report complete: {output_path}\n")
    return output_path


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else None
    main(csv_file)