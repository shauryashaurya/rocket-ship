# nl_stock_screener.py
# A natural language stock screener built with DSPy, yfinance, and ChromaDB.
#
# Given an investment thesis in plain English, this program:
# 1. Decomposes the thesis into structured quantitative filters.
# 2. Screens a universe of tickers via yfinance against those filters.
# 3. Enriches passing candidates with qualitative context from a RAG knowledge base.
# 4. Ranks the candidates and produces per-stock reasoning.
# 5. If too few or too many stocks pass, adjusts filters and retries.

# ============================================================================
# SECTION 1: IMPORTS AND CONFIGURATION
# ============================================================================

import json
import os
import time
from datetime import datetime, timedelta

import chromadb
import dspy
import yfinance as yf

# Configure the language model. Swap the model string and API key as needed.
# Examples: "openai/gpt-4o-mini", "anthropic/claude-sonnet-4-20250514", etc.
LM_MODEL = os.environ.get("DSPY_LM_MODEL", "openai/gpt-4o-mini")
LM_API_KEY = os.environ.get("DSPY_LM_API_KEY", "")

lm = dspy.LM(model=LM_MODEL, api_key=LM_API_KEY, max_tokens=4096)
dspy.configure(lm=lm)

# ============================================================================
# SECTION 2: STOCK UNIVERSE
# ============================================================================

# A curated list of tickers spanning multiple sectors. In production you would
# load the full S&P 500 or Russell 2000 from a file or API. We keep it small
# here so the demo runs in a reasonable time.

STOCK_UNIVERSE = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "META", "NVDA", "CRM", "ADBE", "INTC", "AMD", "ORCL",
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "TMO", "ABT", "BMY", "GILD", "AMGN",
    # Financials
    "JPM", "BAC", "WFC", "GS", "MS", "BLK", "SCHW", "AXP", "C", "USB",
    # Consumer Discretionary
    "AMZN", "TSLA", "HD", "NKE", "SBUX", "MCD", "TGT", "LOW", "BKNG", "TJX",
    # Industrials
    "CAT", "HON", "UPS", "BA", "GE", "RTX", "DE", "LMT", "MMM", "FDX",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
    # Consumer Staples
    "PG", "KO", "PEP", "COST", "WMT", "CL", "MDLZ", "MO", "PM", "KHC",
    # Utilities & Real Estate
    "NEE", "DUK", "SO", "AMT", "PLD", "CCI", "EQIX", "SPG", "O", "WELL",
]


# ============================================================================
# SECTION 3: KNOWLEDGE BASE (ChromaDB RAG)
# ============================================================================

# We populate a small in-memory ChromaDB collection with sample documents.
# In production, these would be 10-K summaries, analyst notes, sector reports,
# earnings call transcripts, or macro research pieces.

SAMPLE_DOCUMENTS = [
    {
        "id": "doc_healthcare_outlook",
        "text": (
            "Healthcare sector outlook 2025: Aging demographics in developed markets "
            "continue to drive demand for therapeutics and medical devices. GLP-1 drugs "
            "are reshaping obesity and diabetes treatment, benefiting companies with "
            "strong pipelines in metabolic disease. Patent cliffs remain a headwind for "
            "large-cap pharma names with blockbuster drugs losing exclusivity in 2025-2026. "
            "Biotech M&A activity is expected to accelerate as big pharma seeks to "
            "replenish pipelines."
        ),
    },
    {
        "id": "doc_tech_valuation",
        "text": (
            "Technology valuations have compressed from 2021 peaks but remain elevated "
            "relative to historical norms. AI infrastructure spending by hyperscalers "
            "continues at unprecedented levels, benefiting semiconductor and cloud "
            "companies. Enterprise software names with strong recurring revenue are "
            "trading at 8-12x forward revenue. Key risk: rising interest rates increase "
            "the discount rate on long-duration growth assets."
        ),
    },
    {
        "id": "doc_energy_transition",
        "text": (
            "Energy sector fundamentals remain constructive. OPEC+ supply discipline "
            "has supported oil prices above $70/barrel. US shale producers are prioritizing "
            "free cash flow and shareholder returns over volume growth. Refining margins "
            "have normalized but remain healthy. Longer term, the energy transition "
            "creates both risks (stranded assets) and opportunities (LNG, carbon capture) "
            "for integrated energy companies."
        ),
    },
    {
        "id": "doc_consumer_spending",
        "text": (
            "Consumer spending has shown resilience despite higher rates. Wage growth "
            "among lower-income cohorts has supported spending at discount and value "
            "retailers. Luxury and discretionary spending has softened, with consumers "
            "trading down across categories. Companies with strong private label brands "
            "and cost discipline are outperforming. Credit card delinquencies are rising "
            "but remain below pre-2008 levels."
        ),
    },
    {
        "id": "doc_rates_macro",
        "text": (
            "The Federal Reserve has signaled a data-dependent approach to rate cuts. "
            "Core PCE inflation remains sticky above the 2% target. Treasury yields "
            "at current levels create competition for equity risk premiums, particularly "
            "for dividend-oriented sectors like utilities and REITs. Financials benefit "
            "from a steeper yield curve and improved net interest margins."
        ),
    },
    {
        "id": "doc_industrial_reshoring",
        "text": (
            "US industrial activity is supported by reshoring trends and infrastructure "
            "spending from the CHIPS Act and Inflation Reduction Act. Construction and "
            "heavy equipment demand remains strong. Supply chain diversification away "
            "from China continues to benefit domestic manufacturers. Defense spending "
            "is bipartisan and growing, supporting aerospace and defense contractors."
        ),
    },
    {
        "id": "doc_pfizer_analysis",
        "text": (
            "Pfizer faces a challenging period as COVID vaccine and Paxlovid revenues "
            "decline sharply from pandemic peaks. The company is executing a cost "
            "reduction program targeting $4B in savings. The Seagen acquisition adds "
            "an oncology pipeline but increased debt load. Free cash flow is expected "
            "to recover in 2025 as cost cuts take effect and new launches ramp. "
            "The stock trades near 10-year lows on a P/E basis."
        ),
    },
    {
        "id": "doc_intel_turnaround",
        "text": (
            "Intel is in the middle of a multi-year turnaround under its IDM 2.0 "
            "strategy. The foundry business requires massive capital expenditure with "
            "uncertain returns. Market share losses in data center to AMD and ARM-based "
            "chips continue. CHIPS Act subsidies provide some offset to capex. The "
            "stock is priced for significant pessimism, trading below book value."
        ),
    },
    {
        "id": "doc_dividend_stocks",
        "text": (
            "High-quality dividend growth stocks remain attractive for long-term "
            "investors. Companies with 10+ year dividend growth streaks, payout ratios "
            "below 60%, and consistent free cash flow generation tend to outperform "
            "in volatile markets. Sectors with strong dividend traditions include "
            "consumer staples, healthcare, and utilities. REITs offer high yields "
            "but face headwinds from elevated interest rates."
        ),
    },
    {
        "id": "doc_free_cash_flow",
        "text": (
            "Free cash flow yield has emerged as a key valuation metric. Companies "
            "generating FCF yields above 5% with sustainable competitive advantages "
            "offer attractive risk-reward. Sectors with the highest median FCF yields "
            "include energy, financials, and mature technology. Capital-light business "
            "models in software and services tend to convert a higher percentage of "
            "revenue to free cash flow."
        ),
    },
]


def build_knowledge_base():
    # Create an ephemeral in-memory ChromaDB client and collection.
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="stock_knowledge_base")
    collection.add(
        documents=[doc["text"] for doc in SAMPLE_DOCUMENTS],
        ids=[doc["id"] for doc in SAMPLE_DOCUMENTS],
    )
    return collection


def retrieve_context(collection, query, n_results=3):
    # Query ChromaDB and return the top matching document texts.
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["documents"][0] if results["documents"] else []


# ============================================================================
# SECTION 4: DSPy SIGNATURES
# ============================================================================

# Signature 1: Decompose a natural language thesis into structured filters.
# The LM outputs a JSON string specifying quantitative screening criteria.
class DecomposeThesis(dspy.Signature):
    """You are a financial analyst. Given an investment thesis in natural language,
    extract structured screening filters as a JSON object. Use only these keys
    (omit any that are not implied by the thesis):
    - sector: string (e.g. "Healthcare", "Technology", "Energy", "Financials",
      "Consumer Discretionary", "Industrials", "Consumer Staples", "Utilities",
      "Real Estate", "Communication Services", "Basic Materials")
    - market_cap_min: number (minimum market cap in USD)
    - market_cap_max: number (maximum market cap in USD)
    - pe_ratio_max: number (maximum trailing P/E ratio)
    - pe_ratio_min: number (minimum trailing P/E ratio)
    - free_cash_flow_positive: boolean (true if FCF must be positive)
    - price_change_max_pct: number (max % price change over lookback, negative = declined)
    - price_change_min_pct: number (min % price change over lookback)
    - price_change_period_days: number (lookback period in days, default 90)
    - dividend_yield_min: number (minimum dividend yield as decimal, e.g. 0.02 = 2%)
    Return ONLY valid JSON. No commentary."""

    thesis: str = dspy.InputField(desc="The investment thesis in plain English")
    filters_json: str = dspy.OutputField(desc="A JSON object of screening filters")


# Signature 2: Given quantitative data and qualitative RAG context for a set
# of candidate stocks, rank them and provide per-stock reasoning.
class RankCandidates(dspy.Signature):
    """You are a financial analyst. Given a list of candidate stocks with their
    financial data and qualitative research context, rank them from most to least
    attractive relative to the stated investment thesis. For each stock, provide
    a brief bull case and bear case (1-2 sentences each). Return your answer as
    a JSON array of objects, each with keys: ticker, rank, bull_case, bear_case.
    Return ONLY valid JSON. No commentary."""

    thesis: str = dspy.InputField(desc="The original investment thesis")
    candidates_data: str = dspy.InputField(desc="JSON array of candidate stock data with financials and context")
    ranked_json: str = dspy.OutputField(desc="JSON array of ranked candidates with reasoning")


# Signature 3: When the initial screen returns too few or too many results,
# the agent decides how to adjust the filters.
class AdjustFilters(dspy.Signature):
    """You are a financial analyst. The stock screen returned an undesirable
    number of results. Given the original filters, the number of results, and
    the target range, adjust the filters to get closer to the target. Relax
    constraints if too few results, tighten if too many. Return ONLY valid JSON
    with the adjusted filters. No commentary."""

    original_filters_json: str = dspy.InputField(desc="The original JSON filters")
    num_results: int = dspy.InputField(desc="How many stocks passed the screen")
    target_min: int = dspy.InputField(desc="Minimum desired number of results")
    target_max: int = dspy.InputField(desc="Maximum desired number of results")
    adjusted_filters_json: str = dspy.OutputField(desc="Adjusted JSON filters")


# ============================================================================
# SECTION 5: YFINANCE SCREENING LOGIC
# ============================================================================

def fetch_stock_data(ticker_symbol):
    # Pull key financial data for a single ticker from yfinance.
    # Returns a dict of the fields we care about, or None on failure.
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        if not info or "marketCap" not in info:
            return None

        # Compute recent price change over a default 90-day window.
        hist = ticker.history(period="6mo")
        price_changes = {}
        if not hist.empty:
            current_price = hist["Close"].iloc[-1]
            for days in [30, 60, 90, 180]:
                if len(hist) >= days:
                    past_price = hist["Close"].iloc[-days]
                    pct = ((current_price - past_price) / past_price) * 100
                    price_changes[days] = round(pct, 2)

        return {
            "ticker": ticker_symbol,
            "name": info.get("shortName", ticker_symbol),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap"),
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "free_cash_flow": info.get("freeCashflow"),
            "dividend_yield": info.get("dividendYield"),
            "revenue": info.get("totalRevenue"),
            "profit_margin": info.get("profitMargins"),
            "debt_to_equity": info.get("debtToEquity"),
            "price_changes": price_changes,
            "current_price": info.get("currentPrice"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }
    except Exception as e:
        print(f"  [warn] Failed to fetch {ticker_symbol}: {e}")
        return None


def apply_filters(stock_data, filters):
    # Check whether a single stock's data passes the given filters.
    # Returns True if the stock passes all specified filters.
    if stock_data is None:
        return False

    sector = filters.get("sector")
    if sector and stock_data.get("sector", "").lower() != sector.lower():
        return False

    mcap = stock_data.get("market_cap")
    if mcap is not None:
        if "market_cap_min" in filters and mcap < filters["market_cap_min"]:
            return False
        if "market_cap_max" in filters and mcap > filters["market_cap_max"]:
            return False

    pe = stock_data.get("trailing_pe")
    if pe is not None:
        if "pe_ratio_max" in filters and pe > filters["pe_ratio_max"]:
            return False
        if "pe_ratio_min" in filters and pe < filters["pe_ratio_min"]:
            return False

    fcf = stock_data.get("free_cash_flow")
    if filters.get("free_cash_flow_positive") and (fcf is None or fcf <= 0):
        return False

    div_yield = stock_data.get("dividend_yield")
    if "dividend_yield_min" in filters:
        if div_yield is None or div_yield < filters["dividend_yield_min"]:
            return False

    period = filters.get("price_change_period_days", 90)
    price_changes = stock_data.get("price_changes", {})
    # Find the closest available period to the requested one.
    available_periods = sorted(price_changes.keys())
    closest_period = min(available_periods, key=lambda p: abs(p - period)) if available_periods else None

    if closest_period is not None:
        pct_change = price_changes[closest_period]
        if "price_change_max_pct" in filters and pct_change > filters["price_change_max_pct"]:
            return False
        if "price_change_min_pct" in filters and pct_change < filters["price_change_min_pct"]:
            return False

    return True


def screen_universe(universe, filters):
    # Screen the full universe of tickers against the filters.
    # Returns a list of (ticker, stock_data) tuples that pass.
    print(f"\n  Screening {len(universe)} tickers...")
    passing = []
    for i, ticker_symbol in enumerate(universe):
        if (i + 1) % 20 == 0:
            print(f"  ... processed {i + 1}/{len(universe)}")
        data = fetch_stock_data(ticker_symbol)
        if apply_filters(data, filters):
            passing.append((ticker_symbol, data))
            print(f"  [pass] {ticker_symbol}")
    print(f"  Screen complete: {len(passing)} stocks passed.\n")
    return passing


# ============================================================================
# SECTION 6: THE SCREENER MODULE (DSPy)
# ============================================================================

class NLStockScreener(dspy.Module):
    # The main DSPy module. Composes filter decomposition, screening,
    # agentic filter adjustment, RAG enrichment, and ranking.

    def __init__(self, stock_universe, knowledge_collection, target_min=3, target_max=10, max_retries=2):
        super().__init__()
        self.stock_universe = stock_universe
        self.knowledge_collection = knowledge_collection
        self.target_min = target_min
        self.target_max = target_max
        self.max_retries = max_retries

        # DSPy predictors. ChainOfThought wraps a Signature and asks the LM
        # to produce intermediate reasoning before the final output.
        self.decompose = dspy.ChainOfThought(DecomposeThesis)
        self.adjust = dspy.ChainOfThought(AdjustFilters)
        self.rank = dspy.ChainOfThought(RankCandidates)

    def forward(self, thesis):
        # Step 1: Decompose the thesis into structured filters.
        print("=" * 60)
        print("STEP 1: Decomposing thesis into filters")
        print("=" * 60)
        decompose_result = self.decompose(thesis=thesis)
        filters = _parse_json(decompose_result.filters_json)
        print(f"  Filters: {json.dumps(filters, indent=2)}")

        # Step 2: Screen the universe. Retry with adjusted filters if needed.
        print("\n" + "=" * 60)
        print("STEP 2: Screening stock universe (with agentic adjustment)")
        print("=" * 60)
        passing = screen_universe(self.stock_universe, filters)

        retries = 0
        while (len(passing) < self.target_min or len(passing) > self.target_max) and retries < self.max_retries:
            retries += 1
            direction = "too few" if len(passing) < self.target_min else "too many"
            print(f"  [{direction}: {len(passing)} results, target {self.target_min}-{self.target_max}]")
            print(f"  Adjusting filters (attempt {retries}/{self.max_retries})...")

            adjust_result = self.adjust(
                original_filters_json=json.dumps(filters),
                num_results=len(passing),
                target_min=self.target_min,
                target_max=self.target_max,
            )
            filters = _parse_json(adjust_result.adjusted_filters_json)
            print(f"  Adjusted filters: {json.dumps(filters, indent=2)}")
            passing = screen_universe(self.stock_universe, filters)

        if not passing:
            print("  No stocks passed any filter configuration. Exiting.")
            return dspy.Prediction(
                filters=filters,
                candidates=[],
                ranked_output=[],
            )

        # Step 3: RAG enrichment. For each passing stock, query the knowledge
        # base for relevant qualitative context.
        print("\n" + "=" * 60)
        print("STEP 3: RAG enrichment from knowledge base")
        print("=" * 60)
        enriched_candidates = []
        for ticker_symbol, stock_data in passing:
            # Build a retrieval query from the stock's sector and the thesis.
            query = f"{stock_data.get('sector', '')} {stock_data.get('industry', '')} {thesis}"
            context_docs = retrieve_context(self.knowledge_collection, query, n_results=2)
            print(f"  {ticker_symbol}: retrieved {len(context_docs)} context documents")
            enriched_candidates.append({
                "ticker": ticker_symbol,
                "financials": {
                    "name": stock_data.get("name"),
                    "sector": stock_data.get("sector"),
                    "industry": stock_data.get("industry"),
                    "market_cap": stock_data.get("market_cap"),
                    "trailing_pe": stock_data.get("trailing_pe"),
                    "forward_pe": stock_data.get("forward_pe"),
                    "free_cash_flow": stock_data.get("free_cash_flow"),
                    "dividend_yield": stock_data.get("dividend_yield"),
                    "profit_margin": stock_data.get("profit_margin"),
                    "debt_to_equity": stock_data.get("debt_to_equity"),
                    "price_changes": stock_data.get("price_changes"),
                    "current_price": stock_data.get("current_price"),
                    "52w_high": stock_data.get("fifty_two_week_high"),
                    "52w_low": stock_data.get("fifty_two_week_low"),
                },
                "qualitative_context": context_docs,
            })

        # Step 4: Rank the candidates using the LM.
        print("\n" + "=" * 60)
        print("STEP 4: Ranking candidates")
        print("=" * 60)
        rank_result = self.rank(
            thesis=thesis,
            candidates_data=json.dumps(enriched_candidates, indent=2, default=str),
        )
        ranked = _parse_json(rank_result.ranked_json)
        print(f"  Ranking complete. {len(ranked)} stocks ranked.\n")

        return dspy.Prediction(
            filters=filters,
            candidates=enriched_candidates,
            ranked_output=ranked,
        )


# ============================================================================
# SECTION 7: UTILITIES
# ============================================================================

def _parse_json(text):
    # Parse a JSON string from LM output, handling common issues like
    # markdown code fences or trailing text.
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    if text.startswith("json"):
        text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON within the text.
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start = text.find(start_char)
            end = text.rfind(end_char)
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    continue
        print(f"  [warn] Could not parse JSON from LM output: {text[:200]}")
        return {}


def print_results(prediction):
    # Pretty-print the final ranked output.
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"\nFilters used: {json.dumps(prediction.filters, indent=2)}")
    print(f"\nCandidates screened: {len(prediction.candidates)}")
    print(f"\n{'='*60}")

    ranked = prediction.ranked_output
    if isinstance(ranked, list):
        for entry in ranked:
            ticker = entry.get("ticker", "???")
            rank = entry.get("rank", "?")
            bull = entry.get("bull_case", "N/A")
            bear = entry.get("bear_case", "N/A")
            print(f"\n  #{rank} {ticker}")
            print(f"     Bull: {bull}")
            print(f"     Bear: {bear}")
    else:
        print(f"  Raw output: {ranked}")
    print()


# ============================================================================
# SECTION 8: MAIN
# ============================================================================

def main():
    # Build the RAG knowledge base.
    print("Building knowledge base...")
    kb = build_knowledge_base()

    # Instantiate the screener module.
    screener = NLStockScreener(
        stock_universe=STOCK_UNIVERSE,
        knowledge_collection=kb,
        target_min=3,
        target_max=8,
        max_retries=2,
    )

    # Define the investment thesis. Change this to whatever you want.
    thesis = (
        "Find me undervalued healthcare companies with strong free cash flow "
        "that have been beaten down in the last 3 months. I want stocks trading "
        "at a low P/E with real earnings power, not speculative biotechs."
    )

    print(f"\nThesis: {thesis}\n")

    # Run the screener.
    result = screener(thesis=thesis)

    # Print results.
    print_results(result)


if __name__ == "__main__":
    main()
