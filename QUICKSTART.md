# Quick Start Guide

Get up and running with Legal Crawl Analysis in 5 minutes.

## Prerequisites

- Python 3.11+
- Poetry installed
- OpenAI API key

## Setup

1. **Install dependencies**:
```bash
poetry install
```

2. **Set your OpenAI API key**:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

3. **Set up directories**:
```bash
poetry run setup-environment
```

## Run Analysis

### Option 1: Command Line (Recommended)
```bash
# Run complete analysis
poetry run legal-crawl-analyzer

# Or run phases separately
poetry run legal-crawl-analyzer --phase 1  # Fast detection only
poetry run legal-crawl-analyzer --phase 2  # GPT analysis only
```

### Option 2: Simple Example Script
```bash
poetry run python example_simple.py
```

### Option 3: Python API
```python
from legal_crawl_analysis import LegalCrawlAnalyzer
import os

analyzer = LegalCrawlAnalyzer(os.getenv('OPENAI_API_KEY'))
phase_one = analyzer.run_phase_one()
phase_two = analyzer.run_phase_two()
analyzer.generate_final_report()
```

## What You'll Get

After running the analysis, check the output directory for:

- 📊 **Statistics**: JSON files with detailed metrics
- 📄 **Report**: `final_report.md` with comprehensive analysis
- 📝 **Data**: Extracted legal documents and classifications
- 📋 **Logs**: Detailed processing logs

## Next Steps

- Adjust configuration in `legal_crawl_analysis/config.py`
- Scale up by increasing `MAX_WARC_FILES`
- Customize GPT prompts for your specific use case
- Export results to CSV/Excel for further analysis

## Need Help?

- Check the full README.md for detailed documentation
- Review logs in `legal_crawl_analysis.log`
- Open an issue on GitHub for support 