# CLI Reference

## Overview

The Epochal CLI provides both interactive and command-line access to the platform.

```bash
# Interactive mode
python -m epochal.cli

# Command mode
python -m epochal.cli <command> [args]
```

---

## Deal Sourcing Commands

### `scan`

Scan market for AI investment opportunities.

```bash
python -m epochal.cli scan
```

**Output:**
- Companies scanned count
- Companies matching thesis count
- Top opportunities with scores, valuations, and signals

---

### `liquidity`

Find companies with upcoming liquidity events.

```bash
python -m epochal.cli liquidity
```

**Output:**
- Liquidity candidates count
- Ranked list with liquidity scores
- Likely event types (IPO, M&A, Secondary)
- Key signals

---

### `evaluate <company>`

Evaluate a specific company against investment thesis.

```bash
python -m epochal.cli evaluate Anthropic
python -m epochal.cli evaluate "Lambda Labs"
```

**Output:**
- Company details (vertical, stage, valuation)
- Score breakdown by dimension
- Total score
- Investment recommendation
- Analysis summary

---

## Research Commands

### `research <company>`

Run comprehensive research on a company.

```bash
python -m epochal.cli research "Mistral AI"
```

**Output:**
- Research queries generated
- Research recorded confirmation
- Sources found

---

### `refresh [--force]`

Refresh research for all tracked companies.

```bash
# Refresh stale research (>3 days old)
python -m epochal.cli refresh

# Force refresh all companies
python -m epochal.cli refresh --force
```

**Output:**
- Companies tracked count
- Recently researched count
- Needing refresh count
- Refresh progress

---

### `research-status`

Show research workflow status.

```bash
python -m epochal.cli research-status
```

**Output:**
- Total companies tracked
- Recently researched count
- Needing refresh count
- Last full refresh timestamp
- Recommended cron schedule

---

## Portfolio Commands

### `portfolio`

View portfolio summary.

```bash
python -m epochal.cli portfolio
```

**Output:**
- Total invested
- Current value
- Unrealized gains/losses
- Position summary

---

### `briefing`

Run comprehensive daily briefing across all agents.

```bash
python -m epochal.cli briefing
```

**Output:**
- Top opportunities
- Market outlook
- Portfolio recommendations
- Action items

---

## Investor Relations Commands

### `substack [topic]`

Draft a Substack article.

```bash
python -m epochal.cli substack
python -m epochal.cli substack thesis
python -m epochal.cli substack "AI infrastructure"
```

**Default topic:** `thesis`

**Output:**
- Word count
- Estimated read time
- Recommended publish time
- Full article draft

---

### `linkedin [topic]`

Draft a LinkedIn post.

```bash
python -m epochal.cli linkedin
python -m epochal.cli linkedin "AI market trends"
```

**Default topic:** `AI market`

**Output:**
- Character count
- Recommended publish time
- Post content
- Suggested hashtags

---

### `twitter [topic]`

Draft a Twitter/X thread.

```bash
python -m epochal.cli twitter
python -m epochal.cli twitter "AI IPOs 2026"
```

**Default topic:** `AI IPOs`

**Output:**
- Tweet count
- Total characters
- Recommended publish time
- Full thread (numbered tweets)

---

### `investor-update`

Draft quarterly investor update.

```bash
python -m epochal.cli investor-update
```

**Output:**
- Update type
- Sections included
- Word count
- Full LP letter draft

---

### `pitch`

Draft fundraising pitch narrative.

```bash
python -m epochal.cli pitch
```

**Output:**
- Pitch type
- Recommended sections
- Word count
- Full pitch narrative

---

### `market-commentary`

Generate AI market commentary.

```bash
python -m epochal.cli market-commentary
```

**Output:**
- Commentary type
- Sections
- Full market analysis

---

## System Commands

### `agents`

Show status of all registered agents.

```bash
python -m epochal.cli agents
```

**Output:**
- Agent name and role
- Active status
- Capabilities list
- Tasks completed count

---

### `thesis`

Display investment thesis summary.

```bash
python -m epochal.cli thesis
```

---

### `help`

Show available commands.

```bash
python -m epochal.cli help
```

---

### `exit` / `quit`

Exit interactive mode.

```
epochal> exit
```
