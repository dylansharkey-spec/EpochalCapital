# Portfolio Agent

## Overview

The Portfolio Agent manages position tracking, performance reporting, and portfolio analytics.

**Role:** `AgentRole.PORTFOLIO_MANAGER`

## Capabilities

| Capability | Description |
|------------|-------------|
| `portfolio_summary` | Generate portfolio overview |
| `track_position` | Add/update position |
| `generate_recommendations` | Investment recommendations |
| `risk_analysis` | Portfolio risk metrics |

## Usage

```bash
# View portfolio summary
python -m epochal.cli portfolio
```

## Portfolio Summary Output

```python
{
    "companies_tracked": 22,
    "deals_in_pipeline": 3,
    "active_positions": 2,
    "exited_positions": 0,
    "total_invested_usd": 5000000,
    "current_value_usd": 6200000,
    "unrealized_gains_usd": 1200000,
    "realized_gains_usd": 0,
    "total_return_pct": 24.0,
}
```

## Data Storage

Portfolio data persisted to `data/portfolio.json`:

- Companies in watchlist
- Deal pipeline status
- Investment positions
- Historical transactions
