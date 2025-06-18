"""
Main entry point for 3-Phase Legal Crawl Analysis
"""

import argparse
import logging
import sys
from pathlib import Path

from .analyzer import ThreePhaseLegalAnalyzer
from .config import OPENAI_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('legal_crawl_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the 3-phase legal document analysis"""
    parser = argparse.ArgumentParser(description="3-Phase Legal Document Analysis for CommonCrawl Data")
    parser.add_argument("--openai-api-key", help="OpenAI API key (can also be set via OPENAI_API_KEY env var)")
    parser.add_argument("--output-dir", default="analysis_output", help="Output directory")
    
    # Analysis control arguments
    parser.add_argument("--max-files", type=str, default="5", 
                       help="Number of WARC files to process ('all' for all files, or a number). Default: 5")
    parser.add_argument("--resume", action="store_true", 
                       help="Resume from where the last run left off")
    parser.add_argument("--reset-progress", action="store_true", 
                       help="Reset progress tracking and start from beginning")
    parser.add_argument("--progress-file", default="analysis_progress.json", 
                       help="File to track analysis progress. Default: analysis_progress.json")
    
    # Phase control arguments
    parser.add_argument("--phase", choices=['1', '2', '3', 'all'], default='all',
                       help="Which phase to run (1=fast detection, 2=sophisticated filtering, 3=passage extraction, all=complete pipeline)")
    parser.add_argument("--force-phase", action="store_true",
                       help="Force re-run of specified phase even if completed")
    
    args = parser.parse_args()
    
    # Parse max_files argument
    if args.max_files.lower() == 'all':
        max_files = None  # Process all files
    else:
        try:
            max_files = int(args.max_files)
            if max_files <= 0:
                logger.error("--max-files must be a positive number or 'all'")
                sys.exit(1)
        except ValueError:
            logger.error("--max-files must be a number or 'all'")
            sys.exit(1)
    
    # Get API key from args or environment
    api_key = args.openai_api_key or OPENAI_API_KEY
    if not api_key:
        logger.error("OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --openai-api-key")
        sys.exit(1)
    
    try:
        analyzer = ThreePhaseLegalAnalyzer(
            output_dir=args.output_dir,
            max_files=max_files,
            progress_file=args.progress_file
        )
        
        # Handle progress reset
        if args.reset_progress:
            analyzer.reset_progress()
            logger.info("Progress tracking has been reset")
        
        # Handle force phase reset
        if args.force_phase and args.phase != 'all':
            phase_num = int(args.phase)
            analyzer.progress_tracker.progress_data[f'phase_{phase_num}']['completed'] = False
            analyzer.progress_tracker.save_progress()
            logger.info(f"Phase {phase_num} marked as incomplete, will be re-run")
        
        # Run analysis based on phase selection
        if args.phase == 'all':
            # Run complete 3-phase pipeline
            logger.info("Running complete 3-phase analysis pipeline")
            if args.resume:
                logger.info("Resume mode enabled - will continue from last completed phase/file")
            
            final_stats = analyzer.run_three_phase_analysis(api_key, resume=args.resume)
            
            # Log comprehensive results
            if final_stats:
                logger.info("\n" + "="*60)
                logger.info("3-PHASE ANALYSIS COMPLETED")
                logger.info("="*60)
                
                # Phase 1 stats
                phase1 = final_stats.get('phase_1_lightning_detection', {})
                logger.info(f"Phase 1 - Lightning Detection:")
                logger.info(f"  Records processed: {phase1.get('records_processed', 0):,}")
                logger.info(f"  Legal documents found: {phase1.get('legal_documents_found', 0):,}")
                logger.info(f"  Detection rate: {phase1.get('detection_rate', 0):.4f}%")
                
                # Phase 2 stats
                phase2 = final_stats.get('phase_2_sophisticated_filtering', {})
                logger.info(f"Phase 2 - Sophisticated Filtering:")
                logger.info(f"  Input documents: {phase2.get('input_documents', 0):,}")
                logger.info(f"  Filtered documents: {phase2.get('filtered_documents', 0):,}")
                logger.info(f"  Filter success rate: {phase2.get('filter_rate', 0):.2f}%")
                
                # Phase 3 stats
                phase3 = final_stats.get('phase_3_passage_extraction', {})
                logger.info(f"Phase 3 - Passage Extraction:")
                logger.info(f"  Input documents: {phase3.get('input_documents', 0):,}")
                logger.info(f"  Extracted passages: {phase3.get('extracted_passages', 0):,}")
                logger.info(f"  OpenAI tokens used: {phase3.get('openai_tokens_used', 0):,}")
                logger.info(f"  Estimated cost: ${phase3.get('estimated_cost_usd', 0):.2f}")
                
                # Output locations
                locations = final_stats.get('output_locations', {})
                logger.info(f"Results saved to: {locations.get('crawl_directory', 'N/A')}")
                logger.info("="*60)
        
        else:
            # Run specific phase
            phase_num = int(args.phase)
            logger.info(f"Running Phase {phase_num} only")
            
            if phase_num == 1:
                logger.info("Phase 1: Lightning Fast Detection")
                if phase_num == 3 and not api_key:
                    logger.error("Phase 3 requires OpenAI API key")
                    sys.exit(1)
                # Note: Individual phase running would need to be implemented
                logger.warning("Individual phase running not yet implemented. Use --phase all for now.")
            
            elif phase_num == 2:
                logger.info("Phase 2: Sophisticated Legal Filtering")
                logger.warning("Individual phase running not yet implemented. Use --phase all for now.")
            
            elif phase_num == 3:
                logger.info("Phase 3: Passage Extraction and Parquet Storage")
                if not api_key:
                    logger.error("Phase 3 requires OpenAI API key")
                    sys.exit(1)
                logger.warning("Individual phase running not yet implemented. Use --phase all for now.")
        
        logger.info("Analysis completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user. Progress has been saved.")
        logger.info("Use --resume to continue from where you left off.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 