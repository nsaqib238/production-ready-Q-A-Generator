"""
Data models for Q&A Generator
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class SourceData(BaseModel):
    """Base model for source data from CSV"""
    source_id: str
    source_type: Literal["clause", "table"]
    text: str
    
    
class ClauseData(SourceData):
    """Model for clause data"""
    source_type: Literal["clause"] = "clause"
    

class TableData(SourceData):
    """Model for table data"""
    source_type: Literal["table"] = "table"


class QAItem(BaseModel):
    """Model for a single Q&A item"""
    dataset_id: str
    source_type: Literal["clause", "table"]
    source_id: str
    discipline_detected: Literal["electrical", "mechanical", "fire", "hydraulic", "ncc", "sir", "unknown"]
    question_type: Literal["direct", "natural", "keyword_poor", "keyword_rich", "trap"]
    question: str
    expected_answer: str
    keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    citation_snippet: str
    confidence: float = Field(ge=0.0, le=1.0)
    

class VerificationResult(BaseModel):
    """Model for verification result"""
    verified: bool
    issues: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    

class RejectedQA(BaseModel):
    """Model for rejected Q&A with reason"""
    qa_item: QAItem
    rejection_reason: str
    verification_result: VerificationResult
    

class ProcessingCheckpoint(BaseModel):
    """Model for processing checkpoint"""
    last_processed_clause_index: int = -1
    last_processed_table_index: int = -1
    total_generated: int = 0
    total_verified: int = 0
    total_rejected: int = 0
    

class PerformanceSummary(BaseModel):
    """Model for performance summary"""
    total_clauses_processed: int = 0
    total_tables_processed: int = 0
    total_qna_generated: int = 0
    total_qna_verified: int = 0
    total_rejected: int = 0
    rejection_reasons: dict = Field(default_factory=dict)
    average_confidence: float = 0.0
    discipline_breakdown: dict = Field(default_factory=dict)
    question_type_breakdown: dict = Field(default_factory=dict)
