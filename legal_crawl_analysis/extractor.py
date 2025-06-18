"""
HTML content extractor with text cleaning capabilities
"""

import re
import logging
import warnings
from typing import Optional
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

# Try to import readability, fall back gracefully if not available
try:
    from readability import Document
    HAS_READABILITY = True
    # Suppress the readability library's verbose logging
    readability_logger = logging.getLogger('readability.readability')
    readability_logger.setLevel(logging.WARNING)
except ImportError:
    HAS_READABILITY = False
    logging.warning("readability-lxml not available. Install with: pip install readability-lxml")

# Ignore XML parsing warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

logger = logging.getLogger(__name__)

class HTMLContentExtractor:
    """Extracts and cleans HTML content from web pages"""
    
    def __init__(self):
        self.has_readability = HAS_READABILITY
        if not self.has_readability:
            logger.warning("readability-lxml not available. Using fallback text extraction.")
        
    def extract_clean_text(self, html_content: str) -> Optional[str]:
        """
        Extract clean text from HTML content using multiple methods
        Returns the cleanest extracted text with fallback methods
        """
        if not html_content or len(html_content.strip()) < 50:
            return None
            
        # Try multiple extraction methods, return the best result
        extraction_methods = []
        
        # Method 1: Use readability to extract main content (if available)
        if self.has_readability:
            try:
                doc = Document(html_content)
                main_content = doc.summary()
                if main_content:
                    clean_text = self._clean_html_text(main_content)
                    if clean_text and len(clean_text) > 50:
                        extraction_methods.append(('readability', clean_text))
            except Exception as e:
                logger.debug(f"Readability extraction failed: {e}")
        
        # Method 2: BeautifulSoup with improved parsing
        try:
            # Try XML parser first for XML documents
            if html_content.strip().startswith('<?xml'):
                soup = BeautifulSoup(html_content, 'xml')
            else:
                soup = BeautifulSoup(html_content, 'lxml')
        except Exception:
            # Fallback to html.parser
            soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        clean_text = self._clean_extracted_text(text)
        if clean_text and len(clean_text) > 30:
            extraction_methods.append(('beautifulsoup', clean_text))
        
        # Method 3: Simple HTML tag removal (fallback)
        try:
            simple_text = re.sub(r'<[^>]+>', '', html_content)
            simple_clean = self._clean_extracted_text(simple_text)
            if simple_clean and len(simple_clean) > 30:
                extraction_methods.append(('simple', simple_clean))
        except Exception:
            pass
        
        # Return the longest/best extraction
        if extraction_methods:
            # Prefer readability, then longest text
            readability_result = next((text for method, text in extraction_methods if method == 'readability'), None)
            if readability_result:
                return readability_result
            
            # Otherwise return the longest text
            return max(extraction_methods, key=lambda x: len(x[1]))[1]
        
        return None
    
    def _clean_html_text(self, html_content: str) -> str:
        """Clean HTML content to plain text"""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
                element.decompose()
            
            text = soup.get_text()
            return self._clean_extracted_text(text)
            
        except Exception:
            # Fallback: simple HTML tag removal
            text = re.sub(r'<[^>]+>', '', html_content)
            return self._clean_extracted_text(text)
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace and formatting"""
        if not text:
            return ""
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # For legal documents, be more permissive - don't filter out short lines
        # as they might contain important legal terms
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Keep lines that are longer than 5 chars or contain legal keywords
            if len(line) > 5 or any(keyword in line.lower() for keyword in 
                                   ['copyright', 'terms', 'privacy', 'policy', 'agreement', 'license', 
                                    'disclaimer', 'legal', 'gdpr', 'ccpa', 'cookie']):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines) 