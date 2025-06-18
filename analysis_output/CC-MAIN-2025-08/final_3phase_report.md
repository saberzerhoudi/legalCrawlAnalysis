# 3-Phase Legal Crawl Analysis Report

**Generated:** 2025-06-16T06:05:32.335050
**Crawl:** CC-MAIN-2025-08
**Total Processing Time:** 2121.11 seconds

## Phase 1: Lightning Fast Detection
- **Records Processed:** 30,084
- **Legal Documents Found:** 1,328
- **Detection Rate:** 4.4143%
- **WARC Files Created:** 0

## Phase 2: Sophisticated Filtering
- **Input Documents:** 1,328
- **Filtered Documents:** 454
- **Filter Success Rate:** 34.19%
- **WARC Files Kept:** 0
- **Metadata Parquet Files:** 0

## Phase 3: Passage Extraction
- **Input Documents:** 454
- **Extracted Passages:** 1,036
- **OpenAI Tokens Used:** 652,494,823
- **Estimated Cost:** $19574.84
- **Final WARC Files:** 1
- **Final Metadata Files:** 1
- **GPT Analysis Files:** 1

## Output Files Structure
```
CC-MAIN-2025-08/
├── phase1_fast_detection/          # WARC files with potential legal docs
├── phase2_sophisticated_filtering/  # Filtered WARC files + metadata parquet
├── phase3_passages_and_warc/       # Final WARC files + metadata + GPT analysis parquet
├── final_3phase_report.json
└── final_3phase_report.md
```
