# LLM-Powered Report Generator

An automated reporting pipeline that reads CSV data, analyses it using a **local LLM** (no cloud APIs, no cost, no data leaves your machine), and generates a formatted multi-page PDF report.

Built as a portfolio project to demonstrate LLM integration, data pipeline design, and automated document generation.

---

## What It Does

- Reads sales/business CSV data
- Summarises it using Pandas
- Sends structured prompts to a locally-hosted LLM via Ollama
- Parses the LLM response into labelled sections
- Generates a formatted PDF with KPI cards, charts, and written analysis

## Architecture
```
CSV → Pandas (summarise) → Ollama/LLaMA (analyse) → ReportLab (PDF)
```

## Why Local LLM?

- No API costs
- No data privacy concerns — everything stays on your machine
- Demonstrates understanding of on-premise AI deployment
- Works offline

## Tech Stack

- **Python** — Pandas, ReportLab, Matplotlib, Requests
- **Ollama** — local LLM inference server
- **LLaMA 3.2 3B** — open-source language model

## Project Structure
```
llm-report-generator/
├── data/
│   └── sales_data.csv
├── output/
│   └── sample_report.pdf
├── src/
│   ├── data_loader.py      # CSV ingestion + Pandas summarisation
│   ├── llm_analyst.py      # Ollama API + prompt engineering
│   ├── chart_builder.py    # Matplotlib chart generation
│   └── report_builder.py   # ReportLab PDF assembly
├── main.py                 # Orchestrator
├── config.py               # Settings (model, paths, temperature)
└── requirements.txt
```

## Quick Start

### 1. Install Ollama and pull a model
```bash
# Install from https://ollama.com
ollama pull llama3.2:3b
```

### 2. Clone and set up Python environment
```bash
git clone https://github.com/YOUR_USERNAME/llm-report-generator.git
cd llm-report-generator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run
```bash
# Make sure Ollama is running
ollama serve

# Generate report
python main.py
```

Report is saved to `output/` with a timestamp.

## Sample Output

See [`output/sample_report.pdf`](output/sample_report.pdf) for an example generated report.

## Planned Improvements

- [ ] Test with real-world datasets (Kaggle)
- [ ] Prompt refinement for more accurate analysis
- [ ] Richer data visualisations
- [ ] CLI arguments for model selection and input file
- [ ] Support for different report types (weekly summary, anomaly detection)

---

*v1.0 — initial working prototype*