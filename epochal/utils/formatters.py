"""Formatting utilities for Epochal Capital."""

from typing import Optional


def format_currency(amount: Optional[float], precision: int = 0) -> str:
    """Format a number as currency."""
    if amount is None:
        return "N/A"

    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.1f}K"
    else:
        return f"${amount:,.{precision}f}"


def format_percentage(value: Optional[float], precision: int = 1) -> str:
    """Format a number as percentage."""
    if value is None:
        return "N/A"
    return f"{value:.{precision}f}%"


def format_report(data: dict, title: str = "Report") -> str:
    """Format a dictionary as a readable report."""
    lines = [f"\n{'=' * 60}", f" {title}", f"{'=' * 60}\n"]

    def format_value(v, indent=0):
        prefix = "  " * indent
        if isinstance(v, dict):
            result = []
            for k, val in v.items():
                if isinstance(val, (dict, list)):
                    result.append(f"{prefix}{k}:")
                    result.append(format_value(val, indent + 1))
                else:
                    result.append(f"{prefix}{k}: {val}")
            return "\n".join(result)
        elif isinstance(v, list):
            if not v:
                return f"{prefix}(empty)"
            result = []
            for item in v:
                if isinstance(item, dict):
                    result.append(format_value(item, indent))
                    result.append(f"{prefix}---")
                else:
                    result.append(f"{prefix}- {item}")
            return "\n".join(result)
        else:
            return f"{prefix}{v}"

    lines.append(format_value(data))
    lines.append(f"\n{'=' * 60}\n")

    return "\n".join(lines)
