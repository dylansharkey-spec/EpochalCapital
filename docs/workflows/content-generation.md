# Content Generation

## Overview

The content generation workflow uses the Investor Relations Agent to create marketing and LP communications.

## Content Types

| Type | Command | Use Case |
|------|---------|----------|
| Substack | `substack [topic]` | Thought leadership, thesis explanation |
| LinkedIn | `linkedin [topic]` | Professional network engagement |
| Twitter | `twitter [topic]` | Social reach, market commentary |
| Investor Update | `investor-update` | Quarterly LP communications |
| Pitch | `pitch` | Fundraising materials |
| Commentary | `market-commentary` | Market analysis |

## Workflow

```
Topic Selection → IR Agent → Template Matching → Portfolio Context → Draft Output
```

### 1. Topic Selection

Topics can be:
- **Explicit**: `substack "AI infrastructure"`
- **Default**: `substack` (uses "thesis")
- **Category-based**: thesis, market, process, portfolio, agents, infrastructure, liquidity

### 2. Template Matching

The agent matches topics to pre-built templates:

```python
titles = {
    "thesis": "Why We're Betting Big on AI Liquidity Events",
    "market": "The AI Investment Landscape: Where We See Opportunity",
    "process": "Inside Epochal Capital: How We Source AI Deals",
    "portfolio": "Our AI Portfolio: Thesis in Action",
    "agents": "Building an AI-Native Investment Firm",
}
```

### 3. Portfolio Context

Drafts automatically include current metrics:
- Companies tracked
- Active positions
- Performance figures
- Pipeline status

### 4. Draft Output

Each draft includes:
- Formatted content
- Platform-specific metadata
- Recommended publish time
- Word/character count
- Suggested hashtags

## Example Workflow

```bash
# 1. Generate investor update
python -m epochal.cli investor-update

# 2. Save to file
# (Copy output to content/update_2026_Q1.md)

# 3. Generate social promotion
python -m epochal.cli linkedin "quarterly update"
python -m epochal.cli twitter "quarterly update"

# 4. Generate long-form follow-up
python -m epochal.cli substack portfolio
```

## Content Calendar

Recommended publishing schedule:

| Day | Content |
|-----|---------|
| Monday | LinkedIn post |
| Tuesday | Substack article |
| Wednesday | Twitter thread |
| Thursday | LinkedIn post |
| Friday | Market commentary |

Quarterly:
- Investor update (end of quarter)
- Pitch refresh (as needed)
