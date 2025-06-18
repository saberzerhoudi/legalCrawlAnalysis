"""
Legal document detection with multiple phases
Phase 1: Lightning fast detection (high recall, false positives OK)
Phase 2: Sophisticated legal content detection (high precision)
"""

import re
import logging
from typing import Dict, List, Set, Optional
from urllib.parse import urlparse
import tldextract

logger = logging.getLogger(__name__)

class LightningFastDetector:
    """Phase 1: Ultra-fast legal document detection optimized for speed and recall"""
    
    def __init__(self):
        # Ultra-fast URL pattern matching (compiled regex for speed)
        self.url_patterns = [
            re.compile(r'privacy', re.IGNORECASE),
            re.compile(r'terms', re.IGNORECASE),
            re.compile(r'legal', re.IGNORECASE),
            re.compile(r'cookie', re.IGNORECASE),
            re.compile(r'policy', re.IGNORECASE),
            re.compile(r'agreement', re.IGNORECASE),
            re.compile(r'disclaimer', re.IGNORECASE),
            re.compile(r'copyright', re.IGNORECASE),
            re.compile(r'license', re.IGNORECASE),
            re.compile(r'tos\b', re.IGNORECASE),
            re.compile(r'gdpr', re.IGNORECASE),
            re.compile(r'impressum', re.IGNORECASE),
            re.compile(r'ccpa', re.IGNORECASE),
            re.compile(r'dmca', re.IGNORECASE),
        ]
        
        # Lightning-fast content keywords (very basic, just for speed)
        self.fast_keywords = {
            'privacy', 'terms', 'legal', 'cookie', 'policy', 'agreement',
            'copyright', 'license', 'gdpr', 'ccpa', 'dmca', 'disclaimer',
            'impressum', 'datenschutz', 'mentions', 'legales'
        }
    
    def is_legal_document(self, url: str, html_content: str) -> Dict:
        """
        Ultra-fast legal document detection
        Optimized for speed - prioritizes recall over precision
        """
        # Quick URL check (fastest)
        for pattern in self.url_patterns:
            if pattern.search(url):
                return {
                    'is_legal': True,
                    'type': 'url_match',
                    'confidence': 0.7,
                    'detection_method': 'url_pattern'
                }
        
        # Quick content check (only first 2000 chars for speed)
        content_sample = html_content[:2000].lower()
        
        # Count keyword matches (very fast)
        keyword_matches = sum(1 for keyword in self.fast_keywords if keyword in content_sample)
        
        if keyword_matches >= 2:  # Lower threshold for high recall
            return {
                'is_legal': True,
                'type': 'content_match',
                'confidence': min(0.3 + (keyword_matches * 0.1), 0.9),
                'detection_method': 'fast_keywords'
            }
        
        return {
            'is_legal': False,
            'type': 'none',
            'confidence': 0.0,
            'detection_method': 'fast_rejection'
        }

class SophisticatedLegalDetector:
    """Phase 2: Sophisticated legal content detection for high precision filtering"""
    
    def __init__(self):
        # Comprehensive legal document patterns
        self.legal_patterns = {
            'privacy': {
                'url_patterns': [
                    r'privacy[_-]?policy', r'privacy[_-]?notice', r'privacy[_-]?statement',
                    r'datenschutz', r'politique[_-]?confidentialite', r'privacidad'
                ],
                'content_patterns': [
                    r'we collect.*information', r'personal data', r'data protection',
                    r'cookies.*tracking', r'third[_-]?party.*services', r'gdpr',
                    r'california.*privacy.*rights', r'ccpa', r'opt[_-]?out'
                ],
                'keywords': [
                    'personal information', 'data collection', 'privacy policy',
                    'cookies', 'tracking', 'third party', 'gdpr', 'ccpa'
                ]
            },
            'terms': {
                'url_patterns': [
                    r'terms[_-]?of[_-]?(use|service)', r'terms[_-]?conditions',
                    r'user[_-]?agreement', r'service[_-]?agreement', r'tos\b'
                ],
                'content_patterns': [
                    r'terms.*conditions', r'user.*agreement', r'service.*agreement',
                    r'prohibited.*use', r'limitation.*liability', r'governing.*law'
                ],
                'keywords': [
                    'terms of service', 'user agreement', 'prohibited use',
                    'limitation of liability', 'governing law', 'dispute resolution'
                ]
            },
            'cookies': {
                'url_patterns': [
                    r'cookie[_-]?policy', r'cookie[_-]?notice', r'cookie[_-]?consent'
                ],
                'content_patterns': [
                    r'cookies.*website', r'essential.*cookies', r'analytics.*cookies',
                    r'advertising.*cookies', r'cookie.*consent', r'manage.*cookies'
                ],
                'keywords': [
                    'cookie policy', 'essential cookies', 'analytics cookies',
                    'advertising cookies', 'cookie consent', 'manage cookies'
                ]
            },
            'copyright': {
                'url_patterns': [
                    r'copyright', r'dmca', r'intellectual[_-]?property'
                ],
                'content_patterns': [
                    r'copyright.*notice', r'all.*rights.*reserved', r'dmca.*takedown',
                    r'intellectual.*property', r'trademark', r'license.*agreement'
                ],
                'keywords': [
                    'copyright notice', 'all rights reserved', 'dmca takedown',
                    'intellectual property', 'trademark', 'license agreement'
                ]
            },
            'legal': {
                'url_patterns': [
                    r'legal[_-]?notice', r'disclaimer', r'impressum', r'mentions[_-]?legales'
                ],
                'content_patterns': [
                    r'legal.*notice', r'disclaimer', r'limitation.*liability',
                    r'governing.*law', r'jurisdiction', r'dispute.*resolution'
                ],
                'keywords': [
                    'legal notice', 'disclaimer', 'limitation of liability',
                    'governing law', 'jurisdiction', 'dispute resolution'
                ]
            }
        }
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        for doc_type in self.legal_patterns:
            patterns = self.legal_patterns[doc_type]
            patterns['compiled_url'] = [re.compile(p, re.IGNORECASE) for p in patterns['url_patterns']]
            patterns['compiled_content'] = [re.compile(p, re.IGNORECASE) for p in patterns['content_patterns']]
    
    def analyze_legal_content(self, url: str, html_content: str, clean_text: str = None) -> Dict:
        """
        Sophisticated analysis to determine if content is truly legal
        Returns detailed classification and confidence
        """
        results = {
            'is_legal': False,
            'document_types': [],
            'confidence_scores': {},
            'total_confidence': 0.0,
            'detection_details': {},
            'analysis_method': 'sophisticated'
        }
        
        # Analyze for each document type
        for doc_type, patterns in self.legal_patterns.items():
            score = self._analyze_document_type(url, html_content, clean_text, doc_type, patterns)
            
            if score > 0.3:  # Threshold for considering this document type
                results['document_types'].append(doc_type)
                results['confidence_scores'][doc_type] = score
                results['detection_details'][doc_type] = self._get_detection_details(
                    url, html_content, clean_text, doc_type, patterns
                )
        
        # Calculate overall confidence
        if results['document_types']:
            results['is_legal'] = True
            results['total_confidence'] = max(results['confidence_scores'].values())
            results['primary_type'] = max(results['confidence_scores'], key=results['confidence_scores'].get)
        
        return results
    
    def _analyze_document_type(self, url: str, html_content: str, clean_text: str, 
                              doc_type: str, patterns: Dict) -> float:
        """Analyze specific document type with scoring"""
        score = 0.0
        
        # URL pattern matching (high weight)
        url_matches = sum(1 for pattern in patterns['compiled_url'] if pattern.search(url))
        score += url_matches * 0.4
        
        # Content pattern matching (medium weight)
        content_to_analyze = clean_text if clean_text else html_content[:5000]
        content_matches = sum(1 for pattern in patterns['compiled_content'] 
                             if pattern.search(content_to_analyze))
        score += content_matches * 0.2
        
        # Keyword matching (lower weight but broad coverage)
        content_lower = content_to_analyze.lower()
        keyword_matches = sum(1 for keyword in patterns['keywords'] 
                             if keyword in content_lower)
        score += keyword_matches * 0.1
        
        # Normalize score
        return min(score, 1.0)
    
    def _get_detection_details(self, url: str, html_content: str, clean_text: str,
                              doc_type: str, patterns: Dict) -> Dict:
        """Get detailed information about what was detected"""
        details = {
            'url_matches': [],
            'content_matches': [],
            'keyword_matches': []
        }
        
        # Find URL matches
        for pattern in patterns['compiled_url']:
            matches = pattern.findall(url)
            if matches:
                details['url_matches'].extend(matches)
        
        # Find content pattern matches
        content_to_analyze = clean_text if clean_text else html_content[:5000]
        for pattern in patterns['compiled_content']:
            matches = pattern.findall(content_to_analyze)
            if matches:
                details['content_matches'].extend(matches[:3])  # Limit to avoid too much data
        
        # Find keyword matches
        content_lower = content_to_analyze.lower()
        for keyword in patterns['keywords']:
            if keyword in content_lower:
                details['keyword_matches'].append(keyword)
        
        return details

class LegalDocumentDetector:
    """Combined detector that can work in different phases"""
    
    def __init__(self):
        self.lightning_detector = LightningFastDetector()
        self.sophisticated_detector = SophisticatedLegalDetector()
    
    def phase_one_detection(self, url: str, html_content: str) -> Dict:
        """Phase 1: Lightning fast detection"""
        return self.lightning_detector.is_legal_document(url, html_content)
    
    def phase_two_detection(self, url: str, html_content: str, clean_text: str = None) -> Dict:
        """Phase 2: Sophisticated legal content analysis"""
        return self.sophisticated_detector.analyze_legal_content(url, html_content, clean_text)
    
    # Legacy method for backward compatibility
    def is_legal_document(self, url: str, html_content: str) -> Dict:
        """Legacy method - uses phase 1 detection"""
        return self.phase_one_detection(url, html_content) 