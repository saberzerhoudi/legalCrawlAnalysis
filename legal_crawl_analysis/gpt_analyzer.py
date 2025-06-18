"""
GPT-4o analyzer for legal documents
"""

import json
import logging
from typing import Dict
import openai

logger = logging.getLogger(__name__)

class GPTLegalAnalyzer:
    """Uses GPT-4o to analyze legal documents for specific clauses"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.total_tokens_used = 0
        self.api_calls = 0
        
    def analyze_document(self, clean_text: str, url: str) -> Dict:
        """
        Analyze legal document using GPT-4o
        Returns detailed analysis of copyright clauses, access levels, etc.
        """
        try:
            self.api_calls += 1
            
            system_prompt = self._get_system_prompt()
            user_prompt = self._get_user_prompt(clean_text, url)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            self.total_tokens_used += response.usage.total_tokens
            
            # Get response content
            response_content = response.choices[0].message.content.strip()
            
            # Check if response is empty
            if not response_content:
                logger.warning(f"Empty response from GPT for URL: {url}")
                return self._get_empty_analysis()
            
            # Try to parse JSON, handle malformed responses
            try:
                # Remove any markdown code blocks if present
                if response_content.startswith("```json"):
                    response_content = response_content.replace("```json", "").replace("```", "").strip()
                elif response_content.startswith("```"):
                    response_content = response_content.replace("```", "").strip()
                
                analysis = json.loads(response_content)
                return analysis
                
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON parsing error for URL {url}: {json_err}")
                logger.error(f"Raw response: {response_content[:200]}...")
                return self._get_empty_analysis()
            
        except Exception as e:
            logger.error(f"Error in GPT analysis for URL {url}: {e}")
            return self._get_empty_analysis()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for GPT analysis"""
        return """You are a legal AI assistant specialized in analyzing web legal documents (privacy policies, terms of service, etc.) for specific copyright and access control clauses.

Your task is to identify and classify specific types of legal clauses in the provided text. 

IMPORTANT: Return ONLY a valid JSON object with no additional text, formatting, or explanations.

JSON Structure:
{
    "copyright_clauses": [
        {
            "text": "exact quote from document",
            "category": "one of the categories below",
            "confidence": 0.8,
            "context": "surrounding context"
        }
    ],
    "access_level": {
        "level": "L0_OPEN_ACCESS",
        "indicators": ["list of specific indicators found"],
        "confidence": 0.8
    },
    "technical_protection_measures": ["list of TPM mentions"],
    "liability_clauses": ["list of liability/indemnification clauses"],
    "jurisdiction_clauses": ["list of jurisdiction/governing law clauses"],
    "data_licensing": ["list of specific data licensing terms"]
}

COPYRIGHT CATEGORIES:
- COPYRIGHT_RETAINED_SITE: Website/service provider retains copyright
- COPYRIGHT_RETAINED_USER: User retains copyright over submitted content
- COPYRIGHT_LICENSED_TO_SITE: User grants specific license to site
- COPYRIGHT_WAIVED: Copyright is waived (public domain)
- HARD_NEGATIVE_DMCA: DMCA/copyright infringement procedures
- HARD_NEGATIVE_THIRD_PARTY: Third-party content/links copyright
- HARD_NEGATIVE_LICENSE_GRANT: User grants license (not full retention)
- EASY_NEGATIVE_IRRELEVANT: Clearly not about copyright
- AMBIGUOUS_COPYRIGHT: Unclear copyright clauses

ACCESS LEVELS:
- L0_OPEN_ACCESS: Standard HTML, simple GET request
- L1_ROBOTS_DISALLOW: robots.txt restrictions
- L2_DYNAMIC_CONTENT: Requires JavaScript rendering
- L3_ACCESS_CONTROL_SIMPLE: Login required, no anti-bot
- L4_ACCESS_CONTROL_CAPTCHA: CAPTCHA protected
- L5_ANTI_BOT_SERVICE: Advanced anti-bot (Cloudflare, etc.)
- L6_PAYWALL: Behind paywall
- L7_BLOCKED: Geo-blocked or unavailable

Return only the JSON object, no other text."""

    def _get_user_prompt(self, text: str, url: str) -> str:
        """Get the user prompt with document text"""
        # Truncate text if too long (keep first 4000 chars for context)
        if len(text) > 4000:
            text = text[:4000] + "... [truncated]"
        
        return f"""Analyze this legal document from URL: {url}

Document text:
{text}

Return only valid JSON following the specified format."""

    def _get_empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            "copyright_clauses": [],
            "access_level": {
                "level": "L0_OPEN_ACCESS",
                "indicators": [],
                "confidence": 0.0
            },
            "technical_protection_measures": [],
            "liability_clauses": [],
            "jurisdiction_clauses": [],
            "data_licensing": []
        } 