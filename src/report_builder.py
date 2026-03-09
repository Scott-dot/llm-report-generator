from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, HRFlowable
)
from datetime import datetime
import os

BLUE = HexColor("#2563eb")
DARK = HexColor("#1e293b")
GREY = HexColor("#64748b")
LIGHT_BG = HexColor("#f1f5f9")
WHITE = HexColor("#ffffff")


def build_styles():
    return {
        "title": ParagraphStyle("ReportTitle", fontSize=24, fontName="Helvetica-Bold", textColor=DARK, spaceAfter=6, leading=28),
        "subtitle": ParagraphStyle("ReportSubtitle", fontSize=12, fontName="Helvetica", textColor=GREY, spaceAfter=20),
        "section_header": ParagraphStyle("SectionHeader", fontSize=14, fontName="Helvetica-Bold", textColor=BLUE, spaceBefore=18, spaceAfter=8),
        "body": ParagraphStyle("BodyText", fontSize=10, fontName="Helvetica", textColor=DARK, leading=16, spaceAfter=10),
        "caption": ParagraphStyle("Caption", fontSize=8, fontName="Helvetica", textColor=GREY, alignment=1, spaceAfter=6),
        "metric_label": ParagraphStyle("MetricLabel", fontSize=9, fontName="Helvetica", textColor=GREY, alignment=1),
        "metric_value": ParagraphStyle("MetricValue", fontSize=18, fontName="Helvetica-Bold", textColor=DARK, alignment=1),
    }


def kpi_card_table(summary, styles):
    kpi_data = [
        [
            Paragraph("Total Revenue", styles["metric_label"]),
            Paragraph("Net Profit", styles["metric_label"]),
            Paragraph("Margin", styles["metric_label"]),
            Paragraph("Units Sold", styles["metric_label"]),
        ],
        [
            Paragraph(f"${summary['total_revenue']:,.0f}", styles["metric_value"]),
            Paragraph(f"${summary['total_profit']:,.0f}", styles["metric_value"]),
            Paragraph(f"{summary['profit_margin_pct']}%", styles["metric_value"]),
            Paragraph(str(summary["total_units_sold"]), styles["metric_value"]),
        ]
    ]
    t = Table(kpi_data, colWidths=[4.25*cm, 4.25*cm, 4.25*cm, 4.25*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, GREY),
        ("LINEBEFORE", (1, 0), (-1, -1), 0.5, GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def performance_table(data, columns, styles):
    header = [Paragraph(col, ParagraphStyle("TH", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=1)) for col in columns[0]]
    rows = [header]
    for name, vals in data.items():
        row = [Paragraph(str(name), ParagraphStyle("TD", fontSize=9, fontName="Helvetica", textColor=DARK))]
        for v in vals:
            row.append(Paragraph(str(v), ParagraphStyle("TDR", fontSize=9, fontName="Helvetica", textColor=DARK, alignment=1)))
        rows.append(row)
    col_w = [17.5 / len(columns[0]) * cm] * len(columns[0])
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("BOX", (0, 0), (-1, -1), 0.5, GREY),
        ("GRID", (0, 0), (-1, -1), 0.25, GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def build_pdf(summary, sections, chart_paths, output_path):
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = build_styles()
    story = []

    story.append(Paragraph("Sales Performance Report", styles["title"]))
    story.append(Paragraph(f"Period: {summary['date_range']}  |  Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=16))

    story.append(Paragraph("Key Metrics", styles["section_header"]))
    story.append(kpi_card_table(summary, styles))
    story.append(Spacer(1, 0.4*cm))

    if sections.get("executive_summary"):
        story.append(Paragraph("Executive Summary", styles["section_header"]))
        story.append(Paragraph(sections["executive_summary"], styles["body"]))

    story.append(Paragraph("Performance Charts", styles["section_header"]))

    chart_items = []
    if "product" in chart_paths:
        chart_items.append([Image(chart_paths["product"], width=8.5*cm, height=5*cm)])
    if "region" in chart_paths:
        if len(chart_items) > 0:
            chart_items[0].append(Image(chart_paths["region"], width=8.5*cm, height=5*cm))
        else:
            chart_items.append([Image(chart_paths["region"], width=8.5*cm, height=5*cm)])

    if chart_items:
        if len(chart_items[0]) == 2:
            chart_table = Table([chart_items[0]], colWidths=[9*cm, 9*cm])
            chart_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
            story.append(chart_table)
        else:
            story.append(chart_items[0][0])

    if "monthly" in chart_paths:
        story.append(Spacer(1, 0.3*cm))
        story.append(Image(chart_paths["monthly"], width=17.5*cm, height=5*cm))
        story.append(Paragraph("Fig 3: Monthly Revenue Trend", styles["caption"]))

    story.append(PageBreak())
    story.append(Paragraph("Detailed Analysis", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BG, spaceAfter=10))

    for section_key, section_title in [
        ("key_findings", "Key Findings"),
        ("trends_and_patterns", "Trends and Patterns"),
        ("recommendations", "Recommendations"),
    ]:
        if sections.get(section_key):
            story.append(Paragraph(section_title, styles["section_header"]))
            story.append(Paragraph(sections[section_key], styles["body"]))

    story.append(Paragraph("Product Performance Breakdown", styles["section_header"]))
    product_table_data = {
        name: [f"${data['revenue']:,.0f}", f"{data['units']:,.0f}", f"${data['avg_order_value']:,.0f}"]
        for name, data in summary["product_breakdown"].items()
    }
    story.append(performance_table(product_table_data, [["Product", "Revenue", "Units Sold", "Avg Order Value"]], styles))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Regional Performance Breakdown", styles["section_header"]))
    region_table_data = {
        name: [f"${data['revenue']:,.0f}", f"{data['units']:,.0f}"]
        for name, data in summary["regional_breakdown"].items()
    }
    story.append(performance_table(region_table_data, [["Region", "Revenue", "Units Sold"]], styles))
    story.append(Spacer(1, 0.4*cm))

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREY, spaceAfter=6))
    story.append(Paragraph(
        "This report was generated automatically. Analysis was produced by a local language model and should be reviewed by a human analyst before distribution.",
        ParagraphStyle("Footer", fontSize=8, fontName="Helvetica", textColor=GREY, alignment=1)
    ))

    doc.build(story)
    print(f"  PDF saved: {output_path}")