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
# Last Updated: January 28, 2026
TRACKED_AI_COMPANIES = [
    {
        "name": "Anthropic",
        "description": "AI safety company building Claude, a helpful, harmless, and honest AI assistant",
        "vertical": AIVertical.FOUNDATION_MODELS,
        "stage": CompanyStage.PRE_IPO,
        "valuation_usd": 350_000_000_000,  # $350B - Jan 2026 doubled round
        "key_investors": ["Google", "Coatue", "GIC", "Sequoia", "Iconiq", "Lightspeed", "Menlo Ventures", "Fidelity", "Spark Capital"],
        "liquidity_signals": [
            "IPO H2 2026 - Wilson Sonsini engaged",
            "$20B mega-round doubled from $10B on demand",
            "$10B ARR confirmed by CEO",
            "Claude Code hit $1B ARR in 6 months",
            "300,000+ enterprise customers",
            "Breakeven expected 2028 - faster than OpenAI",
            "Sequoia broke VC taboo to invest",
        ],
        "revenue_arr_usd": 10_000_000_000,  # $10B ARR
    },
    {
        "name": "OpenAI",
        "description": "Leading AI research lab building GPT models and ChatGPT",
        "vertical": AIVertical.FOUNDATION_MODELS,
        "stage": CompanyStage.PRE_IPO,
        "valuation_usd": 500_000_000_000,  # $500B current, seeking $830B
        "key_investors": ["Microsoft", "SoftBank", "Thrive Capital", "Khosla Ventures", "Tiger Global"],
        "liquidity_signals": [
            "Seeking $100B raise at $830B valuation",
            "IPO H2 2026 or 2027 per CFO",
            "$20B ARR run rate",
            "800M weekly active users",
            "1M+ business customers",
            "$250B Azure commitment, $38B AWS deal",
            "$14B projected loss in 2026",
        ],
        "revenue_arr_usd": 20_000_000_000,  # $20B ARR
    },
    {
        "name": "Databricks",
        "description": "Unified analytics platform for data engineering, data science, and machine learning",
        "vertical": AIVertical.DATA_INFRASTRUCTURE,
        "stage": CompanyStage.PRE_IPO,
        "valuation_usd": 134_000_000_000,  # $134B - Dec 2025
        "key_investors": ["Andreessen Horowitz", "NEA", "Microsoft", "T. Rowe Price", "Thrive Capital", "a16z"],
        "liquidity_signals": [
            "IPO early 2026 target",
            "$4B raise at $134B valuation Dec 2025",
            "$1.8B additional debt Jan 2026 for IPO prep",
            "$4.8B ARR growing 55%+ YoY",
            "CEO targets $1T valuation",
            "Acquired Neon for $1B",
            "Both data warehousing and AI products exceed $1B each",
        ],
        "revenue_arr_usd": 4_800_000_000,  # $4.8B ARR
    },
    {
        "name": "Scale AI",
        "description": "Data labeling and AI infrastructure platform pivoting to enterprise AI applications",
        "vertical": AIVertical.DATA_INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 29_000_000_000,  # $29B after Meta investment
        "key_investors": ["Meta", "Accel", "Index Ventures", "Founders Fund", "Tiger Global"],
        "liquidity_signals": [
            "Revenue doubled in 2025",
            "$1B+ new bookings",
            "$99M US Army contract",
            "Enterprise clients: BP, Mayo Clinic, Allianz",
        ],
        "tags": ["ceo_departed", "leadership_exodus"],  # CEO Alexandr Wang left to join Meta as Chief AI Officer
    },
    {
        "name": "Anduril",
        "description": "Defense technology company using AI for autonomous systems and drones",
        "vertical": AIVertical.ROBOTICS,
        "stage": CompanyStage.PRE_IPO,
        "valuation_usd": 66_400_000_000,  # $66.4B Dec 2025
        "key_investors": ["Founders Fund", "Andreessen Horowitz", "General Catalyst", "Valor Equity Partners"],
        "liquidity_signals": [
            "IPO 2026 after Ohio manufacturing facility launch (July 2026)",
            "$2.5B raise at $30.5B Jun 2025, now $66.4B",
            "Revenue ~$2B estimated 2026",
            "$1B Ohio manufacturing facility investment",
            "CEO says 'definitely' going public",
        ],
        "revenue_arr_usd": 2_000_000_000,  # ~$2B estimated
    },
    {
        "name": "Cohere",
        "description": "Enterprise AI platform for NLP and LLMs, founded by Transformer paper co-author",
        "vertical": AIVertical.ENTERPRISE_AI,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 7_000_000_000,  # $7B after $100M extension
        "key_investors": ["Radical Ventures", "Inovia Capital", "NVIDIA", "Salesforce Ventures", "AMD Ventures", "PSP Investments"],
        "liquidity_signals": [
            "IPO preparation - CFO hired Aug 2025",
            "$600M raised at $6.8B-$7B valuation",
            "$200M+ ARR target end 2025",
            "Employee tender offer ahead of IPO/M&A",
            "450 employees",
        ],
        "revenue_arr_usd": 200_000_000,  # $200M ARR target
    },
    {
        "name": "Perplexity AI",
        "description": "AI-powered answer engine and search platform",
        "vertical": AIVertical.AI_AGENTS,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 20_000_000_000,  # $20B Sept 2025
        "key_investors": ["SoftBank Vision Fund 2", "NVIDIA", "Accel", "Jeff Bezos", "IVP", "NEA"],
        "liquidity_signals": [
            "$200M ARR approaching",
            "$656M revenue target 2026",
            "$1.5B total raised",
            "100x revenue multiple",
            "Enterprise Max product launching",
        ],
        "revenue_arr_usd": 200_000_000,  # ~$200M ARR
    },
    {
        "name": "Glean",
        "description": "Enterprise AI search and knowledge management platform",
        "vertical": AIVertical.ENTERPRISE_AI,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 7_200_000_000,  # $7.2B Jun 2025
        "key_investors": ["Wellington Management", "Sequoia", "Lightspeed", "General Catalyst", "Kleiner Perkins"],
        "liquidity_signals": [
            "$150M Series F at $7.2B Jun 2025",
            "$100M+ ARR achieved",
            "Cash-flow positive",
            "72x revenue multiple - investors getting 'early access to franchise'",
            "CEO founded Rubrik (successful IPO Apr 2024)",
        ],
        "revenue_arr_usd": 100_000_000,  # $100M+ ARR
    },
    {
        "name": "Hugging Face",
        "description": "Open-source AI platform and model hub, expanding into robotics",
        "vertical": AIVertical.DEVELOPER_TOOLS,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 4_500_000_000,  # $4.5B Aug 2023 - no new round
        "key_investors": ["Lux Capital", "Sequoia", "a16z", "Google", "Amazon", "NVIDIA", "Salesforce", "Intel", "AMD"],
        "liquidity_signals": [
            "$130M revenue 2024, up from $70M 2023",
            "367% revenue growth 2022-2023",
            "5M+ users, 1M+ models hosted",
            "LeRobot robotics initiative launched Sept 2025",
            "20,000+ open source repo integrations",
        ],
        "revenue_arr_usd": 130_000_000,  # $130M revenue
    },
    {
        "name": "Mistral AI",
        "description": "French AI company building open-weight LLMs - Europe's AI champion",
        "vertical": AIVertical.FOUNDATION_MODELS,
        "stage": CompanyStage.SERIES_C,
        "valuation_usd": 14_000_000_000,  # €11.7B / ~$14B Sept 2025
        "key_investors": ["ASML", "DST Global", "Andreessen Horowitz", "Bpifrance", "General Catalyst", "Index Ventures", "Lightspeed", "NVIDIA"],
        "liquidity_signals": [
            "€1.7B Series C at €11.7B valuation Sept 2025",
            "Largest European AI funding round ever",
            "Revenue 25x increase YoY",
            "Hundreds of millions in signed contracts",
            "Mistral Compute platform launching 2026 with 18,000 NVIDIA chips",
            "ASML took 11% stake",
            "IPO ambitions signaled by founders",
        ],
        "revenue_arr_usd": 300_000_000,  # Estimated based on growth
    },
    {
        "name": "Groq",
        "description": "AI inference chip company - ACQUIRED BY NVIDIA Dec 2025",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 20_000_000_000,  # $20B NVIDIA acquisition price
        "key_investors": ["BlackRock", "Neuberger Berman", "Samsung", "Cisco", "Altimeter"],
        "liquidity_signals": [
            "ACQUIRED: NVIDIA paid $20B cash Dec 2025",
            "Non-exclusive license deal for LPU technology",
            "Founders and core team joined NVIDIA",
            "Prior valuation $6.9B Sept 2025",
            "SRAM-based LPUs 10-80x faster than HBM",
        ],
        "tags": ["acquired", "liquidity_event_complete"],
    },
    {
        "name": "Weights & Biases",
        "description": "MLOps platform for experiment tracking - ACQUIRED BY COREWEAVE Mar 2025",
        "vertical": AIVertical.MLOps,
        "stage": CompanyStage.SERIES_C,
        "valuation_usd": 1_700_000_000,  # $1.7B acquisition price
        "key_investors": ["Insight Partners", "Felicis Ventures", "Coatue", "Nat Friedman", "Daniel Gross"],
        "liquidity_signals": [
            "ACQUIRED: CoreWeave paid ~$1.7B Mar 2025",
            "Customers include OpenAI, Anthropic, Cohere, Hugging Face",
            "20,000+ open source repo integrations",
        ],
        "tags": ["acquired", "liquidity_event_complete"],
    },
    {
        "name": "Runway",
        "description": "AI-powered video generation and editing platform - Gen-4 model leader",
        "vertical": AIVertical.CREATIVE_AI,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 3_000_000_000,  # $3B Apr 2025
        "key_investors": ["General Atlantic", "Fidelity", "Baillie Gifford", "NVIDIA", "SoftBank", "Google", "Salesforce Ventures"],
        "liquidity_signals": [
            "$308M Series D at $3B valuation Apr 2025",
            "$1.05B total raised",
            "$300M ARR target 2025",
            "AMC Networks partnership Jun 2025",
            "Amazon House of David uses 350+ AI shots",
            "Gen-4 model and API launched",
        ],
        "revenue_arr_usd": 300_000_000,  # Target
    },
    {
        "name": "Replit",
        "description": "AI-powered collaborative coding platform - 'vibe coding' leader",
        "vertical": AIVertical.DEVELOPER_TOOLS,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 9_000_000_000,  # $9B Jan 2026 round in progress
        "key_investors": ["Georgian", "Prysm Capital", "Google AI Futures Fund", "Andreessen Horowitz", "Coatue", "Amex Ventures"],
        "liquidity_signals": [
            "$400M raise at $9B valuation Jan 2026 (in progress)",
            "$250M Series E at $3B Sept 2025",
            "$240M revenue 2025, targeting $1B in 2026",
            "150,000+ paying customers",
            "Revenue grew from $2.8M to $150M ARR in <1 year",
        ],
        "revenue_arr_usd": 240_000_000,  # $240M 2025
    },
    {
        "name": "Adept AI",
        "description": "AI agents company - TALENT ACQUIRED BY AMAZON Jun 2024",
        "vertical": AIVertical.AI_AGENTS,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 1_000_000_000,
        "key_investors": ["General Catalyst", "Spark Capital", "Greylock"],
        "liquidity_signals": [
            "ACQUI-HIRE: Amazon hired founders + team Jun 2024",
            "Amazon licensed Adept technology",
            "Investors roughly recouped $414M investment",
            "Amazon AGI SF Lab created, led by David Luan",
            "~1/3 of employees remain at stub company",
        ],
        "tags": ["acqui_hired", "leadership_exodus"],
    },
    {
        "name": "Character.AI",
        "description": "Conversational AI platform - pivoting post-Google deal",
        "vertical": AIVertical.CREATIVE_AI,
        "stage": CompanyStage.SERIES_A,
        "valuation_usd": 2_500_000_000,  # $2.5B buyout valuation
        "key_investors": ["a16z", "Former Google employees now own as co-op"],
        "liquidity_signals": [
            "RESTRUCTURED: Google paid $2.7B Aug 2024",
            "Founders Shazeer & De Freitas rejoined Google",
            "Investors bought out at $88/share (2.5x Series A)",
            "Company now employee-owned co-op",
            "Pivoting away from LLM development to post-training",
            "Will use open-source models (Llama)",
        ],
        "tags": ["restructured", "talent_departed"],
    },
    {
        "name": "Inflection AI",
        "description": "Personal AI assistant - TALENT ACQUIRED BY MICROSOFT Mar 2024",
        "vertical": AIVertical.AI_AGENTS,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 4_000_000_000,
        "key_investors": ["Microsoft", "NVIDIA", "Reid Hoffman", "Bill Gates"],
        "liquidity_signals": [
            "ACQUI-HIRE: Microsoft paid $650M+ Mar 2024",
            "Mustafa Suleyman now CEO of Microsoft AI",
            "Most staff joined Microsoft",
            "Inflection pivoted to enterprise B2B",
            "FTC reviewing deal",
        ],
        "tags": ["acqui_hired", "leadership_exodus"],
    },
    {
        "name": "Cerebras",
        "description": "AI chip company building wafer-scale processors - 21x faster than NVIDIA Blackwell",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.PRE_IPO,
        "valuation_usd": 22_000_000_000,  # $22B Jan 2026
        "key_investors": ["Alpha Wave Global", "Altimeter Capital", "Benchmark", "G42 (divested)"],
        "liquidity_signals": [
            "IPO Q2 2026 target",
            "$1B raise at $22B valuation Jan 2026 (in progress)",
            "OpenAI $10B compute deal - 750MW through 2028",
            "CFIUS cleared March 2025 after G42 divested",
            "CS-3 system 21x faster than NVIDIA B200",
            "Wafer-scale architecture advantage",
        ],
    },
    {
        "name": "Together AI",
        "description": "Open-source AI cloud platform with enterprise inference",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 3_300_000_000,  # $3.3B Feb 2025
        "key_investors": ["General Catalyst", "Prosperity7", "Salesforce Ventures", "DAMAC Capital", "NVIDIA", "Kleiner Perkins", "Coatue"],
        "liquidity_signals": [
            "$305M Series B at $3.3B valuation Feb 2025",
            "$300M ARR Sept 2025 (up from $30M Feb 2024)",
            "10x revenue growth in 18 months",
            "200MW power capacity secured",
            "36,000 NVIDIA GB200 cluster with Hypertec",
            "$537M total raised",
        ],
        "revenue_arr_usd": 300_000_000,  # $300M ARR
    },
    {
        "name": "Stability AI",
        "description": "Open-source generative AI company behind Stable Diffusion - restructuring",
        "vertical": AIVertical.CREATIVE_AI,
        "stage": CompanyStage.SERIES_B,
        "valuation_usd": 1_000_000_000,  # $1B Jun 2024 - likely lower now
        "key_investors": ["Coatue", "Lightspeed", "O'Shaughnessy Ventures"],
        "liquidity_signals": [
            "New CEO Prem Akkaraju (ex-Weta Digital)",
            "$80M funding Jun 2024",
            "Financial restructuring ongoing",
            "Pivoting to membership/API revenue model",
            "Acquisition more likely than IPO",
        ],
        "tags": ["restructuring", "leadership_change"],
    },
    {
        "name": "Lambda Labs",
        "description": "GPU cloud platform for AI training and inference, powers Microsoft, OpenAI, Anthropic, xAI",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.PRE_IPO,
        "valuation_usd": 5_860_000_000,  # $5.86B per NPM Jan 2026
        "key_investors": ["Mubadala", "NVIDIA", "TWG Global", "ARK Invest", "In-Q-Tel", "G Squared"],
        "liquidity_signals": [
            "IPO H2 2026 target",
            "$350M convertible notes Jan 2026 - 20% discount to IPO",
            "Morgan Stanley, JP Morgan, Citi as IPO advisors",
            "$505M ARR",
            "Microsoft infrastructure deal",
            "Hiive secondary at $54/share",
        ],
        "revenue_arr_usd": 505_000_000,  # $505M ARR
    },
    {
        "name": "Lightmatter",
        "description": "Photonic AI chip company building optical interconnects for AI data centers",
        "vertical": AIVertical.INFRASTRUCTURE,
        "stage": CompanyStage.SERIES_D_PLUS,
        "valuation_usd": 8_730_000_000,  # $8.73B estimated Jan 2026 per Forge
        "key_investors": ["Founders Fund", "Fidelity", "T. Rowe Price", "Lux Capital", "M12"],
        "liquidity_signals": [
            "CEO stated IPO as next funding source",
            "$850M total raised",
            "Passage L200/M1000 platforms launched March 2025",
            "UALink Consortium member",
            "Former NVIDIA CFO Simona Jankowski hired as CFO",
            "Forge estimates $8.73B valuation Jan 2026",
        ],
    },
    {
        "name": "xAI",
        "description": "Elon Musk's AI company building Grok - high valuation risk",
        "vertical": AIVertical.FOUNDATION_MODELS,
        "stage": CompanyStage.SERIES_C,
        "valuation_usd": 230_000_000_000,  # $230B last round - possibly overvalued
        "key_investors": ["Sequoia", "a16z", "Valor Equity Partners", "Kingdom Holdings", "QIA"],
        "liquidity_signals": [
            "Hiive secondary at $121-$135/share (56-79% premium to last round)",
            "$12B Series C at $50B Dec 2024",
            "$6B Series B at $24B May 2024",
            "~$2B estimated revenue",
            "115x revenue multiple - EXTREMELY HIGH",
            "Memphis data center 100K H100 GPUs",
        ],
        "revenue_arr_usd": 2_000_000_000,  # ~$2B estimated
        "tags": ["valuation_risk", "premium_to_last_round"],
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
