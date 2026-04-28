"""
Configuration loader with YAML and environment variable support
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: str = "config.yaml"):
        # Load environment variables
        load_dotenv()
        
        # Load YAML config
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation (e.g., 'llm.model')"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config
    
    @property
    def llm_base_url(self) -> str:
        """Get LLM base URL from env or config"""
        return os.getenv('OLLAMA_BASE_URL') or self.get('llm.base_url', 'http://localhost:11434')
    
    @property
    def llm_model(self) -> str:
        """Get LLM model from env or config"""
        return os.getenv('OLLAMA_MODEL') or self.get('llm.model', 'qwen2.5:7b')
    
    @property
    def llm_temperature(self) -> float:
        """Get LLM temperature from env or config"""
        temp = os.getenv('LLM_TEMPERATURE')
        if temp:
            return float(temp)
        return self.get('llm.temperature', 0.3)
    
    @property
    def llm_timeout(self) -> int:
        """Get LLM timeout from env or config"""
        timeout = os.getenv('LLM_TIMEOUT')
        if timeout:
            return int(timeout)
        return self.get('llm.timeout', 120)
