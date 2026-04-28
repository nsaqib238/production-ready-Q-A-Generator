"""
Discipline detection from text content
"""
from typing import Literal
from src.config import Config


class DisciplineDetector:
    """Detects engineering discipline from text content"""
    
    def __init__(self, config: Config):
        self.config = config
        self.discipline_keywords = config.get('discipline_keywords', {})
    
    def detect(self, text: str) -> Literal["electrical", "mechanical", "fire", "hydraulic", "ncc", "sir", "unknown"]:
        """
        Detect discipline from text based on keyword matching.
        
        Args:
            text: Source text to analyze
            
        Returns:
            Detected discipline or 'unknown'
        """
        text_lower = text.lower()
        
        # Count keyword matches for each discipline
        scores = {}
        
        for discipline, keywords in self.discipline_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                score += text_lower.count(keyword.lower())
            scores[discipline] = score
        
        # Get discipline with highest score
        if scores:
            max_discipline = max(scores, key=scores.get)
            max_score = scores[max_discipline]
            
            # Only return discipline if we have at least one match
            if max_score > 0:
                return max_discipline
        
        return "unknown"
    
    def get_keywords_for_discipline(self, discipline: str) -> list:
        """Get keywords for a specific discipline"""
        return self.discipline_keywords.get(discipline, [])
