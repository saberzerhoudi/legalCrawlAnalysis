"""
CommonCrawl WARC file fetcher
"""

import re
import gzip
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CommonCrawlFetcher:
    """Handles fetching CommonCrawl WARC files"""
    
    BASE_URL = "https://data.commoncrawl.org"
    
    def __init__(self, output_dir: str = "warc_files"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def get_latest_crawl_info(self) -> Dict:
        """Get information about the latest CommonCrawl dump"""
        try:
            # Use the latest crawl info endpoint
            latest_url = f"{self.BASE_URL}/crawl-data/CC-MAIN-2025-08/warc.paths.gz"
            response = requests.get(latest_url, stream=True)
            response.raise_for_status()
            
            logger.info(f"Fetching WARC paths from: {latest_url}")
            
            # Decompress and read the paths
            warc_paths = []
            with gzip.GzipFile(fileobj=response.raw) as gz_file:
                for line_num, line in enumerate(gz_file):
                    if line_num >= 90000:  # Limit to avoid too many files
                        break
                    path = line.decode('utf-8').strip()
                    if path:
                        warc_paths.append(path)
            
            return {
                'name': 'CC-MAIN-2025-08',
                'warc_paths': warc_paths
            }
            
        except Exception as e:
            logger.error(f"Error fetching crawl info: {e}")
            # Fallback to a smaller test set
            return {
                'name': 'CC-MAIN-2024-10',
                'warc_paths': [
                    'crawl-data/CC-MAIN-2024-10/segments/1729219734615.31/warc/CC-MAIN-20241018172648-20241018202648-00000.warc.gz'
                ]
            }
    
    def download_warc_file(self, warc_path: str) -> Optional[Path]:
        """
        Download a WARC file if it doesn't already exist
        Returns the path to the downloaded file or None if failed
        """
        # Extract filename from path
        filename = Path(warc_path).name
        local_path = self.output_dir / filename
        
        # Check if file already exists
        if local_path.exists():
            file_size_mb = local_path.stat().st_size / (1024 * 1024)
            logger.info(f"WARC file already exists: {local_path} ({file_size_mb:.2f} MB)")
            return local_path
        
        try:
            url = f"{self.BASE_URL}/{warc_path}"
            logger.info(f"Downloading WARC file: {url}")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Download with progress
            total_size = 0
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            file_size_mb = total_size / (1024 * 1024)
            logger.info(f"Downloaded and preserved: {local_path} ({file_size_mb:.2f} MB)")
            return local_path
            
        except Exception as e:
            logger.error(f"Error downloading WARC file {warc_path}: {e}")
            # Clean up partial download
            if local_path.exists():
                local_path.unlink()
            return None
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in MB"""
        if file_path.exists():
            return file_path.stat().st_size / (1024 * 1024)
        return 0.0 