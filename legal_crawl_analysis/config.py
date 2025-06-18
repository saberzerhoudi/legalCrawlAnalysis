"""
Configuration settings for Legal Crawl Analyzer
"""

import os
from pathlib import Path

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Directory Configuration
BASE_DIR = Path(__file__).parent.parent
WARC_DIR = BASE_DIR / "warc_files"
OUTPUT_DIR = BASE_DIR / "analysis_output"
LOGS_DIR = BASE_DIR / "logs"

# CommonCrawl Configuration
MAX_WARC_FILES = 5  # Limit for small dump analysis
MAX_RECORDS_PER_WARC = 10000  # Limit records per WARC for testing

# GPT Configuration
GPT_MODEL = "gpt-4o"
MAX_TOKENS_PER_ANALYSIS = 2000
GPT_TEMPERATURE = 0.1

# Legal Document Detection Configuration
MIN_CONFIDENCE_THRESHOLD = 0.4
MIN_CONTENT_LENGTH = 500
MAX_CONTENT_LENGTH_FOR_ANALYSIS = 50000

# Analysis Configuration
ENABLE_DETAILED_LOGGING = True
SAVE_HTML_CONTENT = False  # Set to True if you need to save HTML for debugging

# Rate Limiting
REQUESTS_PER_SECOND = 2  # For CommonCrawl downloads
GPT_REQUESTS_PER_MINUTE = 10  # For OpenAI API calls 