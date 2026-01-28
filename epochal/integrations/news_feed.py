"""
News Feed Monitor for Epochal Capital.

Monitors news sources for material events affecting tracked companies.
Provides real-time intelligence on funding, IPOs, M&A, and leadership changes.
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Callable, Optional


class EventType(str, Enum):
    """Types of material events."""
    FUNDING_ROUND = "funding_round"
    IPO_FILING = "ipo_filing"
    IPO_PRICING = "ipo_pricing"
    ACQUISITION = "acquisition"
    MERGER = "merger"
    LEADERSHIP_CHANGE = "leadership_change"
    LAYOFFS = "layoffs"
    PRODUCT_LAUNCH = "product_launch"
    PARTNERSHIP = "partnership"
    REGULATORY = "regulatory"
    EARNINGS = "earnings"
    SECONDARY_ACTIVITY = "secondary_activity"
    VALUATION_CHANGE = "valuation_change"


class EventSeverity(str, Enum):
    """Severity/importance of event."""
    CRITICAL = "critical"  # Immediate action needed
    HIGH = "high"          # Important, review today
    MEDIUM = "medium"      # Notable, review soon
    LOW = "low"            # Informational


@dataclass
class MaterialEvent:
    """A material event detected from news monitoring."""
    id: str
    company_name: str
    event_type: EventType
    severity: EventSeverity
    headline: str
    summary: str
    source: str
    source_url: str
    published_at: datetime
    detected_at: datetime = field(default_factory=datetime.utcnow)
    valuation_impact: Optional[float] = None  # Estimated % impact
    action_required: bool = False
    tags: list[str] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "headline": self.headline,
            "summary": self.summary,
            "source": self.source,
            "source_url": self.source_url,
            "published_at": self.published_at.isoformat(),
            "detected_at": self.detected_at.isoformat(),
            "valuation_impact": self.valuation_impact,
            "action_required": self.action_required,
            "tags": self.tags,
        }


@dataclass
class NewsSource:
    """Configuration for a news source."""
    name: str
    source_type: str  # rss, api, scraper
    url: str
    priority: int = 1  # 1 = highest priority
    refresh_interval_minutes: int = 15
    api_key: Optional[str] = None
    enabled: bool = True


class NewsFeedMonitor:
    """
    Monitors news sources for material events.

    Features:
    - Multi-source news aggregation
    - Event detection and classification
    - Relevance scoring
    - Alert triggering
    """

    # Keywords for event detection
    EVENT_KEYWORDS = {
        EventType.FUNDING_ROUND: [
            "raised", "funding", "series", "valuation", "investment",
            "capital", "funding round", "led by", "participated",
        ],
        EventType.IPO_FILING: [
            "s-1", "ipo filing", "confidential filing", "sec filing",
            "going public", "ipo preparation", "prospectus",
        ],
        EventType.IPO_PRICING: [
            "ipo priced", "ipo price", "pricing", "shares offered",
            "trading debut", "began trading", "opened at",
        ],
        EventType.ACQUISITION: [
            "acquired", "acquisition", "bought", "purchase", "deal",
            "takeover", "acquiring", "to acquire",
        ],
        EventType.LEADERSHIP_CHANGE: [
            "ceo", "cfo", "cto", "appointed", "resigned", "stepped down",
            "departure", "joins", "named", "executive",
        ],
        EventType.LAYOFFS: [
            "layoffs", "job cuts", "workforce reduction", "restructuring",
            "downsizing", "let go", "laid off",
        ],
        EventType.PARTNERSHIP: [
            "partnership", "partnered", "collaboration", "alliance",
            "joint venture", "teamed up", "strategic partnership",
        ],
        EventType.REGULATORY: [
            "regulatory", "investigation", "probe", "ftc", "doj",
            "antitrust", "compliance", "fine", "penalty",
        ],
        EventType.SECONDARY_ACTIVITY: [
            "secondary", "tender offer", "buyback", "share sale",
            "block trade", "private sale",
        ],
    }

    # Severity mapping based on event type
    DEFAULT_SEVERITY = {
        EventType.FUNDING_ROUND: EventSeverity.HIGH,
        EventType.IPO_FILING: EventSeverity.CRITICAL,
        EventType.IPO_PRICING: EventSeverity.CRITICAL,
        EventType.ACQUISITION: EventSeverity.CRITICAL,
        EventType.MERGER: EventSeverity.CRITICAL,
        EventType.LEADERSHIP_CHANGE: EventSeverity.HIGH,
        EventType.LAYOFFS: EventSeverity.HIGH,
        EventType.PRODUCT_LAUNCH: EventSeverity.MEDIUM,
        EventType.PARTNERSHIP: EventSeverity.MEDIUM,
        EventType.REGULATORY: EventSeverity.HIGH,
        EventType.EARNINGS: EventSeverity.MEDIUM,
        EventType.SECONDARY_ACTIVITY: EventSeverity.HIGH,
        EventType.VALUATION_CHANGE: EventSeverity.HIGH,
    }

    # Default news sources
    DEFAULT_SOURCES = [
        NewsSource(
            name="TechCrunch",
            source_type="rss",
            url="https://techcrunch.com/feed/",
            priority=1,
        ),
        NewsSource(
            name="The Information",
            source_type="api",
            url="https://www.theinformation.com",
            priority=1,
        ),
        NewsSource(
            name="Bloomberg",
            source_type="api",
            url="https://www.bloomberg.com",
            priority=1,
        ),
        NewsSource(
            name="Reuters",
            source_type="api",
            url="https://www.reuters.com",
            priority=2,
        ),
        NewsSource(
            name="CNBC",
            source_type="rss",
            url="https://www.cnbc.com/id/100727362/device/rss/rss.html",
            priority=2,
        ),
        NewsSource(
            name="SEC EDGAR",
            source_type="api",
            url="https://www.sec.gov/cgi-bin/browse-edgar",
            priority=1,
        ),
    ]

    def __init__(
        self,
        tracked_companies: Optional[list[str]] = None,
        data_dir: str = "data/news",
    ):
        self.tracked_companies = tracked_companies or []
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sources = self.DEFAULT_SOURCES.copy()
        self.events: list[MaterialEvent] = []
        self.event_handlers: list[Callable[[MaterialEvent], None]] = []

        self._event_id_counter = 0
        self._load_tracked_companies()

    def _load_tracked_companies(self):
        """Load tracked companies from deal sourcing agent."""
        if not self.tracked_companies:
            try:
                from epochal.agents.deal_sourcing import TRACKED_AI_COMPANIES
                self.tracked_companies = [c["name"] for c in TRACKED_AI_COMPANIES]
            except ImportError:
                pass

    def add_tracked_company(self, company_name: str):
        """Add a company to tracking list."""
        if company_name not in self.tracked_companies:
            self.tracked_companies.append(company_name)

    def remove_tracked_company(self, company_name: str):
        """Remove a company from tracking list."""
        if company_name in self.tracked_companies:
            self.tracked_companies.remove(company_name)

    def add_event_handler(self, handler: Callable[[MaterialEvent], None]):
        """Add a handler to be called when events are detected."""
        self.event_handlers.append(handler)

    def detect_event_type(self, text: str) -> Optional[EventType]:
        """Detect event type from text content."""
        text_lower = text.lower()

        # Check each event type's keywords
        scores = {}
        for event_type, keywords in self.EVENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[event_type] = score

        if scores:
            # Return highest scoring event type
            return max(scores, key=scores.get)
        return None

    def detect_company_mention(self, text: str) -> Optional[str]:
        """Detect if any tracked company is mentioned."""
        text_lower = text.lower()

        for company in self.tracked_companies:
            # Check for exact match or common variations
            company_lower = company.lower()
            if company_lower in text_lower:
                return company

            # Check without common suffixes
            for suffix in [" ai", " labs", " inc", " inc.", " corp"]:
                base_name = company_lower.replace(suffix, "")
                if base_name in text_lower and len(base_name) > 3:
                    return company

        return None

    def calculate_severity(
        self,
        event_type: EventType,
        text: str,
    ) -> EventSeverity:
        """Calculate event severity based on type and content."""
        base_severity = self.DEFAULT_SEVERITY.get(event_type, EventSeverity.MEDIUM)
        text_lower = text.lower()

        # Upgrade severity for certain keywords
        critical_keywords = [
            "bankruptcy", "fraud", "criminal", "sec charges",
            "emergency", "immediate", "urgent",
        ]
        if any(kw in text_lower for kw in critical_keywords):
            return EventSeverity.CRITICAL

        # Check for magnitude indicators
        large_keywords = ["billion", "major", "massive", "significant"]
        if any(kw in text_lower for kw in large_keywords):
            if base_severity == EventSeverity.MEDIUM:
                return EventSeverity.HIGH

        return base_severity

    def extract_valuation(self, text: str) -> Optional[float]:
        """Extract valuation from text."""
        patterns = [
            r"\$(\d+(?:\.\d+)?)\s*(?:billion|B)\s*valuation",
            r"valued\s+at\s+\$(\d+(?:\.\d+)?)\s*(?:billion|B)",
            r"\$(\d+(?:\.\d+)?)\s*(?:billion|B)\s*(?:valuation|value)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1)) * 1_000_000_000

        return None

    def create_event(
        self,
        company_name: str,
        event_type: EventType,
        headline: str,
        summary: str,
        source: str,
        source_url: str,
        published_at: Optional[datetime] = None,
    ) -> MaterialEvent:
        """Create a material event."""
        self._event_id_counter += 1

        severity = self.calculate_severity(event_type, headline + " " + summary)
        valuation = self.extract_valuation(headline + " " + summary)

        # Determine if action required
        action_required = severity in [EventSeverity.CRITICAL, EventSeverity.HIGH]
        if event_type in [EventType.IPO_FILING, EventType.ACQUISITION]:
            action_required = True

        event = MaterialEvent(
            id=f"evt_{self._event_id_counter:06d}",
            company_name=company_name,
            event_type=event_type,
            severity=severity,
            headline=headline,
            summary=summary,
            source=source,
            source_url=source_url,
            published_at=published_at or datetime.utcnow(),
            valuation_impact=valuation,
            action_required=action_required,
            tags=[event_type.value, company_name.lower().replace(" ", "_")],
        )

        # Add to events list
        self.events.append(event)

        # Call handlers
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception:
                pass

        return event

    def process_news_item(
        self,
        headline: str,
        content: str,
        source: str,
        source_url: str,
        published_at: Optional[datetime] = None,
    ) -> Optional[MaterialEvent]:
        """
        Process a news item and create event if relevant.

        Returns MaterialEvent if relevant to tracked companies, None otherwise.
        """
        full_text = f"{headline} {content}"

        # Check if any tracked company is mentioned
        company = self.detect_company_mention(full_text)
        if not company:
            return None

        # Detect event type
        event_type = self.detect_event_type(full_text)
        if not event_type:
            return None

        # Create and return event
        return self.create_event(
            company_name=company,
            event_type=event_type,
            headline=headline,
            summary=content[:500] if len(content) > 500 else content,
            source=source,
            source_url=source_url,
            published_at=published_at,
        )

    async def fetch_and_process_feeds(self) -> list[MaterialEvent]:
        """
        Fetch news from all sources and process for events.

        In production, this would make actual API calls to news sources.
        """
        new_events = []

        # This is the framework - actual implementation would:
        # 1. Call RSS feeds
        # 2. Call news APIs
        # 3. Check SEC EDGAR
        # 4. Process each item through process_news_item

        return new_events

    def get_recent_events(
        self,
        hours: int = 24,
        company: Optional[str] = None,
        event_type: Optional[EventType] = None,
        min_severity: Optional[EventSeverity] = None,
    ) -> list[MaterialEvent]:
        """Get recent events with optional filters."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        filtered = [
            e for e in self.events
            if e.detected_at >= cutoff
        ]

        if company:
            filtered = [e for e in filtered if e.company_name.lower() == company.lower()]

        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]

        if min_severity:
            severity_order = [
                EventSeverity.LOW,
                EventSeverity.MEDIUM,
                EventSeverity.HIGH,
                EventSeverity.CRITICAL,
            ]
            min_index = severity_order.index(min_severity)
            filtered = [
                e for e in filtered
                if severity_order.index(e.severity) >= min_index
            ]

        # Sort by severity (critical first) then by time
        severity_priority = {
            EventSeverity.CRITICAL: 0,
            EventSeverity.HIGH: 1,
            EventSeverity.MEDIUM: 2,
            EventSeverity.LOW: 3,
        }
        filtered.sort(key=lambda e: (severity_priority[e.severity], -e.detected_at.timestamp()))

        return filtered

    def get_action_required_events(self) -> list[MaterialEvent]:
        """Get all events requiring action."""
        return [e for e in self.events if e.action_required]

    def get_events_by_company(self, company_name: str) -> list[MaterialEvent]:
        """Get all events for a specific company."""
        return [
            e for e in self.events
            if e.company_name.lower() == company_name.lower()
        ]

    def get_event_summary(self) -> dict:
        """Get summary of all events."""
        summary = {
            "total_events": len(self.events),
            "by_severity": {},
            "by_type": {},
            "by_company": {},
            "action_required_count": 0,
            "last_24h_count": 0,
        }

        cutoff_24h = datetime.utcnow() - timedelta(hours=24)

        for event in self.events:
            # By severity
            sev = event.severity.value
            summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1

            # By type
            evt_type = event.event_type.value
            summary["by_type"][evt_type] = summary["by_type"].get(evt_type, 0) + 1

            # By company
            company = event.company_name
            summary["by_company"][company] = summary["by_company"].get(company, 0) + 1

            # Action required
            if event.action_required:
                summary["action_required_count"] += 1

            # Last 24h
            if event.detected_at >= cutoff_24h:
                summary["last_24h_count"] += 1

        return summary

    def save_events(self, filename: str = "events.json"):
        """Save events to file."""
        filepath = self.data_dir / filename
        events_data = [e.to_dict() for e in self.events]

        with open(filepath, "w") as f:
            json.dump(events_data, f, indent=2)

    def load_events(self, filename: str = "events.json"):
        """Load events from file."""
        filepath = self.data_dir / filename

        if not filepath.exists():
            return

        with open(filepath) as f:
            events_data = json.load(f)

        for data in events_data:
            event = MaterialEvent(
                id=data["id"],
                company_name=data["company_name"],
                event_type=EventType(data["event_type"]),
                severity=EventSeverity(data["severity"]),
                headline=data["headline"],
                summary=data["summary"],
                source=data["source"],
                source_url=data["source_url"],
                published_at=datetime.fromisoformat(data["published_at"]),
                detected_at=datetime.fromisoformat(data["detected_at"]),
                valuation_impact=data.get("valuation_impact"),
                action_required=data.get("action_required", False),
                tags=data.get("tags", []),
            )
            self.events.append(event)

        # Update counter
        if self.events:
            max_id = max(
                int(e.id.split("_")[1]) for e in self.events
                if e.id.startswith("evt_")
            )
            self._event_id_counter = max_id
