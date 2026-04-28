"""
CSV reader for clauses and tables
"""
import csv
from pathlib import Path
from typing import List
from src.models import ClauseData, TableData


class CSVReader:
    """Reader for clauses and tables CSV files"""
    
    @staticmethod
    def read_clauses(file_path: str) -> List[ClauseData]:
        """
        Read clauses from CSV file.
        Expected columns: source_id, text (or any column containing clause text)
        """
        clauses = []
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Clauses file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Auto-detect column names
            fieldnames = reader.fieldnames or []
            
            # Look for ID column
            id_col = None
            for col in ['source_id', 'id', 'clause_id', 'number']:
                if col in fieldnames:
                    id_col = col
                    break
            
            # Look for text column
            text_col = None
            for col in ['text', 'content', 'clause', 'description']:
                if col in fieldnames:
                    text_col = col
                    break
            
            if not id_col or not text_col:
                raise ValueError(
                    f"Could not auto-detect required columns in {file_path}. "
                    f"Available columns: {fieldnames}. "
                    f"Required: an ID column (source_id/id/clause_id/number) and "
                    f"a text column (text/content/clause/description)"
                )
            
            for row in reader:
                source_id = row.get(id_col, '').strip()
                text = row.get(text_col, '').strip()
                
                if source_id and text:
                    clauses.append(ClauseData(
                        source_id=source_id,
                        text=text
                    ))
        
        return clauses
    
    @staticmethod
    def read_tables(file_path: str) -> List[TableData]:
        """
        Read tables from CSV file.
        Expected columns: source_id, text (or any column containing table text/content)
        """
        tables = []
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Tables file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Auto-detect column names
            fieldnames = reader.fieldnames or []
            
            # Look for ID column
            id_col = None
            for col in ['source_id', 'id', 'table_id', 'number']:
                if col in fieldnames:
                    id_col = col
                    break
            
            # Look for text column
            text_col = None
            for col in ['text', 'content', 'table', 'description', 'data']:
                if col in fieldnames:
                    text_col = col
                    break
            
            if not id_col or not text_col:
                raise ValueError(
                    f"Could not auto-detect required columns in {file_path}. "
                    f"Available columns: {fieldnames}. "
                    f"Required: an ID column (source_id/id/table_id/number) and "
                    f"a text column (text/content/table/description/data)"
                )
            
            for row in reader:
                source_id = row.get(id_col, '').strip()
                text = row.get(text_col, '').strip()
                
                if source_id and text:
                    tables.append(TableData(
                        source_id=source_id,
                        text=text
                    ))
        
        return tables
