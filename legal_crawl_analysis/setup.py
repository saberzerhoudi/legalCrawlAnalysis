"""
Setup script for Legal Crawl Analyzer with Poetry
"""

import os
import sys
from pathlib import Path

def setup_directories():
    """Create necessary directories"""
    directories = [
        "warc_files",
        "analysis_output", 
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_openai_api_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OpenAI API key not found in environment variables")
        print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    else:
        print("✓ OpenAI API key found")
        return True

def main():
    """Main setup function"""
    print("Setting up Legal Crawl Analyzer environment...\n")
    
    print("1. Creating directories...")
    setup_directories()
    
    print("\n2. Checking OpenAI API key...")
    api_key_ok = check_openai_api_key()
    
    print("\n" + "="*50)
    if api_key_ok:
        print("✅ Setup completed successfully!")
        print("\nYou can now run the analyzer:")
        print("poetry run legal-crawl-analyzer")
        print("# or")
        print("poetry run python -m legal_crawl_analysis.main")
    else:
        print("❌ Setup incomplete. Please set your OpenAI API key.")
        print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)

if __name__ == "__main__":
    main() 