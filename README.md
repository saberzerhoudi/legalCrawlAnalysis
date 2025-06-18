# Legal Crawl Analysis

A comprehensive Python package for analyzing legal documents in CommonCrawl data using a sophisticated 3-phase pipeline: lightning-fast detection, sophisticated filtering, and detailed GPT-4o analysis.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
  - [Example Scripts](#example-scripts)
- [3-Phase Pipeline](#3-phase-pipeline)
- [Data Models](#data-models)
- [Output Formats](#output-formats)
- [Classification Systems](#classification-systems)
- [Progress Tracking](#progress-tracking)
- [Performance & Scaling](#performance--scaling)
- [Cost Estimation](#cost-estimation)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

**Legal Crawl Analysis** is a library designed for large-scale analysis of legal documents found in CommonCrawl web archives. The system processes web records to identify, extract, and analyze legal content including privacy policies, terms of service, copyright notices, and other legal documents.

### Use Cases

- **Legal Research**: Large-scale studies of digital legal landscapes
- **Compliance Analysis**: Tracking GDPR, CCPA, and other regulatory compliance patterns
- **Policy Evolution Studies**: Understanding how legal language changes over time
- **Industry Analysis**: Comparing legal practices across different sectors
- **Data Rights Research**: Analyzing how platforms handle user data and rights

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

### Core Features

- **Multi-Phase Processing**: Progressive refinement from broad detection to detailed analysis
- **Scalable Architecture**: Processes datasets ranging from thousands to billions of records
- **Intelligent Caching**: Avoids reprocessing with sophisticated progress tracking
- **Cost Management**: Real-time token tracking and cost estimation for OpenAI usage
- **Flexible Configuration**: Extensive configuration options for different use cases
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Multiple Output Formats**: JSON, Parquet, Markdown reports, and statistics
- **Resume Functionality**: Graceful handling of interruptions with automatic resume
- **Error Recovery**: Robust error handling with detailed error reporting

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

### Prerequisites

- **Python**: 3.11 or higher
- **Poetry**: For dependency management
- **OpenAI API Key**: For GPT-4o analysis
- **Storage**: Minimum 50GB free space for WARC files
- **Memory**: Minimum 8GB RAM (16GB recommended for large analyses)

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

### Example Scripts

#### Simple Example (`example_simple.py`)
```bash
# Run the basic example
poetry run python example_simple.py
```
This script demonstrates:
- Basic analyzer setup
- Incremental analysis execution
- Results interpretation
- Cost estimation

#### 3-Phase Example (`example_3phase_analysis.py`)
```bash
# Run the 3-phase example
poetry run python example_3phase_analysis.py
```
This script demonstrates:
- Phase-by-phase execution
- Progress tracking
- Advanced configuration
- Detailed result analysis

#### Progress Tracking Example (`example_progress_tracking.py`)
```bash
# Run the progress tracking example
poetry run python example_progress_tracking.py
```
This script demonstrates:
- Resume functionality
- Progress file management
- Error recovery
- Statistics accumulation

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

## Data Models

### Core Data Structures

#### `LegalDocument`
```python
@dataclass
class LegalDocument:
    url: str                                    # Document URL
    title: str                                  # Page title
    domain: str                                 # Domain name
    content_type: str                          # Document type
    html_content: str                          # Raw HTML
    clean_text: str                            # Cleaned text
    copyright_clauses: List[CopyrightClause]   # Copyright analysis
    access_level: AccessLevel                  # Access restriction level
    technical_protection_measures: List[str]   # Technical protections
    liability_clauses: List[str]               # Liability statements
    jurisdiction_clauses: List[str]            # Jurisdiction information
    data_licensing: List[str]                  # Data licensing terms
    warc_record_id: str                        # WARC record identifier
    timestamp: str                             # Processing timestamp
```

#### `CopyrightClause`
```python
@dataclass
class CopyrightClause:
    text: str           # Original clause text
    category: str       # Classification category
    confidence: float   # Classification confidence
    context: str        # Surrounding context
```

#### `AccessLevel`
```python
@dataclass
class AccessLevel:
    level: str              # Access level (L0-L7)
    indicators: List[str]   # Detection indicators
    confidence: float       # Classification confidence
```

#### `PhaseOneStats`
```python
@dataclass
class PhaseOneStats:
    total_warcs_processed: int              # Number of WARC files
    total_records_examined: int             # Total records processed
    legal_documents_detected: int           # Legal documents found
    detection_time_seconds: float           # Processing time
    domain_distribution: Dict[str, int]     # Documents per domain
    document_type_distribution: Dict[str, int] # Document types
    size_distribution: Dict[str, int]       # Document sizes
```

#### `PhaseTwoStats`
```python
@dataclass
class PhaseTwoStats:
    documents_analyzed: int                 # Documents processed
    copyright_categories: Dict[str, int]    # Copyright classifications
    access_levels: Dict[str, int]          # Access level distribution
    technical_measures: Dict[str, int]     # Technical protections
    processing_time_seconds: float         # Processing time
    openai_api_calls: int                  # OpenAI API usage
    total_tokens_used: int                 # Token consumption
```

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

## Progress Tracking

### Progress File Format (`analysis_progress.json`)
```json
{
  "last_processed_index": 4,
  "processed_files": [
    "crawl-data/CC-MAIN-2025-08/.../file1.warc.gz",
    "crawl-data/CC-MAIN-2025-08/.../file2.warc.gz"
  ],
  "total_files_to_process": 10,
  "start_time": "2025-01-15T10:30:00Z",
  "last_update": "2025-01-15T11:45:30Z",
  "cumulative_stats": {
    "total_records_processed": 180000,
    "legal_documents_found": 1250,
    "documents_analyzed": 1200,
    "openai_api_calls": 1200,
    "openai_tokens_used": 2400000,
    "estimated_cost_usd": 12.50
  },
  "phase_status": {
    "phase1_complete": true,
    "phase2_complete": true,
    "phase3_complete": false
  }
}
```

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

## Performance & Scaling

### Performance Characteristics

#### Phase 1: Lightning Fast Detection
- **Throughput**: 50,000+ records/minute
- **Memory Usage**: Low (~200MB)
- **Storage**: ~1KB per detected document
- **Scalability**: Linear with number of records

#### Phase 2: Sophisticated Filtering  
- **Throughput**: 1,000+ documents/minute
- **Memory Usage**: Medium (~1GB)
- **Storage**: ~5KB per filtered document
- **Scalability**: Linear with number of detected documents

#### Phase 3: GPT Analysis
- **Throughput**: 100-200 documents/minute (API limited)
- **Memory Usage**: High (~2-4GB)
- **Storage**: ~50KB per document + WARC preservation
- **Scalability**: Limited by OpenAI API rate limits

### Scaling Recommendations

#### Small Scale (1-10 WARC files)
- **Use case**: Development, testing, small studies
- **Resources**: 8GB RAM, 50GB storage
- **Time**: 1-6 hours
- **Cost**: $5-50

#### Medium Scale (10-100 WARC files)
- **Use case**: Research projects, institutional studies
- **Resources**: 16GB RAM, 500GB storage
- **Time**: 1-3 days
- **Cost**: $50-500

#### Large Scale (100-1000 WARC files)
- **Use case**: Comprehensive studies, industry analysis
- **Resources**: 32GB RAM, 5TB storage
- **Time**: 1-4 weeks
- **Cost**: $500-5000

#### Enterprise Scale (1000+ WARC files)
- **Use case**: Internet-scale analysis, academic research
- **Resources**: Distributed processing, cloud infrastructure
- **Time**: Months to years
- **Cost**: $5000+

## Cost Estimation

### OpenAI API Costs (GPT-4o)

Current pricing (as of 2025):
- **Input tokens**: $0.0025 per 1K tokens
- **Output tokens**: $0.01 per 1K tokens

#### Typical Usage Patterns
- **Average input**: 1,200 tokens per document
- **Average output**: 300 tokens per document
- **Cost per document**: ~$0.006

#### Cost by Scale
```python
# Small analysis (100 documents)
documents = 100
cost = documents * 0.006  # ~$0.60

# Medium analysis (1,000 documents)  
documents = 1000
cost = documents * 0.006  # ~$6.00

# Large analysis (10,000 documents)
documents = 10000
cost = documents * 0.006  # ~$60.00
```

#### Cost Monitoring
Real-time cost tracking is built into the system:
- Token usage logged for each API call
- Cumulative cost calculated and displayed
- Cost estimates provided before processing
- Detailed cost breakdown in statistics files

## Development

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd legal-crawl-analysis

# Install with development dependencies
poetry install --with dev

# Set up pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Type checking
poetry run mypy .

# Code formatting
poetry run black .
poetry run isort .

# Linting
poetry run flake8 .
```

### Development Dependencies

#### Core Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Git hooks

#### Configuration

**Black** (`pyproject.toml`):
```toml
[tool.black]
line-length = 88
target-version = ['py311']
```

**isort** (`pyproject.toml`):
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
```

**mypy** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Testing

#### Test Structure
```
tests/
├── test_analyzer.py         # Main analyzer tests
├── test_detector.py         # Detection logic tests
├── test_extractor.py        # Content extraction tests
├── test_gpt_analyzer.py     # GPT integration tests
├── test_models.py           # Data model tests
├── fixtures/                # Test data
│   ├── sample_warc.gz
│   ├── sample_html/
│   └── expected_outputs/
└── conftest.py              # Test configuration
```

#### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=legal_crawl_analysis

# Run specific test file
poetry run pytest tests/test_analyzer.py

# Run with verbose output
poetry run pytest -v

# Run integration tests only
poetry run pytest -m integration
```

### Contributing Guidelines

#### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 80%
- Use meaningful variable and function names

#### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

#### Issue Templates
- **Bug reports**: Include reproduction steps
- **Feature requests**: Describe use case and benefits
- **Documentation**: Specify what needs clarification

## Troubleshooting

### Common Issues

#### Installation Problems

**Poetry not found**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

**Python version compatibility**
```bash
# Check Python version
python --version

# Should be 3.11 or higher
# Use pyenv to manage Python versions if needed
```

#### Runtime Issues

**OpenAI API key not set**
```bash
# Set environment variable
export OPENAI_API_KEY='your-api-key-here'

# Or pass directly to command
poetry run legal-crawl-analyzer --openai-api-key YOUR_KEY
```

**Insufficient disk space**
```bash
# Check available space
df -h

# WARC files can be large (1GB+ each)
# Ensure adequate storage before processing
```

**Memory issues during processing**
```bash
# Monitor memory usage
htop

# Reduce MAX_RECORDS_PER_WARC in config.py
# Process fewer files simultaneously
```

#### API Issues

**OpenAI rate limiting**
```
Error: Rate limit exceeded for gpt-4o
```
Solution: Reduce `GPT_REQUESTS_PER_MINUTE` in config.py

**OpenAI API errors**
```
Error: Invalid API key
```
Solution: Verify API key and billing status

**Network connectivity issues**
```
Error: Failed to download WARC file
```
Solution: Check internet connection and retry

#### Processing Issues

**No legal documents found**
- Common with small samples
- Try increasing `MAX_WARC_FILES`
- Lower `MIN_CONFIDENCE_THRESHOLD`

**High false positive rate in Phase 1**
- Expected behavior (30-70% false positives)
- Phase 2 will filter out false positives
- Adjust thresholds if needed

**GPT analysis producing inconsistent results**
- Check prompt templates in `gpt_analyzer.py`
- Verify content quality and length
- Consider adjusting temperature settings

### Debugging

#### Logging Configuration
```python
# Enable debug logging
ENABLE_DETAILED_LOGGING = True

# Set log level in environment
export LEGAL_CRAWL_LOG_LEVEL=DEBUG
```

#### Log File Locations
- **Main log**: `legal_crawl_analysis.log`
- **Error log**: `analysis_output/errors.log`
- **Progress log**: `analysis_output/progress.log`

#### Debugging Tools
```bash
# Inspect WARC files
poetry run python -c "
from legal_crawl_analysis import CommonCrawlFetcher
fetcher = CommonCrawlFetcher()
fetcher.inspect_warc_file('path/to/file.warc.gz')
"

# Test legal detection
poetry run python -c "
from legal_crawl_analysis import LegalDocumentDetector
detector = LegalDocumentDetector()
result = detector.is_legal_document('https://example.com/privacy', 'content')
print(result)
"

# Test GPT analysis
poetry run python -c "
from legal_crawl_analysis import GPTLegalAnalyzer
analyzer = GPTLegalAnalyzer('your-api-key')
result = analyzer.analyze_legal_document('sample text')
print(result)
"
```

### Performance Monitoring

#### System Metrics
- CPU usage during processing
- Memory consumption patterns
- Disk I/O for WARC files
- Network usage for downloads

#### Application Metrics
- Processing rate (records/minute)
- Detection accuracy (precision/recall)
- API response times
- Error rates by component

#### Monitoring Tools
```bash
# System monitoring
htop           # CPU and memory
iotop          # Disk I/O
nethogs        # Network usage

# Application monitoring
tail -f legal_crawl_analysis.log  # Live log monitoring
```

## Contributing

### Development Workflow

1. **Set up development environment**
2. **Choose an area to contribute**
3. **Write tests for new functionality**
4. **Implement changes**
5. **Ensure all tests pass**
6. **Update documentation**
7. **Submit pull request**

### Areas for Contribution

#### Beginner-Friendly
- Documentation improvements
- Example scripts and tutorials
- Test coverage expansion
- Bug fixes and error handling

#### Intermediate
- New legal document detectors
- Additional classification categories
- Performance optimizations
- Configuration enhancements

#### Advanced
- Alternative AI models integration
- Distributed processing support
- Real-time analysis capabilities
- Advanced visualization tools

### Community

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Wiki**: Community documentation and examples
- **License**: Open source under MIT license

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{legal_crawl_analysis,
  title = {Legal Crawl Analysis: A Comprehensive System for Analyzing Legal Documents in CommonCrawl Data},
  author = {Saber Zerhoudi},
  institution = {University of Passau},
  year = {2025},
  url = {https://github.com/your-repo/legal-crawl-analysis}
}
```

## Advanced Features & Implementation Details

### Three-Phase Analysis Implementation

The system implements a sophisticated `ThreePhaseLegalAnalyzer` class with advanced capabilities:

#### `ThreePhaseProgressTracker`
```python
class ThreePhaseProgressTracker:
    """Track progress across the 3-phase analysis pipeline"""
    
    def __init__(self, progress_file: str):
        self.progress_file = progress_file
        self.progress_data = self._load_progress()
    
    # Methods:
    # - update_phase_1(file_index, warc_path, legal_docs_found, records_processed)
    # - update_phase_2(file_index, warc_name, filtered_docs)
    # - update_phase_3(file_index, warc_name, extracted_passages, tokens_used)
    # - complete_phase(phase)
    # - get_phase_start_index(phase)
    # - reset()
```

#### Phase-Specific Processing Methods

##### Phase 1 Processing
```python
def _process_warc_phase_1(self, warc_file: Path, warc_path: str) -> Tuple[int, int]:
    """Process WARC file for Phase 1 lightning fast detection"""
    # - Streams through WARC records
    # - Applies fast keyword and URL pattern matching
    # - Saves legal document candidates to WARC format
    # - Returns (legal_docs_found, records_processed)
```

##### Phase 2 Processing
```python
def _process_phase2_warc_filtering(self, phase1_warc_file: Path) -> List[Dict]:
    """Apply sophisticated legal filtering to Phase 1 candidates"""
    # - Loads Phase 1 WARC files
    # - Applies advanced legal document classification
    # - Filters out false positives
    # - Returns list of filtered legal documents
```

##### Phase 3 Processing
```python
def _process_phase3_gpt_analysis(self, phase2_warc_file: Path) -> Tuple[List[Dict], int]:
    """Extract legal passages using GPT-4o analysis"""
    # - Processes Phase 2 filtered documents
    # - Applies GPT-4o for detailed legal clause extraction
    # - Returns (extracted_passages, total_tokens_used)
```

### WARC File Management

#### WARC Preservation Strategy
- **Phase 1**: Creates new WARC files with legal document candidates
- **Phase 2**: Filters and reorganizes WARC data
- **Phase 3**: Preserves final WARC files with complete analysis metadata

#### WARC Directory Structure
```
analysis_output/
└── CC-MAIN-2025-08/
    ├── phase1_fast_detection/
    │   ├── legal_candidates_000.warc.gz
    │   ├── legal_candidates_001.warc.gz
    │   └── ...
    ├── phase2_sophisticated_filtering/
    │   ├── filtered_legal_000.warc.gz
    │   ├── filtered_legal_001.warc.gz
    │   └── ...
    └── phase3_passages_and_warc/
        ├── final_analysis_000.warc.gz
        ├── extracted_passages.parquet
        ├── extraction_metadata.parquet
        └── gpt_analysis_results.json
```

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

### Complete API Reference

#### `LegalCrawlAnalyzer` Class Methods

##### Initialization
```python
LegalCrawlAnalyzer(
    openai_api_key: str,
    output_dir: str = "analysis_output",
    max_warc_files: int = 5,
    confidence_threshold: float = 0.4,
    enable_resume: bool = True,
    progress_file: str = "analysis_progress.json"
)
```

##### Core Analysis Methods
```python
# Run complete analysis pipeline
run_incremental_analysis() -> Tuple[PhaseOneStats, PhaseTwoStats]

# Run individual phases
run_phase_one() -> PhaseOneStats
run_phase_two() -> PhaseTwoStats
run_phase_three() -> PhaseTwoStats

# Run 3-phase analysis with WARC preservation
run_three_phase_analysis(openai_api_key: str, resume: bool = False) -> Dict

# Generate comprehensive reports
generate_final_report() -> None
generate_phase_report(phase: int) -> Dict
```

##### Data Access Methods
```python
# Load analysis results
load_phase_one_results() -> List[Dict]
load_phase_two_results() -> List[Dict]
load_legal_documents() -> List[LegalDocument]

# Access statistics
get_phase_one_stats() -> PhaseOneStats
get_phase_two_stats() -> PhaseTwoStats
get_cumulative_stats() -> Dict

# Progress management
save_progress() -> None
load_progress() -> Dict
reset_progress() -> None
```

#### `LegalDocumentDetector` Class Methods

##### Detection Methods
```python
# Core detection
is_legal_document(url: str, content: str) -> Tuple[bool, float, str]

# Specialized detectors
detect_privacy_policy(url: str, content: str) -> Tuple[bool, float]
detect_terms_of_service(url: str, content: str) -> Tuple[bool, float]
detect_cookie_policy(url: str, content: str) -> Tuple[bool, float]
detect_copyright_notice(url: str, content: str) -> Tuple[bool, float]

# Pattern-based detection
url_pattern_match(url: str) -> Tuple[bool, float, List[str]]
content_pattern_match(content: str) -> Tuple[bool, float, List[str]]
keyword_density_analysis(content: str) -> float
```

##### Configuration Methods
```python
# Threshold management
set_confidence_threshold(threshold: float) -> None
get_confidence_threshold() -> float

# Pattern management
add_url_pattern(pattern: str, weight: float = 1.0) -> None
add_keyword_pattern(pattern: str, weight: float = 1.0) -> None
remove_pattern(pattern: str) -> None
```

#### `GPTLegalAnalyzer` Class Methods

##### Analysis Methods
```python
# Core analysis
analyze_legal_document(content: str) -> Dict

# Specialized analysis
extract_copyright_clauses(content: str) -> List[CopyrightClause]
analyze_access_level(content: str) -> AccessLevel
identify_technical_protections(content: str) -> List[str]
extract_liability_clauses(content: str) -> List[str]
identify_jurisdiction_clauses(content: str) -> List[str]
analyze_data_licensing(content: str) -> List[str]
```

##### Token and Cost Management
```python
# Token tracking
get_token_usage() -> Dict
estimate_cost(content: str) -> float
get_cumulative_cost() -> float

# Rate limiting
set_rate_limit(requests_per_minute: int) -> None
check_rate_limit() -> bool
```

### Error Handling and Recovery

#### Exception Hierarchy
```python
class LegalCrawlAnalysisError(Exception):
    """Base exception for legal crawl analysis"""
    pass

class WARCProcessingError(LegalCrawlAnalysisError):
    """Errors during WARC file processing"""
    pass

class GPTAnalysisError(LegalCrawlAnalysisError):
    """Errors during GPT analysis"""
    pass

class ConfigurationError(LegalCrawlAnalysisError):
    """Configuration-related errors"""
    pass

class ProgressTrackingError(LegalCrawlAnalysisError):
    """Progress tracking and resume errors"""
    pass
```

#### Error Recovery Strategies
```python
# Automatic retry with exponential backoff
@retry(max_attempts=3, backoff_factor=2.0)
def robust_gpt_analysis(self, content: str) -> Dict:
    """GPT analysis with automatic retry"""
    pass

# Progress checkpoint recovery
def recover_from_checkpoint(self, checkpoint_file: str) -> bool:
    """Recover analysis from saved checkpoint"""
    pass

# Partial result preservation
def save_partial_results(self, results: List[Dict], phase: int) -> None:
    """Save partial results during processing"""
    pass
```

### Performance Optimization

#### Memory Management
```python
# Streaming WARC processing
def stream_warc_records(self, warc_file: Path) -> Iterator[Dict]:
    """Memory-efficient WARC record streaming"""
    pass

# Batch processing
def process_in_batches(self, items: List, batch_size: int = 1000) -> Iterator[List]:
    """Process items in memory-efficient batches"""
    pass

# Memory monitoring
def monitor_memory_usage(self) -> Dict:
    """Monitor current memory usage"""
    pass
```

#### Parallel Processing
```python
# Multi-threaded WARC processing
def parallel_warc_processing(self, warc_files: List[Path], workers: int = 4) -> List[Dict]:
    """Process multiple WARC files in parallel"""
    pass

# Concurrent GPT analysis
def concurrent_gpt_analysis(self, documents: List[str], max_concurrent: int = 5) -> List[Dict]:
    """Process multiple documents concurrently"""
    pass
```

### Integration Patterns

#### Custom Detectors
```python
class CustomLegalDetector(LegalDocumentDetector):
    """Example custom legal document detector"""
    
    def __init__(self, custom_patterns: List[str]):
        super().__init__()
        self.custom_patterns = custom_patterns
    
    def detect_custom_legal_type(self, url: str, content: str) -> Tuple[bool, float]:
        """Implement custom detection logic"""
        pass
```

#### Custom Analyzers
```python
class CustomGPTAnalyzer(GPTLegalAnalyzer):
    """Example custom GPT analyzer"""
    
    def __init__(self, api_key: str, custom_prompts: Dict[str, str]):
        super().__init__(api_key)
        self.custom_prompts = custom_prompts
    
    def analyze_custom_clauses(self, content: str) -> List[Dict]:
        """Implement custom clause analysis"""
        pass
```

#### Plugin Architecture
```python
# Plugin interface
class AnalysisPlugin:
    """Base class for analysis plugins"""
    
    def pre_process(self, content: str) -> str:
        """Pre-process content before analysis"""
        pass
    
    def post_process(self, results: Dict) -> Dict:
        """Post-process analysis results"""
        pass
    
    def validate_results(self, results: Dict) -> bool:
        """Validate analysis results"""
        pass

# Plugin registration
analyzer.register_plugin('custom_plugin', CustomAnalysisPlugin())
```

### Data Export and Integration

#### Export Formats
```python
# Export to various formats
analyzer.export_to_csv('results.csv')
analyzer.export_to_excel('results.xlsx')
analyzer.export_to_sqlite('results.db')
analyzer.export_to_postgresql('postgresql://connection_string')

# Custom export format
def export_to_custom_format(self, output_file: str, format_spec: Dict) -> None:
    """Export results to custom format"""
    pass
```

#### Database Integration
```python
# Database connectors
from legal_crawl_analysis.connectors import (
    PostgreSQLConnector,
    MySQLConnector,
    MongoDBConnector,
    ElasticsearchConnector
)

# Usage example
postgres = PostgreSQLConnector('postgresql://connection_string')
postgres.create_tables()
postgres.insert_analysis_results(results)
```

#### API Integration
```python
# REST API client
from legal_crawl_analysis.api import LegalAnalysisAPIClient

client = LegalAnalysisAPIClient('https://api.example.com')
client.upload_results(results)
client.get_analysis_status(job_id)
```

## Contact

- **Author**: Saber Zerhoudi
- **Email**: saber.zerhoudi@uni-passau.de
- **Institution**: University of Passau
- **Project**: Legal Document Analysis Research 