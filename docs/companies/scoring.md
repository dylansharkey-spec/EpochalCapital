# Scoring Methodology

## Overview

Epochal Capital uses a quantitative scoring model to evaluate companies against our investment thesis.

## Scoring Dimensions

### 1. Vertical Fit (25%)

How well does the company align with our target verticals?

| Vertical | Score |
|----------|-------|
| Foundation Models | 100 |
| AI Infrastructure | 100 |
| AI Agents | 85 |
| Developer Tools | 75 |
| Enterprise AI | 75 |
| Creative AI | 60 |
| Other | 40 |

### 2. Stage Fit (20%)

Is the company at our preferred investment stage?

| Stage | Score |
|-------|-------|
| Pre-IPO | 100 |
| Series D+ | 90 |
| Series C | 80 |
| Series B | 70 |
| Series A | 40 |
| Seed | 20 |

### 3. Liquidity Signals (25%)

What evidence exists for near-term liquidity?

**High Score (80-100):**
- IPO filing submitted
- Banker engagement (Morgan Stanley, Goldman, etc.)
- S-1 preparation
- Secondary market activity

**Medium Score (50-79):**
- IPO discussions in press
- Strategic M&A rumors
- Secondary demand
- Advisor hiring

**Low Score (0-49):**
- No public signals
- Recent funding (unlikely near-term exit)
- Operational challenges

### 4. Investor Quality (20%)

Quality of existing investor base:

| Tier | Examples | Score |
|------|----------|-------|
| Tier 1 | Sequoia, a16z, Benchmark | 100 |
| Tier 1 Strategic | Google, Microsoft, Nvidia | 90 |
| Tier 2 | NEA, Greylock, Lightspeed | 85 |
| Tier 3 | Other institutional | 60 |
| Unknown | Limited information | 40 |

### 5. Revenue Metrics (15%)

Revenue scale and growth (when available):

| ARR Range | Score |
|-----------|-------|
| $1B+ | 100 |
| $500M-$1B | 90 |
| $100M-$500M | 80 |
| $50M-$100M | 70 |
| $10M-$50M | 50 |
| <$10M | 30 |
| Unknown | 40 |

## Score Calculation

```python
total_score = (
    vertical_score * 0.25 +
    stage_score * 0.20 +
    liquidity_score * 0.25 +
    investor_score * 0.20 +
    revenue_score * 0.15
)
```

## Penalties

### Leadership Exodus Penalty (50%)

Applied to liquidity score when:
- CEO departed to strategic investor
- Mass executive exodus
- Acqui-hire signals

```python
if company has ["ceo_departed", "leadership_exodus", "gutted"]:
    liquidity_score *= 0.50  # 50% penalty
```

## Score Interpretation

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Exceptional | Prioritize for investment |
| 80-89 | Strong | Active pursuit |
| 70-79 | Good | Monitor closely |
| 60-69 | Moderate | Watchlist |
| 50-59 | Weak | Deprioritize |
| <50 | Poor | Pass |

## Example Scoring

### Anthropic (Score: 92.5)

| Dimension | Score | Weighted |
|-----------|-------|----------|
| Vertical Fit | 100 | 25.0 |
| Stage Fit | 90 | 18.0 |
| Liquidity Signals | 95 | 23.75 |
| Investor Quality | 95 | 19.0 |
| Revenue Metrics | 90 | 13.5 |
| **Total** | | **92.5** |

### Scale AI (Score: ~55, penalized)

| Dimension | Score | Weighted |
|-----------|-------|----------|
| Vertical Fit | 75 | 18.75 |
| Stage Fit | 100 | 20.0 |
| Liquidity Signals | 30 | 7.5 (penalized 50%) |
| Investor Quality | 90 | 18.0 |
| Revenue Metrics | 80 | 12.0 |
| **Total** | | **~55** |

*Leadership exodus penalty applied due to CEO departure to Meta.*
