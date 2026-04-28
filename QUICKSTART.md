# Quick Start Guide

## Prerequisites

You'll need Ollama running with a model. Here's how to set it up:

```bash
# 1. Install Ollama (on your local machine)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama server
ollama serve

# 3. Pull a model (in a new terminal)
ollama pull qwen2.5:7b
```

## Running the Tool

```bash
# Test the setup first
python test_setup.py

# Run with default settings
python main.py

# Or with a different model
python main.py --model llama3.1:8b

# Start fresh (clear previous outputs)
python main.py --clear
```

## Expected Output

The tool will process all clauses and tables from `data/clauses.csv` and `data/tables.csv`, generating:

1. **output/generated_qna.jsonl** - Verified Q&A pairs (one per line)
2. **output/rejected_qna.jsonl** - Rejected Q&A with reasons (one per line)
3. **output/model_performance_summary.json** - Overall statistics

## Inspecting Results

```bash
# Count verified Q&A
wc -l output/generated_qna.jsonl

# Count rejected Q&A
wc -l output/rejected_qna.jsonl

# View summary
cat output/model_performance_summary.json | python -m json.tool

# View a few generated Q&A
head -n 3 output/generated_qna.jsonl | python -m json.tool
```

## Resume Support

If you interrupt the process (Ctrl+C), just run it again:

```bash
python main.py
```

It will resume from the last checkpoint automatically.

To start completely fresh:

```bash
python main.py --reset --clear
```

## Using Your Own Data

Replace the sample files in `data/`:
- `data/clauses.csv` - Your clauses/requirements
- `data/tables.csv` - Your tables/data

CSV format (flexible column names):
```csv
source_id,text
1.2.3,"Your clause text here..."
```

The tool auto-detects common column names like `id`, `clause_id`, `text`, `content`, etc.

## Supported Models

Any Ollama model works. Tested with:
- qwen2.5:7b (recommended)
- llama3.1:8b
- mistral:7b
- deepseek-r1:7b

Larger models (13B, 70B) give better results but need more RAM.

## Troubleshooting

**"Connection refused"**
- Make sure Ollama is running: `ollama serve`

**"Model not found"**
- Pull the model: `ollama pull qwen2.5:7b`
- Check available: `ollama list`

**"Failed to parse JSON"**
- Try a different model
- Check rejected_qna.jsonl for details

## Configuration

Edit `config.yaml` to customize:
- LLM model and settings
- Processing batch size
- Checkpoint interval
- Input/output paths
- Discipline keywords

See README.md for full documentation.
