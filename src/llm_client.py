"""
Ollama LLM Client for Q&A generation and verification
"""
import json
import requests
from typing import List, Dict, Any, Optional
from src.config import Config
from src.models import QAItem, VerificationResult


class OllamaClient:
    """Client for interacting with Ollama LLM"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.llm_base_url.rstrip('/')
        self.model = config.llm_model
        self.temperature = config.llm_temperature
        self.timeout = config.llm_timeout
    
    def _call_llm(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Call Ollama LLM with a prompt
        
        Args:
            prompt: User prompt
            system: Optional system prompt
            
        Returns:
            LLM response text
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": self.config.get("llm.keep_alive", "30m"),
            # Ask Ollama to enforce JSON output (supported by newer Ollama versions).
            # If unsupported, Ollama will ignore it and still return text.
            "format": "json",
            "options": {
                "temperature": self.temperature,
                "num_predict": int(self.config.get("llm.num_predict", 800)),
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(
                url,
                json=payload,
                # Separate connect and read timeouts (read timeout is the long one)
                timeout=(10, self.timeout)
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to call Ollama LLM: {str(e)}")

    @staticmethod
    def _extract_json_array(text: str) -> str:
        """
        Best-effort extraction of a JSON array from a model response.
        Helps when the model adds extra text around the array.
        """
        s = text.strip()
        start = s.find('[')
        end = s.rfind(']')
        if start == -1 or end == -1 or end <= start:
            return s
        return s[start:end + 1]
    
    def generate_qna(
        self,
        source_type: str,
        source_id: str,
        source_text: str,
        dataset_id: str
    ) -> List[QAItem]:
        """
        Generate Q&A for a source (clause or table)
        
        Args:
            source_type: "clause" or "table"
            source_id: ID of the source
            source_text: Text content of the source
            dataset_id: Unique dataset identifier
            
        Returns:
            List of QAItem objects
        """
        system_prompt = """You are an engineering standards analyst. The text below may come from electrical, mechanical, fire, hydraulic, NCC, SIR, or another building code.

Your job is to generate realistic user questions and answers based ONLY on the provided text.

Rules:
- Do NOT use outside knowledge.
- Do NOT invent values, limits, exceptions, or clause references.
- Do NOT assume the discipline unless supported by text.
- The expected answer must be directly supported by the provided text.
- The expected answer must preserve key engineering context: subject, condition/scope, and requirement/value.
- Prefer complete technical phrasing over shorthand fragments.
- Citation snippet must be exact text from the source.
- Trap questions must expose common misunderstandings but must not create false unsupported answers.
- Keywords and missing_keywords must prioritize retrieval-critical technical phrases (including multi-word phrases), not only single tokens.

Return ONLY a valid JSON array with no additional text or markdown formatting."""
        
        user_prompt = f"""SOURCE TYPE: {source_type}
SOURCE ID: {source_id}
TEXT: {source_text}

Generate exactly 5 questions:
- 1 direct question (straightforward, uses key terms from the text)
- 1 natural user-style question (how someone would actually ask)
- 1 keyword-poor question (uses different words, but still about the same topic)
- 1 keyword-rich question (includes many technical terms)
- 1 trap question (common misconception or edge case)

For each question, provide:
- discipline_detected: electrical | mechanical | fire | hydraulic | ncc | sir | unknown (based on text content only)
- question_type: direct | natural | keyword_poor | keyword_rich | trap
- question: the question text
- expected_answer: answer supported by the source text, including full engineering context
- keywords: list of important keywords present in the question
  * include at least 6 entries
  * include at least 2 multi-word technical phrases where possible
- missing_keywords: list of important retrieval-critical terms from source that are NOT in the question
  * prioritize multi-word technical phrases
  * include 3 to 8 entries
- trap question requirements:
  * must contain a plausible but incorrect assumption
  * expected_answer must explicitly correct that assumption using source text only
- citation_snippet: exact text from source that supports the answer
- confidence: 0.0 to 1.0 (how confident you are the answer is fully supported)

OUTPUT JSON ARRAY (no markdown, no code blocks):
[
  {{
    "discipline_detected": "...",
    "question_type": "...",
    "question": "...",
    "expected_answer": "...",
    "keywords": ["..."],
    "missing_keywords": ["..."],
    "citation_snippet": "...",
    "confidence": 0.0
  }}
]"""
        
        try:
            response = self._call_llm(user_prompt, system_prompt)
            
            # Clean up response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            # If Ollama 'format: json' is honored, response may be a JSON object string.
            # We still handle the original contract: a JSON array.
            response = self._extract_json_array(response)
            
            # Parse JSON response
            qa_data = json.loads(response)
            
            # Convert to QAItem objects
            qa_items = []
            for item in qa_data:
                qa_item = QAItem(
                    dataset_id=dataset_id,
                    source_type=source_type,
                    source_id=source_id,
                    discipline_detected=item.get('discipline_detected', 'unknown'),
                    question_type=item['question_type'],
                    question=item['question'],
                    expected_answer=item['expected_answer'],
                    keywords=item.get('keywords', []),
                    missing_keywords=item.get('missing_keywords', []),
                    citation_snippet=item['citation_snippet'],
                    confidence=item.get('confidence', 0.5)
                )
                qa_items.append(qa_item)
            
            return qa_items
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}\nResponse: {response}")
        except Exception as e:
            raise Exception(f"Failed to generate Q&A: {str(e)}")
    
    def verify_qna(self, qa_item: QAItem, source_text: str) -> VerificationResult:
        """
        Verify a Q&A item against the source text
        
        Args:
            qa_item: QAItem to verify
            source_text: Original source text
            
        Returns:
            VerificationResult
        """
        system_prompt = """You are a strict engineering compliance verifier. Check the Q&A using ONLY the source text.

Reject if:
- answer is not directly supported by source
- citation does not prove the answer
- values or limits are invented
- discipline is guessed without support
- question needs another clause/table to answer
- trap question is misleading in an unsafe way

Return ONLY a valid JSON object with no additional text or markdown formatting."""
        
        user_prompt = f"""SOURCE TEXT:
{source_text}

Q&A TO VERIFY:
Question: {qa_item.question}
Answer: {qa_item.expected_answer}
Citation: {qa_item.citation_snippet}
Discipline: {qa_item.discipline_detected}

Verify this Q&A strictly. Return JSON only (no markdown, no code blocks):
{{
  "verified": true or false,
  "issues": ["list of issues found, empty if verified"],
  "confidence": 0.0 to 1.0
}}"""
        
        try:
            response = self._call_llm(user_prompt, system_prompt)
            
            # Clean up response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON response
            result_data = json.loads(response)
            
            return VerificationResult(
                verified=result_data.get('verified', False),
                issues=result_data.get('issues', []),
                confidence=result_data.get('confidence', 0.5)
            )
            
        except json.JSONDecodeError as e:
            # If parsing fails, return unverified with error
            return VerificationResult(
                verified=False,
                issues=[f"Failed to parse verification response: {str(e)}"],
                confidence=0.0
            )
        except Exception as e:
            return VerificationResult(
                verified=False,
                issues=[f"Verification failed: {str(e)}"],
                confidence=0.0
            )
