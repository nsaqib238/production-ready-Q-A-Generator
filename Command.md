## 🪟 Windows Setup - PowerShell Commands

## Step 1: Install Ollama on Windows

Download and install:
- Go to: https://ollama.com/download/windows
- Download `OllamaSetup.exe`
- Run the installer (it will install and start automatically)

Or use Windows Package Manager:

```powershell
winget install Ollama.Ollama
```

## Step 2: Check if Ollama is Running

```powershell
# Check if Ollama process is running
Get-Process ollama -ErrorAction SilentlyContinue

# Optional: on some installs Ollama registers as a Windows service.
# If this returns "service not found", that's OK.
Get-Service -Name "Ollama" -ErrorAction SilentlyContinue
```

If not running:

```powershell
# Start the Ollama server in this terminal (leave it running)
ollama serve
```

## Step 3: Test Ollama Connection

```powershell
# Test if API responds
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET
```

## Step 4: Install a Model

```powershell
# Pull the qwen model (takes 5-10 minutes, ~5GB download)
ollama pull qwen2.5:7b

# Check installed models
ollama list
```

## Step 5: Test the Model

```powershell
# Quick test
ollama run qwen2.5:7b "Say hello"
```

Press `Ctrl+D` or type `/bye` to exit the test.

## Step 6: Run Your Q&A Generator

```powershell
# Navigate to your project
cd C:\Users\contr\Documents\GitHub\production-ready-Q-A-Generator

# Run it
python main.py
```

## 🔧 Fix Dependency Issues (Recommended)

Your system may have conflicting package versions. Use a virtual environment:

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

When done, deactivate:

```powershell
deactivate
```

## 📋 Quick Troubleshooting

If Ollama won't start:

```powershell
# If you installed a service, try restarting it (ignore errors if it doesn't exist)
Restart-Service -Name "Ollama" -ErrorAction SilentlyContinue

# Otherwise, start the server manually (leave it running)
ollama serve

# Wait a moment for it to bind to port 11434
Start-Sleep -Seconds 2

# Test again
Invoke-WebRequest -Uri "http://localhost:11434/api/tags"
```

If you get "command not found" for `ollama`:

```powershell
# Check if PowerShell can find it
Get-Command ollama

# If needed, add default install location to PATH for the current session
$env:Path += ";$env:LOCALAPPDATA\Programs\Ollama"

# Re-check
Get-Command ollama
```

---

## Step 1: Install Ollama

```powershell
# Download and install from:
# https://ollama.com/download/windows

# Or use winget:
winget install Ollama.Ollama
```

## Step 2: Verify Ollama is Running

```powershell
# Check if running
Get-Process ollama -ErrorAction SilentlyContinue

# Optional: check service (some installs won't have one)
Get-Service -Name "Ollama" -ErrorAction SilentlyContinue
```

## Step 3: Pull a Model

```powershell
# Pull the model (will take a few minutes)
ollama pull qwen2.5:7b
```

## Step 4: Test It

```powershell
# Test the model works
ollama run qwen2.5:7b "Hello"

# Test the API
Invoke-WebRequest -Uri "http://localhost:11434/api/tags"
```

## Step 5: Run Your Q&A Generator

```powershell
cd C:\Users\contr\Documents\GitHub\production-ready-Q-A-Generator
python main.py
```

## 💡 Recommended: Use Virtual Environment

To avoid the pydantic version conflicts:

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
