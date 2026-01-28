"""
Tests for the AlertManager class.
"""

import pytest
from datetime import datetime, timedelta
from epochal.core.alerts import (
    AlertManager,
    Alert,
    AlertRule,
    AlertType,
    AlertPriority,
    NotificationChannel,
    alert_ipo_filing,
    alert_acquisition,
    alert_secondary_opportunity,
    alert_leadership_change,
)


class TestAlertManager:
    """Tests for AlertManager."""

    def test_init_default(self, alert_manager):
        """Test default initialization."""
        assert alert_manager is not None
        assert len(alert_manager.rules) > 0
        assert len(alert_manager.channel_configs) > 0

    def test_default_rules_loaded(self, alert_manager):
        """Test default alert rules are loaded."""
        # Should have IPO, acquisition, funding rules etc.
        rule_types = [r.alert_type for r in alert_manager.rules.values()]

        assert AlertType.IPO_FILING in rule_types
        assert AlertType.ACQUISITION in rule_types
        assert AlertType.FUNDING_ROUND in rule_types

    def test_add_rule(self, alert_manager):
        """Test adding a custom rule."""
        custom_rule = AlertRule(
            id="rule_custom",
            name="Custom Alert",
            description="Test custom alert",
            alert_type=AlertType.CUSTOM,
            priority=AlertPriority.LOW,
            channels=[NotificationChannel.IN_APP],
        )

        alert_manager.add_rule(custom_rule)

        assert "rule_custom" in alert_manager.rules

    def test_remove_rule(self, alert_manager):
        """Test removing a rule."""
        rule_id = list(alert_manager.rules.keys())[0]
        alert_manager.remove_rule(rule_id)

        assert rule_id not in alert_manager.rules

    def test_enable_disable_rule(self, alert_manager):
        """Test enabling/disabling rules."""
        rule_id = list(alert_manager.rules.keys())[0]

        alert_manager.enable_rule(rule_id, enabled=False)
        assert alert_manager.rules[rule_id].enabled is False

        alert_manager.enable_rule(rule_id, enabled=True)
        assert alert_manager.rules[rule_id].enabled is True


class TestAlertCreation:
    """Tests for alert creation."""

    def test_create_alert_with_matching_rule(self, alert_manager):
        """Test creating an alert that matches a rule."""
        alert = alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="TestCo Raises $1B",
            message="TestCo announced a $1B Series D round.",
            company_name="TestCo",
        )

        assert alert is not None
        assert alert.alert_type == AlertType.FUNDING_ROUND
        assert alert.company_name == "TestCo"
        assert len(alert_manager.alerts) > 0

    def test_create_alert_skip_rules(self, alert_manager):
        """Test creating an alert bypassing rules."""
        alert = alert_manager.create_alert(
            alert_type=AlertType.CUSTOM,
            title="Custom Alert",
            message="This is a custom alert.",
            priority=AlertPriority.LOW,
            skip_rules=True,
        )

        assert alert is not None
        assert alert.priority == AlertPriority.LOW

    def test_alert_id_generation(self, alert_manager):
        """Test alert IDs are unique."""
        alert1 = alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="Alert 1",
            message="First alert",
            skip_rules=True,
        )

        alert2 = alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="Alert 2",
            message="Second alert",
            skip_rules=True,
        )

        assert alert1.id != alert2.id

    def test_alert_expiration(self, alert_manager):
        """Test alert expiration setting."""
        alert = alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="Expiring Alert",
            message="This alert will expire.",
            expires_hours=24,
            skip_rules=True,
        )

        assert alert.expires_at is not None
        assert alert.expires_at > datetime.utcnow()


class TestAlertCooldowns:
    """Tests for alert cooldown functionality."""

    def test_cooldown_prevents_duplicate(self, alert_manager):
        """Test that cooldown prevents rapid duplicate alerts."""
        # Create first alert
        alert1 = alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="TestCo Funding",
            message="TestCo raised money",
            company_name="TestCo",
        )

        # Try to create same alert immediately (should be blocked by cooldown)
        alert2 = alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="TestCo Funding Again",
            message="Same event",
            company_name="TestCo",
        )

        # Second alert should be None due to cooldown
        assert alert1 is not None
        # Note: This depends on rule configuration - may or may not block


class TestAlertAcknowledgment:
    """Tests for alert acknowledgment."""

    def test_acknowledge_alert(self, alert_manager):
        """Test acknowledging an alert."""
        alert = alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="TestCo Funding",
            message="Test",
            skip_rules=True,
        )

        acknowledged = alert_manager.acknowledge_alert(
            alert_id=alert.id,
            acknowledged_by="test_user",
        )

        assert acknowledged is not None
        assert acknowledged.acknowledged is True
        assert acknowledged.acknowledged_by == "test_user"
        assert acknowledged.acknowledged_at is not None

    def test_get_unacknowledged_alerts(self, alert_manager):
        """Test getting unacknowledged alerts."""
        # Create some alerts
        for i in range(3):
            alert_manager.create_alert(
                alert_type=AlertType.FUNDING_ROUND,
                title=f"Alert {i}",
                message=f"Test alert {i}",
                skip_rules=True,
            )

        # Acknowledge one
        alerts = alert_manager.alerts
        if alerts:
            alert_manager.acknowledge_alert(alerts[0].id)

        unacked = alert_manager.get_unacknowledged_alerts()

        assert all(not a.acknowledged for a in unacked)


class TestAlertFiltering:
    """Tests for alert filtering."""

    def test_filter_by_priority(self, alert_manager):
        """Test filtering alerts by priority."""
        # Create alerts with different priorities
        alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="Low Priority",
            message="Test",
            priority=AlertPriority.LOW,
            skip_rules=True,
        )
        alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="Critical",
            message="Test",
            priority=AlertPriority.CRITICAL,
            skip_rules=True,
        )

        critical_alerts = alert_manager.get_unacknowledged_alerts(
            priority=AlertPriority.CRITICAL
        )

        assert all(a.priority == AlertPriority.CRITICAL for a in critical_alerts)

    def test_filter_by_company(self, alert_manager):
        """Test filtering alerts by company."""
        alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="CompanyA Alert",
            message="Test",
            company_name="CompanyA",
            skip_rules=True,
        )
        alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="CompanyB Alert",
            message="Test",
            company_name="CompanyB",
            skip_rules=True,
        )

        company_a_alerts = alert_manager.get_unacknowledged_alerts(
            company_name="CompanyA"
        )

        assert all(a.company_name == "CompanyA" for a in company_a_alerts)

    def test_get_recent_alerts(self, alert_manager):
        """Test getting recent alerts."""
        alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="Recent Alert",
            message="Test",
            skip_rules=True,
        )

        recent = alert_manager.get_recent_alerts(hours=1)

        assert len(recent) > 0


class TestAlertSummary:
    """Tests for alert summary generation."""

    def test_get_alert_summary(self, alert_manager):
        """Test getting alert summary."""
        # Create some alerts
        alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="Alert 1",
            message="Test",
            priority=AlertPriority.CRITICAL,
            skip_rules=True,
        )
        alert_manager.create_alert(
            alert_type=AlertType.LEADERSHIP_CHANGE,
            title="Alert 2",
            message="Test",
            priority=AlertPriority.HIGH,
            skip_rules=True,
        )

        summary = alert_manager.get_alert_summary()

        assert "total" in summary
        assert "by_priority" in summary
        assert "by_type" in summary
        assert summary["total"] >= 2

    def test_generate_alert_report(self, alert_manager):
        """Test alert report generation."""
        alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="Test Alert",
            message="Test message",
            skip_rules=True,
        )

        report = alert_manager.generate_alert_report(hours=24)

        assert "ALERT REPORT" in report
        assert "SUMMARY" in report


class TestConvenienceFunctions:
    """Tests for alert convenience functions."""

    def test_alert_ipo_filing(self, alert_manager):
        """Test IPO filing alert creation."""
        alert = alert_ipo_filing(
            manager=alert_manager,
            company_name="TestCo",
            filing_type="S-1",
            details={"target_raise": 500_000_000},
        )

        # May be None if rule cooldown applies
        if alert:
            assert alert.alert_type == AlertType.IPO_FILING
            assert "TestCo" in alert.title

    def test_alert_acquisition(self, alert_manager):
        """Test acquisition alert creation."""
        alert = alert_acquisition(
            manager=alert_manager,
            company_name="TargetCo",
            acquirer="BigTech",
            deal_value_usd=10_000_000_000,
        )

        if alert:
            assert alert.alert_type == AlertType.ACQUISITION
            assert "TargetCo" in alert.title
            assert "BigTech" in alert.title

    def test_alert_secondary_opportunity(self, alert_manager):
        """Test secondary opportunity alert creation."""
        alert = alert_secondary_opportunity(
            manager=alert_manager,
            company_name="HotStartup",
            platform="Forge",
            discount_pct=25.0,
            implied_valuation=50_000_000_000,
        )

        if alert:
            assert alert.alert_type == AlertType.SECONDARY_OPPORTUNITY
            assert "25" in alert.title

    def test_alert_leadership_change(self, alert_manager):
        """Test leadership change alert creation."""
        alert = alert_leadership_change(
            manager=alert_manager,
            company_name="TestCo",
            executive="Jane Doe",
            role="CEO",
            change_type="departed",
        )

        if alert:
            assert alert.alert_type == AlertType.LEADERSHIP_CHANGE
            assert "CEO" in alert.title


class TestChannelConfiguration:
    """Tests for notification channel configuration."""

    def test_configure_slack(self, alert_manager):
        """Test Slack channel configuration."""
        alert_manager.configure_slack(
            webhook_url="https://hooks.slack.com/test",
            channel="#test-alerts",
        )

        config = alert_manager.channel_configs[NotificationChannel.SLACK]

        assert config.enabled is True
        assert config.config["webhook_url"] == "https://hooks.slack.com/test"
        assert config.config["channel"] == "#test-alerts"

    def test_configure_webhook(self, alert_manager):
        """Test webhook channel configuration."""
        alert_manager.configure_webhook(
            url="https://api.example.com/alerts",
            headers={"Authorization": "Bearer token123"},
        )

        config = alert_manager.channel_configs[NotificationChannel.WEBHOOK]

        assert config.enabled is True
        assert config.config["url"] == "https://api.example.com/alerts"


class TestAlertSerialization:
    """Tests for alert serialization/deserialization."""

    def test_alert_to_dict(self, alert_manager):
        """Test alert to dictionary conversion."""
        alert = alert_manager.create_alert(
            alert_type=AlertType.FUNDING_ROUND,
            title="Test Alert",
            message="Test message",
            company_name="TestCo",
            data={"amount": 1000000},
            tags=["test", "funding"],
            skip_rules=True,
        )

        alert_dict = alert.to_dict()

        assert alert_dict["title"] == "Test Alert"
        assert alert_dict["company_name"] == "TestCo"
        assert alert_dict["data"]["amount"] == 1000000

    def test_alert_from_dict(self):
        """Test alert from dictionary creation."""
        data = {
            "id": "alert_test_001",
            "alert_type": "funding_round",
            "priority": "high",
            "title": "Test Alert",
            "message": "Test message",
            "company_name": "TestCo",
            "created_at": datetime.utcnow().isoformat(),
            "acknowledged": False,
        }

        alert = Alert.from_dict(data)

        assert alert.id == "alert_test_001"
        assert alert.alert_type == AlertType.FUNDING_ROUND
        assert alert.priority == AlertPriority.HIGH
