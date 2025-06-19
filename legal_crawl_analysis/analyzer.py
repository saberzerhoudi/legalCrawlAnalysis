"""
3-Phase Legal Crawl Analyzer:
Phase 1: Lightning fast detection (high recall)
Phase 2: Sophisticated legal content detection (high precision) 
Phase 3: Passage extraction and storage (parquet format)
"""

import json
import gzip
import time
import logging
import signal
import shutil
import re
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple

# Try to import pandas, fall back gracefully if not available
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logging.warning("pandas not available. Install with: pip install pandas pyarrow")

from warcio.archiveiterator import ArchiveIterator
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders
import tldextract

from .models import LegalDocument, CopyrightClause, AccessLevel, PhaseOneStats, PhaseTwoStats
from .fetcher import CommonCrawlFetcher
from .detector import LegalDocumentDetector
from .extractor import HTMLContentExtractor
from .gpt_analyzer import GPTLegalAnalyzer

logger = logging.getLogger(__name__)

class ThreePhaseProgressTracker:
    """Track progress across the 3-phase analysis pipeline"""
    
    def __init__(self, progress_file: str):
        self.progress_file = progress_file
        self.progress_data = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load existing progress or create new structure"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
        
        return {
            'crawl_name': '',
            'start_time': '',
            'total_files_to_process': 0,
            'phase_1': {'completed': False, 'current_file_index': 0, 'stats': {}},
            'phase_2': {'completed': False, 'current_file_index': 0, 'stats': {}},
            'phase_3': {'completed': False, 'current_file_index': 0, 'stats': {}},
            'overall_stats': {
                'total_records_processed': 0,
                'legal_documents_found_phase1': 0,
                'legal_documents_filtered_phase2': 0,
                'passages_extracted_phase3': 0,
                'total_openai_tokens_used': 0
            }
        }
    
    def save_progress(self):
        """Save current progress to file"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def update_phase_1(self, file_index: int, warc_path: str, legal_docs_found: int, records_processed: int):
        """Update Phase 1 progress"""
        self.progress_data['phase_1']['current_file_index'] = file_index
        self.progress_data['phase_1']['stats'][warc_path] = {
            'legal_docs_found': legal_docs_found,
            'records_processed': records_processed,
            'timestamp': datetime.now().isoformat()
        }
        self.progress_data['overall_stats']['legal_documents_found_phase1'] += legal_docs_found
        self.progress_data['overall_stats']['total_records_processed'] += records_processed
        self.save_progress()
    
    def update_phase_2(self, file_index: int, warc_name: str, filtered_docs: int):
        """Update Phase 2 progress"""
        self.progress_data['phase_2']['current_file_index'] = file_index
        self.progress_data['phase_2']['stats'][warc_name] = {
            'filtered_docs': filtered_docs,
            'timestamp': datetime.now().isoformat()
        }
        self.progress_data['overall_stats']['legal_documents_filtered_phase2'] += filtered_docs
        self.save_progress()
    
    def update_phase_3(self, file_index: int, warc_name: str, extracted_passages: int, tokens_used: int):
        """Update Phase 3 progress"""
        self.progress_data['phase_3']['current_file_index'] = file_index
        self.progress_data['phase_3']['stats'][warc_name] = {
            'extracted_passages': extracted_passages,
            'tokens_used': tokens_used,
            'timestamp': datetime.now().isoformat()
        }
        self.progress_data['overall_stats']['passages_extracted_phase3'] += extracted_passages
        self.progress_data['overall_stats']['total_openai_tokens_used'] += tokens_used
        self.save_progress()
    
    def complete_phase(self, phase: int):
        """Mark a phase as completed"""
        self.progress_data[f'phase_{phase}']['completed'] = True
        self.save_progress()
    
    def get_phase_start_index(self, phase: int) -> int:
        """Get the starting index for resuming a phase"""
        return self.progress_data[f'phase_{phase}']['current_file_index']
    
    def reset(self):
        """Reset all progress"""
        self.progress_data = self._load_progress().__class__(self.progress_file)._load_progress()
        self.save_progress()

class ThreePhaseLegalAnalyzer:
    """Enhanced 3-phase legal document analyzer with WARC preservation"""
    
    def __init__(self, output_dir: str = "analysis_output", max_files: Optional[int] = 5, 
                 progress_file: str = "analysis_progress.json", keep_original_warcs: bool = False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_files = max_files
        self.keep_original_warcs = keep_original_warcs
        
        # Initialize components
        self.fetcher = CommonCrawlFetcher()
        self.detector = LegalDocumentDetector()
        self.extractor = HTMLContentExtractor()
        self.progress_tracker = ThreePhaseProgressTracker(progress_file)
        
        # Phase directories (will be set during analysis)
        self.crawl_dir = None
        self.phase1_dir = None
        self.phase2_dir = None
        self.phase3_dir = None
        
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info("Received interrupt signal. Saving progress...")
            self.progress_tracker.save_progress()
            logger.info("Progress saved. Exiting gracefully.")
            exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run_three_phase_analysis(self, openai_api_key: str, resume: bool = False) -> Dict:
        """
        Run complete 3-phase analysis with WARC preservation:
        Phase 1: Lightning fast detection → Save WARC records
        Phase 2: Sophisticated legal filtering → Move/delete WARC + create metadata parquet  
        Phase 3: Passage extraction → Copy WARC + metadata + create GPT analysis parquet
        """
        logger.info("Starting 3-phase legal document analysis with WARC preservation")
        
        # Get crawl information
        crawl_info = self.fetcher.get_latest_crawl_info()
        crawl_name = crawl_info['name']
        
        # Setup crawl-specific directories
        self.crawl_dir = self.output_dir / crawl_name
        self.crawl_dir.mkdir(exist_ok=True)
        
        self.phase1_dir = self.crawl_dir / "phase1_fast_detection"
        self.phase2_dir = self.crawl_dir / "phase2_sophisticated_filtering"
        self.phase3_dir = self.crawl_dir / "phase3_passages_and_warc"
        
        for dir_path in [self.phase1_dir, self.phase2_dir, self.phase3_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Store crawl info
        self.progress_tracker.progress_data['crawl_name'] = crawl_name
        
        # Determine files to process
        all_warc_paths = crawl_info['warc_paths']
        if self.max_files is None:
            warc_paths = all_warc_paths
        else:
            warc_paths = all_warc_paths[:self.max_files]
        
        self.progress_tracker.progress_data['total_files_to_process'] = len(warc_paths)
        if not self.progress_tracker.progress_data['start_time']:
            self.progress_tracker.progress_data['start_time'] = datetime.now().isoformat()
        
        overall_start_time = time.time()
        
        try:
            # Phase 1: Lightning Fast Detection → Save WARC records
            if not self.progress_tracker.progress_data['phase_1']['completed']:
                logger.info("=== PHASE 1: Lightning Fast Detection + WARC Storage ===")
                self._run_phase_1(warc_paths, resume)
                self.progress_tracker.complete_phase(1)
            else:
                logger.info("Phase 1 already completed, skipping")
            
            # Phase 2: Sophisticated Legal Filtering → Move/delete WARC + create metadata parquet
            if not self.progress_tracker.progress_data['phase_2']['completed']:
                logger.info("=== PHASE 2: Sophisticated Filtering + WARC Management ===")
                self._run_phase_2(resume)
                self.progress_tracker.complete_phase(2)
            else:
                logger.info("Phase 2 already completed, skipping")
            
            # Phase 3: Passage Extraction → Copy WARC + metadata + create GPT analysis parquet
            if not self.progress_tracker.progress_data['phase_3']['completed']:
                logger.info("=== PHASE 3: Passage Extraction + Final WARC Storage ===")
                self.gpt_analyzer = GPTLegalAnalyzer(openai_api_key)
                self._run_phase_3(resume)
                self.progress_tracker.complete_phase(3)
            else:
                logger.info("Phase 3 already completed, skipping")
            
            total_time = time.time() - overall_start_time
            final_report = self._generate_final_report(total_time)
            
            return final_report
            
        except Exception as e:
            logger.error(f"Error in 3-phase analysis: {e}")
            self.progress_tracker.save_progress()
            raise
    
    def _run_phase_1(self, warc_paths: List[str], resume: bool):
        """Phase 1: Lightning fast detection and WARC record storage"""
        start_index = 0
        if resume:
            start_index = self.progress_tracker.get_phase_start_index(1)
            logger.info(f"Resuming Phase 1 from file index {start_index}")
        
        logger.info(f"Phase 1: Processing {len(warc_paths)} WARC files with lightning fast detection")
        
        for i in range(start_index, len(warc_paths)):
            warc_path = warc_paths[i]
            logger.info(f"Phase 1: Processing {i+1}/{len(warc_paths)}: {warc_path}")
            
            try:
                # Download WARC file
                warc_file = self.fetcher.download_warc_file(warc_path)
                if not warc_file:
                    logger.error(f"Failed to download WARC file: {warc_path}")
                    continue
                
                # Process WARC file and save legal document records
                legal_docs_found, records_processed = self._process_warc_phase_1(warc_file, warc_path)
                
                # Update progress
                self.progress_tracker.update_phase_1(i, warc_path, legal_docs_found, records_processed)
                
                logger.info(f"Phase 1 completed for {warc_file.name}: {legal_docs_found} legal document WARC records saved from {records_processed} records")
                
            except Exception as e:
                logger.error(f"Error in Phase 1 processing {warc_path}: {e}")
            
            finally:
                # Keep the original WARC file - NEVER DELETE
                if warc_file and warc_file.exists():
                    logger.info(f"Preserved original WARC file: {warc_file}")
    
    def _process_warc_phase_1(self, warc_file: Path, warc_path: str) -> Tuple[int, int]:
        """Process single WARC file in Phase 1 - extract and save legal document WARC records"""
        legal_docs_found = 0
        records_processed = 0
        
        # Create output WARC file for legal documents
        output_warc_file = self.phase1_dir / f"{warc_file.stem}_legal_docs.warc.gz"
        
        try:
            # First pass: identify legal documents
            legal_urls = set()
            
            with gzip.open(warc_file, 'rb') as input_f:
                for record in ArchiveIterator(input_f):
                    if record.rec_type == 'response':
                        records_processed += 1
                        
                        if records_processed % 5000 == 0:
                            logger.info(f"Phase 1: Processed {records_processed} records, found {legal_docs_found} potential legal documents")
                        
                        # Extract URL and content for detection
                        url = record.rec_headers.get_header('WARC-Target-URI')
                        if not url:
                            continue
                        
                        content = record.content_stream().read()
                        if not content:
                            continue
                        
                        try:
                            html_content = content.decode('utf-8', errors='ignore')
                        except:
                            continue
                        
                        # Lightning fast detection
                        detection_result = self.detector.phase_one_detection(url, html_content)
                        
                        if detection_result['is_legal']:
                            legal_urls.add(url)
                            legal_docs_found += 1
            
            # Second pass: copy the legal records if any were found
            if legal_urls:
                urls_to_copy = legal_urls.copy()  # Make a copy to track what we still need
                
                with gzip.open(warc_file, 'rb') as input_f:
                    with open(output_warc_file, 'wb') as output_f:
                        writer = WARCWriter(output_f, gzip=True)
                        
                        for record in ArchiveIterator(input_f):
                            if record.rec_type == 'response':
                                url = record.rec_headers.get_header('WARC-Target-URI')
                                if url in urls_to_copy:
                                    # Copy the original record directly - this preserves all structure
                                    writer.write_record(record)
                                    urls_to_copy.remove(url)  # Remove to avoid duplicates
                                    
                                    # Stop when we've copied all legal records
                                    if not urls_to_copy:
                                        break
                
                logger.info(f"Successfully wrote {len(legal_urls)} legal document records to {output_warc_file}")
            else:
                logger.info("No legal documents found to write")
        
        except Exception as e:
            logger.error(f"Error processing WARC file {warc_file} in Phase 1: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Remove empty output file
        if legal_docs_found == 0 and output_warc_file.exists():
            output_warc_file.unlink()
            logger.debug(f"Removed empty WARC file: {output_warc_file}")
        
        return legal_docs_found, records_processed
    
    def _run_phase_2(self, resume: bool):
        """Phase 2: Sophisticated legal filtering with WARC management and metadata creation"""
        # Get all Phase 1 WARC files
        phase1_warc_files = list(self.phase1_dir.glob("*_legal_docs.warc.gz"))
        logger.info(f"Phase 2: Processing {len(phase1_warc_files)} Phase 1 WARC files")
        
        start_index = 0
        if resume:
            start_index = self.progress_tracker.get_phase_start_index(2)
            logger.info(f"Resuming Phase 2 from file index {start_index}")
        
        for i in range(start_index, len(phase1_warc_files)):
            phase1_warc_file = phase1_warc_files[i]
            logger.info(f"Phase 2: Processing {i+1}/{len(phase1_warc_files)}: {phase1_warc_file.name}")
            
            try:
                filtered_docs = self._process_phase2_warc_filtering(phase1_warc_file)
                
                # Update progress
                warc_name = phase1_warc_file.stem.replace('_legal_docs', '')
                self.progress_tracker.update_phase_2(i, warc_name, len(filtered_docs))
                
                logger.info(f"Phase 2 completed for {phase1_warc_file.name}: {len(filtered_docs)} documents passed sophisticated filtering")
                
            except Exception as e:
                logger.error(f"Error in Phase 2 processing {phase1_warc_file}: {e}")
    
    def _process_phase2_warc_filtering(self, phase1_warc_file: Path) -> List[Dict]:
        """Process Phase 1 WARC file with sophisticated legal detection"""
        filtered_documents = []
        documents_to_keep = []  # Store actual WARC records to keep
        
        try:
            # First pass: analyze all records and decide which to keep
            with gzip.open(phase1_warc_file, 'rb') as f:
                for record in ArchiveIterator(f):
                    if record.rec_type == 'response':
                        # Extract URL and content
                        url = record.rec_headers.get_header('WARC-Target-URI')
                        if not url:
                            continue
                        
                        content = record.content_stream().read()
                        if not content:
                            continue
                        
                        try:
                            html_content = content.decode('utf-8', errors='ignore')
                        except:
                            continue
                        
                        # Extract clean text for sophisticated analysis
                        clean_text = self.extractor.extract_clean_text(html_content)
                        
                        if not clean_text or len(clean_text) < 30:
                            continue
                        
                        # Sophisticated legal detection
                        sophisticated_result = self.detector.phase_two_detection(url, html_content, clean_text)
                        
                        if sophisticated_result['is_legal'] and sophisticated_result['total_confidence'] > 0.3:
                            # Prepare metadata
                            doc_metadata = {
                                'url': url,
                                'domain': tldextract.extract(url).domain,
                                'warc_path': phase1_warc_file.name,
                                'confidence_score': sophisticated_result['total_confidence'],
                                'detection_method': 'sophisticated_analysis',
                                'document_types': json.dumps(sophisticated_result['document_types']),
                                'timestamp': datetime.now().isoformat(),
                                'html_content_length': len(html_content),
                                'clean_text_length': len(clean_text),
                                'phase2_analysis': json.dumps(sophisticated_result)
                            }
                            
                            filtered_documents.append(doc_metadata)
                            documents_to_keep.append(record)
            
            # If we have documents that passed filtering
            if filtered_documents:
                # Move WARC file to Phase 2 directory
                phase2_warc_file = self.phase2_dir / phase1_warc_file.name
                shutil.move(str(phase1_warc_file), str(phase2_warc_file))
                
                # Create metadata parquet file
                if HAS_PANDAS:
                    metadata_df = pd.DataFrame(filtered_documents)
                    metadata_parquet = self.phase2_dir / f"{phase1_warc_file.stem}_metadata.parquet"
                    metadata_df.to_parquet(metadata_parquet, index=False)
                    logger.debug(f"Saved metadata parquet: {metadata_parquet}")
                
                # Also save JSON for debugging
                metadata_json = self.phase2_dir / f"{phase1_warc_file.stem}_metadata.json"
                with open(metadata_json, 'w', encoding='utf-8') as f:
                    json.dump(filtered_documents, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Moved WARC to Phase 2 and created metadata for {len(filtered_documents)} documents")
            else:
                # Delete WARC file if no documents passed filtering
                phase1_warc_file.unlink()
                logger.info(f"Deleted WARC file - no documents passed sophisticated filtering")
        
        except Exception as e:
            logger.error(f"Error processing Phase 2 WARC file {phase1_warc_file}: {e}")
            # Clean up on error
            if phase1_warc_file.exists():
                phase1_warc_file.unlink()
        
        return filtered_documents
    
    def _run_phase_3(self, resume: bool):
        """Phase 3: Passage extraction with WARC and metadata preservation"""
        # Get all Phase 2 WARC files
        phase2_warc_files = list(self.phase2_dir.glob("*_legal_docs.warc.gz"))
        logger.info(f"Phase 3: Processing {len(phase2_warc_files)} Phase 2 WARC files")
        
        start_index = 0
        if resume:
            start_index = self.progress_tracker.get_phase_start_index(3)
            logger.info(f"Resuming Phase 3 from file index {start_index}")
        
        for i in range(start_index, len(phase2_warc_files)):
            phase2_warc_file = phase2_warc_files[i]
            logger.info(f"Phase 3: Processing {i+1}/{len(phase2_warc_files)}: {phase2_warc_file.name}")
            
            try:
                extracted_passages, tokens_used = self._process_phase3_gpt_analysis(phase2_warc_file)
                
                # Update progress
                warc_name = phase2_warc_file.stem.replace('_legal_docs', '')
                self.progress_tracker.update_phase_3(i, warc_name, len(extracted_passages), tokens_used)
                
                logger.info(f"Phase 3 completed for {phase2_warc_file.name}: {len(extracted_passages)} passages extracted")
                
            except Exception as e:
                logger.error(f"Error in Phase 3 processing {phase2_warc_file}: {e}")
    
    def _process_phase3_gpt_analysis(self, phase2_warc_file: Path) -> Tuple[List[Dict], int]:
        """Process Phase 2 WARC file with GPT analysis and create final storage"""
        extracted_passages = []
        total_tokens_used = 0
        
        # Create incremental output files
        gpt_parquet = self.phase3_dir / f"{phase2_warc_file.stem}_gpt_analysis.parquet"
        gpt_json = self.phase3_dir / f"{phase2_warc_file.stem}_gpt_analysis.json"
        
        try:
            # Move WARC file to Phase 3 directory (not copy)
            phase3_warc_file = self.phase3_dir / phase2_warc_file.name
            shutil.move(str(phase2_warc_file), str(phase3_warc_file))
            
            # Move metadata parquet file to Phase 3 directory (not copy)
            metadata_parquet = self.phase2_dir / f"{phase2_warc_file.stem}_metadata.parquet"
            if metadata_parquet.exists():
                phase3_metadata_parquet = self.phase3_dir / f"{phase2_warc_file.stem}_metadata.parquet"
                shutil.move(str(metadata_parquet), str(phase3_metadata_parquet))
            
            # Also move the JSON metadata file if it exists
            metadata_json = self.phase2_dir / f"{phase2_warc_file.stem}_metadata.json"
            if metadata_json.exists():
                phase3_metadata_json = self.phase3_dir / f"{phase2_warc_file.stem}_metadata.json"
                shutil.move(str(metadata_json), str(phase3_metadata_json))
            
            # Process WARC file for GPT analysis (now reading from phase3 location)
            document_count = 0
            
            with gzip.open(phase3_warc_file, 'rb') as f:
                for record in ArchiveIterator(f):
                    if record.rec_type == 'response':
                        # Extract URL and content
                        url = record.rec_headers.get_header('WARC-Target-URI')
                        if not url:
                            continue
                        
                        content = record.content_stream().read()
                        if not content:
                            continue
                        
                        try:
                            html_content = content.decode('utf-8', errors='ignore')
                        except:
                            continue
                        
                        # Extract clean text
                        clean_text = self.extractor.extract_clean_text(html_content)
                        if not clean_text or len(clean_text) < 200:
                            continue
                        
                        document_count += 1
                        logger.info(f"Phase 3: Processing document {document_count} - {url}")
                        
                        # Track tokens used for THIS document only
                        previous_token_count = self.gpt_analyzer.total_tokens_used
                        gpt_result = self.gpt_analyzer.analyze_document(clean_text, url)
                        tokens_for_this_doc = self.gpt_analyzer.total_tokens_used - previous_token_count
                        total_tokens_used += tokens_for_this_doc
                        
                        # Prepare GPT analysis data
                        passage_data = {
                            'url': url,
                            'domain': tldextract.extract(url).domain,
                            'warc_file': phase3_warc_file.name,
                            'gpt_analysis': json.dumps(gpt_result),
                            'clean_text_length': len(clean_text),
                            'copyright_clauses_count': len(gpt_result.get('copyright_clauses', [])),
                            'access_level': gpt_result.get('access_level', {}).get('level', 'unknown'),
                            'technical_protection_measures_count': len(gpt_result.get('technical_protection_measures', [])),
                            'liability_clauses_count': len(gpt_result.get('liability_clauses', [])),
                            'jurisdiction_clauses_count': len(gpt_result.get('jurisdiction_clauses', [])),
                            'data_licensing_count': len(gpt_result.get('data_licensing', [])),
                            'extraction_timestamp': datetime.now().isoformat(),
                            'tokens_used': tokens_for_this_doc
                        }
                        
                        extracted_passages.append(passage_data)
                        
                        # SAVE AFTER EACH DOCUMENT - This is the key improvement
                        self._save_incremental_gpt_results(extracted_passages, gpt_parquet, gpt_json)
                        
                        logger.info(f"Saved GPT analysis for {url} - {len(gpt_result.get('copyright_clauses', []))} copyright clauses found")
            
            logger.info(f"Phase 3 completed: WARC + metadata moved, {len(extracted_passages)} GPT analyses saved")
            
        except Exception as e:
            logger.error(f"Error in Phase 3 processing {phase2_warc_file}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return extracted_passages, total_tokens_used

    def _save_incremental_gpt_results(self, extracted_passages: List[Dict], gpt_parquet: Path, gpt_json: Path):
        """Save GPT analysis results incrementally after each document"""
        try:
            # Save as parquet (overwrites previous version)
            if extracted_passages and HAS_PANDAS:
                gpt_analysis_df = pd.DataFrame(extracted_passages)
                gpt_analysis_df.to_parquet(gpt_parquet, index=False)
            
            # Save as JSON (overwrites previous version)
            if extracted_passages:
                with open(gpt_json, 'w', encoding='utf-8') as f:
                    json.dump(extracted_passages, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Incrementally saved {len(extracted_passages)} GPT analyses")
            
        except Exception as e:
            logger.error(f"Error saving incremental GPT results: {e}")
    
    def _generate_final_report(self, total_time: float) -> Dict:
        """Generate comprehensive 3-phase analysis report"""
        try:
            progress = self.progress_tracker.progress_data
            
            final_report = {
                'crawl_info': {
                    'crawl_name': progress['crawl_name'],
                    'total_processing_time_seconds': total_time,
                    'files_planned': progress['total_files_to_process']
                },
                'phase_1_lightning_detection': {
                    'records_processed': progress['overall_stats']['total_records_processed'],
                    'legal_documents_found': progress['overall_stats']['legal_documents_found_phase1'],
                    'detection_rate': (progress['overall_stats']['legal_documents_found_phase1'] / 
                                     max(progress['overall_stats']['total_records_processed'], 1)) * 100,
                    'warc_files_created': len(list(self.phase1_dir.glob("*.warc.gz")))
                },
                'phase_2_sophisticated_filtering': {
                    'input_documents': progress['overall_stats']['legal_documents_found_phase1'],
                    'filtered_documents': progress['overall_stats']['legal_documents_filtered_phase2'],
                    'filter_rate': (progress['overall_stats']['legal_documents_filtered_phase2'] / 
                                  max(progress['overall_stats']['legal_documents_found_phase1'], 1)) * 100,
                    'warc_files_kept': len(list(self.phase2_dir.glob("*.warc.gz"))),
                    'metadata_parquet_files': len(list(self.phase2_dir.glob("*_metadata.parquet")))
                },
                'phase_3_passage_extraction': {
                    'input_documents': progress['overall_stats']['legal_documents_filtered_phase2'],
                    'extracted_passages': progress['overall_stats']['passages_extracted_phase3'],
                    'openai_tokens_used': progress['overall_stats']['total_openai_tokens_used'],
                    'estimated_cost_usd': progress['overall_stats']['total_openai_tokens_used'] * 0.00003,  # GPT-4o pricing
                    'final_warc_files': len(list(self.phase3_dir.glob("*.warc.gz"))),
                    'final_metadata_files': len(list(self.phase3_dir.glob("*_metadata.parquet"))),
                    'gpt_analysis_files': len(list(self.phase3_dir.glob("*_gpt_analysis.parquet")))
                },
                'output_files': {
                    'phase1_warc_files': [str(f) for f in self.phase1_dir.glob("*.warc.gz")],
                    'phase2_warc_files': [str(f) for f in self.phase2_dir.glob("*.warc.gz")],
                    'phase2_metadata_files': [str(f) for f in self.phase2_dir.glob("*_metadata.parquet")],
                    'phase3_warc_files': [str(f) for f in self.phase3_dir.glob("*.warc.gz")],
                    'phase3_metadata_files': [str(f) for f in self.phase3_dir.glob("*_metadata.parquet")],
                    'phase3_gpt_files': [str(f) for f in self.phase3_dir.glob("*_gpt_analysis.parquet")]
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Save final report
            report_path = self.crawl_dir / "final_3phase_report.json"
            with open(report_path, 'w') as f:
                json.dump(final_report, f, indent=2)
            
            # Create markdown report
            self._create_3phase_markdown_report(final_report)
            
            logger.info(f"3-Phase analysis report generated: {report_path}")
            return final_report
            
        except Exception as e:
            logger.error(f"Error generating final report: {e}")
            return {}
    
    def _create_3phase_markdown_report(self, report_data: Dict):
        """Create markdown report for 3-phase analysis"""
        try:
            report_path = self.crawl_dir / "final_3phase_report.md"
            
            with open(report_path, 'w') as f:
                f.write("# 3-Phase Legal Crawl Analysis Report\n\n")
                f.write(f"**Generated:** {report_data['timestamp']}\n")
                f.write(f"**Crawl:** {report_data['crawl_info']['crawl_name']}\n")
                f.write(f"**Total Processing Time:** {report_data['crawl_info']['total_processing_time_seconds']:.2f} seconds\n\n")
                
                # Phase 1 results
                p1 = report_data['phase_1_lightning_detection']
                f.write("## Phase 1: Lightning Fast Detection\n")
                f.write(f"- **Records Processed:** {p1['records_processed']:,}\n")
                f.write(f"- **Legal Documents Found:** {p1['legal_documents_found']:,}\n")
                f.write(f"- **Detection Rate:** {p1['detection_rate']:.4f}%\n")
                f.write(f"- **WARC Files Created:** {p1['warc_files_created']}\n\n")
                
                # Phase 2 results
                p2 = report_data['phase_2_sophisticated_filtering']
                f.write("## Phase 2: Sophisticated Filtering\n")
                f.write(f"- **Input Documents:** {p2['input_documents']:,}\n")
                f.write(f"- **Filtered Documents:** {p2['filtered_documents']:,}\n")
                f.write(f"- **Filter Success Rate:** {p2['filter_rate']:.2f}%\n")
                f.write(f"- **WARC Files Kept:** {p2['warc_files_kept']}\n")
                f.write(f"- **Metadata Parquet Files:** {p2['metadata_parquet_files']}\n\n")
                
                # Phase 3 results
                p3 = report_data['phase_3_passage_extraction']
                f.write("## Phase 3: Passage Extraction\n")
                f.write(f"- **Input Documents:** {p3['input_documents']:,}\n")
                f.write(f"- **Extracted Passages:** {p3['extracted_passages']:,}\n")
                f.write(f"- **OpenAI Tokens Used:** {p3['openai_tokens_used']:,}\n")
                f.write(f"- **Estimated Cost:** ${p3['estimated_cost_usd']:.2f}\n")
                f.write(f"- **Final WARC Files:** {p3['final_warc_files']}\n")
                f.write(f"- **Final Metadata Files:** {p3['final_metadata_files']}\n")
                f.write(f"- **GPT Analysis Files:** {p3['gpt_analysis_files']}\n\n")
                
                f.write("## Output Files Structure\n")
                f.write("```\n")
                f.write(f"{report_data['crawl_info']['crawl_name']}/\n")
                f.write("├── phase1_fast_detection/          # WARC files with potential legal docs\n")
                f.write("├── phase2_sophisticated_filtering/  # Filtered WARC files + metadata parquet\n")
                f.write("├── phase3_passages_and_warc/       # Final WARC files + metadata + GPT analysis parquet\n")
                f.write("├── final_3phase_report.json\n")
                f.write("└── final_3phase_report.md\n")
                f.write("```\n")
            
            logger.info(f"3-Phase markdown report created: {report_path}")
            
        except Exception as e:
            logger.error(f"Error creating markdown report: {e}")
    
    def reset_progress(self):
        """Reset analysis progress and clean up directories"""
        self.progress_tracker.reset()
        
        # Clean up phase directories if they exist
        for phase_dir in [self.phase1_dir, self.phase2_dir, self.phase3_dir]:
            if phase_dir and phase_dir.exists():
                shutil.rmtree(phase_dir)
                phase_dir.mkdir(exist_ok=True)
        
        logger.info("Progress reset and directories cleaned")

# Backward compatibility
LegalCrawlAnalyzer = ThreePhaseLegalAnalyzer 