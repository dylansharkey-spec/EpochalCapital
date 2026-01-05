"""
Core data models for Epochal Capital investment tracking.

These models represent the fundamental entities in our investment workflow:
- Companies we're tracking or invested in
- Deals (investment opportunities)
- Investments (actual positions)
- Funds and SPVs (investment vehicles)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class CompanyStage(Enum):
    """Stage of company development."""
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D_PLUS = "series_d_plus"
    PRE_IPO = "pre_ipo"
    PUBLIC = "public"


class LiquidityEventType(Enum):
    """Types of potential liquidity events."""
    IPO = "ipo"
    DIRECT_LISTING = "direct_listing"
    SPAC = "spac"
    ACQUISITION = "acquisition"
    SECONDARY_SALE = "secondary_sale"
    TENDER_OFFER = "tender_offer"
    BUYBACK = "buyback"


class DealStatus(Enum):
    """Status of a deal in our pipeline."""
    DISCOVERED = "discovered"
    RESEARCHING = "researching"
    DUE_DILIGENCE = "due_diligence"
    NEGOTIATING = "negotiating"
    COMMITTED = "committed"
    CLOSED = "closed"
    PASSED = "passed"
    LOST = "lost"


class DealSource(Enum):
    """Source of the deal."""
    DIRECT = "direct"
    BROKER = "broker"
    SPV = "spv"
    FUND = "fund"
    SECONDARY_PLATFORM = "secondary_platform"
    NETWORK = "network"
    AI_SOURCED = "ai_sourced"


class AIVertical(Enum):
    """AI company verticals we track."""
    FOUNDATION_MODELS = "foundation_models"
    INFRASTRUCTURE = "infrastructure"
    DEVELOPER_TOOLS = "developer_tools"
    ENTERPRISE_AI = "enterprise_ai"
    AI_AGENTS = "ai_agents"
    ROBOTICS = "robotics"
    AUTONOMOUS_VEHICLES = "autonomous_vehicles"
    HEALTHCARE_AI = "healthcare_ai"
    FINTECH_AI = "fintech_ai"
    CREATIVE_AI = "creative_ai"
    SECURITY_AI = "security_ai"
    DATA_INFRASTRUCTURE = "data_infrastructure"
    MLOps = "mlops"
    OTHER = "other"


@dataclass
class Company:
    """
    Represents a company we're tracking or invested in.

    Attributes:
        id: Unique identifier
        name: Company name
        description: Brief description of what they do
        vertical: AI vertical they operate in
        stage: Current funding stage
        founded_year: Year company was founded
        headquarters: Location of headquarters
        website: Company website
        valuation_usd: Last known valuation in USD
        valuation_date: Date of last valuation
        total_raised_usd: Total funding raised
        key_investors: List of notable investors
        employee_count: Approximate employee count
        revenue_arr_usd: Annual recurring revenue if known
        liquidity_signals: Signals indicating potential liquidity
        notes: Additional notes
        created_at: When we started tracking
        updated_at: Last update timestamp
        tags: Custom tags for categorization
    """
    name: str
    description: str
    vertical: AIVertical
    stage: CompanyStage
    id: str = field(default_factory=lambda: str(uuid4()))
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    valuation_usd: Optional[float] = None
    valuation_date: Optional[datetime] = None
    total_raised_usd: Optional[float] = None
    key_investors: list[str] = field(default_factory=list)
    employee_count: Optional[int] = None
    revenue_arr_usd: Optional[float] = None
    liquidity_signals: list[str] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "vertical": self.vertical.value,
            "stage": self.stage.value,
            "founded_year": self.founded_year,
            "headquarters": self.headquarters,
            "website": self.website,
            "valuation_usd": self.valuation_usd,
            "valuation_date": self.valuation_date.isoformat() if self.valuation_date else None,
            "total_raised_usd": self.total_raised_usd,
            "key_investors": self.key_investors,
            "employee_count": self.employee_count,
            "revenue_arr_usd": self.revenue_arr_usd,
            "liquidity_signals": self.liquidity_signals,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Company":
        """Create from dictionary."""
        data = data.copy()
        data["vertical"] = AIVertical(data["vertical"])
        data["stage"] = CompanyStage(data["stage"])
        if data.get("valuation_date"):
            data["valuation_date"] = datetime.fromisoformat(data["valuation_date"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


@dataclass
class LiquidityEvent:
    """Represents a potential or confirmed liquidity event."""
    event_type: LiquidityEventType
    expected_date: Optional[datetime] = None
    confidence: float = 0.0  # 0-1 confidence score
    source: str = ""
    notes: str = ""
    confirmed: bool = False


@dataclass
class Deal:
    """
    Represents an investment opportunity.

    Attributes:
        id: Unique identifier
        company_id: Reference to the company
        company_name: Company name (denormalized for convenience)
        status: Current deal status
        source: How we found this deal
        source_name: Name of broker/platform/contact
        share_class: Type of shares (common, preferred, etc.)
        price_per_share_usd: Offered price per share
        minimum_investment_usd: Minimum check size
        total_available_usd: Total allocation available
        valuation_implied_usd: Implied valuation at this price
        discount_to_last_round: Discount vs last primary round
        liquidity_event: Expected liquidity event
        terms: Key deal terms
        documents: List of document references
        contacts: Contact information
        due_date: When we need to decide by
        thesis_score: How well it fits our thesis (0-100)
        notes: Additional notes
        created_at: When deal was added
        updated_at: Last update
    """
    company_id: str
    company_name: str
    source: DealSource
    id: str = field(default_factory=lambda: str(uuid4()))
    status: DealStatus = DealStatus.DISCOVERED
    source_name: str = ""
    share_class: str = "common"
    price_per_share_usd: Optional[float] = None
    minimum_investment_usd: Optional[float] = None
    total_available_usd: Optional[float] = None
    valuation_implied_usd: Optional[float] = None
    discount_to_last_round: Optional[float] = None
    liquidity_event: Optional[LiquidityEvent] = None
    terms: dict = field(default_factory=dict)
    documents: list[str] = field(default_factory=list)
    contacts: list[dict] = field(default_factory=list)
    due_date: Optional[datetime] = None
    thesis_score: Optional[float] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "status": self.status.value,
            "source": self.source.value,
            "source_name": self.source_name,
            "share_class": self.share_class,
            "price_per_share_usd": self.price_per_share_usd,
            "minimum_investment_usd": self.minimum_investment_usd,
            "total_available_usd": self.total_available_usd,
            "valuation_implied_usd": self.valuation_implied_usd,
            "discount_to_last_round": self.discount_to_last_round,
            "liquidity_event": {
                "event_type": self.liquidity_event.event_type.value,
                "expected_date": self.liquidity_event.expected_date.isoformat() if self.liquidity_event.expected_date else None,
                "confidence": self.liquidity_event.confidence,
                "source": self.liquidity_event.source,
                "notes": self.liquidity_event.notes,
                "confirmed": self.liquidity_event.confirmed,
            } if self.liquidity_event else None,
            "terms": self.terms,
            "documents": self.documents,
            "contacts": self.contacts,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "thesis_score": self.thesis_score,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Investment:
    """
    Represents an actual investment position.

    Attributes:
        id: Unique identifier
        deal_id: Reference to the deal
        company_id: Reference to the company
        company_name: Company name
        vehicle_type: How we invested (direct, spv, fund)
        vehicle_id: Reference to SPV or Fund if applicable
        shares: Number of shares owned
        cost_basis_usd: Total cost of investment
        cost_per_share_usd: Cost per share
        current_value_usd: Current estimated value
        investment_date: When investment was made
        status: Active, exited, written off
        exit_date: When we exited (if applicable)
        exit_proceeds_usd: Proceeds from exit
        realized_gain_usd: Realized gain/loss
        notes: Additional notes
    """
    deal_id: str
    company_id: str
    company_name: str
    vehicle_type: str  # "direct", "spv", "fund"
    cost_basis_usd: float
    id: str = field(default_factory=lambda: str(uuid4()))
    vehicle_id: Optional[str] = None
    shares: Optional[float] = None
    cost_per_share_usd: Optional[float] = None
    current_value_usd: Optional[float] = None
    investment_date: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"  # active, exited, written_off
    exit_date: Optional[datetime] = None
    exit_proceeds_usd: Optional[float] = None
    realized_gain_usd: Optional[float] = None
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "deal_id": self.deal_id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "vehicle_type": self.vehicle_type,
            "vehicle_id": self.vehicle_id,
            "shares": self.shares,
            "cost_basis_usd": self.cost_basis_usd,
            "cost_per_share_usd": self.cost_per_share_usd,
            "current_value_usd": self.current_value_usd,
            "investment_date": self.investment_date.isoformat(),
            "status": self.status,
            "exit_date": self.exit_date.isoformat() if self.exit_date else None,
            "exit_proceeds_usd": self.exit_proceeds_usd,
            "realized_gain_usd": self.realized_gain_usd,
            "notes": self.notes,
        }


@dataclass
class SPV:
    """
    Represents a Special Purpose Vehicle for investment.

    Attributes:
        id: Unique identifier
        name: SPV name
        target_company_id: Company this SPV invests in
        manager: SPV manager/sponsor
        management_fee: Annual management fee percentage
        carry: Carried interest percentage
        minimum_investment_usd: Minimum LP commitment
        total_raised_usd: Total capital raised
        our_commitment_usd: Our commitment amount
        status: Open, closed, liquidated
        documents: Legal documents
        notes: Additional notes
    """
    name: str
    target_company_id: str
    manager: str
    id: str = field(default_factory=lambda: str(uuid4()))
    management_fee: float = 0.0
    carry: float = 0.20
    minimum_investment_usd: Optional[float] = None
    total_raised_usd: Optional[float] = None
    our_commitment_usd: Optional[float] = None
    status: str = "open"  # open, closed, liquidated
    documents: list[str] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "target_company_id": self.target_company_id,
            "manager": self.manager,
            "management_fee": self.management_fee,
            "carry": self.carry,
            "minimum_investment_usd": self.minimum_investment_usd,
            "total_raised_usd": self.total_raised_usd,
            "our_commitment_usd": self.our_commitment_usd,
            "status": self.status,
            "documents": self.documents,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Fund:
    """
    Represents an external fund we invest through.

    Attributes:
        id: Unique identifier
        name: Fund name
        manager: Fund manager
        vintage_year: Fund vintage year
        strategy: Investment strategy/focus
        management_fee: Annual management fee
        carry: Carried interest
        our_commitment_usd: Our LP commitment
        called_capital_usd: Capital called to date
        distributions_usd: Distributions received
        nav_usd: Current NAV of our position
        target_companies: Companies fund has invested in
        status: Active, fully invested, liquidating, liquidated
        notes: Additional notes
    """
    name: str
    manager: str
    vintage_year: int
    id: str = field(default_factory=lambda: str(uuid4()))
    strategy: str = ""
    management_fee: float = 0.02
    carry: float = 0.20
    our_commitment_usd: Optional[float] = None
    called_capital_usd: float = 0.0
    distributions_usd: float = 0.0
    nav_usd: Optional[float] = None
    target_companies: list[str] = field(default_factory=list)
    status: str = "active"
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "manager": self.manager,
            "vintage_year": self.vintage_year,
            "strategy": self.strategy,
            "management_fee": self.management_fee,
            "carry": self.carry,
            "our_commitment_usd": self.our_commitment_usd,
            "called_capital_usd": self.called_capital_usd,
            "distributions_usd": self.distributions_usd,
            "nav_usd": self.nav_usd,
            "target_companies": self.target_companies,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }
