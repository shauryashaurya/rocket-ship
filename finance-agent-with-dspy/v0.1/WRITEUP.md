# DSPy + Yahoo Finance: Natural Language Stock Screener

## What This Document Covers

This document explains the core concepts of DSPy, describes how they apply to the Natural Language Stock Screener (`nl_stock_screener.py`), and walks through the code section by section.

---

## Part 1: DSPy Core Concepts

### What DSPy Is

DSPy is a framework for programming with language models. Instead of writing prompts by hand, you define typed input/output specifications (called Signatures) and compose them into Modules. DSPy then handles prompt construction, and optionally optimizes prompts and few-shot examples automatically against a metric you define.

The key shift: you write *programs*, not *prompts*.

### Signatures

A Signature is a typed contract between your code and the language model. It specifies what goes in and what comes out, with field descriptions. DSPy converts this into a prompt automatically.

```python
class DecomposeThesis(dspy.Signature):
    """Given an investment thesis, extract structured screening filters as JSON."""
    thesis: str = dspy.InputField(desc="The investment thesis in plain English")
    filters_json: str = dspy.OutputField(desc="A JSON object of screening filters")
```

The docstring becomes the instruction. The fields become labeled slots in the prompt. The LM fills in the output fields.

Why this matters: the Signature is a *declaration*, not an implementation. DSPy can change how it prompts the LM (adding few-shot examples, chain-of-thought reasoning, etc.) without you rewriting anything.

### InputField and OutputField

These annotate which fields the user provides and which the LM should produce. They are purely declarative. `desc` provides the LM with a natural-language description of what each field contains.

### Modules

A Module is a composable unit of LM-powered logic. It inherits from `dspy.Module` and has a `forward()` method, similar to PyTorch.

```python
class NLStockScreener(dspy.Module):
    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought(DecomposeThesis)
    
    def forward(self, thesis):
        result = self.decompose(thesis=thesis)
        return result
```

Modules can contain other Modules. This is how you compose multi-step reasoning pipelines.

### Predictors

A Predictor is a Module that wraps a Signature and calls the LM. The two most common ones:

- `dspy.Predict(SomeSignature)` -- calls the LM and returns the output fields directly.
- `dspy.ChainOfThought(SomeSignature)` -- asks the LM to produce step-by-step reasoning before answering. This generally improves accuracy for complex tasks.

`ChainOfThought` internally adds a `reasoning` field to the prompt, asking the LM to think before it answers. You do not need to engineer this yourself.

### dspy.LM and dspy.configure

`dspy.LM` wraps a language model provider. It accepts a model string (using LiteLLM conventions) and an API key:

```python
lm = dspy.LM(model="openai/gpt-4o-mini", api_key="sk-...")
dspy.configure(lm=lm)
```

`dspy.configure` sets the global default LM. All predictors use this LM unless overridden. Supported providers include OpenAI, Anthropic, Cohere, local models via Ollama, and anything LiteLLM supports.

### dspy.Prediction

The return type of any Module's `forward()` method. It behaves like a namespace: you can access fields as attributes (`result.filters_json`) or by indexing (`result["filters_json"]`). You can also create them manually to return structured results from your own Modules.

### Optimizers (Teleprompters)

This is DSPy's distinguishing feature. An optimizer takes:

1. Your Module (the program).
2. A dataset of examples (input/output pairs).
3. A metric function (how to score outputs).

It then automatically searches for the best prompt, few-shot examples, or fine-tuning data to maximize your metric. Common optimizers:

- `BootstrapFewShot` -- generates and selects few-shot examples by running the program on training data and keeping outputs that pass the metric.
- `MIPROv2` -- jointly optimizes instructions and few-shot examples.
- `BootstrapFinetune` -- generates training data and fine-tunes the LM.

We do not use an optimizer in this demo because it requires a labeled dataset of (thesis, correct_stocks) pairs. In production, you would collect examples of investment theses and their expected screen results, then compile the module:

```python
optimizer = dspy.BootstrapFewShot(metric=my_metric, max_bootstrapped_demos=4)
compiled_screener = optimizer.compile(screener, trainset=my_examples)
```

This is where DSPy becomes meaningfully different from a prompt template: the program improves itself.

### ReAct and Agentic Patterns

DSPy provides `dspy.ReAct` for tool-using agents, and `dspy.Tool` for wrapping Python functions as tools the LM can call. Our screener uses a simpler agentic pattern: a retry loop where the LM adjusts filters based on screening results. This is a form of agentic behavior (the system acts, observes, and adapts) without requiring the full ReAct framework.

---

## Part 2: How RAG Fits In

RAG (Retrieval-Augmented Generation) means retrieving relevant documents from a knowledge base and injecting them into the LM's context before it generates output.

In our screener, RAG serves a specific purpose: after quantitative screening identifies candidate stocks, we retrieve qualitative context (sector reports, company analyses, macro commentary) to give the ranking step information that numbers alone cannot provide.

We use ChromaDB as the vector store. ChromaDB embeds documents using a small local model and supports similarity search. The retrieval is *agentic* in the sense that the query is constructed dynamically based on each stock's sector and the user's thesis, rather than being a static lookup.

```
User thesis --> Decompose into filters --> Screen tickers via yfinance
                                                |
                                                v
                                        Passing stocks
                                                |
                                     For each stock, build a
                                     retrieval query from its
                                     sector + the thesis
                                                |
                                                v
                                        ChromaDB similarity search
                                                |
                                                v
                                        Qualitative context injected
                                        into the ranking prompt
```

---

## Part 3: Code Walkthrough

### Section 1: Imports and Configuration

The code imports DSPy, yfinance, and ChromaDB. It reads the LM model string and API key from environment variables, falling back to `openai/gpt-4o-mini` by default. `dspy.configure(lm=lm)` sets the global LM for all DSPy predictors.

To run with Anthropic instead of OpenAI:

```bash
export DSPY_LM_MODEL="anthropic/claude-sonnet-4-20250514"
export DSPY_LM_API_KEY="sk-ant-..."
```

### Section 2: Stock Universe

A list of ~100 tickers across 10 sectors. This is the search space the screener filters through. In production, you would load a larger universe from a CSV or API. The list is intentionally small so the demo completes in a few minutes (each ticker requires an API call to Yahoo Finance).

### Section 3: Knowledge Base

`SAMPLE_DOCUMENTS` contains 10 short research-style documents covering sector outlooks, specific companies, and macro themes. `build_knowledge_base()` loads them into an in-memory ChromaDB collection. ChromaDB handles embedding automatically using a small local model (MiniLM-L6-v2).

`retrieve_context(collection, query, n_results=3)` runs a similarity search and returns the top matching document texts as a list of strings.

In production, you would populate this with real research: 10-K filings, earnings call transcripts, analyst notes, macro reports. The quality of the RAG output is directly proportional to the quality of the documents you put in.

### Section 4: DSPy Signatures

Three Signatures define the three LM-powered steps:

**DecomposeThesis**: Takes a natural-language thesis, outputs a JSON object of quantitative filters. The docstring enumerates the allowed filter keys and their types so the LM knows the schema. This is the "NL-to-structured-query compiler."

**RankCandidates**: Takes the thesis and a JSON array of enriched candidate data (financials + RAG context), outputs a ranked JSON array with bull/bear cases per stock. This is where quantitative and qualitative data merge.

**AdjustFilters**: Takes the original filters, the number of results, and a target range. Outputs adjusted filters. This powers the agentic retry loop.

All three request JSON-only output. The `_parse_json` utility handles common LM output quirks (markdown fences, preamble text).

### Section 5: Screening Logic

`fetch_stock_data(ticker)` calls yfinance to get a stock's fundamentals: market cap, P/E, free cash flow, dividend yield, margins, and price history. It computes percentage price changes over 30/60/90/180 day windows.

`apply_filters(stock_data, filters)` checks a single stock against the filter dict. Each filter is optional; only specified filters are enforced. This function is deliberately simple: a chain of if-statements. No magic.

`screen_universe(universe, filters)` loops through every ticker, fetches data, applies filters, and returns the passing list. It prints progress every 20 tickers.

### Section 6: The Screener Module

`NLStockScreener` is a `dspy.Module` with three `ChainOfThought` predictors (decompose, adjust, rank). Its `forward()` method runs the full pipeline:

1. **Decompose**: Call the LM to convert thesis to filters.
2. **Screen + Adjust**: Run the screen. If the result count is outside the target range (default 3-8), call the LM to adjust filters and re-screen. Retry up to `max_retries` times. This is the agentic loop.
3. **Enrich**: For each passing stock, build a retrieval query and pull context from ChromaDB.
4. **Rank**: Pass the enriched candidate data to the LM for final ranking with reasoning.

The module returns a `dspy.Prediction` containing the final filters, enriched candidates, and ranked output.

### Section 7: Utilities

`_parse_json(text)` handles the reality that LMs sometimes wrap JSON in code fences, add preamble, or produce slightly malformed output. It tries direct parsing first, then falls back to extracting the first JSON object or array from the text.

`print_results(prediction)` formats the final output for the terminal.

### Section 8: Main

Builds the knowledge base, instantiates the screener with target range 3-8, defines a sample thesis, runs the pipeline, and prints results.

---

## Part 4: Running the Code

### Prerequisites

```bash
pip install dspy yfinance chromadb
```

### Environment Variables

```bash
export DSPY_LM_MODEL="openai/gpt-4o-mini"      # or any LiteLLM-compatible model
export DSPY_LM_API_KEY="your-api-key-here"
```

### Execution

```bash
python nl_stock_screener.py
```

The first run will take a few minutes because yfinance fetches data for each ticker sequentially. Subsequent runs benefit from yfinance's local caching.

### Changing the Thesis

Edit the `thesis` string in `main()`. Examples:

- "Find me large-cap technology stocks with high profit margins that have underperformed the market this quarter"
- "I want energy companies with strong free cash flow and dividend yields above 3%"
- "Show me beaten-down industrial stocks with low debt-to-equity ratios that could benefit from infrastructure spending"

### Adding to the Knowledge Base

Add entries to `SAMPLE_DOCUMENTS` or replace the list entirely with your own research documents. Each entry needs an `id` (unique string) and `text` (the document content). For serious use, load documents from files:

```python
import os
docs = []
for fname in os.listdir("research_docs/"):
    with open(f"research_docs/{fname}") as f:
        docs.append({"id": fname, "text": f.read()})
```

### Future: Adding an Optimizer

To make the screener improve over time, collect labeled examples:

```python
example = dspy.Example(
    thesis="Find undervalued healthcare stocks with strong FCF",
    # The "correct" output you expect
).with_inputs("thesis")

trainset = [example1, example2, ...]

def metric(example, prediction, trace=None):
    # Score the prediction against the expected output
    # Return a float between 0 and 1
    ...

optimizer = dspy.BootstrapFewShot(metric=metric, max_bootstrapped_demos=4)
compiled_screener = optimizer.compile(screener, trainset=trainset)
compiled_screener.save("optimized_screener.json")
```

This would automatically find few-shot examples that improve the LM's filter decomposition and ranking accuracy.

---

## Part 5: Architecture Diagram

```
                        User Thesis (natural language)
                                    |
                                    v
                    +-------------------------------+
                    |  DecomposeThesis (DSPy CoT)   |
                    |  NL --> JSON filter spec       |
                    +-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |  screen_universe()            |
                    |  yfinance data + apply_filters|
                    +-------------------------------+
                                    |
                          Count in range?
                         /              \
                       No                Yes
                       |                  |
                       v                  |
              +------------------+        |
              | AdjustFilters    |        |
              | (DSPy CoT)      |--------+
              | relax/tighten   |
              +------------------+
                                    |
                                    v
                    +-------------------------------+
                    |  RAG Enrichment               |
                    |  ChromaDB similarity search   |
                    |  per candidate stock          |
                    +-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |  RankCandidates (DSPy CoT)    |
                    |  financials + context --> rank |
                    +-------------------------------+
                                    |
                                    v
                        Ranked output with reasoning
```
