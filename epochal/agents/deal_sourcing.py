"""
Deal Sourcing Agent for Epochal Capital.

Responsible for:
- Discovering new AI companies matching our thesis
- Identifying potential liquidity events
- Finding deal flow from brokers, platforms, and networks
- Scoring opportunities against investment criteria
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from epochal.agents.base import Agent, AgentRole, AgentTask, AgentResult, TaskStatus
from epochal.core.models import (
    AIVertical,
    Company,
    CompanyStage,
    Deal,
    DealSource,
    DealStatus,
    LiquidityEvent,
    LiquidityEventType,
)
from epochal.core.thesis import InvestmentThesis


@dataclass
class DealOpportunity:
    """A potential deal opportunity discovered by the agent."""
    company_name: str
    description: str
    vertical: AIVertical
    stage: CompanyStage
    valuation_usd: Optional[float] = None
    liquidity_signal: Optional[str] = None
    source: str = ""
    confidence: float = 0.0
    notes: str = ""


# Known high-value AI companies to track (this would be updated dynamically)
TRACKED_AI_COMPANIES = [
    {
        "name": "Anthropic",
        "description": "AI safety company building Claude, a helpful, harmless, and honest AI assistant",
        "vertical": AIVertical.FOUNDATION_MODELS,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 60_000_000_000,
        "key_investors": ["Google", "Spark Capital", "Salesforce Ventures", "Menlo Ventures", "Lightspeed", "General Catalyst", "Tiger Global", "Thrive Capital"],
        "liquidity_signals": ["Strong revenue growth", "Enterprise adoption", "Potential IPO discussions", "AWS partnership", "$2B+ ARR run rate"],
        "revenue_arr_usd": 2_000_000_000,
    },
    {
        "name": "OpenAI",
        "description": "Leading AI research lab building GPT models and ChatGPT",
        "vertical": AIVertical.FOUNDATION_MODELS,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 157_000_000_000,
        "key_investors": ["Microsoft", "Thrive Capital", "Khosla Ventures", "Tiger Global"],
        "liquidity_signals": ["Massive revenue growth", "Enterprise deals", "Restructuring discussions"],
    },
    {
        "name": "Databricks",
        "description": "Unified analytics platform for data engineering, data science, and machine learning",
        "vertical": AIVertical.DATA_INFRASTRUCTURE,
        "stage": CompanyStage.PRE_IPO,
        "valuation_usd": 62_000_000_000,
        "key_investors": ["Andreessen Horowitz", "NEA", "Microsoft", "T. Rowe Price"],
        "liquidity_signals": ["Strong IPO candidate", "High ARR growth", "Public market readiness"],
    },
    {
        "name": "Scale AI",
        "description": "Data labeling and AI infrastructure platform",
        "vertical": AIVertical.DATA_INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 14_000_000_000,
        "key_investors": ["Accel", "Index Ventures", "Founders Fund", "Tiger Global", "Meta"],
        "liquidity_signals": ["Government contracts", "Enterprise growth"],
        "tags": ["ceo_departed", "leadership_exodus"],  # CEO left to join Meta - company gutted
    },
    {
        "name": "Anduril",
        "description": "Defense technology company using AI for autonomous systems",
        "vertical": AIVertical.ROBOTICS,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 14_000_000_000,
        "key_investors": ["Andreessen Horowitz", "General Catalyst", "Founders Fund"],
        "liquidity_signals": ["Major defense contracts", "IPO preparation", "Strategic importance"],
    },
    {
        "name": "Cohere",
        "description": "Enterprise AI platform for NLP and LLMs",
        "vertical": AIVertical.ENTERPRISE_AI,
        "stage": CompanyStage.SERIES_C,
        "valuation_usd": 5_500_000_000,
        "key_investors": ["Inovia Capital", "NVIDIA", "Salesforce Ventures", "Index Ventures"],
        "liquidity_signals": ["Enterprise revenue growth", "Multi-cloud strategy"],
    },
    {
        "name": "Perplexity AI",
        "description": "AI-powered answer engine and search platform",
        "vertical": AIVertical.AI_AGENTS,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 9_000_000_000,
        "key_investors": ["IVP", "NEA", "Databricks Ventures", "NVIDIA"],
        "liquidity_signals": ["Rapid user growth", "Enterprise product launch", "High investor interest"],
    },
    {
        "name": "Glean",
        "description": "Enterprise AI search and knowledge management platform",
        "vertical": AIVertical.ENTERPRISE_AI,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 4_600_000_000,
        "key_investors": ["Sequoia", "Lightspeed", "General Catalyst", "Kleiner Perkins"],
        "liquidity_signals": ["Strong ARR growth", "Enterprise expansion", "IPO potential"],
    },
    {
        "name": "Hugging Face",
        "description": "Open-source AI platform and model hub",
        "vertical": AIVertical.DEVELOPER_TOOLS,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 4_500_000_000,
        "key_investors": ["Lux Capital", "Sequoia", "a]16z", "Google", "Salesforce"],
        "liquidity_signals": ["Community growth", "Enterprise adoption", "Strategic value"],
    },
    {
        "name": "Mistral AI",
        "description": "French AI company building open-weight LLMs",
        "vertical": AIVertical.FOUNDATION_MODELS,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 6_000_000_000,
        "key_investors": ["Andreessen Horowitz", "Lightspeed", "General Catalyst"],
        "liquidity_signals": ["European AI leader", "Strategic partnerships", "Rapid scaling"],
    },
    {
        "name": "Groq",
        "description": "AI inference chip company for ultra-fast LLM serving",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 2_800_000_000,
        "key_investors": ["Tiger Global", "D1 Capital", "BlackRock", "NVIDIA"],
        "liquidity_signals": ["Infrastructure demand", "Inference market growth"],
        "tags": ["leadership_exodus"],  # Key leadership moved to NVIDIA
    },
    {
        "name": "Weights & Biases",
        "description": "MLOps platform for experiment tracking and model management",
        "vertical": AIVertical.MLOps,
        "stage": CompanyStage.SERIES_C,
        "valuation_usd": 1_250_000_000,
        "key_investors": ["Insight Partners", "Felicis Ventures", "Coatue"],
        "liquidity_signals": ["MLOps market growth", "Enterprise adoption"],
    },
    {
        "name": "Runway",
        "description": "AI-powered video generation and editing platform",
        "vertical": AIVertical.CREATIVE_AI,
        "stage": CompanyStage.SERIES_C,
        "valuation_usd": 1_500_000_000,
        "key_investors": ["Google", "NVIDIA", "Salesforce Ventures", "Felicis"],
        "liquidity_signals": ["Creative AI market leader", "Enterprise adoption"],
    },
    {
        "name": "Replit",
        "description": "AI-powered collaborative coding platform",
        "vertical": AIVertical.DEVELOPER_TOOLS,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 1_160_000_000,
        "key_investors": ["Andreessen Horowitz", "Khosla Ventures", "Coatue"],
        "liquidity_signals": ["Developer adoption", "AI coding assistant growth"],
    },
    {
        "name": "Adept AI",
        "description": "Building AI agents that can take actions in software",
        "vertical": AIVertical.AI_AGENTS,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 1_000_000_000,
        "key_investors": ["General Catalyst", "Spark Capital", "Greylock"],
        "liquidity_signals": ["Agent AI market growth", "Enterprise interest"],
    },
    {
        "name": "Character.AI",
        "description": "Conversational AI platform for creating AI characters",
        "vertical": AIVertical.CREATIVE_AI,
        "stage": CompanyStage.SERIES_A,
        "valuation_usd": 1_000_000_000,
        "key_investors": ["Andreessen Horowitz", "Google"],
        "liquidity_signals": ["Consumer traction", "Acquisition interest"],
    },
    {
        "name": "Inflection AI",
        "description": "Personal AI assistant company",
        "vertical": AIVertical.AI_AGENTS,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 4_000_000_000,
        "key_investors": ["Microsoft", "NVIDIA", "Reid Hoffman", "Bill Gates"],
        "liquidity_signals": ["Major tech backing", "Strategic value"],
    },
    {
        "name": "Cerebras",
        "description": "AI chip company building wafer-scale processors",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 4_000_000_000,
        "key_investors": ["Alpha Wave Global", "Altimeter Capital", "Benchmark"],
        "liquidity_signals": ["AI chip demand", "IPO filing", "Infrastructure buildout"],
    },
    {
        "name": "Together AI",
        "description": "Open-source AI cloud platform",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_A,
        "valuation_usd": 1_250_000_000,
        "key_investors": ["Kleiner Perkins", "NVIDIA", "NEA"],
        "liquidity_signals": ["Open-source AI growth", "Cloud platform expansion"],
    },
    {
        "name": "Stability AI",
        "description": "Open-source generative AI company behind Stable Diffusion",
        "vertical": AIVertical.CREATIVE_AI,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 1_000_000_000,
        "key_investors": ["Coatue", "Lightspeed", "O'Shaughnessy Ventures"],
        "liquidity_signals": ["Image generation leader", "Enterprise licensing"],
    },
    {
        "name": "Lambda Labs",
        "description": "GPU cloud platform for AI training and inference, powers Microsoft, OpenAI, Anthropic, xAI",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.PRE_IPO,
        "valuation_usd": 12_000_000_000,  # Estimated $10-15B after Series E
        "key_investors": ["NVIDIA", "TWG Global", "ARK Invest", "In-Q-Tel", "G Squared"],
        "liquidity_signals": [
            "IPO targeting H1 2026",
            "Hired Morgan Stanley, JP Morgan, Citi as IPO advisors",
            "$1.5B Series E Nov 2025",
            "$500M ARR run rate",
            "Microsoft infrastructure deal",
            "NVIDIA strategic backer",
        ],
        "revenue_arr_usd": 500_000_000,
    },
    {
        "name": "Lightmatter",
        "description": "Photonic AI chip company building optical interconnects for AI data centers",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 4_400_000_000,
        "key_investors": ["Founders Fund", "Fidelity", "T. Rowe Price", "Lux Capital", "M12"],
        "liquidity_signals": [
            "CEO stated IPO as next funding source",
            "$850M total raised",
            "Passage L200/M1000 platforms launched March 2025",
            "UALink Consortium member",
            "Major chip packaging partnerships",
        ],
    },
]


class DealSourcingAgent(Agent):
    """
    Agent responsible for sourcing and evaluating investment opportunities.

    Capabilities:
    - scan_market: Discover new AI companies
    - evaluate_company: Score a company against thesis
    - find_liquidity_events: Identify upcoming liquidity opportunities
    - source_deals: Find deal flow from various channels
    - generate_pipeline_report: Summarize deal pipeline
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.DEAL_SOURCING,
            name="Deal Sourcing Agent",
            description="Discovers and evaluates AI investment opportunities",
        )
        self.thesis = InvestmentThesis()
        self.tracked_companies: list[dict] = TRACKED_AI_COMPANIES

    def _register_capabilities(self):
        """Register deal sourcing capabilities."""
        self.register_capability(
            name="scan_market",
            description="Scan the market for new AI companies matching thesis",
            handler=self._scan_market,
        )
        self.register_capability(
            name="evaluate_company",
            description="Evaluate a specific company against investment thesis",
            handler=self._evaluate_company,
            required_inputs=["company_name"],
        )
        self.register_capability(
            name="find_liquidity_events",
            description="Identify companies with upcoming liquidity events",
            handler=self._find_liquidity_events,
        )
        self.register_capability(
            name="generate_opportunities",
            description="Generate list of current investment opportunities",
            handler=self._generate_opportunities,
        )

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a deal sourcing task."""
        start_time = datetime.utcnow()
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = start_time

        try:
            capability_name = task.input_data.get("capability", "scan_market")

            if capability_name == "scan_market":
                result_data = await self._scan_market()
            elif capability_name == "evaluate_company":
                company_name = task.input_data.get("company_name")
                result_data = await self._evaluate_company(company_name)
            elif capability_name == "find_liquidity_events":
                result_data = await self._find_liquidity_events()
            elif capability_name == "generate_opportunities":
                result_data = await self._generate_opportunities()
            else:
                raise ValueError(f"Unknown capability: {capability_name}")

            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.tasks_completed += 1

            return AgentResult(
                task_id=task.id,
                success=True,
                data=result_data,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            self.tasks_failed += 1
            return AgentResult(
                task_id=task.id,
                success=False,
                error=str(e),
                execution_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
            )

    async def _scan_market(self) -> dict:
        """Scan market for AI companies matching thesis."""
        matching_companies = []

        for company_data in self.tracked_companies:
            # Create company object for scoring
            company = Company(
                name=company_data["name"],
                description=company_data["description"],
                vertical=company_data["vertical"],
                stage=company_data["stage"],
                valuation_usd=company_data.get("valuation_usd"),
                key_investors=company_data.get("key_investors", []),
                liquidity_signals=company_data.get("liquidity_signals", []),
                tags=company_data.get("tags", []),
            )

            # Score against thesis
            scores = self.thesis.score_company(company)

            if scores["total"] >= 50:  # Only include companies scoring 50+
                matching_companies.append({
                    "name": company.name,
                    "description": company.description,
                    "vertical": company.vertical.value,
                    "stage": company.stage.value,
                    "valuation_usd": company.valuation_usd,
                    "thesis_score": scores["total"],
                    "liquidity_signals": company.liquidity_signals,
                    "key_investors": company.key_investors,
                })

        # Sort by thesis score
        matching_companies.sort(key=lambda x: x["thesis_score"], reverse=True)

        return {
            "companies_scanned": len(self.tracked_companies),
            "companies_matching": len(matching_companies),
            "top_opportunities": matching_companies[:10],
            "scan_timestamp": datetime.utcnow().isoformat(),
        }

    async def _evaluate_company(self, company_name: str) -> dict:
        """Evaluate a specific company against thesis."""
        # Find company in tracked list
        company_data = None
        for c in self.tracked_companies:
            if c["name"].lower() == company_name.lower():
                company_data = c
                break

        if not company_data:
            return {
                "error": f"Company '{company_name}' not found in tracked companies",
                "suggestion": "Add company to tracking list first",
            }

        company = Company(
            name=company_data["name"],
            description=company_data["description"],
            vertical=company_data["vertical"],
            stage=company_data["stage"],
            valuation_usd=company_data.get("valuation_usd"),
            key_investors=company_data.get("key_investors", []),
            liquidity_signals=company_data.get("liquidity_signals", []),
            tags=company_data.get("tags", []),
        )

        scores = self.thesis.score_company(company)

        return {
            "company": company.name,
            "vertical": company.vertical.value,
            "stage": company.stage.value,
            "valuation_usd": company.valuation_usd,
            "scores": scores,
            "recommendation": self._get_recommendation(scores["total"]),
            "analysis": self._generate_analysis(company, scores),
        }

    async def _find_liquidity_events(self) -> dict:
        """Find companies with upcoming liquidity events."""
        liquidity_candidates = []

        for company_data in self.tracked_companies:
            signals = company_data.get("liquidity_signals", [])

            # Score liquidity potential
            liquidity_score = 0
            event_type = None

            for signal in signals:
                signal_lower = signal.lower()
                if "ipo" in signal_lower:
                    liquidity_score += 40
                    event_type = "IPO"
                if "acquisition" in signal_lower:
                    liquidity_score += 30
                    event_type = event_type or "Acquisition"
                if "secondary" in signal_lower:
                    liquidity_score += 20
                    event_type = event_type or "Secondary"
                if "tender" in signal_lower:
                    liquidity_score += 25
                    event_type = event_type or "Tender Offer"
                if "growth" in signal_lower or "revenue" in signal_lower:
                    liquidity_score += 15
                if "enterprise" in signal_lower:
                    liquidity_score += 10

            if liquidity_score > 0:
                liquidity_candidates.append({
                    "name": company_data["name"],
                    "stage": company_data["stage"].value,
                    "valuation_usd": company_data.get("valuation_usd"),
                    "liquidity_score": min(100, liquidity_score),
                    "likely_event_type": event_type,
                    "signals": signals,
                })

        # Sort by liquidity score
        liquidity_candidates.sort(key=lambda x: x["liquidity_score"], reverse=True)

        return {
            "candidates_found": len(liquidity_candidates),
            "top_liquidity_candidates": liquidity_candidates[:10],
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    async def _generate_opportunities(self) -> dict:
        """Generate list of current investment opportunities."""
        opportunities = []

        for company_data in self.tracked_companies:
            company = Company(
                name=company_data["name"],
                description=company_data["description"],
                vertical=company_data["vertical"],
                stage=company_data["stage"],
                valuation_usd=company_data.get("valuation_usd"),
                key_investors=company_data.get("key_investors", []),
                liquidity_signals=company_data.get("liquidity_signals", []),
                tags=company_data.get("tags", []),
            )

            scores = self.thesis.score_company(company)

            # Only include high-scoring companies
            if scores["total"] >= 60:
                opportunities.append({
                    "company": company.name,
                    "description": company.description,
                    "vertical": company.vertical.value,
                    "stage": company.stage.value,
                    "valuation_usd": company.valuation_usd,
                    "thesis_score": scores["total"],
                    "key_investors": company.key_investors,
                    "liquidity_signals": company.liquidity_signals,
                    "recommendation": self._get_recommendation(scores["total"]),
                })

        opportunities.sort(key=lambda x: x["thesis_score"], reverse=True)

        return {
            "total_opportunities": len(opportunities),
            "opportunities": opportunities,
            "thesis_summary": self.thesis.get_thesis_summary(),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on thesis score."""
        if score >= 80:
            return "STRONG BUY - High priority opportunity"
        elif score >= 70:
            return "BUY - Fits thesis well"
        elif score >= 60:
            return "CONSIDER - Worth deeper diligence"
        elif score >= 50:
            return "WATCH - Monitor for developments"
        else:
            return "PASS - Does not fit current thesis"

    def _generate_analysis(self, company: Company, scores: dict) -> str:
        """Generate qualitative analysis for a company."""
        analysis = []

        # Vertical analysis
        if scores["vertical_fit"] >= 80:
            analysis.append(f"Strong vertical fit in {company.vertical.value}")
        else:
            analysis.append(f"Moderate vertical fit - {company.vertical.value}")

        # Stage analysis
        if scores["stage_fit"] >= 80:
            analysis.append(f"Ideal stage for our thesis ({company.stage.value})")
        else:
            analysis.append(f"Stage ({company.stage.value}) may require longer hold period")

        # Investor quality
        if scores["investor_quality"] >= 75:
            analysis.append("Backed by top-tier investors")
        elif scores["investor_quality"] >= 50:
            analysis.append("Good investor syndicate")

        # Liquidity signals
        if scores["liquidity_signals"] >= 60:
            analysis.append("Strong liquidity signals present")
        else:
            analysis.append("Limited near-term liquidity visibility")

        return " | ".join(analysis)

    def add_company_to_track(self, company_data: dict):
        """Add a new company to the tracking list."""
        self.tracked_companies.append(company_data)

    def get_tracking_list(self) -> list[dict]:
        """Get current tracking list."""
        return self.tracked_companies
