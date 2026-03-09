import requests
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def build_prompt(summary: dict) -> str:
    products = "\n".join([
        f"  - {name}: ${data['revenue']:,.0f} revenue, {data['units']:,.0f} units"
        for name, data in summary["product_breakdown"].items()
    ])
    
    regions = "\n".join([
        f"  - {name}: ${data['revenue']:,.0f} revenue, {data['units']:,.0f} units"
        for name, data in summary["regional_breakdown"].items()
    ])
    
    reps = "\n".join([
        f"  - {name}: ${data['revenue']:,.0f} revenue, {data['transactions']} transactions"
        for name, data in summary["rep_performance"].items()
    ])
    
    monthly = "\n".join([
        f"  - {month}: ${data['revenue']:,.0f} revenue"
        for month, data in summary["monthly_trend"].items()
    ])
    
    prompt = f"""You are a senior business analyst. Analyse the following sales data and write a concise executive summary.

SALES DATA SUMMARY
Period: {summary['date_range']}
Total Revenue: ${summary['total_revenue']:,.2f}
Total Cost: ${summary['total_cost']:,.2f}
Total Profit: ${summary['total_profit']:,.2f}
Profit Margin: {summary['profit_margin_pct']}%
Units Sold: {summary['total_units_sold']}
Return Rate: {summary['return_rate_pct']}%

PRODUCT PERFORMANCE:
{products}

REGIONAL PERFORMANCE:
{regions}

SALES REP PERFORMANCE:
{reps}

MONTHLY TREND:
{monthly}

Write a structured analysis with these FOUR sections. Use plain text — no markdown, no bullet points, no asterisks.

EXECUTIVE SUMMARY
Write 2-3 sentences summarising overall business performance.

KEY FINDINGS
Write 3-4 sentences highlighting the most important insights from product, regional, and rep performance data.

TRENDS AND PATTERNS
Write 2-3 sentences describing any notable trends in the monthly data and what they might indicate.

RECOMMENDATIONS
Write 3 specific, actionable recommendations based on the data. Number them 1, 2, 3.

Keep the entire response under 400 words. Be specific — use the actual numbers from the data."""
    
    return prompt


def call_ollama(prompt: str) -> str:
    url = f"{config.OLLAMA_BASE_URL}/api/generate"
    
    payload = {
        "model": config.MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": config.TEMPERATURE,
            "num_predict": config.MAX_TOKENS,
        }
    }
    
    try:
        print(f"  Calling {config.MODEL_NAME} via Ollama...")
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result["response"].strip()
    
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. Is it running?\n"
            "Start it with: ollama serve\n"
            "Then verify with: ollama list"
        )
    
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise RuntimeError(
                f"Model '{config.MODEL_NAME}' not found.\n"
                f"Pull it with: ollama pull {config.MODEL_NAME}"
            )
        raise RuntimeError(f"Ollama API error: {e}")
    
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Ollama timed out after 120 seconds.\n"
            "Try a smaller model (llama3.2:1b) or reduce MAX_TOKENS in config.py"
        )


def generate_insights(summary: dict) -> str:
    prompt = build_prompt(summary)
    return call_ollama(prompt)


def parse_sections(raw_text: str) -> dict:
    sections = {
        "executive_summary": "",
        "key_findings": "",
        "trends_and_patterns": "",
        "recommendations": "",
    }
    
    section_markers = {
        "EXECUTIVE SUMMARY": "executive_summary",
        "KEY FINDINGS": "key_findings",
        "TRENDS AND PATTERNS": "trends_and_patterns",
        "RECOMMENDATIONS": "recommendations",
    }
    
    current_section = None
    lines = raw_text.split("\n")
    
    for line in lines:
        line_upper = line.strip().upper()
        
        matched = False
        for marker, key in section_markers.items():
            if marker in line_upper:
                current_section = key
                matched = True
                break
        
        if not matched and current_section and line.strip():
            sections[current_section] += line.strip() + " "
    
    for key in sections:
        sections[key] = sections[key].strip()
    
    if not any(sections.values()):
        sections["executive_summary"] = raw_text.strip()
    
    return sections