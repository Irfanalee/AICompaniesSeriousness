# New Project Structure Documentation

## Overview

The project has been restructured into a production-grade, modular architecture with separated concerns, cost optimization, and professional development practices.

## Directory Structure

```
AICompaniesSeriousness/
├── agents/                    # Agent modules (one file per agent type)
│   ├── __init__.py
│   ├── base_agent.py         # Base class with common functionality
│   ├── lead_agent.py         # Document location agent
│   ├── company_analysis_agent.py  # Company-specific analysis sub-agents
│   └── synthesis_agent.py    # Report synthesis agent
│
├── config/                    # Configuration management
│   ├── __init__.py
│   └── settings.py           # Settings loaded from .env
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── cache.py              # Caching for cost optimization
│   ├── logger.py             # Logging utilities
│   └── token_counter.py      # Token tracking & cost estimation
│
├── .cache/                    # Cache directory (auto-created)
├── reports/                   # Generated reports (auto-created)
│
├── .env                       # Environment variables (YOU MUST CONFIGURE)
├── .env.example              # Example environment file
├── .gitignore                # Git exclusions
├── requirements.txt          # Python dependencies
│
├── orchestrator.py           # Main orchestration logic
├── main.py                   # Entry point (executable)
│
└── [documentation files]     # README, guides, etc.
```

## Key Improvements

### 1. Modular Architecture
- Each agent in its own file
- Clear separation of concerns
- Easy to maintain and extend

### 2. Cost Optimization
- **Token tracking**: Monitor usage per agent
- **Caching**: Avoid re-analyzing same data (24-hour TTL)
- **Model selection**: Use cheaper models (Haiku) for simple tasks
- **Cost estimation**: See estimated cost after each run

### 3. Configuration Management
- All settings in `.env` file
- Easy to change models, token limits, features
- Environment-based configuration

### 4. Production Features
- **Logging**: Comprehensive logging throughout
- **Error handling**: Retry logic with exponential backoff
- **Caching**: File-based caching system
- **Token counting**: Track and estimate costs
- **CLI interface**: Rich command-line options

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env and set your API key
nano .env
# or
code .env
```

**Required**: Set `ANTHROPIC_API_KEY` in `.env`

### 3. Run Analysis
```bash
# Basic usage (analyzes default 6 companies)
python main.py

# Analyze specific companies
python main.py --companies "Microsoft" "Google" "Amazon"

# Custom output filename
python main.py --output my_report.md

# Quiet mode
python main.py --quiet

# Clear cache before running
python main.py --clear-cache

# See all options
python main.py --help
```

## Configuration Options (.env file)

### API Configuration
```bash
ANTHROPIC_API_KEY=your-key-here
```

### Model Selection (Cost Optimization)
```bash
# Use cheaper Haiku for document location (simple task)
LEAD_AGENT_MODEL=claude-haiku-4-5-20250929

# Use Sonnet for analysis (balanced)
SUB_AGENT_MODEL=claude-sonnet-4-5-20250929

# Use Sonnet for synthesis (important output)
SYNTHESIS_AGENT_MODEL=claude-sonnet-4-5-20250929
```

**Cost Impact**:
- Haiku: $0.80/M input, $4.00/M output (cheapest)
- Sonnet: $3.00/M input, $15.00/M output (balanced)
- Opus: $15.00/M input, $75.00/M output (most capable)

### Token Limits (Control Costs)
```bash
MAX_TOKENS_LEAD_AGENT=2000    # Document location
MAX_TOKENS_SUB_AGENT=3000     # Company analysis
MAX_TOKENS_SYNTHESIS=6000     # Report creation
```

Lower limits = lower costs, but may truncate responses.

### Features
```bash
ENABLE_CACHING=true           # Cache responses (saves money)
PARALLEL_EXECUTION=false      # Future: parallel sub-agents
VERBOSE=true                  # Detailed console output
```

### Output
```bash
OUTPUT_DIR=reports            # Where to save reports
CACHE_DIR=.cache             # Cache storage location
```

## Agent Architecture

### BaseAgent
**File**: `agents/base_agent.py`

Common functionality for all agents:
- API calls with retry logic
- Caching support
- Token tracking
- JSON extraction
- Error handling

### LeadAgent
**File**: `agents/lead_agent.py`

**Purpose**: Locate 10-K filings and earnings transcripts

**Model**: Haiku (cheap, simple task)

**Token limit**: 2,000

**Caching**: Yes (documents don't change often)

### CompanyAnalysisAgent
**File**: `agents/company_analysis_agent.py`

**Purpose**: Analyze individual company documents

**Model**: Sonnet (balanced)

**Token limit**: 3,000 per company

**Caching**: Yes

**Tasks**:
- Count "Generative AI" mentions
- Count "Machine Learning" mentions
- Extract AI CapEx spending
- Find CFO quotes on ROI

### SynthesisAgent
**File**: `agents/synthesis_agent.py`

**Purpose**: Create comprehensive cross-company report

**Model**: Sonnet (important output)

**Token limit**: 6,000

**Caching**: No (always generate fresh report)

## Cost Optimization Features

### 1. Intelligent Caching
```python
# Responses cached for 24 hours
# Same query = no API call = $0 cost

# Clear cache when needed
python main.py --clear-cache

# Clear only expired
python main.py --clear-expired-cache
```

### 2. Model Selection
```
Task Complexity → Model Choice → Cost

Simple (locate docs)  → Haiku  → $0.80-4.00/M tokens
Medium (analyze)      → Sonnet → $3.00-15.00/M tokens
Complex (synthesis)   → Sonnet → $3.00-15.00/M tokens
```

### 3. Token Limits
- Strict limits prevent runaway costs
- Configurable per agent type
- Monitor actual usage

### 4. Token Tracking
After each run:
```
TOKEN USAGE SUMMARY
============================================================
Total Tokens: 25,430
  Input:  18,200
  Output: 7,230

By Agent:
  LeadAgent:
    Input:  1,500
    Output: 500
  OracleAnalyst:
    Input:  2,800
    Output: 1,200
  ...

Estimated Cost: $0.32
============================================================
```

## Usage Examples

### Basic Analysis
```bash
python main.py
```

### Custom Companies
```bash
python main.py --companies "Microsoft" "Apple" "Amazon" "Google"
```

### With Custom Output
```bash
python main.py --output tech_giants_analysis.md
```

### Clear Cache First
```bash
python main.py --clear-cache --companies "Oracle" "SAP"
```

### Quiet Mode
```bash
python main.py --quiet
```

### Help
```bash
python main.py --help
```

## Output

### Report Location
```
reports/ai_investment_analysis_20241208_143022.md
```

### Report Contains
1. Metadata header
2. Executive Summary
3. Talk vs Walk Comparison Table
4. Key Findings
5. CFO Perspectives
6. Investment Patterns
7. Conclusions & Recommendations

### Console Output (Verbose Mode)
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
      • AI CapEx: $2.1B in cloud infrastructure and AI-enabled...

  ...

[PHASE 3] Report Synthesis
--------------------------------------------------------------------------------
  ✓ Report synthesis complete

================================================================================
ANALYSIS COMPLETE
================================================================================

✓ Report saved to: reports/ai_investment_analysis_20241208_143022.md
✓ Time elapsed: 45.3 seconds

[TOKEN USAGE SUMMARY shown here]
```

## Extending the System

### Add a New Agent Type

1. Create new file in `agents/`:
```python
# agents/risk_analysis_agent.py
from .base_agent import BaseAgent

class RiskAnalysisAgent(BaseAgent):
    def __init__(self, client, cache=None):
        super().__init__(
            name="RiskAnalyzer",
            role="Analyze AI-related risks...",
            agent_type="sub",  # or create new type
            client=client,
            cache=cache
        )

    def analyze_risks(self, company_data):
        # Your logic here
        pass
```

2. Update `agents/__init__.py`:
```python
from .risk_analysis_agent import RiskAnalysisAgent
__all__ = [..., 'RiskAnalysisAgent']
```

3. Use in orchestrator.py

### Add New Configuration

1. Add to `.env`:
```bash
RISK_ANALYSIS_ENABLED=true
```

2. Add to `config/settings.py`:
```python
RISK_ANALYSIS_ENABLED: bool = os.getenv('RISK_ANALYSIS_ENABLED', 'false').lower() == 'true'
```

3. Use in code:
```python
if Settings.RISK_ANALYSIS_ENABLED:
    # Run risk analysis
    pass
```

## Cost Estimation

### Per Analysis (6 companies)

**With Caching Disabled**:
- Lead Agent (Haiku): ~1,500 tokens → ~$0.01
- 6 Sub-Agents (Sonnet): ~18,000 tokens → ~$0.25
- Synthesis (Sonnet): ~6,000 tokens → ~$0.08
- **Total**: ~$0.34

**With Caching Enabled** (subsequent runs):
- Only uncached parts charged
- Typical savings: 60-80%
- **Total**: ~$0.10-$0.15

### Cost per Company
- ~$0.04-$0.06 per company analyzed
- Scales linearly

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
Edit `.env` file and set your API key.

### "No module named 'anthropic'"
```bash
pip install -r requirements.txt
```

### High costs
1. Enable caching: `ENABLE_CACHING=true`
2. Use Haiku where possible
3. Lower token limits
4. Reduce companies analyzed

### Cache not working
Check:
1. `ENABLE_CACHING=true` in `.env`
2. `.cache/` directory exists (auto-created)
3. Cache not expired (24-hour TTL)

### Slow performance
1. Increase token limits (faster responses)
2. Enable parallel execution (future feature)
3. Use faster model (Haiku)

## Migration from Old Structure

### Old Files (Deprecated)
- ~~`multi_agent_research.py`~~ → Now: modular `agents/` folder
- ~~`multi_agent_research_with_fetch.py`~~ → Now: `main.py` + `orchestrator.py`
- ~~`run_analysis.sh`~~ → Now: `python main.py`

### What to Delete (Optional)
You can safely delete:
- `multi_agent_research.py`
- `multi_agent_research_with_fetch.py`
- `run_analysis.sh`

Keep:
- All documentation files
- `.env` (configure it!)
- New modular structure

## Best Practices

### 1. Always Use .env
Never hardcode API keys in code.

### 2. Enable Caching for Development
Saves money during testing.

### 3. Monitor Token Usage
Check the summary after each run.

### 4. Start Small
Test with 1-2 companies before running full analysis.

### 5. Use Version Control
```bash
git add agents/ config/ utils/ orchestrator.py main.py
git commit -m "Production-grade multi-agent system"
```

### 6. Clear Cache Periodically
```bash
python main.py --clear-expired-cache
```

## Support

- **Documentation**: See README.md, USAGE_GUIDE.md
- **Architecture**: See ARCHITECTURE.md
- **Examples**: See demo_output.md
- **This guide**: For new structure specifics

---

**Version**: 2.0 (Production-grade Modular Architecture)
**Date**: December 8, 2024
**Status**: ✅ Ready for Production Use
