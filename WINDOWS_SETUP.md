# Windows Setup Guide

## Step-by-Step Ollama Setup for Windows

### 1. Install Ollama

**Option A: Using the Installer (Recommended)**
1. Go to: https://ollama.com/download/windows
2. Download `OllamaSetup.exe`
3. Run the installer
4. Ollama will automatically start as a Windows service

**Option B: Using Winget**
```powershell
winget install Ollama.Ollama
```

### 2. Verify Ollama is Running

Open PowerShell and check:

```powershell
# Check if Ollama service is running
Get-Service -Name "Ollama"

# Or check the process
Get-Process ollama -ErrorAction SilentlyContinue
```

If not running, start it:
```powershell
# Start Ollama service
Start-Service -Name "Ollama"

# Or manually run
ollama serve
```

### 3. Test Ollama Connection

```powershell
# Test if Ollama API is accessible
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET
```

If you get a response, Ollama is running correctly!

### 4. Pull a Model

```powershell
# Pull the default model (Qwen 2.5 7B)
ollama pull qwen2.5:7b

# Or try other models
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull deepseek-r1:7b
```

This will take a few minutes as it downloads the model (3-5 GB).

### 5. Verify the Model

```powershell
# List installed models
ollama list

# Test the model
ollama run qwen2.5:7b "Hello, can you hear me?"
```

### 6. Run the Q&A Generator

```powershell
# Go to your project directory
cd C:\Users\contr\Documents\GitHub\production-ready-Q-A-Generator

# Run the generator
python main.py
```

## Troubleshooting

### Issue: "404 Client Error: Not Found"

**Solution 1: Restart Ollama**
```powershell
# Stop and restart
Stop-Service -Name "Ollama"
Start-Service -Name "Ollama"

# Wait a few seconds, then test
Start-Sleep -Seconds 5
Invoke-WebRequest -Uri "http://localhost:11434/api/tags"
```

**Solution 2: Run Ollama manually**
```powershell
# Open a new PowerShell window and run:
ollama serve
```
Keep this window open while using the Q&A generator.

**Solution 3: Check if port 11434 is in use**
```powershell
# Check what's using port 11434
netstat -ano | findstr :11434
```

### Issue: "Model not found"

```powershell
# Pull the model first
ollama pull qwen2.5:7b

# Verify it's installed
ollama list
```

### Issue: Dependency conflicts (pydantic versions)

Your system has multiple packages requiring different pydantic versions. Two options:

**Option A: Create a virtual environment (Recommended)**
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the tool
python main.py
```

**Option B: Upgrade dependencies**
```powershell
# Upgrade to compatible versions
pip install --upgrade pydantic requests tqdm
```

### Issue: "Invalid distribution -vicorn"

This is a corrupted package warning. Fix it:
```powershell
# Find and remove the corrupted package
pip uninstall uvicorn
pip install uvicorn
```

## Quick Commands Reference

```powershell
# Check Ollama status
ollama list

# Pull a model
ollama pull qwen2.5:7b

# Test a model
ollama run qwen2.5:7b "test"

# Start Ollama service
Start-Service -Name "Ollama"

# Stop Ollama service
Stop-Service -Name "Ollama"

# Run Q&A Generator
python main.py

# Run with different model
python main.py --model llama3.1:8b

# Clear previous outputs and start fresh
python main.py --clear
```

## Recommended Setup for Clean Installation

```powershell
# 1. Create project virtual environment
cd C:\Users\contr\Documents\GitHub\production-ready-Q-A-Generator
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify Ollama is running
ollama list

# 4. If no models, pull one
ollama pull qwen2.5:7b

# 5. Test setup
python test_setup.py

# 6. Run the generator
python main.py
```

## System Requirements

- **Windows 10/11** (64-bit)
- **RAM**: 8GB minimum (16GB recommended for 7B models)
- **Disk**: 10GB free space for models
- **Python**: 3.8+ (you have 3.10, which is perfect)

## Model Recommendations

| Model | Size | RAM Needed | Speed | Quality |
|-------|------|------------|-------|---------|
| qwen2.5:7b | 4.7GB | 8GB | Fast | Excellent |
| llama3.1:8b | 4.9GB | 8GB | Fast | Excellent |
| mistral:7b | 4.1GB | 8GB | Very Fast | Good |
| deepseek-r1:7b | 4.7GB | 8GB | Fast | Excellent |

## Next Steps

1. ✅ Install Ollama
2. ✅ Start Ollama service
3. ✅ Pull a model (qwen2.5:7b recommended)
4. ✅ Test with `ollama run qwen2.5:7b "test"`
5. ✅ Run `python test_setup.py` to verify everything
6. ✅ Run `python main.py` to generate Q&A

## Support

If you still have issues:
1. Check Ollama is running: `Get-Process ollama`
2. Check the API: `Invoke-WebRequest http://localhost:11434/api/tags`
3. Check models: `ollama list`
4. Try manual start: `ollama serve` in a separate window
