#!/usr/bin/env python3
"""
Test script to verify the Q&A Generator setup
"""
import sys
from pathlib import Path

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    try:
        from src.config import Config
        from src.models import QAItem, SourceData, PerformanceSummary
        from src.csv_reader import CSVReader
        from src.discipline_detector import DisciplineDetector
        from src.llm_client import OllamaClient
        from src.processor import QAProcessor
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from src.config import Config
        config = Config()
        print(f"✓ Config loaded")
        print(f"  - LLM Model: {config.llm_model}")
        print(f"  - LLM Base URL: {config.llm_base_url}")
        print(f"  - Temperature: {config.llm_temperature}")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_csv_reader():
    """Test CSV reading"""
    print("\nTesting CSV reader...")
    try:
        from src.csv_reader import CSVReader
        
        clauses = CSVReader.read_clauses('data/clauses.csv')
        tables = CSVReader.read_tables('data/tables.csv')
        
        print(f"✓ Loaded {len(clauses)} clauses and {len(tables)} tables")
        
        if clauses:
            print(f"  - First clause: {clauses[0].source_id}")
            print(f"  - Text preview: {clauses[0].text[:50]}...")
        
        if tables:
            print(f"  - First table: {tables[0].source_id}")
            print(f"  - Text preview: {tables[0].text[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ CSV reader error: {e}")
        return False

def test_discipline_detector():
    """Test discipline detection"""
    print("\nTesting discipline detector...")
    try:
        from src.config import Config
        from src.discipline_detector import DisciplineDetector
        
        config = Config()
        detector = DisciplineDetector(config)
        
        test_cases = [
            ("Electrical installations shall be designed with circuit breakers", "electrical"),
            ("HVAC systems must provide adequate ventilation", "mechanical"),
            ("Fire sprinkler systems shall be installed", "fire"),
            ("Water supply pipes and drainage systems", "hydraulic"),
            ("This random text has no keywords", "unknown")
        ]
        
        passed = 0
        for text, expected in test_cases:
            result = detector.detect(text)
            if result == expected:
                print(f"✓ '{text[:40]}...' → {result}")
                passed += 1
            else:
                print(f"✗ '{text[:40]}...' → {result} (expected {expected})")
        
        print(f"  - Passed {passed}/{len(test_cases)} tests")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"✗ Discipline detector error: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection (non-blocking)"""
    print("\nTesting Ollama connection...")
    try:
        import requests
        from src.config import Config
        
        config = Config()
        base_url = config.llm_base_url
        
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✓ Ollama is running at {base_url}")
            if models:
                print(f"  - Available models: {', '.join([m['name'] for m in models])}")
            else:
                print(f"  - No models installed. Run: ollama pull {config.llm_model}")
            return True
        else:
            print(f"✗ Ollama responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Ollama is not running at {base_url}")
        print("  - Install Ollama: https://ollama.com/")
        print("  - Start Ollama: ollama serve")
        print(f"  - Pull a model: ollama pull {config.llm_model}")
        return False
    except Exception as e:
        print(f"✗ Ollama connection error: {e}")
        return False

def test_output_directory():
    """Test output directory"""
    print("\nTesting output directory...")
    try:
        output_dir = Path("output")
        if not output_dir.exists():
            output_dir.mkdir()
            print("✓ Created output directory")
        else:
            print("✓ Output directory exists")
        return True
    except Exception as e:
        print(f"✗ Output directory error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("Q&A GENERATOR - SETUP VERIFICATION")
    print("=" * 80)
    
    tests = [
        test_imports,
        test_config,
        test_csv_reader,
        test_discipline_detector,
        test_output_directory,
        test_ollama_connection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! Ready to run the Q&A generator.")
        print("\nNext steps:")
        print("  1. Ensure Ollama is running: ollama serve")
        print("  2. Pull a model: ollama pull qwen2.5:7b")
        print("  3. Run the generator: python main.py")
    elif results[-1] == False:
        print("\n⚠ Setup is mostly complete, but Ollama is not running.")
        print("\nTo use the tool:")
        print("  1. Install Ollama: https://ollama.com/")
        print("  2. Start Ollama: ollama serve")
        print("  3. Pull a model: ollama pull qwen2.5:7b")
        print("  4. Run the generator: python main.py")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
