"""
Legal Crawl Analysis - A comprehensive system for analyzing legal documents in CommonCrawl data.

This package provides tools for:
1. Fetching CommonCrawl WARC files  
2. Fast detection of legal documents (privacy policies, ToS, etc.)
3. Detailed GPT-4o analysis of copyright clauses and access levels
4. Comprehensive statistics and reporting
"""

__version__ = "0.1.0"
__author__ = "Saber Zerhoudi"
__email__ = "saber.zerhoudi@uni-passau.de"

from .analyzer import LegalCrawlAnalyzer
from .detector import LegalDocumentDetector
from .extractor import HTMLContentExtractor
from .fetcher import CommonCrawlFetcher
from .gpt_analyzer import GPTLegalAnalyzer
from .models import (
    LegalDocument,
    CopyrightClause,
    AccessLevel,
    PhaseOneStats,
    PhaseTwoStats
)

__all__ = [
    "LegalCrawlAnalyzer",
    "LegalDocumentDetector", 
    "HTMLContentExtractor",
    "CommonCrawlFetcher",
    "GPTLegalAnalyzer",
    "LegalDocument",
    "CopyrightClause",
    "AccessLevel",
    "PhaseOneStats",
    "PhaseTwoStats",
]