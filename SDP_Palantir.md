# Self‑Declarative Pipelines: A Palantir Foundry Perspective (with Foundry‑Native Examples)

## Collab

## TL;DR
Spark 4.1’s Spark Declarative Pipelines (SDP) popularize a dataset‑centric approach—declare the datasets and queries; let the engine plan and run the graph. In Palantir Foundry, you build the same kind of pipelines using Transforms (@transform, @transform_df, @incremental) that materialize datasets and are orchestrated by Pipelines with scheduling, lineage, and governance built‑in. 

## Overview
Data engineering is moving from imperative, job‑centric orchestration to dataset‑centric systems. SDP formalizes this in core Spark: you specify what datasets should exist and how they’re derived; Spark plans the graph, retries, and incremental updates for you (SDP guide). Foundry embodies the same philosophy: you declare Transforms that read inputs and write outputs (datasets); Pipelines schedule execution; and Lineage tracks the DAG across your enterprise (Transforms, Lineage, Pipelines).

## What SDP Is (and how it maps)
- SDP introduces flows, datasets (streaming tables, materialized views, temporary views), and a pipeline spec to run them (SDP guide).
- Foundry maps naturally:
  - SDP flow → Foundry Transform reading Inputs and writing one or more Outputs (Transforms).
	- SDP materialized view → Persisted transform output dataset (the canonical way to “materialize” in Foundry).
	- SDP temporary view → Intermediate dataset (or a Foundry View if you want read‑time union/dedup without storing new files) (Views).
	- SDP graph execution → Foundry Pipelines + schedules + Lineage to monitor dependencies and impact.
	- For incremental behavior, Foundry provides the @incremental() decorator
