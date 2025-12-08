# Setup Guide - Production-Grade Multi-Agent System

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `anthropic` - Claude API client
- `python-dotenv` - Environment variable management

### Step 2: Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env
# or use your preferred editor
```

**Edit `.env` file**:
```bash
ANTHROPIC_API_KEY=your-actual-api-key-here
```

Get your API key from: https://console.anthropic.com/

### Step 3: Run Analysis
```bash
python main.py
```

That's it! The system will:
1. Locate documents for 6 companies
2. Analyze AI investments
3. Generate a comprehensive report
4. Save to `reports/` directory
5. Display token usage and cost estimate

---

## 📋 Detailed Setup

### System Requirements

- **Python**: 3.8 or higher
- **pip**: Latest version recommended
- **Internet**: Required for API calls
- **API Key**: Anthropic API key

### Installation Steps

#### 1. Clone/Navigate to Project
```bash
cd /Users/irfan/Documents/AI_Projects/AICompaniesSeriousness
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment

**Option A: Copy example file**
```bash
cp .env.example .env
```

Then edit `.env`:
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional (defaults are optimized)
DEFAULT_MODEL=claude-sonnet-4-5-20250929
LEAD_AGENT_MODEL=claude-haiku-4-5-20250929
SUB_AGENT_MODEL=claude-sonnet-4-5-20250929
SYNTHESIS_AGENT_MODEL=claude-sonnet-4-5-20250929

MAX_TOKENS_LEAD_AGENT=2000
MAX_TOKENS_SUB_AGENT=3000
MAX_TOKENS_SYNTHESIS=6000

ENABLE_CACHING=true
VERBOSE=true
```

**Option B: Set environment variable directly**
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

#### 5. Verify Setup
```bash
# Check Python version
python --version
# Should be 3.8+

# Check dependencies installed
pip list | grep anthropic
pip list | grep python-dotenv

# Check .env file exists
cat .env | grep ANTHROPIC_API_KEY
```

---

## 🎯 First Run

### Test with Default Companies
```bash
python main.py
```

Expected output:
```
================================================================================
MULTI-AGENT RESEARCH SYSTEM
AI Investment Analysis: Talk vs Walk
================================================================================

[PHASE 1] Document Location
--------------------------------------------------------------------------------
  ✓ Located documents for 6 companies

[PHASE 2] Company Analysis
--------------------------------------------------------------------------------

  [1/6] Analyzing Oracle...
      • Gen AI mentions: 42
      • ML mentions: 67
      • AI CapEx: $2.1B in cloud infrastructure...

  [2/6] Analyzing IBM...
  ...

[PHASE 3] Report Synthesis
--------------------------------------------------------------------------------
  ✓ Report synthesis complete

================================================================================
ANALYSIS COMPLETE
================================================================================

✓ Report saved to: reports/ai_investment_analysis_20241208_143022.md
✓ Time elapsed: 45.3 seconds

TOKEN USAGE SUMMARY
============================================================
Total Tokens: 25,430
  Input:  18,200
  Output: 7,230

Estimated Cost: $0.32
============================================================
```

### Check the Report
```bash
cat reports/ai_investment_analysis_*.md
```

---

## ⚙️ Configuration Guide

### Cost Optimization Settings

#### 1. Model Selection (Biggest Cost Impact)

**Ultra Low Cost** (~$0.15 per analysis):
```bash
LEAD_AGENT_MODEL=claude-haiku-4-5-20250929
SUB_AGENT_MODEL=claude-haiku-4-5-20250929
SYNTHESIS_AGENT_MODEL=claude-haiku-4-5-20250929
```

**Balanced** (~$0.32 per analysis) - **RECOMMENDED**:
```bash
LEAD_AGENT_MODEL=claude-haiku-4-5-20250929
SUB_AGENT_MODEL=claude-sonnet-4-5-20250929
SYNTHESIS_AGENT_MODEL=claude-sonnet-4-5-20250929
```

**High Quality** (~$0.85 per analysis):
```bash
LEAD_AGENT_MODEL=claude-sonnet-4-5-20250929
SUB_AGENT_MODEL=claude-opus-4-5-20251101
SYNTHESIS_AGENT_MODEL=claude-opus-4-5-20251101
```

#### 2. Token Limits

**Strict (Low Cost)**:
```bash
MAX_TOKENS_LEAD_AGENT=1500
MAX_TOKENS_SUB_AGENT=2500
MAX_TOKENS_SYNTHESIS=5000
```

**Standard (Recommended)**:
```bash
MAX_TOKENS_LEAD_AGENT=2000
MAX_TOKENS_SUB_AGENT=3000
MAX_TOKENS_SYNTHESIS=6000
```

**Generous (High Quality)**:
```bash
MAX_TOKENS_LEAD_AGENT=3000
MAX_TOKENS_SUB_AGENT=4000
MAX_TOKENS_SYNTHESIS=8000
```

#### 3. Caching (Always Enable for Dev)

```bash
ENABLE_CACHING=true  # Saves 60-80% on repeat runs
CACHE_DIR=.cache
```

### Feature Flags

```bash
VERBOSE=true              # Show detailed progress
PARALLEL_EXECUTION=false  # Future feature
```

### Output Settings

```bash
OUTPUT_DIR=reports        # Where reports are saved
```

---

## 🧪 Testing Your Setup

### 1. Test with Single Company
```bash
python main.py --companies "Oracle" --quiet
```

Should complete in ~10 seconds, cost ~$0.05.

### 2. Test Caching
```bash
# First run (uses API)
python main.py --companies "IBM"

# Second run (uses cache, free)
python main.py --companies "IBM"
```

Second run should be instant and show no token usage.

### 3. Test Custom Output
```bash
python main.py --companies "Cisco" "SAP" --output test_report.md
```

Check `reports/test_report.md` exists.

### 4. Test Cache Management
```bash
# Clear all cache
python main.py --clear-cache-only

# Clear expired only
python main.py --clear-expired-cache
```

---

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"

**Solution**:
```bash
# Check if .env file exists
ls -la .env

# Check if API key is set
cat .env | grep ANTHROPIC_API_KEY

# If not set, edit .env:
nano .env
# Add: ANTHROPIC_API_KEY=your-key-here
```

### Error: "No module named 'anthropic'"

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or install directly
pip install anthropic python-dotenv
```

### Error: "Permission denied: ./main.py"

**Solution**:
```bash
# Make executable
chmod +x main.py

# Or run with python explicitly
python main.py
```

### High API Costs

**Solutions**:
1. Enable caching: `ENABLE_CACHING=true`
2. Use Haiku model: `SUB_AGENT_MODEL=claude-haiku-4-5-20250929`
3. Lower token limits: `MAX_TOKENS_SUB_AGENT=2000`
4. Test with fewer companies first

### Slow Performance

**Solutions**:
1. Check internet connection
2. Increase token limits
3. Use faster model (Haiku)
4. Enable caching for repeat runs

### Cache Not Working

**Check**:
```bash
# Verify caching enabled
cat .env | grep ENABLE_CACHING
# Should show: ENABLE_CACHING=true

# Check cache directory exists
ls -la .cache/

# Check for cache files
ls .cache/
```

---

## 📊 Understanding Costs

### Pricing (as of Dec 2024)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Haiku | $0.80 | $4.00 |
| Sonnet | $3.00 | $15.00 |
| Opus | $15.00 | $75.00 |

### Typical Usage (6 companies)

**Recommended Configuration**:
- Lead (Haiku): 1,500 tokens → $0.01
- 6x Analysis (Sonnet): 18,000 tokens → $0.25
- Synthesis (Sonnet): 6,000 tokens → $0.08
- **Total**: ~$0.34 per run

**With Caching** (subsequent runs):
- Cached responses: $0
- Only new data charged
- **Typical**: ~$0.10 per run

### Cost Per Company
- 1 company: ~$0.06
- 5 companies: ~$0.28
- 10 companies: ~$0.55
- 20 companies: ~$1.10

---

## 🔧 Advanced Configuration

### Custom Cache Duration

Edit `orchestrator.py`:
```python
self.cache = Cache(Settings.CACHE_DIR, ttl_hours=48)  # 48 hours
```

### Parallel Execution (Future)

Set in `.env`:
```bash
PARALLEL_EXECUTION=true
```

Currently sequential to avoid rate limits. Will be async in future.

### Custom Logging Level

In `main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## ✅ Verification Checklist

Before running production analysis:

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured
- [ ] `ANTHROPIC_API_KEY` set in `.env`
- [ ] Tested with single company
- [ ] Caching working (tested repeat run)
- [ ] Reports generating in `reports/` directory
- [ ] Token usage summary displays correctly
- [ ] Costs are acceptable

---

## 🎓 Next Steps

After setup:

1. **Read NEW_STRUCTURE.md** - Understand the architecture
2. **Run with default companies** - See full system in action
3. **Customize companies** - Analyze your target companies
4. **Adjust settings** - Optimize for your cost/quality needs
5. **Review reports** - Check output quality
6. **Schedule runs** - Set up periodic analysis

---

## 📚 Documentation Index

- **This file**: Setup instructions
- **NEW_STRUCTURE.md**: Architecture & usage
- **README.md**: Project overview
- **QUICK_START.md**: 3-step quickstart
- **USAGE_GUIDE.md**: Detailed usage
- **ARCHITECTURE.md**: System design

---

**Setup Version**: 2.0
**Last Updated**: December 8, 2024
**Status**: ✅ Ready for Production
