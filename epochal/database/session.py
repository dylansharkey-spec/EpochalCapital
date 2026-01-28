"""
Database session management for Epochal Capital.

Provides:
- Engine creation
- Session management
- Database initialization
- Migration utilities
"""

import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional, TypeVar

try:
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.engine import Engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Engine = None
    Session = None

from epochal.database.models import (
    Base,
    CompanyDB,
    DealDB,
    InvestmentDB,
    AlertDB,
    ResearchDB,
)


# Type variable for generic queries
T = TypeVar("T")

# Default database path
DEFAULT_DB_PATH = "data/epochal.db"

# Global engine instance
_engine: Optional[Engine] = None
_SessionLocal = None


def get_engine(db_path: str = DEFAULT_DB_PATH) -> Optional[Engine]:
    """
    Get or create the database engine.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLAlchemy Engine instance
    """
    global _engine

    if not SQLALCHEMY_AVAILABLE:
        print("SQLAlchemy not installed. Run: pip install sqlalchemy")
        return None

    if _engine is None:
        # Ensure directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # Create engine with SQLite optimizations
        _engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )

        # Enable foreign keys for SQLite
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    return _engine


def get_session() -> Optional[Session]:
    """
    Get a new database session.

    Returns:
        SQLAlchemy Session instance
    """
    global _SessionLocal

    if not SQLALCHEMY_AVAILABLE:
        return None

    engine = get_engine()
    if engine is None:
        return None

    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=engine)

    return _SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.

    Usage:
        with session_scope() as session:
            session.add(obj)
            session.commit()
    """
    session = get_session()
    if session is None:
        raise RuntimeError("Database session not available")

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Initialize the database schema.

    Args:
        db_path: Path to SQLite database file

    Returns:
        True if successful, False otherwise
    """
    if not SQLALCHEMY_AVAILABLE:
        print("SQLAlchemy not installed. Run: pip install sqlalchemy")
        return False

    engine = get_engine(db_path)
    if engine is None:
        return False

    # Create all tables
    Base.metadata.create_all(engine)

    print(f"Database initialized at: {db_path}")
    return True


def drop_all_tables(db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Drop all tables (use with caution!).

    Args:
        db_path: Path to SQLite database file

    Returns:
        True if successful, False otherwise
    """
    if not SQLALCHEMY_AVAILABLE:
        return False

    engine = get_engine(db_path)
    if engine is None:
        return False

    Base.metadata.drop_all(engine)
    return True


class DatabaseManager:
    """
    High-level database manager for Epochal Capital.

    Provides CRUD operations and utilities for all entities.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.engine = get_engine(db_path)
        self._ensure_initialized()

    def _ensure_initialized(self):
        """Ensure database is initialized."""
        if self.engine is not None:
            Base.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Get a session context manager."""
        with session_scope() as s:
            yield s

    # Company operations
    def add_company(self, company_data: dict) -> Optional[CompanyDB]:
        """Add a new company."""
        with self.session() as session:
            company = CompanyDB(**company_data)
            session.add(company)
            session.flush()
            return company

    def get_company(self, company_id: str) -> Optional[CompanyDB]:
        """Get a company by ID."""
        with self.session() as session:
            return session.query(CompanyDB).filter_by(id=company_id).first()

    def get_company_by_name(self, name: str) -> Optional[CompanyDB]:
        """Get a company by name."""
        with self.session() as session:
            return session.query(CompanyDB).filter(
                CompanyDB.name.ilike(name)
            ).first()

    def list_companies(
        self,
        vertical: Optional[str] = None,
        stage: Optional[str] = None,
        limit: int = 100,
    ) -> list[CompanyDB]:
        """List companies with optional filters."""
        with self.session() as session:
            query = session.query(CompanyDB)

            if vertical:
                query = query.filter_by(vertical=vertical)
            if stage:
                query = query.filter_by(stage=stage)

            return query.order_by(CompanyDB.name).limit(limit).all()

    def update_company(self, company_id: str, updates: dict) -> Optional[CompanyDB]:
        """Update a company."""
        with self.session() as session:
            company = session.query(CompanyDB).filter_by(id=company_id).first()
            if company:
                for key, value in updates.items():
                    if hasattr(company, key):
                        setattr(company, key, value)
                company.updated_at = datetime.utcnow()
                session.flush()
            return company

    def delete_company(self, company_id: str) -> bool:
        """Delete a company."""
        with self.session() as session:
            company = session.query(CompanyDB).filter_by(id=company_id).first()
            if company:
                session.delete(company)
                return True
            return False

    # Deal operations
    def add_deal(self, deal_data: dict) -> Optional[DealDB]:
        """Add a new deal."""
        with self.session() as session:
            deal = DealDB(**deal_data)
            session.add(deal)
            session.flush()
            return deal

    def get_deal(self, deal_id: str) -> Optional[DealDB]:
        """Get a deal by ID."""
        with self.session() as session:
            return session.query(DealDB).filter_by(id=deal_id).first()

    def list_deals(
        self,
        status: Optional[str] = None,
        company_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[DealDB]:
        """List deals with optional filters."""
        with self.session() as session:
            query = session.query(DealDB)

            if status:
                query = query.filter_by(status=status)
            if company_id:
                query = query.filter_by(company_id=company_id)

            return query.order_by(DealDB.created_at.desc()).limit(limit).all()

    def update_deal_status(self, deal_id: str, status: str) -> Optional[DealDB]:
        """Update a deal's status."""
        with self.session() as session:
            deal = session.query(DealDB).filter_by(id=deal_id).first()
            if deal:
                deal.status = status
                deal.updated_at = datetime.utcnow()
                session.flush()
            return deal

    # Investment operations
    def add_investment(self, investment_data: dict) -> Optional[InvestmentDB]:
        """Add a new investment."""
        with self.session() as session:
            investment = InvestmentDB(**investment_data)
            session.add(investment)
            session.flush()
            return investment

    def get_investment(self, investment_id: str) -> Optional[InvestmentDB]:
        """Get an investment by ID."""
        with self.session() as session:
            return session.query(InvestmentDB).filter_by(id=investment_id).first()

    def list_investments(
        self,
        status: Optional[str] = None,
        company_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[InvestmentDB]:
        """List investments with optional filters."""
        with self.session() as session:
            query = session.query(InvestmentDB)

            if status:
                query = query.filter_by(status=status)
            if company_id:
                query = query.filter_by(company_id=company_id)

            return query.order_by(InvestmentDB.investment_date.desc()).limit(limit).all()

    def update_investment_value(
        self,
        investment_id: str,
        current_value: float,
    ) -> Optional[InvestmentDB]:
        """Update an investment's current value."""
        with self.session() as session:
            investment = session.query(InvestmentDB).filter_by(id=investment_id).first()
            if investment:
                investment.current_value_usd = current_value
                investment.last_valuation_date = datetime.utcnow()
                investment.updated_at = datetime.utcnow()
                session.flush()
            return investment

    # Alert operations
    def add_alert(self, alert_data: dict) -> Optional[AlertDB]:
        """Add a new alert."""
        with self.session() as session:
            alert = AlertDB(**alert_data)
            session.add(alert)
            session.flush()
            return alert

    def get_unacknowledged_alerts(
        self,
        priority: Optional[str] = None,
        limit: int = 100,
    ) -> list[AlertDB]:
        """Get unacknowledged alerts."""
        with self.session() as session:
            query = session.query(AlertDB).filter_by(acknowledged=False)

            if priority:
                query = query.filter_by(priority=priority)

            return query.order_by(AlertDB.created_at.desc()).limit(limit).all()

    def acknowledge_alert(self, alert_id: str, user: str = "system") -> Optional[AlertDB]:
        """Acknowledge an alert."""
        with self.session() as session:
            alert = session.query(AlertDB).filter_by(id=alert_id).first()
            if alert:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                alert.acknowledged_by = user
                session.flush()
            return alert

    # Research operations
    def add_research(self, research_data: dict) -> Optional[ResearchDB]:
        """Add a research record."""
        with self.session() as session:
            research = ResearchDB(**research_data)
            session.add(research)
            session.flush()
            return research

    def get_latest_research(self, company_id: str) -> Optional[ResearchDB]:
        """Get the latest research for a company."""
        with self.session() as session:
            return session.query(ResearchDB).filter_by(
                company_id=company_id
            ).order_by(ResearchDB.research_date.desc()).first()

    def get_research_history(
        self,
        company_id: str,
        limit: int = 10,
    ) -> list[ResearchDB]:
        """Get research history for a company."""
        with self.session() as session:
            return session.query(ResearchDB).filter_by(
                company_id=company_id
            ).order_by(ResearchDB.research_date.desc()).limit(limit).all()

    # Migration utilities
    def migrate_from_json(self, data_dir: str = "data") -> dict:
        """
        Migrate data from JSON files to database.

        Args:
            data_dir: Directory containing JSON data files

        Returns:
            Dictionary with migration counts
        """
        data_path = Path(data_dir)
        counts = {
            "companies": 0,
            "deals": 0,
            "investments": 0,
            "alerts": 0,
        }

        # Migrate companies
        companies_file = data_path / "companies.json"
        if companies_file.exists():
            with open(companies_file) as f:
                companies = json.load(f)
            for company_data in companies:
                try:
                    self.add_company(company_data)
                    counts["companies"] += 1
                except Exception as e:
                    print(f"Error migrating company: {e}")

        # Migrate deals
        deals_file = data_path / "deals.json"
        if deals_file.exists():
            with open(deals_file) as f:
                deals = json.load(f)
            for deal_data in deals:
                try:
                    self.add_deal(deal_data)
                    counts["deals"] += 1
                except Exception as e:
                    print(f"Error migrating deal: {e}")

        # Migrate investments
        investments_file = data_path / "investments.json"
        if investments_file.exists():
            with open(investments_file) as f:
                investments = json.load(f)
            for investment_data in investments:
                try:
                    self.add_investment(investment_data)
                    counts["investments"] += 1
                except Exception as e:
                    print(f"Error migrating investment: {e}")

        # Migrate alerts
        alerts_file = data_path / "alerts" / "alerts.json"
        if alerts_file.exists():
            with open(alerts_file) as f:
                alerts = json.load(f)
            for alert_data in alerts:
                try:
                    self.add_alert(alert_data)
                    counts["alerts"] += 1
                except Exception as e:
                    print(f"Error migrating alert: {e}")

        return counts

    def export_to_json(self, output_dir: str = "data/export") -> dict:
        """
        Export database to JSON files.

        Args:
            output_dir: Directory for exported JSON files

        Returns:
            Dictionary with export counts
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        counts = {
            "companies": 0,
            "deals": 0,
            "investments": 0,
            "alerts": 0,
        }

        # Export companies
        companies = self.list_companies(limit=10000)
        companies_data = [c.to_dict() for c in companies]
        with open(output_path / "companies.json", "w") as f:
            json.dump(companies_data, f, indent=2)
        counts["companies"] = len(companies_data)

        # Export deals
        deals = self.list_deals(limit=10000)
        deals_data = [d.to_dict() for d in deals]
        with open(output_path / "deals.json", "w") as f:
            json.dump(deals_data, f, indent=2)
        counts["deals"] = len(deals_data)

        # Export investments
        investments = self.list_investments(limit=10000)
        investments_data = [i.to_dict() for i in investments]
        with open(output_path / "investments.json", "w") as f:
            json.dump(investments_data, f, indent=2)
        counts["investments"] = len(investments_data)

        return counts

    def get_portfolio_summary(self) -> dict:
        """Get portfolio summary from database."""
        with self.session() as session:
            # Count companies by vertical
            companies = session.query(CompanyDB).all()
            by_vertical = {}
            for c in companies:
                v = c.vertical or "unknown"
                by_vertical[v] = by_vertical.get(v, 0) + 1

            # Active investments
            active_investments = session.query(InvestmentDB).filter_by(status="active").all()
            total_invested = sum(i.cost_basis_usd or 0 for i in active_investments)
            current_value = sum(i.current_value_usd or i.cost_basis_usd or 0 for i in active_investments)

            # Deals in pipeline
            active_deals = session.query(DealDB).filter(
                DealDB.status.in_(["sourcing", "diligence", "negotiation"])
            ).count()

            # Unacked alerts
            unacked_alerts = session.query(AlertDB).filter_by(acknowledged=False).count()

            return {
                "companies_tracked": len(companies),
                "companies_by_vertical": by_vertical,
                "active_investments": len(active_investments),
                "total_invested_usd": total_invested,
                "current_value_usd": current_value,
                "unrealized_gain_usd": current_value - total_invested,
                "deals_in_pipeline": active_deals,
                "unacknowledged_alerts": unacked_alerts,
            }
