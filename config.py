import os

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:3b"

DATA_DIR = "data"
OUTPUT_DIR = "output"
DEFAULT_CSV = os.path.join(DATA_DIR, "sales_data.csv")

MAX_TOKENS = 800
TEMPERATURE = 0.3

REPORT_TITLE = "Sales Performance Report"
COMPANY_NAME = "Demo Company"