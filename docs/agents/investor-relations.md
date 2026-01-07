# Investor Relations Agent

## Overview

The Investor Relations Agent handles LP communications, content creation, and fundraising support.

**Role:** `AgentRole.INVESTOR_RELATIONS`

## Capabilities

| Capability | Description | Output |
|------------|-------------|--------|
| `draft_substack` | Long-form thought leadership | ~500-800 word article |
| `draft_linkedin` | Professional network post | ~300 char post |
| `draft_twitter` | Twitter/X thread | 8-tweet thread |
| `draft_investor_update` | Quarterly LP update | Formatted letter |
| `draft_fundraising_pitch` | Pitch narrative | Investment memo |
| `generate_market_commentary` | Market analysis | Sector commentary |

## Brand Voice

The agent maintains consistent brand voice:

```python
BRAND_VOICE = {
    "name": "Epochal Capital",
    "tagline": "Investing at the AI Inflection Point",
    "positioning": "AI-focused investment fund targeting private companies with upcoming liquidity events",
    "key_themes": [
        "AI transformation of industries",
        "Liquidity-focused investing",
        "Data-driven deal sourcing",
        "Multi-agent operational excellence",
    ],
    "tone_guidelines": [
        "Authoritative but accessible",
        "Forward-looking and optimistic",
        "Data-driven and analytical",
        "Transparent about thesis and process",
    ],
}
```

## Usage

### CLI Commands

```bash
# Draft Substack article
python -m epochal.cli substack thesis
python -m epochal.cli substack "AI infrastructure"

# Draft LinkedIn post
python -m epochal.cli linkedin
python -m epochal.cli linkedin "market trends"

# Draft Twitter thread
python -m epochal.cli twitter
python -m epochal.cli twitter "AI IPOs 2026"

# Draft investor update
python -m epochal.cli investor-update

# Draft fundraising pitch
python -m epochal.cli pitch

# Generate market commentary
python -m epochal.cli market-commentary
```

### Programmatic Usage

```python
from epochal.agents.investor_relations import InvestorRelationsAgent
from epochal.agents.base import AgentTask, AgentRole

agent = InvestorRelationsAgent(portfolio=portfolio)

# Draft content
task = AgentTask(
    name="Draft LinkedIn",
    description="Draft LinkedIn post",
    agent_role=AgentRole.INVESTOR_RELATIONS,
    input_data={
        "capability": "draft_linkedin",
        "topic": "AI infrastructure",
    },
)
result = await agent.execute_task(task)
```

## Content Types

### Substack Article

Long-form thought leadership (500-800 words):
- Investment thesis explanations
- Market analysis
- Portfolio insights
- Process deep-dives

**Best publish time:** Tuesday or Thursday, 10am EST

### LinkedIn Post

Professional network engagement (~300 chars):
- Market observations
- Company highlights
- Thesis updates
- Thought leadership

**Best publish time:** Tuesday-Thursday, 8-10am local

### Twitter Thread

8-tweet format for social reach:
- Numbered insights
- Data points and rankings
- Clear call-to-action

**Best publish time:** Weekdays 12-1pm or 5-6pm EST

### Investor Update

Quarterly LP communication:
- Executive summary
- Portfolio performance
- Deal pipeline
- Market commentary
- Outlook

### Fundraising Pitch

Investment memo structure:
- Opportunity overview
- Investment thesis
- Competitive advantage
- Team and track record
- Terms

## Output Format

All drafts return a `ContentDraft` object:

```python
{
    "draft": {
        "content_type": "linkedin_post",
        "title": "",
        "body": "...",
        "summary": "...",
        "hashtags": ["AI", "Investing", "VentureCapital"],
        "call_to_action": "Follow for updates",
        "target_audience": "Finance professionals",
        "tone": "professional",
        "word_count": 150,
    },
    "platform": "LinkedIn",
    "recommended_publish_time": "Tuesday-Thursday, 8-10am",
    "character_count": 892,
}
```
