# Configuration

## Thesis Configuration

The investment thesis is configured in `epochal/core/thesis.py`.

### Scoring Weights

```python
ThesisCriteria(
    scoring_weights={
        "vertical_fit": 0.25,        # Alignment with target sectors
        "stage_fit": 0.20,           # Series B - Pre-IPO preference
        "liquidity_signals": 0.25,   # IPO/M&A indicators
        "investor_quality": 0.20,    # VC tier quality
        "valuation_attractiveness": 0.15,  # Discount to intrinsic value
    }
)
```

### Valuation Criteria

```python
ThesisCriteria(
    min_valuation_usd=100_000_000,      # $100M minimum
    max_valuation_usd=50_000_000_000,   # $50B maximum
    preferred_valuation_min=500_000_000, # $500M preferred min
    preferred_valuation_max=10_000_000_000,  # $10B preferred max
)
```

### Stage Preferences

```python
ThesisCriteria(
    preferred_stages=[
        CompanyStage.SERIES_B,
        CompanyStage.SERIES_C,
        CompanyStage.SERIES_D,
        CompanyStage.PRE_IPO,
    ]
)
```

### Vertical Priorities

```python
ThesisCriteria(
    preferred_verticals=[
        AIVertical.FOUNDATION_MODELS,
        AIVertical.AI_INFRASTRUCTURE,
        AIVertical.AI_AGENTS,
        AIVertical.DEVELOPER_TOOLS,
        AIVertical.ENTERPRISE_AI,
    ]
)
```

### Leadership Exodus Penalty

```python
ThesisCriteria(
    leadership_exodus_penalty=0.50,  # 50% penalty to liquidity score
)
```

Applied when company has tags like:
- `ceo_departed`
- `leadership_exodus`
- `gutted`
- `acqui-hire`

---

## Research Workflow Configuration

### Refresh Schedule

Recommended cron schedule for automated research:

```bash
# Monday and Thursday at 6am
0 6 * * 1,4 python scripts/scheduled_research.py
```

### Research Age Threshold

```python
# In research_workflows.py
MAX_RESEARCH_AGE_DAYS = 3  # Trigger refresh after 3 days
```

---

## Data Storage

### Portfolio Data

```
data/portfolio.json
```

Stores:
- Companies in watchlist
- Active investments
- Deals in pipeline
- Historical positions

### Research History

```
data/research_history.json
```

Stores:
- Last research date per company
- Research queries executed
- Sources found
- Research summaries

---

## Environment Variables

```bash
# Optional: Custom data directory
export EPOCHAL_DATA_DIR=/path/to/data

# Optional: API keys for integrations (planned)
export FORGE_API_KEY=xxx
export EQUITYZEN_API_KEY=xxx
```

---

## Adding Tracked Companies

Edit `epochal/agents/deal_sourcing.py`:

```python
TRACKED_AI_COMPANIES = [
    {
        "name": "New Company",
        "description": "What they do",
        "vertical": AIVertical.AI_INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_C,
        "valuation_usd": 5_000_000_000,
        "key_investors": ["Sequoia", "a16z"],
        "liquidity_signals": ["IPO discussions", "Revenue growth"],
        "tags": [],  # Optional: ["strategic_investor", "ceo_departed"]
    },
    # ... existing companies
]
```

After adding, run research:

```bash
python -m epochal.cli research "New Company"
```
