# Legal Crawl Analysis

A Python package for analyzing legal documents in CommonCrawl data using a sophisticated 3-phase pipeline: lightning-fast detection, sophisticated filtering, and detailed GPT-4o analysis.


## Overview

**Legal Crawl Analysis** is a library designed for large-scale analysis of legal documents found in CommonCrawl web archives. The system processes web records to identify, extract, and analyze legal content including privacy policies, terms of service, copyright notices, and other legal documents.


## Architecture

### System Components

The system is built using a modular architecture with clear separation of concerns:

```
legal_crawl_analysis/
├── analyzer.py          # Main orchestration and pipeline management
├── fetcher.py           # CommonCrawl WARC file downloading and management
├── detector.py          # Legal document detection (Phases 1 & 2)
├── extractor.py         # HTML content extraction and cleaning
├── gpt_analyzer.py      # GPT-4o integration for detailed analysis
├── models.py            # Data structures and type definitions
├── config.py            # Configuration management
├── main.py              # Command-line interface
└── setup.py             # Environment setup utilities
```

### Core Classes

#### `LegalCrawlAnalyzer`
The main orchestrator that coordinates the entire analysis pipeline.
- Manages 3-phase processing workflow
- Handles progress tracking and resume functionality
- Coordinates between different components
- Generates comprehensive reports

#### `CommonCrawlFetcher`
Handles downloading and managing CommonCrawl WARC files.
- Downloads WARC files from CommonCrawl S3 buckets
- Manages local WARC file storage
- Provides streaming access to WARC records
- Handles network errors and retries

#### `LegalDocumentDetector`
Implements the legal document detection logic for Phases 1 and 2.
- **Phase 1**: Lightning-fast keyword and URL pattern matching
- **Phase 2**: Sophisticated content analysis and filtering
- Configurable confidence thresholds
- Multiple detection strategies

#### `HTMLContentExtractor`
Extracts and cleans HTML content from web pages.
- Removes noise (ads, navigation, etc.)
- Extracts main content using readability algorithms
- Handles various HTML encodings
- Preserves legal text structure

#### `GPTLegalAnalyzer`
Manages GPT-4o integration for detailed legal analysis.
- Structured prompting for consistent results
- Token usage tracking and cost estimation
- Rate limiting and error handling
- Supports multiple analysis types

### Data Flow

```
CommonCrawl WARC Files
    ↓
Phase 1: Lightning Fast Detection (50K+ records/min)
    ↓
Phase 2: Sophisticated Filtering (1K+ docs/min)
    ↓
Phase 3: GPT Analysis & Extraction (100+ docs/min)
    ↓
Structured Output (JSON, Parquet, Reports)
```

## Features

### Analysis Capabilities

#### Legal Document Detection
- Privacy policies and privacy notices
- Terms of service and terms of use
- Cookie policies and consent management
- Copyright and intellectual property notices
- Legal disclaimers and liability statements
- GDPR and CCPA compliance pages
- Data processing agreements
- License agreements

#### Content Classification
- **Copyright Analysis**: 9 detailed categories of copyright clauses
- **Access Level Assessment**: 8-level classification from open access to blocked
- **Technical Protection Measures**: Detection of DRM and access controls
- **Liability Clauses**: Identification of limitation of liability statements
- **Jurisdiction Clauses**: Legal jurisdiction and governing law identification
- **Data Licensing**: Analysis of data usage and licensing terms

#### Quality Metrics
- Confidence scores for all classifications
- Detection method tracking
- Content quality assessment
- Completeness indicators

## Installation


### Installation Steps

```bash
# Clone the repository
git clone <repository-url>
cd legal-crawl-analysis

# Install dependencies using Poetry
poetry install

# Install development dependencies (optional)
poetry install --with dev

# Set up environment
poetry run setup-environment

# Configure OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

### Verification

```bash
# Test the installation
poetry run python test_package.py

# Run a simple example
poetry run python example_simple.py
```

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY='your-openai-api-key'

# Optional
export LEGAL_CRAWL_OUTPUT_DIR='/path/to/output'
export LEGAL_CRAWL_WARC_DIR='/path/to/warc/files'
export LEGAL_CRAWL_LOG_LEVEL='INFO'
```

### Configuration File (`legal_crawl_analysis/config.py`)

#### API Configuration
```python
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GPT_MODEL = "gpt-4o"                    # OpenAI model to use
MAX_TOKENS_PER_ANALYSIS = 2000          # Token limit per analysis
GPT_TEMPERATURE = 0.1                   # Temperature for GPT responses
GPT_REQUESTS_PER_MINUTE = 10            # Rate limiting for OpenAI API
```

#### Processing Configuration
```python
MAX_WARC_FILES = 5                      # Number of WARC files to process
MAX_RECORDS_PER_WARC = 10000           # Records per WARC (for testing)
MIN_CONFIDENCE_THRESHOLD = 0.4          # Minimum confidence for detection
MIN_CONTENT_LENGTH = 500                # Minimum content length
MAX_CONTENT_LENGTH_FOR_ANALYSIS = 50000 # Maximum content for GPT analysis
```

#### Directory Configuration
```python
BASE_DIR = Path(__file__).parent.parent
WARC_DIR = BASE_DIR / "warc_files"      # WARC file storage
OUTPUT_DIR = BASE_DIR / "analysis_output" # Analysis results
LOGS_DIR = BASE_DIR / "logs"            # Log files
```

#### Advanced Configuration
```python
ENABLE_DETAILED_LOGGING = True          # Verbose logging
SAVE_HTML_CONTENT = False              # Save HTML for debugging
REQUESTS_PER_SECOND = 2                # Rate limit for downloads
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Run complete analysis with default settings
poetry run legal-crawl-analyzer

# Specify OpenAI API key inline
poetry run legal-crawl-analyzer --openai-api-key YOUR_KEY

# Process specific number of WARC files
poetry run legal-crawl-analyzer --max-files 10

# Process all available files (use with caution!)
poetry run legal-crawl-analyzer --max-files all
```

#### Phase-Specific Processing
```bash
# Run only Phase 1 (fast detection)
poetry run legal-crawl-analyzer --phase 1

# Run only Phase 2 (sophisticated filtering)
poetry run legal-crawl-analyzer --phase 2

# Run only Phase 3 (GPT analysis)
poetry run legal-crawl-analyzer --phase 3 --openai-api-key YOUR_KEY

# Run all phases
poetry run legal-crawl-analyzer --phase all --openai-api-key YOUR_KEY
```

#### Progress Management
```bash
# Resume interrupted analysis
poetry run legal-crawl-analyzer --resume

# Reset progress and start over
poetry run legal-crawl-analyzer --reset-progress

# Use custom progress file
poetry run legal-crawl-analyzer --progress-file my_analysis.json

# Force re-run of specific phase
poetry run legal-crawl-analyzer --phase 2 --force-phase
```

#### Output Control
```bash
# Specify custom output directory
poetry run legal-crawl-analyzer --output-dir /path/to/output

# Enable debug logging
poetry run legal-crawl-analyzer --log-level DEBUG

# Save intermediate results
poetry run legal-crawl-analyzer --save-intermediate
```

### Python API

#### Basic Usage
```python
import os
from legal_crawl_analysis import LegalCrawlAnalyzer

# Initialize analyzer
analyzer = LegalCrawlAnalyzer(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    output_dir="analysis_output"
)

# Run complete analysis
phase_one_stats, phase_two_stats = analyzer.run_incremental_analysis()

# Generate final report
analyzer.generate_final_report()
```

#### Advanced Usage
```python
from legal_crawl_analysis import (
    LegalCrawlAnalyzer,
    LegalDocumentDetector,
    GPTLegalAnalyzer,
    CommonCrawlFetcher
)

# Custom configuration
analyzer = LegalCrawlAnalyzer(
    openai_api_key="your-key",
    output_dir="custom_output",
    max_warc_files=20,
    confidence_threshold=0.6
)

# Run phases individually
phase_one_stats = analyzer.run_phase_one()
print(f"Found {phase_one_stats.legal_documents_detected} legal documents")

if phase_one_stats.legal_documents_detected > 0:
    phase_two_stats = analyzer.run_phase_two()
    print(f"Analyzed {phase_two_stats.documents_analyzed} documents")

# Access detailed results
legal_docs = analyzer.load_phase_one_results()
analyzed_docs = analyzer.load_phase_two_results()
```

#### Component-Level Usage
```python
# Use individual components
from legal_crawl_analysis import LegalDocumentDetector, HTMLContentExtractor

# Initialize detector
detector = LegalDocumentDetector(confidence_threshold=0.5)

# Extract content
extractor = HTMLContentExtractor()
clean_text = extractor.extract_main_content(html_content)

# Detect legal documents
is_legal, confidence, doc_type = detector.is_legal_document(url, clean_text)
```


## 3-Phase Pipeline

### Phase 1: Lightning Fast Detection

**Purpose**: Cast a wide net to capture all potential legal documents
**Speed**: ~50,000 records/minute
**Accuracy**: High recall (95%+), moderate precision (30-70%)

#### Detection Methods
- **URL Pattern Matching**: Detects URLs containing legal keywords
  - `/privacy`, `/terms`, `/legal`, `/cookies`, `/disclaimer`
  - `/policy`, `/agreement`, `/license`, `/copyright`
- **Fast Keyword Scanning**: Scans first 2000 characters for legal terms
- **Domain-Based Heuristics**: Identifies legal document patterns by domain
- **Content Type Detection**: Recognizes common legal document structures

#### Output Format
```json
{
  "url": "https://example.com/privacy-policy",
  "warc_path": "crawl-data/CC-MAIN-2025-08/.../file.warc.gz",
  "detection_type": "url_match",
  "confidence_score": 0.7,
  "detection_method": "url_pattern",
  "html_sample": "first 3000 characters...",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Phase 2: Sophisticated Legal Filtering

**Purpose**: Apply rigorous legal content analysis to filter candidates
**Speed**: ~1,000 documents/minute
**Accuracy**: High precision (80%+), maintains high recall

#### Detection Methods
- **Multi-Pattern Legal Classification**: Advanced pattern matching
- **Content Structure Analysis**: Analyzes document organization
- **Legal Keyword Density**: Calculates legal term frequency
- **Document Type Scoring**: Type-specific confidence scoring
- **Context Analysis**: Examines surrounding content

#### Categories Detected
- Privacy policies and privacy notices
- Terms of service and terms of use
- Cookie policies and consent management
- Copyright and intellectual property notices
- Legal disclaimers and liability statements
- GDPR/CCPA compliance documents

#### Output Format
```json
{
  "url": "https://example.com/privacy-policy",
  "phase2_analysis": {
    "is_legal": true,
    "document_types": ["privacy", "cookies"],
    "total_confidence": 0.85,
    "detection_details": {
      "privacy": {
        "url_matches": ["privacy-policy"],
        "content_matches": ["personal data", "cookies"],
        "keyword_matches": ["data collection", "gdpr"]
      }
    },
    "content_quality": {
      "length": 15000,
      "structure_score": 0.8,
      "completeness": 0.9
    }
  }
}
```

### Phase 3: Passage Extraction & Storage

**Purpose**: Extract specific legal passages and store in structured format
**Speed**: ~100-200 documents/minute (GPT API limited)
**Accuracy**: High precision legal clause extraction

#### Processing Steps
1. **Content Retrieval**: Re-download and extract full HTML content
2. **Content Cleaning**: Remove navigation, ads, and noise
3. **GPT-4o Analysis**: Detailed legal clause extraction
4. **Classification**: Categorize copyright, access levels, etc.
5. **Structured Storage**: Save in Parquet and JSON formats
6. **WARC Preservation**: Maintain original WARC files for reference

#### Analysis Types
- **Copyright Clauses**: 9-category classification system
- **Access Levels**: 8-level access restriction analysis
- **Technical Protection Measures**: DRM and access control detection
- **Liability Clauses**: Limitation of liability identification
- **Jurisdiction Clauses**: Legal jurisdiction analysis
- **Data Licensing**: Data usage and licensing terms


## Output Formats

### Directory Structure
```
analysis_output/
├── CC-MAIN-2025-08/                    # CommonCrawl batch directory
│   ├── phase1_legal_documents.json     # Phase 1 results
│   ├── phase1_statistics.json          # Phase 1 statistics
│   ├── phase2_analyzed_documents.json  # Phase 2 results
│   ├── phase2_statistics.json          # Phase 2 statistics
│   ├── extracted_passages.parquet      # Phase 3 structured data
│   ├── extraction_metadata.parquet     # Phase 3 metadata
│   ├── final_report.md                 # Comprehensive report
│   └── warc_files/                     # Preserved WARC files
│       ├── CC-MAIN-*.warc.gz
│       └── ...
├── analysis_progress.json              # Progress tracking
└── legal_crawl_analysis.log           # System logs
```

### JSON Output Formats

#### Phase 1 Results (`phase1_legal_documents.json`)
```json
[
  {
    "url": "https://example.com/privacy",
    "warc_path": "crawl-data/CC-MAIN-2025-08/.../file.warc.gz",
    "detection_type": "url_match",
    "confidence_score": 0.8,
    "detection_method": "url_pattern",
    "html_sample": "<!DOCTYPE html>...",
    "timestamp": "2025-01-15T10:30:00Z",
    "domain": "example.com",
    "content_length": 15000
  }
]
```

#### Phase 2 Results (`phase2_analyzed_documents.json`)
```json
[
  {
    "url": "https://example.com/privacy",
    "gpt_analysis": {
      "copyright_clauses": [
        {
          "text": "All content is owned by Example Corp",
          "category": "COPYRIGHT_RETAINED_SITE",
          "confidence": 0.9,
          "context": "intellectual property section"
        }
      ],
      "access_level": {
        "level": "L0_OPEN_ACCESS",
        "indicators": ["standard HTML", "no restrictions"],
        "confidence": 0.95
      },
      "technical_protection_measures": [],
      "liability_clauses": ["limitation of liability"],
      "jurisdiction_clauses": ["Delaware law"],
      "data_licensing": ["user grants license"]
    },
    "processing_metadata": {
      "tokens_used": 1500,
      "processing_time": 2.3,
      "model_version": "gpt-4o",
      "timestamp": "2025-01-15T10:32:15Z"
    }
  }
]
```

### Parquet Output (Phase 3)

#### `extracted_passages.parquet`
Structured data optimized for analysis:
- Columnar format for efficient querying
- Compressed storage for large datasets
- Schema enforcement for data consistency
- Compatible with pandas, polars, and analytics tools

#### `extraction_metadata.parquet`
Metadata about the extraction process:
- Processing timestamps and versions
- Token usage and costs
- Quality metrics and confidence scores
- Source WARC file references

### Markdown Reports

#### `final_report.md`
Comprehensive analysis report including:
- Executive summary of findings
- Statistical breakdowns by category
- Distribution charts and tables
- Notable patterns and insights
- Processing statistics and costs
- Recommendations for further analysis

## Classification Systems

### Copyright Categories

The system classifies copyright clauses into 9 detailed categories:

#### Primary Categories
- **`COPYRIGHT_RETAINED_SITE`**: Website/service provider retains copyright
  - Example: "All content on this site is owned by Example Corp"
- **`COPYRIGHT_RETAINED_USER`**: User retains copyright over submitted content
  - Example: "You retain ownership of content you submit"
- **`COPYRIGHT_LICENSED_TO_SITE`**: User grants specific license to site
  - Example: "You grant us a license to use your content"
- **`COPYRIGHT_WAIVED`**: Copyright is waived (public domain)
  - Example: "Content is released to the public domain"

#### Negative Categories
- **`HARD_NEGATIVE_DMCA`**: DMCA/copyright infringement procedures
  - Example: "To report copyright infringement, contact..."
- **`HARD_NEGATIVE_THIRD_PARTY`**: Third-party content/links copyright
  - Example: "Third-party links may be subject to their own copyright"
- **`HARD_NEGATIVE_LICENSE_GRANT`**: User grants license (not full retention)
  - Example: "By posting, you grant us rights to..."

#### Other Categories
- **`EASY_NEGATIVE_IRRELEVANT`**: Clearly not about copyright
  - Example: "Our customer service hours are..."
- **`AMBIGUOUS_COPYRIGHT`**: Unclear copyright clauses
  - Example: "Content may be subject to various rights"

### Access Levels

8-level classification system for website access restrictions:

- **`L0_OPEN_ACCESS`**: Standard HTML, simple GET request
  - No restrictions, publicly accessible
- **`L1_ROBOTS_DISALLOW`**: robots.txt restrictions
  - Crawling discouraged but technically accessible
- **`L2_DYNAMIC_CONTENT`**: Requires JavaScript rendering
  - Content loaded dynamically via JavaScript
- **`L3_ACCESS_CONTROL_SIMPLE`**: Login required, no anti-bot measures
  - Basic authentication required
- **`L4_ACCESS_CONTROL_CAPTCHA`**: CAPTCHA protected
  - Human verification required
- **`L5_ANTI_BOT_SERVICE`**: Advanced anti-bot (Cloudflare, etc.)
  - Sophisticated bot detection systems
- **`L6_PAYWALL`**: Behind paywall
  - Payment required for access
- **`L7_BLOCKED`**: Geo-blocked or completely unavailable
  - Access denied or content unavailable

### Technical Protection Measures

Detection categories for technical access controls:
- **DRM Systems**: Digital rights management implementations
- **Access Controls**: Authentication and authorization systems
- **Bot Protection**: Anti-automation measures
- **Rate Limiting**: Request throttling mechanisms
- **Geo-blocking**: Geographic access restrictions
- **Content Encryption**: Encrypted content delivery



### Resume Functionality

The system supports robust resume capabilities:

#### Automatic Resume
```bash
# Automatically resume from last checkpoint
poetry run legal-crawl-analyzer --resume
```

#### Manual Progress Management
```bash
# Reset progress and start over
poetry run legal-crawl-analyzer --reset-progress

# Use custom progress file
poetry run legal-crawl-analyzer --progress-file custom_analysis.json

# Force re-run of specific phase
poetry run legal-crawl-analyzer --phase 2 --force-phase
```

#### Graceful Interruption Handling
- **SIGINT (Ctrl+C)**: Saves progress and exits cleanly
- **SIGTERM**: Saves progress before shutdown
- **Unexpected crashes**: Progress saved after each file
- **Network interruptions**: Automatic retry with backoff


### Advanced Configuration Options

#### Environment Variables (Complete List)
```bash
# Core Configuration
export OPENAI_API_KEY='your-openai-api-key'
export LEGAL_CRAWL_OUTPUT_DIR='/path/to/output'
export LEGAL_CRAWL_WARC_DIR='/path/to/warc/files'
export LEGAL_CRAWL_LOG_LEVEL='INFO'  # DEBUG, INFO, WARNING, ERROR

# Performance Tuning
export LEGAL_CRAWL_MAX_WORKERS='4'
export LEGAL_CRAWL_CHUNK_SIZE='1000'
export LEGAL_CRAWL_MEMORY_LIMIT='8GB'

# API Configuration
export LEGAL_CRAWL_GPT_MODEL='gpt-4o'
export LEGAL_CRAWL_GPT_TEMPERATURE='0.1'
export LEGAL_CRAWL_MAX_TOKENS='2000'
export LEGAL_CRAWL_REQUESTS_PER_MINUTE='10'

# Processing Configuration
export LEGAL_CRAWL_MIN_CONFIDENCE='0.4'
export LEGAL_CRAWL_MIN_CONTENT_LENGTH='500'
export LEGAL_CRAWL_MAX_CONTENT_LENGTH='50000'
```

#### Advanced Configuration Parameters (`config.py`)
```python
# WARC Processing Configuration
WARC_COMPRESSION_LEVEL = 6              # GZIP compression level
WARC_RECORD_BATCH_SIZE = 1000          # Records per batch
WARC_MEMORY_BUFFER_SIZE = 64 * 1024     # Buffer size for WARC writing

# Detection Configuration  
KEYWORD_MATCH_THRESHOLD = 3            # Minimum keyword matches
URL_PATTERN_WEIGHT = 0.8               # URL pattern confidence weight
CONTENT_PATTERN_WEIGHT = 0.6           # Content pattern confidence weight
DOMAIN_WHITELIST = []                  # Specific domains to include
DOMAIN_BLACKLIST = []                  # Specific domains to exclude

# GPT Analysis Configuration
GPT_RETRY_ATTEMPTS = 3                 # Retry failed API calls
GPT_BACKOFF_FACTOR = 2.0              # Exponential backoff multiplier
GPT_TIMEOUT_SECONDS = 30               # API call timeout
GPT_BATCH_SIZE = 10                    # Documents per batch

# Output Configuration
ENABLE_INCREMENTAL_SAVES = True        # Save results incrementally
SAVE_RAW_HTML = False                  # Include raw HTML in outputs
COMPRESS_JSON_OUTPUT = True            # GZIP compress JSON files
PARQUET_COMPRESSION = 'snappy'         # Parquet compression algorithm
```


## Contact

- **Author**: Saber Zerhoudi
- **Email**: saber.zerhoudi@uni-passau.de
- **Institution**: University of Passau
- **Project**: Legal Document Analysis Research 