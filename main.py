#!/usr/bin/env python3
"""
Q&A Generator CLI
Main entry point for the Q&A generation tool
"""
import argparse
import sys
from pathlib import Path

from src.config import Config
from src.processor import QAProcessor


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Q&A Generator - Test LLM performance on code/standard datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default config
  python main.py

  # Run with custom config file
  python main.py --config my_config.yaml

  # Override LLM model
  python main.py --model llama3.1:8b

  # Clear previous outputs and start fresh
  python main.py --clear

  # Reset checkpoint and restart from beginning
  python main.py --reset

For more information, see README.md
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='Override LLM model from config (e.g., qwen2.5:7b, llama3.1:8b)'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear previous output files before starting'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset checkpoint and restart from beginning'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = Config(args.config)
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {args.config}")
        print("Please create a config.yaml file or specify a valid config file with --config")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Override model if specified
    if args.model:
        config._config['llm']['model'] = args.model
    
    # Clear outputs if requested
    if args.clear:
        output_dir = Path("output")
        if output_dir.exists():
            for file in ['generated_qna.jsonl', 'rejected_qna.jsonl', 
                        'model_performance_summary.json', '.checkpoint.json']:
                file_path = output_dir / file
                if file_path.exists():
                    file_path.unlink()
                    print(f"✓ Cleared {file}")
    
    # Reset checkpoint if requested
    if args.reset:
        checkpoint_path = Path("output/.checkpoint.json")
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            print("✓ Reset checkpoint")
    
    # Create processor and run
    try:
        processor = QAProcessor(config)
        processor.process_all()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress has been saved.")
        print("Run again to resume from checkpoint.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
