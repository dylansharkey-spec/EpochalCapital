# Investment Thesis

## Core Thesis

**Epochal Capital invests in private AI companies with upcoming liquidity events.**

We believe:

1. **AI is transformational, not incremental** — The companies we track are building new categories, not features
2. **Liquidity windows are opening** — After years of private market growth, IPOs and M&A are accelerating
3. **Information asymmetry creates alpha** — The private AI market is opaque; systematic research provides edge

## Target Profile

### Company Characteristics

| Criteria | Range | Preferred |
|----------|-------|-----------|
| **Valuation** | $100M - $50B | $500M - $10B |
| **Stage** | Series B - Pre-IPO | Series C - Pre-IPO |
| **Revenue** | $10M+ ARR | $50M+ ARR |
| **Liquidity Timeline** | 12-36 months | 18-24 months |
| **Discount to Last Round** | 10%+ | 25%+ |

### Target Verticals

| Vertical | Examples | Priority |
|----------|----------|----------|
| Foundation Models | Anthropic, Mistral, Cohere | High |
| AI Infrastructure | Databricks, Cerebras, Lambda | High |
| AI Agents | Perplexity, Adept | Medium-High |
| Developer Tools | Hugging Face, Replit | Medium |
| Enterprise AI | Glean, Scale AI | Medium |
| Creative AI | Runway, Stability AI | Medium |

## Scoring Model

Our proprietary scoring model evaluates companies across five dimensions:

### Scoring Weights

```
Liquidity Signals     25%  — IPO filings, banker engagement, secondary activity
Vertical Fit          25%  — Alignment with target sectors
Investor Quality      20%  — Tier-one VC backing, strategic investors
Stage Fit             20%  — Series B through Pre-IPO preference
Revenue Metrics       15%  — ARR scale and growth rate (when available)
```

### Score Interpretation

| Score | Interpretation | Action |
|-------|----------------|--------|
| 90-100 | Exceptional fit | Prioritize for investment |
| 80-89 | Strong fit | Active pursuit |
| 70-79 | Good fit | Monitor closely |
| 60-69 | Moderate fit | Watchlist |
| <60 | Poor fit | Deprioritize |

## Risk Factors

### Leadership Exodus Penalty

We apply a **50% penalty** to liquidity scores when we detect signals that a company is being "gutted" by a strategic investor:

- CEO departure to join strategic investor
- Mass executive exodus
- Acqui-hire signals

This is distinct from healthy strategic investment, which we view positively.

### Other Red Flags

- Customer concentration >50%
- Unclear path to profitability
- Regulatory headwinds
- Key person risk
- Competitive moat erosion

## Thesis Configuration

The thesis is configurable via `epochal/core/thesis.py`:

```python
from epochal.core.thesis import ThesisCriteria

criteria = ThesisCriteria(
    preferred_stages=[CompanyStage.SERIES_C, CompanyStage.SERIES_D, CompanyStage.PRE_IPO],
    preferred_verticals=[AIVertical.FOUNDATION_MODELS, AIVertical.AI_INFRASTRUCTURE],
    min_valuation_usd=100_000_000,
    max_valuation_usd=50_000_000_000,
    preferred_liquidity_months=18,
    scoring_weights={
        "vertical_fit": 0.25,
        "stage_fit": 0.20,
        "liquidity_signals": 0.25,
        "investor_quality": 0.20,
        "valuation_attractiveness": 0.15,
    },
)
```
