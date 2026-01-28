"""
Alert & Notification System for Epochal Capital.

Provides configurable alerts for material events, price movements,
and portfolio changes with multi-channel notification support.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional
import hashlib


class AlertPriority(str, Enum):
    """Alert priority levels."""
    CRITICAL = "critical"   # Immediate attention required
    HIGH = "high"           # Review within hours
    MEDIUM = "medium"       # Review within 24 hours
    LOW = "low"             # Informational


class AlertType(str, Enum):
    """Types of alerts."""
    # Material events
    IPO_FILING = "ipo_filing"
    IPO_PRICING = "ipo_pricing"
    FUNDING_ROUND = "funding_round"
    ACQUISITION = "acquisition"
    LEADERSHIP_CHANGE = "leadership_change"

    # Price alerts
    PRICE_TARGET_HIT = "price_target_hit"
    PRICE_SPIKE = "price_spike"
    PRICE_DROP = "price_drop"
    SECONDARY_OPPORTUNITY = "secondary_opportunity"

    # Portfolio alerts
    POSITION_THRESHOLD = "position_threshold"
    CONCENTRATION_WARNING = "concentration_warning"
    EXPIRATION_WARNING = "expiration_warning"

    # Risk alerts
    RISK_SCORE_CHANGE = "risk_score_change"
    REGULATORY_UPDATE = "regulatory_update"

    # System alerts
    RESEARCH_COMPLETE = "research_complete"
    DEAL_STATUS_CHANGE = "deal_status_change"
    CUSTOM = "custom"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    IN_APP = "in_app"
    CONSOLE = "console"


@dataclass
class Alert:
    """An alert instance."""
    id: str
    alert_type: AlertType
    priority: AlertPriority
    title: str
    message: str
    company_name: Optional[str] = None
    data: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    channels_sent: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "alert_type": self.alert_type.value,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "company_name": self.company_name,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "acknowledged": self.acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "channels_sent": self.channels_sent,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Alert":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            alert_type=AlertType(data["alert_type"]),
            priority=AlertPriority(data["priority"]),
            title=data["title"],
            message=data["message"],
            company_name=data.get("company_name"),
            data=data.get("data", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            acknowledged=data.get("acknowledged", False),
            acknowledged_at=datetime.fromisoformat(data["acknowledged_at"]) if data.get("acknowledged_at") else None,
            acknowledged_by=data.get("acknowledged_by"),
            channels_sent=data.get("channels_sent", []),
            tags=data.get("tags", []),
        )


@dataclass
class AlertRule:
    """Rule for triggering alerts."""
    id: str
    name: str
    description: str
    alert_type: AlertType
    priority: AlertPriority
    enabled: bool = True
    conditions: dict = field(default_factory=dict)
    channels: list[NotificationChannel] = field(default_factory=list)
    companies: Optional[list[str]] = None  # None = all companies
    cooldown_minutes: int = 60  # Minimum time between same alerts
    last_triggered: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "alert_type": self.alert_type.value,
            "priority": self.priority.value,
            "enabled": self.enabled,
            "conditions": self.conditions,
            "channels": [c.value for c in self.channels],
            "companies": self.companies,
            "cooldown_minutes": self.cooldown_minutes,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
        }


@dataclass
class ChannelConfig:
    """Configuration for a notification channel."""
    channel: NotificationChannel
    enabled: bool = True
    config: dict = field(default_factory=dict)
    # e.g., for email: {"smtp_host": "...", "recipients": [...]}
    # e.g., for slack: {"webhook_url": "...", "channel": "#alerts"}
    # e.g., for webhook: {"url": "...", "headers": {...}}


class AlertManager:
    """
    Central alert management system.

    Features:
    - Configurable alert rules
    - Multi-channel notifications
    - Alert deduplication and cooldowns
    - Alert history and acknowledgment
    """

    # Default alert rules
    DEFAULT_RULES = [
        AlertRule(
            id="rule_ipo_filing",
            name="IPO Filing Alert",
            description="Alert when a tracked company files for IPO",
            alert_type=AlertType.IPO_FILING,
            priority=AlertPriority.CRITICAL,
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            cooldown_minutes=1440,  # 24 hours
        ),
        AlertRule(
            id="rule_acquisition",
            name="Acquisition Alert",
            description="Alert when a tracked company is acquired",
            alert_type=AlertType.ACQUISITION,
            priority=AlertPriority.CRITICAL,
            channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            cooldown_minutes=1440,
        ),
        AlertRule(
            id="rule_funding",
            name="Funding Round Alert",
            description="Alert on new funding rounds",
            alert_type=AlertType.FUNDING_ROUND,
            priority=AlertPriority.HIGH,
            channels=[NotificationChannel.SLACK, NotificationChannel.IN_APP],
            cooldown_minutes=60,
        ),
        AlertRule(
            id="rule_leadership",
            name="Leadership Change Alert",
            description="Alert on C-suite changes",
            alert_type=AlertType.LEADERSHIP_CHANGE,
            priority=AlertPriority.HIGH,
            channels=[NotificationChannel.EMAIL],
            cooldown_minutes=60,
        ),
        AlertRule(
            id="rule_secondary_opportunity",
            name="Secondary Market Opportunity",
            description="Alert when attractive secondary pricing appears",
            alert_type=AlertType.SECONDARY_OPPORTUNITY,
            priority=AlertPriority.HIGH,
            channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
            conditions={"discount_pct_min": 20},
            cooldown_minutes=240,  # 4 hours
        ),
        AlertRule(
            id="rule_price_drop",
            name="Price Drop Alert",
            description="Alert on significant price drops",
            alert_type=AlertType.PRICE_DROP,
            priority=AlertPriority.HIGH,
            channels=[NotificationChannel.SLACK],
            conditions={"drop_pct_threshold": 15},
            cooldown_minutes=1440,
        ),
        AlertRule(
            id="rule_risk_change",
            name="Risk Score Change",
            description="Alert when company risk score changes significantly",
            alert_type=AlertType.RISK_SCORE_CHANGE,
            priority=AlertPriority.MEDIUM,
            channels=[NotificationChannel.IN_APP],
            conditions={"score_change_threshold": 15},
            cooldown_minutes=1440,
        ),
    ]

    def __init__(self, data_dir: str = "data/alerts"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.alerts: list[Alert] = []
        self.rules: dict[str, AlertRule] = {}
        self.channel_configs: dict[NotificationChannel, ChannelConfig] = {}
        self.handlers: dict[NotificationChannel, Callable] = {}

        self._alert_counter = 0
        self._initialize_default_rules()
        self._initialize_default_channels()
        self._load_alerts()

    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        for rule in self.DEFAULT_RULES:
            self.rules[rule.id] = rule

    def _initialize_default_channels(self):
        """Initialize default channel configurations."""
        # Console channel (always enabled for dev)
        self.channel_configs[NotificationChannel.CONSOLE] = ChannelConfig(
            channel=NotificationChannel.CONSOLE,
            enabled=True,
        )

        # In-app channel
        self.channel_configs[NotificationChannel.IN_APP] = ChannelConfig(
            channel=NotificationChannel.IN_APP,
            enabled=True,
        )

        # Other channels disabled by default until configured
        for channel in [NotificationChannel.EMAIL, NotificationChannel.SLACK,
                        NotificationChannel.WEBHOOK, NotificationChannel.SMS]:
            self.channel_configs[channel] = ChannelConfig(
                channel=channel,
                enabled=False,
            )

        # Register default handlers
        self.handlers[NotificationChannel.CONSOLE] = self._console_handler
        self.handlers[NotificationChannel.IN_APP] = self._in_app_handler

    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        self._alert_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"alert_{timestamp}_{self._alert_counter:04d}"

    def _dedup_key(self, alert_type: AlertType, company_name: Optional[str], data: dict) -> str:
        """Generate deduplication key for alerts."""
        key_parts = [alert_type.value]
        if company_name:
            key_parts.append(company_name.lower())
        if data:
            key_parts.append(json.dumps(data, sort_keys=True))
        return hashlib.md5("".join(key_parts).encode()).hexdigest()[:12]

    def configure_channel(
        self,
        channel: NotificationChannel,
        enabled: bool = True,
        config: Optional[dict] = None,
    ):
        """Configure a notification channel."""
        self.channel_configs[channel] = ChannelConfig(
            channel=channel,
            enabled=enabled,
            config=config or {},
        )

    def configure_slack(self, webhook_url: str, channel: str = "#alerts"):
        """Configure Slack notifications."""
        self.configure_channel(
            NotificationChannel.SLACK,
            enabled=True,
            config={"webhook_url": webhook_url, "channel": channel},
        )
        self.handlers[NotificationChannel.SLACK] = self._slack_handler

    def configure_email(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        recipients: list[str],
        from_address: str = "alerts@epochal.capital",
    ):
        """Configure email notifications."""
        self.configure_channel(
            NotificationChannel.EMAIL,
            enabled=True,
            config={
                "smtp_host": smtp_host,
                "smtp_port": smtp_port,
                "username": username,
                "password": password,
                "recipients": recipients,
                "from_address": from_address,
            },
        )
        self.handlers[NotificationChannel.EMAIL] = self._email_handler

    def configure_webhook(self, url: str, headers: Optional[dict] = None):
        """Configure webhook notifications."""
        self.configure_channel(
            NotificationChannel.WEBHOOK,
            enabled=True,
            config={"url": url, "headers": headers or {}},
        )
        self.handlers[NotificationChannel.WEBHOOK] = self._webhook_handler

    def add_rule(self, rule: AlertRule):
        """Add or update an alert rule."""
        self.rules[rule.id] = rule

    def remove_rule(self, rule_id: str):
        """Remove an alert rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]

    def enable_rule(self, rule_id: str, enabled: bool = True):
        """Enable or disable a rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = enabled

    def check_cooldown(self, rule: AlertRule) -> bool:
        """Check if rule is in cooldown period."""
        if not rule.last_triggered:
            return False
        cooldown_end = rule.last_triggered + timedelta(minutes=rule.cooldown_minutes)
        return datetime.utcnow() < cooldown_end

    def create_alert(
        self,
        alert_type: AlertType,
        title: str,
        message: str,
        priority: Optional[AlertPriority] = None,
        company_name: Optional[str] = None,
        data: Optional[dict] = None,
        tags: Optional[list[str]] = None,
        expires_hours: Optional[int] = None,
        skip_rules: bool = False,
    ) -> Optional[Alert]:
        """
        Create and dispatch an alert.

        Args:
            alert_type: Type of alert
            title: Alert title
            message: Alert message
            priority: Priority (if not set, uses rule default)
            company_name: Associated company
            data: Additional data
            tags: Alert tags
            expires_hours: Hours until alert expires
            skip_rules: If True, bypasses rule checking

        Returns:
            Created Alert or None if filtered by rules
        """
        data = data or {}

        # Find matching rule
        matching_rule = None
        if not skip_rules:
            for rule in self.rules.values():
                if not rule.enabled:
                    continue
                if rule.alert_type != alert_type:
                    continue
                if rule.companies and company_name and company_name not in rule.companies:
                    continue
                if self.check_cooldown(rule):
                    continue
                matching_rule = rule
                break

            if not matching_rule and not skip_rules:
                # No matching rule, check if we should create anyway
                # Default: only create alerts that have matching rules
                return None

        # Determine priority
        if priority is None:
            priority = matching_rule.priority if matching_rule else AlertPriority.MEDIUM

        # Create alert
        alert = Alert(
            id=self._generate_alert_id(),
            alert_type=alert_type,
            priority=priority,
            title=title,
            message=message,
            company_name=company_name,
            data=data,
            tags=tags or [],
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours) if expires_hours else None,
        )

        # Store alert
        self.alerts.append(alert)

        # Update rule last triggered
        if matching_rule:
            matching_rule.last_triggered = datetime.utcnow()

        # Dispatch to channels
        channels = matching_rule.channels if matching_rule else [NotificationChannel.IN_APP]
        self._dispatch_alert(alert, channels)

        # Save alerts
        self._save_alerts()

        return alert

    def _dispatch_alert(self, alert: Alert, channels: list[NotificationChannel]):
        """Dispatch alert to specified channels."""
        for channel in channels:
            config = self.channel_configs.get(channel)
            if not config or not config.enabled:
                continue

            handler = self.handlers.get(channel)
            if handler:
                try:
                    handler(alert, config)
                    alert.channels_sent.append(channel.value)
                except Exception as e:
                    print(f"Error sending to {channel.value}: {e}")

    def _console_handler(self, alert: Alert, config: ChannelConfig):
        """Console notification handler."""
        priority_icons = {
            AlertPriority.CRITICAL: "🚨",
            AlertPriority.HIGH: "⚠️",
            AlertPriority.MEDIUM: "📢",
            AlertPriority.LOW: "ℹ️",
        }
        icon = priority_icons.get(alert.priority, "📢")
        print(f"\n{icon} [{alert.priority.value.upper()}] {alert.title}")
        print(f"   {alert.message}")
        if alert.company_name:
            print(f"   Company: {alert.company_name}")
        print()

    def _in_app_handler(self, alert: Alert, config: ChannelConfig):
        """In-app notification handler (stores for UI retrieval)."""
        # In-app alerts are already stored in self.alerts
        pass

    async def _slack_handler(self, alert: Alert, config: ChannelConfig):
        """Slack notification handler."""
        # Implementation would use aiohttp to post to Slack webhook
        webhook_url = config.config.get("webhook_url")
        if not webhook_url:
            return

        priority_colors = {
            AlertPriority.CRITICAL: "#dc3545",
            AlertPriority.HIGH: "#fd7e14",
            AlertPriority.MEDIUM: "#ffc107",
            AlertPriority.LOW: "#17a2b8",
        }

        payload = {
            "attachments": [{
                "color": priority_colors.get(alert.priority, "#6c757d"),
                "title": alert.title,
                "text": alert.message,
                "fields": [],
                "footer": f"Epochal Capital | {alert.alert_type.value}",
                "ts": int(alert.created_at.timestamp()),
            }]
        }

        if alert.company_name:
            payload["attachments"][0]["fields"].append({
                "title": "Company",
                "value": alert.company_name,
                "short": True,
            })

        # In production, would use aiohttp:
        # async with aiohttp.ClientSession() as session:
        #     await session.post(webhook_url, json=payload)
        print(f"[SLACK] Would send to {webhook_url}: {alert.title}")

    async def _email_handler(self, alert: Alert, config: ChannelConfig):
        """Email notification handler."""
        # Implementation would use smtplib or aiosmtplib
        recipients = config.config.get("recipients", [])
        from_address = config.config.get("from_address", "alerts@epochal.capital")

        subject = f"[{alert.priority.value.upper()}] {alert.title}"
        body = f"""
{alert.message}

Company: {alert.company_name or 'N/A'}
Type: {alert.alert_type.value}
Priority: {alert.priority.value}
Time: {alert.created_at.strftime('%Y-%m-%d %H:%M UTC')}

---
Epochal Capital Alert System
"""
        print(f"[EMAIL] Would send to {recipients}: {subject}")

    async def _webhook_handler(self, alert: Alert, config: ChannelConfig):
        """Webhook notification handler."""
        url = config.config.get("url")
        headers = config.config.get("headers", {})

        if not url:
            return

        payload = alert.to_dict()

        # In production, would use aiohttp:
        # async with aiohttp.ClientSession() as session:
        #     await session.post(url, json=payload, headers=headers)
        print(f"[WEBHOOK] Would POST to {url}: {alert.title}")

    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str = "system",
    ) -> Optional[Alert]:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                alert.acknowledged_by = acknowledged_by
                self._save_alerts()
                return alert
        return None

    def get_unacknowledged_alerts(
        self,
        priority: Optional[AlertPriority] = None,
        alert_type: Optional[AlertType] = None,
        company_name: Optional[str] = None,
    ) -> list[Alert]:
        """Get unacknowledged alerts with optional filters."""
        alerts = [a for a in self.alerts if not a.acknowledged]

        if priority:
            alerts = [a for a in alerts if a.priority == priority]

        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]

        if company_name:
            alerts = [
                a for a in alerts
                if a.company_name and a.company_name.lower() == company_name.lower()
            ]

        # Sort by priority (critical first) then by time
        priority_order = {
            AlertPriority.CRITICAL: 0,
            AlertPriority.HIGH: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.LOW: 3,
        }
        alerts.sort(key=lambda a: (priority_order[a.priority], -a.created_at.timestamp()))

        return alerts

    def get_recent_alerts(
        self,
        hours: int = 24,
        include_acknowledged: bool = True,
    ) -> list[Alert]:
        """Get recent alerts."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        alerts = [a for a in self.alerts if a.created_at >= cutoff]

        if not include_acknowledged:
            alerts = [a for a in alerts if not a.acknowledged]

        return sorted(alerts, key=lambda a: a.created_at, reverse=True)

    def get_alert_summary(self) -> dict:
        """Get summary of alerts."""
        summary = {
            "total": len(self.alerts),
            "unacknowledged": 0,
            "by_priority": {p.value: 0 for p in AlertPriority},
            "by_type": {},
            "last_24h": 0,
            "critical_unacked": 0,
        }

        cutoff_24h = datetime.utcnow() - timedelta(hours=24)

        for alert in self.alerts:
            if not alert.acknowledged:
                summary["unacknowledged"] += 1
                if alert.priority == AlertPriority.CRITICAL:
                    summary["critical_unacked"] += 1

            summary["by_priority"][alert.priority.value] += 1

            alert_type = alert.alert_type.value
            summary["by_type"][alert_type] = summary["by_type"].get(alert_type, 0) + 1

            if alert.created_at >= cutoff_24h:
                summary["last_24h"] += 1

        return summary

    def _save_alerts(self):
        """Save alerts to disk."""
        filepath = self.data_dir / "alerts.json"
        alerts_data = [a.to_dict() for a in self.alerts[-1000:]]  # Keep last 1000

        with open(filepath, "w") as f:
            json.dump(alerts_data, f, indent=2)

    def _load_alerts(self):
        """Load alerts from disk."""
        filepath = self.data_dir / "alerts.json"

        if not filepath.exists():
            return

        try:
            with open(filepath) as f:
                alerts_data = json.load(f)

            for data in alerts_data:
                try:
                    alert = Alert.from_dict(data)
                    self.alerts.append(alert)
                except Exception:
                    pass

            # Update counter
            if self.alerts:
                max_num = max(
                    int(a.id.split("_")[-1]) for a in self.alerts
                    if a.id.startswith("alert_")
                )
                self._alert_counter = max_num
        except Exception:
            pass

    def clear_expired_alerts(self):
        """Remove expired alerts."""
        now = datetime.utcnow()
        self.alerts = [
            a for a in self.alerts
            if not a.expires_at or a.expires_at > now
        ]
        self._save_alerts()

    def generate_alert_report(self, hours: int = 24) -> str:
        """Generate alert report for specified time period."""
        alerts = self.get_recent_alerts(hours=hours)
        summary = self.get_alert_summary()

        report = f"""
ALERT REPORT - Last {hours} Hours
{'=' * 50}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

SUMMARY
-------
Total Alerts: {summary['total']}
Last {hours}h: {summary['last_24h']}
Unacknowledged: {summary['unacknowledged']}
Critical (Unacked): {summary['critical_unacked']}

BY PRIORITY
-----------
"""
        for priority in AlertPriority:
            count = summary['by_priority'][priority.value]
            report += f"{priority.value:10}: {count}\n"

        report += "\nRECENT ALERTS\n"
        report += "-" * 50 + "\n"

        for alert in alerts[:20]:
            ack = "✓" if alert.acknowledged else "○"
            report += (
                f"\n{ack} [{alert.priority.value.upper()}] {alert.title}\n"
                f"   {alert.created_at.strftime('%Y-%m-%d %H:%M')} | "
                f"{alert.company_name or 'General'}\n"
                f"   {alert.message[:100]}{'...' if len(alert.message) > 100 else ''}\n"
            )

        return report


# Convenience functions for quick alert creation
def alert_ipo_filing(
    manager: AlertManager,
    company_name: str,
    filing_type: str = "S-1",
    details: Optional[dict] = None,
) -> Optional[Alert]:
    """Create IPO filing alert."""
    return manager.create_alert(
        alert_type=AlertType.IPO_FILING,
        title=f"IPO Filing: {company_name} filed {filing_type}",
        message=f"{company_name} has filed an {filing_type} with the SEC, signaling IPO preparation.",
        company_name=company_name,
        data={"filing_type": filing_type, **(details or {})},
        tags=["ipo", "regulatory", "liquidity_event"],
    )


def alert_acquisition(
    manager: AlertManager,
    company_name: str,
    acquirer: str,
    deal_value_usd: Optional[float] = None,
) -> Optional[Alert]:
    """Create acquisition alert."""
    value_str = f" for ${deal_value_usd/1e9:.1f}B" if deal_value_usd else ""
    return manager.create_alert(
        alert_type=AlertType.ACQUISITION,
        title=f"Acquisition: {company_name} to be acquired by {acquirer}",
        message=f"{company_name} is being acquired by {acquirer}{value_str}.",
        company_name=company_name,
        data={"acquirer": acquirer, "deal_value_usd": deal_value_usd},
        tags=["m&a", "liquidity_event"],
    )


def alert_secondary_opportunity(
    manager: AlertManager,
    company_name: str,
    platform: str,
    discount_pct: float,
    implied_valuation: Optional[float] = None,
) -> Optional[Alert]:
    """Create secondary market opportunity alert."""
    val_str = f" (implied ${implied_valuation/1e9:.1f}B valuation)" if implied_valuation else ""
    return manager.create_alert(
        alert_type=AlertType.SECONDARY_OPPORTUNITY,
        title=f"Secondary Opportunity: {company_name} at {discount_pct:.0f}% discount",
        message=f"Attractive secondary pricing available on {platform} for {company_name} at {discount_pct:.0f}% discount to last round{val_str}.",
        company_name=company_name,
        data={
            "platform": platform,
            "discount_pct": discount_pct,
            "implied_valuation": implied_valuation,
        },
        tags=["secondary", "opportunity"],
    )


def alert_leadership_change(
    manager: AlertManager,
    company_name: str,
    executive: str,
    role: str,
    change_type: str = "departed",
) -> Optional[Alert]:
    """Create leadership change alert."""
    return manager.create_alert(
        alert_type=AlertType.LEADERSHIP_CHANGE,
        title=f"Leadership Change: {company_name} {role} {change_type}",
        message=f"{executive} ({role}) has {change_type} {company_name}.",
        company_name=company_name,
        data={"executive": executive, "role": role, "change_type": change_type},
        tags=["leadership", "risk_factor"],
    )
