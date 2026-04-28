"""
Main processor for Q&A generation with batch processing and resume support
"""
import json
import time
from pathlib import Path
from typing import List, Tuple
from tqdm import tqdm

from src.config import Config
from src.models import (
    SourceData, QAItem, RejectedQA, 
    ProcessingCheckpoint, PerformanceSummary
)
from src.csv_reader import CSVReader
from src.discipline_detector import DisciplineDetector
from src.llm_client import OllamaClient


class QAProcessor:
    """Main processor for Q&A generation"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm_client = OllamaClient(config)
        self.discipline_detector = DisciplineDetector(config)
        
        # Output paths
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        self.generated_qna_path = self.output_dir / "generated_qna.jsonl"
        self.rejected_qna_path = self.output_dir / "rejected_qna.jsonl"
        self.summary_path = self.output_dir / "model_performance_summary.json"
        self.checkpoint_path = self.output_dir / ".checkpoint.json"
        
        # Statistics
        self.stats = PerformanceSummary()
        
        # Load checkpoint if exists
        self.checkpoint = self._load_checkpoint()
    
    def _load_checkpoint(self) -> ProcessingCheckpoint:
        """Load checkpoint from file if exists"""
        if self.checkpoint_path.exists():
            try:
                with open(self.checkpoint_path, 'r') as f:
                    data = json.load(f)
                    return ProcessingCheckpoint(**data)
            except Exception as e:
                print(f"Warning: Failed to load checkpoint: {e}")
        
        return ProcessingCheckpoint()
    
    def _save_checkpoint(self):
        """Save current checkpoint to file"""
        try:
            with open(self.checkpoint_path, 'w') as f:
                json.dump(self.checkpoint.model_dump(), f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save checkpoint: {e}")
    
    def _append_generated_qna(self, qa_item: QAItem):
        """Append generated Q&A to JSONL file"""
        with open(self.generated_qna_path, 'a', encoding='utf-8') as f:
            f.write(qa_item.model_dump_json() + '\n')
    
    def _append_rejected_qna(self, rejected: RejectedQA):
        """Append rejected Q&A to JSONL file"""
        with open(self.rejected_qna_path, 'a', encoding='utf-8') as f:
            f.write(rejected.model_dump_json() + '\n')
    
    def _save_summary(self):
        """Save performance summary to JSON file"""
        with open(self.summary_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats.model_dump(), f, indent=2)
    
    def _process_source(
        self, 
        source: SourceData, 
        dataset_id: str,
        max_retries: int = 3
    ) -> Tuple[int, int, int]:
        """
        Process a single source (clause or table)
        
        Returns:
            Tuple of (generated, verified, rejected) counts
        """
        generated = 0
        verified = 0
        rejected = 0
        
        for attempt in range(max_retries):
            try:
                # Generate Q&A
                qa_items = self.llm_client.generate_qna(
                    source_type=source.source_type,
                    source_id=source.source_id,
                    source_text=source.text,
                    dataset_id=dataset_id
                )
                
                generated = len(qa_items)
                
                # Verify each Q&A
                for qa_item in qa_items:
                    verification_result = self.llm_client.verify_qna(
                        qa_item=qa_item,
                        source_text=source.text
                    )
                    
                    if verification_result.verified:
                        # Save to generated file
                        self._append_generated_qna(qa_item)
                        verified += 1
                        
                        # Update statistics
                        self.stats.total_qna_verified += 1
                        
                        # Track discipline breakdown
                        discipline = qa_item.discipline_detected
                        self.stats.discipline_breakdown[discipline] = \
                            self.stats.discipline_breakdown.get(discipline, 0) + 1
                        
                        # Track question type breakdown
                        qtype = qa_item.question_type
                        self.stats.question_type_breakdown[qtype] = \
                            self.stats.question_type_breakdown.get(qtype, 0) + 1
                    else:
                        # Save to rejected file
                        rejection_reason = "; ".join(verification_result.issues)
                        rejected_qa = RejectedQA(
                            qa_item=qa_item,
                            rejection_reason=rejection_reason,
                            verification_result=verification_result
                        )
                        self._append_rejected_qna(rejected_qa)
                        rejected += 1
                        
                        # Update statistics
                        self.stats.total_rejected += 1
                        self.stats.rejection_reasons[rejection_reason] = \
                            self.stats.rejection_reasons.get(rejection_reason, 0) + 1
                
                # Success - break retry loop
                break
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # Last attempt failed - log and continue
                    print(f"\nFailed to process {source.source_type} {source.source_id} after {max_retries} attempts: {e}")
                    
                    # Still count as processed but all rejected
                    generated = 0
                    verified = 0
                    rejected = 5  # Expected 5 questions
                    
                    error_reason = f"Processing failed: {str(e)}"
                    self.stats.rejection_reasons[error_reason] = \
                        self.stats.rejection_reasons.get(error_reason, 0) + 1
                else:
                    # Retry after a short delay
                    time.sleep(2)
        
        return generated, verified, rejected
    
    def process_all(self):
        """Process all clauses and tables"""
        print("=" * 80)
        print("Q&A GENERATOR - LLM Performance Benchmark Tool")
        print("=" * 80)
        print(f"LLM Model: {self.llm_client.model}")
        print(f"LLM Base URL: {self.llm_client.base_url}")
        print(f"Temperature: {self.llm_client.temperature}")
        print("=" * 80)
        
        # Load data
        print("\nLoading input files...")
        clauses_file = self.config.get('input.clauses_file', 'data/clauses.csv')
        tables_file = self.config.get('input.tables_file', 'data/tables.csv')
        
        try:
            clauses = CSVReader.read_clauses(clauses_file)
            print(f"✓ Loaded {len(clauses)} clauses from {clauses_file}")
        except FileNotFoundError:
            print(f"✗ Clauses file not found: {clauses_file}")
            clauses = []
        except Exception as e:
            print(f"✗ Error loading clauses: {e}")
            clauses = []
        
        try:
            tables = CSVReader.read_tables(tables_file)
            print(f"✓ Loaded {len(tables)} tables from {tables_file}")
        except FileNotFoundError:
            print(f"✗ Tables file not found: {tables_file}")
            tables = []
        except Exception as e:
            print(f"✗ Error loading tables: {e}")
            tables = []
        
        if not clauses and not tables:
            print("\n✗ No data to process. Exiting.")
            return
        
        # Resume support
        start_clause_idx = self.checkpoint.last_processed_clause_index + 1
        start_table_idx = self.checkpoint.last_processed_table_index + 1
        
        if start_clause_idx > 0 or start_table_idx > 0:
            print(f"\n⟳ Resuming from checkpoint:")
            print(f"  - Clauses: starting at index {start_clause_idx}")
            print(f"  - Tables: starting at index {start_table_idx}")
        
        # Process clauses
        if clauses:
            print(f"\n{'='*80}")
            print(f"Processing {len(clauses)} Clauses")
            print(f"{'='*80}")
            
            for idx, clause in enumerate(tqdm(clauses[start_clause_idx:], 
                                              desc="Clauses", 
                                              initial=start_clause_idx,
                                              total=len(clauses))):
                actual_idx = start_clause_idx + idx
                dataset_id = f"clause_{clause.source_id}"
                
                gen, ver, rej = self._process_source(
                    clause, 
                    dataset_id,
                    max_retries=self.config.get('processing.max_retries', 3)
                )
                
                # Update stats
                self.stats.total_qna_generated += gen
                self.checkpoint.total_generated += gen
                self.checkpoint.total_verified += ver
                self.checkpoint.total_rejected += rej
                
                # Update checkpoint
                self.checkpoint.last_processed_clause_index = actual_idx
                self.stats.total_clauses_processed = actual_idx + 1
                
                # Save checkpoint periodically
                checkpoint_interval = self.config.get('processing.checkpoint_interval', 5)
                if (actual_idx + 1) % checkpoint_interval == 0:
                    self._save_checkpoint()
                    self._save_summary()
        
        # Process tables
        if tables:
            print(f"\n{'='*80}")
            print(f"Processing {len(tables)} Tables")
            print(f"{'='*80}")
            
            for idx, table in enumerate(tqdm(tables[start_table_idx:], 
                                            desc="Tables",
                                            initial=start_table_idx,
                                            total=len(tables))):
                actual_idx = start_table_idx + idx
                dataset_id = f"table_{table.source_id}"
                
                gen, ver, rej = self._process_source(
                    table, 
                    dataset_id,
                    max_retries=self.config.get('processing.max_retries', 3)
                )
                
                # Update stats
                self.stats.total_qna_generated += gen
                self.checkpoint.total_generated += gen
                self.checkpoint.total_verified += ver
                self.checkpoint.total_rejected += rej
                
                # Update checkpoint
                self.checkpoint.last_processed_table_index = actual_idx
                self.stats.total_tables_processed = actual_idx + 1
                
                # Save checkpoint periodically
                checkpoint_interval = self.config.get('processing.checkpoint_interval', 5)
                if (actual_idx + 1) % checkpoint_interval == 0:
                    self._save_checkpoint()
                    self._save_summary()
        
        # Calculate average confidence
        if self.stats.total_qna_verified > 0:
            # Calculate from generated file
            total_confidence = 0.0
            count = 0
            
            if self.generated_qna_path.exists():
                with open(self.generated_qna_path, 'r') as f:
                    for line in f:
                        try:
                            qa = json.loads(line)
                            total_confidence += qa.get('confidence', 0.0)
                            count += 1
                        except:
                            pass
            
            if count > 0:
                self.stats.average_confidence = total_confidence / count
        
        # Final save
        self._save_checkpoint()
        self._save_summary()
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self):
        """Print final summary"""
        print(f"\n{'='*80}")
        print("PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"Total Clauses Processed:  {self.stats.total_clauses_processed}")
        print(f"Total Tables Processed:   {self.stats.total_tables_processed}")
        print(f"Total Q&A Generated:      {self.stats.total_qna_generated}")
        print(f"Total Q&A Verified:       {self.stats.total_qna_verified}")
        print(f"Total Rejected:           {self.stats.total_rejected}")
        print(f"Average Confidence:       {self.stats.average_confidence:.2f}")
        
        print(f"\n{'='*80}")
        print("DISCIPLINE BREAKDOWN")
        print(f"{'='*80}")
        for discipline, count in sorted(self.stats.discipline_breakdown.items()):
            print(f"{discipline:15s}: {count}")
        
        print(f"\n{'='*80}")
        print("QUESTION TYPE BREAKDOWN")
        print(f"{'='*80}")
        for qtype, count in sorted(self.stats.question_type_breakdown.items()):
            print(f"{qtype:15s}: {count}")
        
        if self.stats.rejection_reasons:
            print(f"\n{'='*80}")
            print("TOP REJECTION REASONS")
            print(f"{'='*80}")
            sorted_reasons = sorted(
                self.stats.rejection_reasons.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            for reason, count in sorted_reasons[:10]:
                # Truncate long reasons
                display_reason = reason[:60] + "..." if len(reason) > 60 else reason
                print(f"{count:3d} | {display_reason}")
        
        print(f"\n{'='*80}")
        print("OUTPUT FILES")
        print(f"{'='*80}")
        print(f"Generated Q&A:  {self.generated_qna_path}")
        print(f"Rejected Q&A:   {self.rejected_qna_path}")
        print(f"Summary:        {self.summary_path}")
        print(f"{'='*80}\n")
