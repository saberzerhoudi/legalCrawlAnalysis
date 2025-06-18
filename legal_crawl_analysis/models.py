"""
Data models for Legal Crawl Analysis
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class CopyrightClause:
    """Represents a copyright clause with its classification"""
    text: str
    category: str
    confidence: float
    context: str

@dataclass
class AccessLevel:
    """Represents the access level analysis of a webpage"""
    level: str
    indicators: List[str]
    confidence: float

@dataclass
class LegalDocument:
    """Represents a legal document found in WARC data"""
    url: str
    title: str
    domain: str
    content_type: str
    html_content: str
    clean_text: str
    copyright_clauses: List[CopyrightClause]
    access_level: AccessLevel
    technical_protection_measures: List[str]
    liability_clauses: List[str]
    jurisdiction_clauses: List[str]
    data_licensing: List[str]
    warc_record_id: str
    timestamp: str

@dataclass
class PhaseOneStats:
    """Statistics from Phase 1 - Fast legal document detection"""
    total_warcs_processed: int
    total_records_examined: int
    legal_documents_detected: int
    detection_time_seconds: float
    domain_distribution: Dict[str, int]
    document_type_distribution: Dict[str, int]
    size_distribution: Dict[str, int]

@dataclass  
class PhaseTwoStats:
    """Statistics from Phase 2 - Detailed GPT analysis"""
    documents_analyzed: int
    copyright_categories: Dict[str, int]
    access_levels: Dict[str, int]
    technical_measures: Dict[str, int]
    processing_time_seconds: float
    openai_api_calls: int
    total_tokens_used: int 