# Quick Start

## Installation

```bash
# Clone the repository
git clone https://github.com/epochal-capital/EpochalCapital.git
cd EpochalCapital

# Install in development mode
pip install -e ".[dev]"
```

## Running the CLI

### Interactive Mode

```bash
python -m epochal.cli
```

This opens an interactive prompt:

```
============================================================
  EPOCHAL CAPITAL - AI Investment Platform
  Private AI Companies with Liquidity Potential
============================================================

AVAILABLE COMMANDS:
----------------------------------------
  scan                      Scan market for AI investment opportunities
  liquidity                 Find companies with upcoming liquidity events
  evaluate <company>        Evaluate a specific company
  research <company>        Run comprehensive research on a company
  refresh                   Refresh research for all tracked companies
  research-status           Show research workflow status
  portfolio                 View portfolio summary
  briefing                  Run comprehensive daily briefing
  agents                    Show agent status
  thesis                    Show investment thesis
  substack [topic]          Draft a Substack article
  linkedin [topic]          Draft a LinkedIn post
  twitter [topic]           Draft a Twitter thread
  investor-update           Draft quarterly investor update
  pitch                     Draft fundraising pitch narrative
  market-commentary         Generate AI market commentary
  help                      Show this help message
  exit                      Exit the CLI

epochal>
```

### Command Line Mode

Run individual commands directly:

```bash
# Scan for opportunities
python -m epochal.cli scan

# Evaluate a specific company
python -m epochal.cli evaluate Anthropic

# Find liquidity events
python -m epochal.cli liquidity

# Run daily briefing
python -m epochal.cli briefing

# Draft content
python -m epochal.cli substack thesis
python -m epochal.cli linkedin
python -m epochal.cli twitter
```

## Common Workflows

### 1. Morning Market Scan

```bash
# Get top opportunities
python -m epochal.cli scan

# Check liquidity events
python -m epochal.cli liquidity
```

### 2. Company Deep Dive

```bash
# Evaluate against thesis
python -m epochal.cli evaluate "Lambda Labs"

# Run comprehensive research
python -m epochal.cli research "Lambda Labs"
```

### 3. Weekly Research Refresh

```bash
# Check what needs refreshing
python -m epochal.cli research-status

# Refresh all stale research
python -m epochal.cli refresh

# Force refresh everything
python -m epochal.cli refresh --force
```

### 4. Content Generation

```bash
# Draft investor update
python -m epochal.cli investor-update

# Draft social content
python -m epochal.cli linkedin
python -m epochal.cli twitter

# Draft thought leadership
python -m epochal.cli substack thesis
```

## Programmatic Usage

```python
import asyncio
from epochal.cli import EpochalCLI

async def main():
    cli = EpochalCLI()

    # Scan for opportunities
    opportunities = await cli.scan_opportunities()

    # Evaluate a company
    evaluation = await cli.evaluate_company("Anthropic")
    print(f"Score: {evaluation['scores']['total']}/100")

    # Run research
    research = await cli.research_company("Mistral AI")

    # Generate content
    article = await cli.draft_substack("AI infrastructure")

asyncio.run(main())
```

## Next Steps

- [Architecture Overview](platform/architecture.md)
- [CLI Reference](platform/cli-reference.md)
- [Agent Documentation](agents/overview.md)
