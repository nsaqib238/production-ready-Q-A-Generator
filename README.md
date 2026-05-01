# Q&A Generator - LLM Performance Benchmark Tool

A standalone tool to test LLM performance on engineering standards, building codes, and technical documentation by generating high-quality benchmark Q&A pairs.

## 🎯 Purpose

This tool helps you evaluate how well an LLM can:
- Understand technical clauses and tables from various engineering disciplines
- Generate realistic questions that users would actually ask
- Provide accurate answers strictly based on source text
- Detect and classify engineering disciplines automatically
- Handle edge cases and trap questions

## 📋 Features

- ✅ **Multi-Discipline Support**: Electrical, Mechanical, Fire, Hydraulic, NCC, SIR, and unknown standards
- ✅ **5 Question Types**: Direct, natural, keyword-poor, keyword-rich, and trap questions
- ✅ **Auto-Detection**: Automatically detects engineering discipline from text content
- ✅ **Local LLM**: Uses Ollama for privacy and control (Qwen, Llama, Mistral, DeepSeek)
- ✅ **Batch Processing**: Process multiple clauses/tables efficiently
- ✅ **Resume Support**: Checkpoint-based resume if interrupted
- ✅ **Verification**: Built-in Q&A verification against source text
- ✅ **Detailed Logging**: Rejected items logged with reasons
- ✅ **Performance Metrics**: Comprehensive summary with confidence scores

## 🚀 Quick Start

### Prerequisites

1. **Python 3.12+** (already installed in this environment)
2. **Ollama** - Install and run Ollama with a model:

```bash
# Install Ollama (on your local machine)
curl -fsSL https://ollama.com/install.sh | sh



ollama --version
ollama run llama3.1



# Pull a model (choose one)
ollama pull qwen2.5:7b        # Recommended - good balance
ollama pull llama3.1:8b       # Alternative
ollama pull mistral:7b        # Alternative
ollama pull deepseek-r1:7b    # Alternative

# Start Ollama server (usually starts automatically)
ollama serve
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template (optional)
cp .env.example .env
```

### Prepare Your Data

Create two CSV files in the `data/` directory:

**clauses.csv**:
```csv
source_id,text
3.1.1,"Electrical installations shall be designed and constructed..."
3.2.4,"A main earthing conductor shall connect..."
```

**tables.csv**:
```csv
source_id,text
Table 3.1,"Cable Current Carrying Capacity (75°C Thermoplastic)..."
Table 4.2,"Maximum Circuit Lengths (metres) for 5% voltage drop..."
```

**Note**: The CSV reader auto-detects column names. It looks for:
- ID columns: `source_id`, `id`, `clause_id`, `table_id`, `number`
- Text columns: `text`, `content`, `clause`, `table`, `description`, `data`

### Run

```bash
# Basic usage (uses config.yaml settings)
python main.py

# Use a different model
python main.py --model llama3.1:8b

# Start fresh (clear previous outputs)
python main.py --clear

# Reset checkpoint and restart
python main.py --reset

# Use custom config file
python main.py --config my_config.yaml
```

## 📁 Project Structure

```
.
├── main.py                 # CLI entry point
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── src/
│   ├── __init__.py
│   ├── models.py         # Pydantic data models
│   ├── config.py         # Configuration loader
│   ├── csv_reader.py     # CSV file reader
│   ├── discipline_detector.py  # Discipline detection
│   ├── llm_client.py     # Ollama LLM client
│   └── processor.py      # Main processing logic
├── data/
│   ├── clauses.csv       # Input: clauses
│   └── tables.csv        # Input: tables
└── output/
    ├── generated_qna.jsonl          # Verified Q&A pairs
    ├── rejected_qna.jsonl           # Rejected Q&A with reasons
    ├── model_performance_summary.json  # Performance metrics
    └── .checkpoint.json             # Resume checkpoint
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
llm:
  model: "qwen2.5:7b"           # LLM model to use
  base_url: "http://localhost:11434"
  temperature: 0.3               # Lower = more consistent
  timeout: 120                   # Request timeout (seconds)

processing:
  max_retries: 3                # Retries for failed items
  checkpoint_interval: 5        # Save progress every N items
  resume_enabled: true          # Enable resume support

input:
  clauses_file: "data/clauses.csv"
  tables_file: "data/tables.csv"

output:
  generated_qna: "output/generated_qna.jsonl"
  rejected_qna: "output/rejected_qna.jsonl"
  performance_summary: "output/model_performance_summary.json"
```

You can also override settings via environment variables:
```bash
export OLLAMA_MODEL=llama3.1:8b
export OLLAMA_BASE_URL=http://localhost:11434
export LLM_TEMPERATURE=0.3
```

## 📊 Output Files

### 1. generated_qna.jsonl
Each line is a verified Q&A pair in JSON format:

```json
{
  "dataset_id": "clause_3.1.1",
  "source_type": "clause",
  "source_id": "3.1.1",
  "discipline_detected": "electrical",
  "question_type": "direct",
  "question": "What protection must electrical installations provide?",
  "expected_answer": "Protection against electric shock, fire, thermal effects...",
  "keywords": ["electrical", "protection", "installations"],
  "missing_keywords": ["AS/NZS 3000", "circuit protection"],
  "citation_snippet": "Electrical installations shall be designed and constructed to provide protection...",
  "confidence": 0.95
}
```

### 2. rejected_qna.jsonl
Rejected Q&A pairs with reasons:

```json
{
  "qa_item": { /* full Q&A item */ },
  "rejection_reason": "answer is not directly supported by source",
  "verification_result": {
    "verified": false,
    "issues": ["The answer mentions requirements not present in source text"],
    "confidence": 0.2
  }
}
```

### 3. model_performance_summary.json
Overall performance metrics:

```json
{
  "total_clauses_processed": 8,
  "total_tables_processed": 5,
  "total_qna_generated": 65,
  "total_qna_verified": 58,
  "total_rejected": 7,
  "average_confidence": 0.87,
  "discipline_breakdown": {
    "electrical": 65
  },
  "question_type_breakdown": {
    "direct": 13,
    "natural": 13,
    "keyword_poor": 13,
    "keyword_rich": 13,
    "trap": 6
  },
  "rejection_reasons": {
    "answer is not directly supported by source": 4,
    "citation does not prove the answer": 3
  }
}
```

## 🔍 Question Types Explained

1. **Direct Question**: Straightforward, uses key terms from the text
   - Example: "What is the minimum depth for underground cables?"

2. **Natural User-Style**: How someone would actually ask
   - Example: "How deep do I need to bury electrical cables?"

3. **Keyword-Poor**: Uses different words, but same topic
   - Example: "What's the depth requirement for buried wiring?"

4. **Keyword-Rich**: Includes many technical terms
   - Example: "What is the minimum burial depth for underground electrical cable installations in accordance with regulations?"

5. **Trap Question**: Tests common misconceptions or edge cases
   - Example: "Can I install cables at 400mm depth if they're in conduit?" (if not supported by text)

## 🛠️ Supported Models

The tool works with any Ollama-compatible model. Tested with:

- **qwen2.5:7b** - Recommended, good balance of speed and quality
- **llama3.1:8b** - Alternative, strong reasoning
- **mistral:7b** - Alternative, fast
- **deepseek-r1:7b** - Alternative, code-focused

Larger models (13B, 70B) will give better results but require more resources.

## 🔄 Resume Support

The tool automatically saves progress every N items (configurable). If interrupted:

1. Press `Ctrl+C` to stop
2. Run `python main.py` again to resume from checkpoint
3. Use `--reset` to start from scratch

## 📝 Discipline Detection

The tool automatically detects engineering disciplines based on keyword matching:

- **Electrical**: voltage, ampere, circuit, conductor, wiring, switchboard, earthing
- **Mechanical**: ventilation, HVAC, air conditioning, duct, fan, refrigeration
- **Fire**: fire, smoke, sprinkler, alarm, emergency, evacuation
- **Hydraulic**: water, plumbing, drainage, pipe, sanitary, sewer
- **NCC**: NCC, BCA, Building Code, Australian Standard
- **SIR**: SIR, Victorian, service rules
- **Unknown**: No clear match

## 🐛 Troubleshooting

### "Failed to call Ollama LLM: Connection refused"
- Ensure Ollama is running: `ollama serve`
- Check base URL in config.yaml matches your Ollama server

### "Model not found"
- Pull the model: `ollama pull qwen2.5:7b`
- Check available models: `ollama list`

### "Failed to parse LLM response as JSON"
- Try increasing temperature in config.yaml
- Try a different model
- Check the rejected_qna.jsonl for details

### CSV column detection errors
- Ensure CSV has headers
- Use supported column names (see "Prepare Your Data" section)
- Check for special characters or encoding issues

## 📄 License

This is a standalone tool for benchmarking LLM performance. Use it to evaluate and improve your LLM's understanding of technical documentation.

## 🤝 Contributing

This tool is designed to be:
- **Simple**: Easy to understand and modify
- **Standalone**: No external dependencies except Ollama
- **Inspectable**: All outputs in human-readable formats

Feel free to adapt it for your specific needs!

## 📚 Sample Data

The `data/` directory includes sample electrical standard clauses and tables for testing. Replace with your own standards data (electrical, mechanical, fire, hydraulic, NCC, SIR, etc.).

---

**Happy Benchmarking! 🚀**
