---
layout: default
title: "Leveraging DSPy with Foundry AIP: Adaptive AI Meets Enterprise-Grade Infrastructure"
---




# Leveraging DSPy with Foundry AIP: Adaptive AI Meets Enterprise-Grade Infrastructure                             
                              
<img src="./images/05-dspy-aip-foundry.png" width="95%" align="center" alt="MLOps in Palantir Foundry" />                          
                          
                          
---                          

## Collab

1. [Nilesh Saraf](https://github.com/nileshsaraf56), [LinkedIn](https://www.linkedin.com/in/nilesh-saraf-8b7aa327b/)
2. [Abhishek Chaudhury](https://github.com/achaudhury7378), [LinkedIn](https://www.linkedin.com/in/abhishek-chaudhury-07422b191/)

## Introduction

As LLM-powered systems move from demos to real enterprise workflows, traditional prompting starts to show its limits. Static prompts are brittle, hard to evaluate systematically, and difficult to optimize as requirements evolve—especially in Retrieval-Augmented Generation (RAG) systems.

**DSPy** reframes this problem. Instead of writing and manually tweaking prompts, DSPy treats LLM interactions as declarative programs. You define structured task signatures, evaluation criteria, and reasoning modules. DSPy then compiles and optimizes prompts automatically. Prompting becomes engineering.

On the enterprise side, **Palantir Foundry** and its AI layer, **Foundry AIP (Artificial Intelligence Platform)**, provide the governed infrastructure required to deploy AI systems securely. Foundry AIP integrates LLMs with permissioned enterprise data, ensuring traceability, compliance, and operational resilience.

The real opportunity lies in combining DSPy’s adaptive reasoning layer with Foundry AIP’s production-grade foundation.

---

# A Lightweight Use Case: Natural Language Stock Screening

To explore these ideas, I built a stock screener locally using DSPy. The goal was not just to screen stocks—but to demonstrate how structured LLM programs, RAG, and real-time financial data can be composed into a modular system.

The application:

- Accepts a natural-language investment thesis.
- Decomposes it into structured filters.
- Screens a predefined stock universe.
- Enriches results with RAG-based qualitative context.
- Ranks candidates using LLM reasoning.
- Uses real-time data via yfinance.
- Stores embeddings in ChromaDB.
- Leverages Gemini as the language model.
- Uses DSPy modules to define analytical signatures and optimize prompts.

The important takeaway is not the stock screener itself, but the architecture: modular reasoning, evaluation-driven optimization, and interchangeable retrieval strategies.

![View Notebook](./finance-agent-with-dspy/rag-stock-screener-with-dspy.ipynb)

---

## Defining the Stock Universe

We start with a diversified universe across sectors:

```python
STOCK_UNIVERSE = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "META", "NVDA", "CRM", "ADBE", "INTC", "AMD", "ORCL",
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "TMO", "ABT", "BMY", "GILD", "AMGN",
    # Financials
    "JPM", "BAC", "WFC", "GS", "MS", "BLK", "SCHW", "AXP", "C", "USB",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
]
```

In an enterprise setting powered by Foundry AIP, this universe would not be hardcoded. It would come from governed datasets—permissioned financial tables, internal watchlists, or proprietary analytics assets.

This is where Foundry’s data lineage and access control become critical.

---

## Engineering with DSPy: Structured Reasoning Instead of Static Prompts

The core shift is how reasoning is defined.

Instead of writing a long prompt like:

> “Given this thesis, extract filters and rank stocks…”

We define formal signatures.

## DSPy Signatures: Turning Prompts into Programs

```python
class DecomposeThesis(dspy.Signature):
    """Extract structured screening filters as JSON."""
    thesis: str = dspy.InputField()
    filters_json: str = dspy.OutputField()


class RankCandidates(dspy.Signature):
    """Rank candidate stocks and provide bull/bear cases."""
    thesis: str = dspy.InputField()
    candidates_data: str = dspy.InputField()
    ranked_json: str = dspy.OutputField()
```
These signatures act like typed interfaces for LLM behavior.

DSPy then wraps them with `ChainOfThought`, allowing intermediate reasoning while still enforcing structured JSON outputs.

In an enterprise deployment:

- **DSPy** manages reasoning and optimization.
- **Foundry AIP** ensures outputs remain auditable and governed.

---

# Retrieval-Augmented Generation (RAG)

The screener enriches quantitative data with qualitative research context using a vector database.

## Building and Querying the Knowledge Base

```python
def build_knowledge_base():
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="stock_knowledge_base")

    collection.add(
        documents=[doc["text"] for doc in SAMPLE_DOCUMENTS],
        ids=[doc["id"] for doc in SAMPLE_DOCUMENTS],
    )
    return collection


def retrieve_context(collection, query, n_results=3):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["documents"][0] if results["documents"] else []
```

![build-knowledge-base](images/Build_Knowledge_Base.png?raw=True)

In this local prototype:

- The knowledge base is in-memory.
- Documents are simplified macro and sector summaries.

In a Foundry AIP environment:

- Embeddings could be generated from governed document repositories.
- Retrieval could operate on permissioned analyst reports.
- Every query could be logged and audited.

DSPy allows retrieval strategies to evolve—hybrid search, reranking, query rewriting—without rewriting the entire system.

---

# Agentic Screening and Adaptive Filters

One of the most interesting aspects of DSPy is that it enables *agentic adjustment*.

If too few or too many stocks pass the filters, the model dynamically modifies constraints.

## Agentic Filter Adjustment + Orchestration

```python
class NLStockScreener(dspy.Module):

    def __init__(self, stock_universe, knowledge_collection):
        super().__init__()
        self.stock_universe = stock_universe
        self.knowledge_collection = knowledge_collection

        self.decompose = dspy.ChainOfThought(DecomposeThesis)
        self.adjust = dspy.ChainOfThought(AdjustFilters)
        self.rank = dspy.ChainOfThought(RankCandidates)

    def forward(self, thesis):
        # Step 1: Decompose thesis
        decompose_result = self.decompose(thesis=thesis)
        filters = _parse_json(decompose_result.filters_json)

        # Step 2: Screen
        passing = screen_universe(self.stock_universe, filters)

        # Step 3: RAG enrichment
        enriched_candidates = []
        for ticker_symbol, stock_data in passing:
            query = f"{stock_data.get('sector', '')} {thesis}"
            context_docs = retrieve_context(self.knowledge_collection, query, n_results=2)
            enriched_candidates.append({
                "ticker": ticker_symbol,
                "financials": stock_data,
                "qualitative_context": context_docs,
            })

        # Step 4: Rank
        rank_result = self.rank(
            thesis=thesis,
            candidates_data=json.dumps(enriched_candidates, indent=2),
        )

        return _parse_json(rank_result.ranked_json)
```
This module composes:

- Thesis decomposition  
- Quantitative screening  
- RAG enrichment  
- LLM-based ranking  

The result is a multi-step reasoning pipeline—defined programmatically rather than prompt-crafted manually.

---

![rag-final-result](images/RAG_Final_Result.png?raw=True)

# Where Foundry AIP Comes In

The stock screener was built locally. But the architectural pattern aligns extremely well with Foundry AIP.

Conceptually:

| Layer        | Responsibility                                              |
|-------------|-------------------------------------------------------------|
| DSPy        | Declarative reasoning, prompt optimization, agentic adjustments |
| Foundry AIP | Data governance, permissioning, deployment, monitoring     |

Inside Foundry AIP, this could mean:

- Screening internal financial or operational datasets.  
- Running DSPy modules as controlled AI transformations.  
- Logging every LLM interaction.  
- Enforcing role-based access controls.  
- Monitoring model drift and performance.  

DSPy optimizes **how** the model reasons.  
Foundry AIP governs **where and under what constraints** it runs.

---
# The Value Unlocked

## Innovation Without Sacrificing Governance

DSPy allows rapid iteration:

- Swap LLM backends.  
- Change retrieval logic.  
- Improve prompts automatically.  
- Introduce evaluation-driven optimization.  

Foundry AIP ensures:

- Strict data access control.  
- Compliance with internal policy.  
- Traceable model outputs.  
- Enterprise-grade reliability.  

Organizations no longer have to choose between speed and security.

---

## Future-Proof RAG Architectures

RAG techniques evolve rapidly.

With DSPy:

- Retrieval modules are modular.  
- Signatures remain stable.  
- Prompts are compiled, not hardcoded.  

With Foundry:

- Infrastructure remains stable.  
- Governance policies persist across upgrades.  
- Production systems remain resilient.  

This makes AI systems both adaptive and durable.

---

## Bridging Research and Production

Many AI systems remain stuck as prototypes because:

- They lack governance.  
- They lack observability.  
- They are not structured enough to scale

DSPy formalizes experimentation.  
Foundry AIP formalizes production.  

Together, they create a clear path from innovation to enterprise deployment.

---

# Conclusion

DSPy turns prompting into programmable, optimizable reasoning.  
Foundry AIP provides the secure, governed environment required for enterprise AI.

The stock screener is simply an illustration of what structured LLM engineering can look like. The broader opportunity lies in combining:

- Adaptive reasoning  
- Modular RAG pipelines  
- Evaluation-driven optimization  
- Enterprise-grade governance

When DSPy and Foundry AIP are leveraged together, organizations can innovate at the frontier of AI—while maintaining the discipline, security, and resilience that enterprise environments demand.
     
   
---
		   
# [Back to Rocket Ship front page](https://shauryashaurya.github.io/rocket-ship/)            