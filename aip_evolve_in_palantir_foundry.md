# AIP Evolve in Palantir Foundry
*Advancing Enterprise AI Through Agent-Driven Optimization*

## Collab

1. [Anudeep Chatradi](https://github.com/anudeepchatradi), [LinkedIn](https://www.linkedin.com/in/anudeep-chatradi-78757298/)
2. [Ankita Hatibaruah](https://github.com/Ahb98), [LinkedIn](http://linkedin.com/in/ankita-hatibaruah-bb2a62218)    


## TL;DR

AIP Evolve is a Palantir Foundry capability that coordinates AI Forward Deployed Engineer (AI FDE) agents to systematically optimize existing enterprise AI systems. By combining goal-driven engineering, iterative experimentation, and structured evaluation through capabilities such as AIP Evals, it helps teams explore improvements in inference cost, latency, and output quality while maintaining validation and human oversight. This article explores how AIP Evolve works, how it integrates with the broader Foundry ecosystem, how it differs from other AIP capabilities, and how organizations can use it to drive measurable improvements in production AI workflows.

## 1. What Is AIP Evolve?

Enterprise AI development does not end when an application goes live. Over time, organizations need to reduce operating costs, improve response times, maintain output quality, and adapt to changing models and business requirements.

**AIP Evolve is a Palantir Foundry capability that coordinates fleets of AI Forward Deployed Engineer (AI FDE) agents to improve existing AI systems.** Users define the target, optimization goal, validation strategy, and operational constraints. The agents explore potential improvements, evaluate candidate changes, and prepare a proposal for review before changes are merged.

Common optimization goals include:
- Reducing model inference costs.
- Improving response latency.
- Increasing evaluation scores.
- Migrating to alternative models.
- Pursuing custom optimization objectives.

AIP Evolve is part of Palantir's broader Artificial Intelligence Platform (AIP). It focuses on improving existing AI implementations rather than replacing the tools used to build applications, manage enterprise data, or deliver operational workflows.

### Understanding AI FDE

AI FDE is an AI-powered engineering capability that enables users to interact with Foundry resources through natural-language instructions and available tools. Depending on its configured permissions and context, it can inspect resources, work with code repositories, modify data transformations, develop functions, and execute engineering operations.

Within AIP Evolve, AI FDE agents perform coordinated engineering activities to explore and validate potential improvements. Rather than simply suggesting an optimization, they can investigate an existing implementation, experiment with alternatives, examine results, and prepare supporting artifacts for review.

The distinction is important: AI FDE is the engineering capability; AIP Evolve coordinates AI FDE agents for the specific purpose of optimizing existing AI systems.


### The evolution of enterprise AI

| Stage | Focus | Key activity |
|---|---|---|
| Build | Develop AI capabilities | Create prompts, functions, models, and workflows |
| Deploy | Operationalize AI | Integrate AI into business processes and applications |
| Evolve | Improve existing AI | Explore changes, validate outcomes, and review proposals |


## 2. The Problem: Why Is AIP Evolve Needed?

Once an AI workflow is operational, improving it can require repeated experiments, engineering effort, and careful validation. A cheaper model might produce less reliable results; a faster prompt might introduce regressions; and a change that works for one scenario may fail on another.

| Pain point | Business impact | Engineering challenge |
|---|---|---|
| High inference costs | Higher operating expenditure | Find lower-cost alternatives without unacceptable quality loss |
| High latency | Slower business processes and poor user experience | Compare model and workflow alternatives |
| Inconsistent outputs | Reduced trust and more manual correction | Define meaningful evaluation criteria |
| Manual experimentation | Longer optimization cycles | Run and compare experiments efficiently |
| Regression risk | Potential operational disruption | Validate candidate changes against a baseline |
| Changing models and requirements | Repeated maintenance effort | Reassess existing implementations over time |

AIP Evolve addresses these challenges through a structured, agent-driven optimization process. It does not automatically guarantee lower costs or better quality; results depend on the target system, evaluation strategy, and available alternatives.

**Central question:** Can AI-assisted engineering reduce the effort required to improve an existing AI system while preserving measurable quality and appropriate change controls?

## 3. How AIP Evolve Works

AIP Evolve turns an optimization objective into an iterative engineering workflow. Users specify what should improve, how success will be measured, and what changes agents are permitted to make.

### Optimization lifecycle

```mermaid
flowchart TD
    A["Select existing AI resource"] --> B["Define optimization goal"]
    B --> C["Configure validation and constraints"]
    C --> D["Orchestrate AI FDE agents"]
    D --> E["Explore candidate changes"]
    E --> F["Evaluate against baseline"]
    F --> G["Prepare proposal and evidence"]
    G --> H{"Review proposal"}
    H -- "Accept" --> I["Review and merge, where applicable"]
    H -- "Revise" --> J["Provide additional instructions"]
    J --> D
    I --> K["Measure operational impact"]
```

This is a conceptual representation of the optimization lifecycle, not an exact depiction of the platform's internal architecture.

### Key steps

1. **Select the target:** Identify the AI function or workflow to improve.
2. **Define the goal:** Choose an objective such as cost reduction, lower latency, model migration, or evaluation-score improvement.
3. **Set validation and constraints:** Select representative test cases or evaluation suites, configure scoring criteria and acceptable output divergence, and limit permitted changes and iterations.
4. **Explore alternatives:** AI FDE coordinates engineering activities to inspect the target, explore candidate changes, and evaluate their results.
5. **Compare results:** Review the baseline and candidate outputs, evaluation results, supporting evidence, and confidence assessments.
6. **Review and merge:** Inspect the proposed changes through Global Branching, where applicable, before merging.
7. **Measure operational impact:** Confirm that the adopted change delivers the intended business outcome.

### Visibility into agent activity

AIP Evolve provides an agent graph that allows users to follow the work performed during an evolution. Depending on the task, this can show specialist activities related to analysis, test-case creation, model selection, evaluation, prompt engineering, and proposal preparation.

This provides visibility into the optimization process, not just its final recommendation. Engineers can inspect agent goals, insights, and artifacts to understand how candidate changes were explored and evaluated.

Review does not mean automatic production deployment. AIP Evolve presents a proposal for review. When applicable, users can inspect proposed changes through Global Branching or the relevant code review workflow. They can also resume the evolution in AI FDE with additional instructions.

The workflow should not be interpreted as a guarantee that every candidate passing evaluation will be merged or deployed automatically.

The key distinction is that AIP Evolve does more than suggest a change. It coordinates iterative exploration and validation against a defined objective, then presents a proposal for review.

However, passing an evaluation is not proof of production correctness. Test coverage, representative data, evaluation quality, and appropriate human review remain essential.


## 4. Integration With the Foundry Ecosystem

AIP Evolve operates within the wider Foundry environment. The following diagram groups capabilities by responsibility rather than representing an exact deployment topology.

<img width="2034" height="1634" alt="Screenshot_2026-10-24-01-14-44-18_96b26121e545231a3c569311a54cda96" src="https://github.com/user-attachments/assets/6a3809e7-3679-4dc3-a209-02a4cfc2789a" />


### Responsibilities of the main components

| Component | Primary responsibility | Relationship to AIP Evolve |
|---|---|---|
| AIP Evolve | Coordinate the optimization process | Defines the goal and manages the evolution workflow |
| AI FDE | Execute engineering tasks using an AI agent | Explores and evaluates candidate changes |
| AIP Evals | Test AI functions using test cases and evaluation criteria | Can provide a structured way to assess candidate quality |
| Ontology | Model enterprise objects, relationships, logic, and actions | Required installation context for the AIP Evolve Marketplace product |
| Global Branching | Manage and review proposed changes | Supports review before changes are merged |
| Workshop | Build operational applications and interfaces | May host the business workflow using the AI capability being optimized |
| Datasets and pipelines | Provide and transform enterprise data | May supply the data and context used by the target AI system or its validation |

AIP Evolve requires AIP to be enabled, access to AI FDE, installation of the AIP Evolve Marketplace product in an Ontology, and access to the target resource and any validation data or evaluation suites used.

Workshop is part of the broader Foundry ecosystem, but it is not a universal prerequisite for using AIP Evolve.

### AIP Evals: The evaluation layer

#### Understanding AIP Evals

AIP Evals is a testing environment designed to evaluate AI functions, including supported AIP Logic, chatbot, and code-authored functions. It supports structured testing of AI systems, where output variability makes conventional one-off testing insufficient.

An evaluation suite can include:

Target functions: The AI functions being tested.

Test cases: Inputs and, where appropriate, expected outputs.

Evaluation functions: Rules or evaluators that compare actual outputs against expectations.

Metrics: Results used to assess performance at the individual test-case level and across a suite.

AIP Evals supports built-in evaluators, such as exact-match and regular-expression matching, alongside custom evaluation functions and LLM-as-a-judge evaluation where appropriate.

Evaluation suites can be used to compare different target functions on the same test cases and examine variation across runs.

Within AIP Evolve, users can select test cases or existing evaluation suites as part of the validation strategy. The choice depends on the target and optimization objective.

Important distinction: AIP Evals measures whether a function meets defined evaluation criteria. AIP Evolve coordinates the exploration of candidate improvements. The two capabilities complement each other, but they serve different purposes.

### AI FDE and governance

#### Engineering controls and review

AI FDE operates within the user's existing Foundry permissions and can be configured with specific tools and context. Depending on the workflow, it can propose changes through Global Branching or a Code Repository pull request for review.

This helps teams retain visibility over engineering actions and apply existing access controls. However, permissions and branching do not eliminate the need to verify generated code, validate business logic, and review proposed changes before production use.


## 5. How AIP Evolve Differs From Other Foundry Capabilities

The distinction is primarily about responsibility within the AI lifecycle.

| Capability | Primary purpose | How it complements AIP Evolve |
|---|---|---|
| AIP Logic | Build AI-powered functions and workflows | Provides AI components that may be optimized |
| AIP Evals | Evaluate AI functions against test cases and metrics | Helps assess quality and compare candidate results |
| AI FDE | Carry out engineering operations through an AI agent | Performs the agent-driven work coordinated by Evolve |
| Workshop | Build user-facing operational applications | Provides interfaces for business users |
| Ontology | Represent enterprise objects, relationships, and actions | Supplies the broader enterprise context |
| Global Branching | Review and manage proposed changes | Supports controlled change review and merging |
| **AIP Evolve** | **Coordinate iterative optimization of existing AI systems** | **Connects goals, agent-driven exploration, validation, and proposal review** |

AIP Evolve does not replace the other capabilities. Its purpose is to bring a structured optimization process to an existing AI implementation, using relevant Foundry tools and resources where applicable.

## 6. Business Value and Practical Applications

### Illustrative example: AI-powered inventory allocation

Consider a company using an AI workflow to interpret customer orders and recommend how inventory should be allocated. The workflow is already operational, but its compute cost is higher than desired.

**Step 1 — Establish the baseline**

Record the current model, cost per call, response latency, evaluation results, and performance on representative test cases.

**Step 2 — Define the optimization**

Set a cost-reduction goal, choose representative validation cases, define acceptable output divergence, and restrict the types of changes agents may propose.

**Step 3 — Explore and validate**

AIP Evolve coordinates AI FDE agents to investigate the workflow, explore alternatives such as model or prompt changes, and compare candidate results against the baseline.

**Step 4 — Review the proposal**

Inspect the recommended changes, cost measurements, output comparisons, evaluation results, and limitations. Review the proposed changes before merging.

**Step 5 — Measure the outcome**

After adoption, measure performance under comparable workloads and verify that the optimization has not introduced unacceptable regressions.

### Documented example: Cost optimization in AIP Evolve

#### Quantitative evidence from Palantir's documentation

Palantir's official AIP Evolve documentation provides an example of optimizing an AI-powered inventory allocation workflow.

In that example, the candidate used a different model and prompt guardrails. The baseline and candidate both passed all 10 selected test cases, while average compute cost decreased by 65%.


| Metric                     | Baseline              | Candidate             |
|----------------------------|----------------------:|----------------------:|
| Average compute per call   | 204.6 compute-seconds | 72.4 compute-seconds  |
| Selected test cases passed | 10 of 10              | 10 of 10              |


This is a documented example, not a guarantee of typical savings. The result applies to the example's workload and evaluation strategy. Passing 10 test cases does not prove equivalence across every possible input, and compute-seconds should not be confused with end-to-end response latency or monetary cost.

### Additional example: Optimizing an insurance claims assistant

#### Illustrative business use case

Consider an insurance organization using an AI function to extract information from claim documents and generate structured summaries for claims handlers.

The existing function is operational, but the organization wants to migrate to a more economical model without compromising the accuracy of critical claim information.

Step 1 — Establish the baseline

Record the current model, average inference cost, response latency, and evaluation results for representative claims.

Step 2 — Define the optimization objective

Configure the evolution to reduce cost while preserving the required extraction quality. Establish constraints around permitted model and prompt changes.

Step 3 — Explore candidate improvements

AI FDE agents investigate the existing function and explore candidate changes, such as alternative models or prompt modifications.

Step 4 — Validate the candidates

Use representative test cases or an existing evaluation suite to assess whether critical fields are extracted correctly and the expected output structure is maintained.

Step 5 — Review the proposal

Compare cost, latency, evaluation results, and sample outputs. Pay particular attention to critical errors, such as incorrect policy numbers or claim amounts.

Step 6 — Measure the business impact

After the change is adopted, compare operational performance under equivalent conditions and verify that the reduction in cost has not introduced unacceptable errors.

This is a hypothetical scenario illustrating how cost optimization can be combined with quality constraints and engineering review. It is not a claim of a measured customer outcome.


### Suggested business KPIs

| Intended outcome | KPI |
|---|---|
| Lower AI expenditure | Cost per successful task; monthly inference cost |
| Better responsiveness | Median and p95 latency |
| Improved output quality | Evaluation pass rate; task-specific quality score |
| Fewer regressions | Critical test failures; post-release incident rate |
| Higher engineering productivity | Engineer-hours per optimization cycle |
| Faster delivery | Time from optimization request to approved change |

A successful optimization balances cost, speed, and quality. Reducing compute cost alone does not prove that the business outcome has improved.

Where actual results are available, present a before-and-after comparison using equivalent workloads and test conditions. Otherwise, label the example as illustrative rather than presenting hypothetical savings as measured results.

## 7. Conclusion and Strategic Implications

AIP Evolve extends Foundry's AI engineering capabilities by coordinating AI FDE agents to explore and validate improvements to existing AI systems. It gives teams a structured way to pursue objectives such as lower cost, reduced latency, improved evaluation scores, and model migration.

Its value can be considered from three perspectives:

- **Business leaders:** A way to pursue measurable improvements in AI operating costs, responsiveness, and quality.
- **Architects and engineers:** A structured process for agent-driven experimentation, evaluation, and proposed changes.
- **Governance teams:** An opportunity to combine explicit constraints, evaluation evidence, and review practices with human oversight.

### The relationship between the capabilities

AI FDE provides the engineering capabilities, AIP Evals helps measure function performance, and AIP Evolve coordinates iterative optimization. Global Branching and Code Repository review workflows can support controlled change management, depending on the resources involved.

The results still depend on sound evaluation design, representative test cases, appropriate permissions, and disciplined review. AIP Evolve should therefore be viewed as an optimization capability—not a guarantee of autonomous, risk-free improvement.

In short: Foundry provides the environment to build and operate enterprise AI solutions; AI FDE enables agent-driven engineering; AIP Evals measures AI function performance; and AIP Evolve coordinates the process of systematically improving existing AI systems over time.

### References

1. [Palantir — AIP Evolve overview](https://www.palantir.com/docs/foundry/aip-evolve/overview)
2. [Palantir — AI FDE overview](https://www.palantir.com/docs/foundry/ai-fde/overview)
3. [Palantir — AIP Evals overview](https://www.palantir.com/docs/foundry/aip-evals/overview)
4. [Palantir — Global Branching overview](https://www.palantir.com/docs/foundry/global-branching)
5. [Palantir — AI FDE best practices](https://www.palantir.com/docs/foundry/ai-fde/best-practices)

---
