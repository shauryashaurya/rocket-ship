## Self Declarative Pipeline: A Palantir Foundry Perspective
This repository provides a structured, end to end overview of Spark Declarative Pipelines (SDP) introduced in Spark 4.1, using reinsurance‑domain examples and explaining why SDP aligns naturally with Palantir Foundry’s data‑platform philosophy.
The intent is two fold:
- Serve as a technical reference for SDP concepts and examples
- Explain why Palantir teams are especially well‑positioned to adopt SDP

## Overview
Data engineering is moving away from job‑centric pipelines toward dataset‑centric systems.
With Spark 4.1, Declarative Pipelines (SDP) formalize this shift. Instead of explicitly handling execution order, scheduling, and retries, engineers declare what datasets should exist and how they are derived. Spark handles the rest.
For engineers working with Palantir Foundry, this model will feel immediately familiar.

## What is Spark Declarative Pipelines (SDP)?
Spark Declarative Pipelines (SDP) is a declarative framework for building reliable, maintainable, and testable data pipelines on Apache Spark.
Rather than writing orchestration logic, SDP lets you describe intent:
- What datasets should exist
- What transformations define them
  
Spark automatically manages:
- Dependency resolution
- Execution ordering
- Incremental processing
- Error handling 
- Parallelization

This mirrors the Palantir Foundry philosophy:
  Declare the data product,let the platform manage execution.
​

## What SDP Supports
SDP is designed for both batch and streaming workloads and supports common enterprise use cases:
- Data ingestion from cloud storage\(Amazon S3, Azure ADLS Gen2, Google Cloud Storage)
- Data ingestion from message buses\(Apache Kafka, Amazon Kinesis, Google Pub/Sub, Azure EventHub)
- Incremental batch and streaming transformations

## Why SDP Matters (Especially at Palantir)
Palantir data platforms emphasize:
- Dataset lineage
- Ontology‑driven modeling
- Incremental recomputation
- A strict separation between what data represents and how it is computed
	
SDP brings these same principles directly into open‑source Spark.
  Foundry‑style pipeline semantics become native Spark semantics with SDP.
​

## Dataflow Graph
Every SDP pipeline is represented as a dataflow graph:
- Nodes → datasets (tables or views)
- Edges → flows (transformations)
Spark automatically:
- Builds the DAG
- Resolves dependencies
- Executes flows in the correct order
- Parallelizes execution when possible
  
No explicit orchestration is required.

## Key Concepts in SDP
### Flows
A flow is the fundamental unit of data processing in SDP.
A flow:
- Reads from a source
- Applies user‑defined logic
- Writes to a target dataset
- Supports both batch and streaming semantics
Example (SQL):
```sql
CREATE STREAMING TABLE claimsenriched
AS SELECT * FROM STREAM rawclaims;
```
This statement:
- Creates a streaming table
- Defines the flow
- Registers the dependency on raw_claims

### Datasets
A dataset is a queryable output produced by one or more flows.
SDP defines three types of datasets:
Streaming Tables
- Incremental processing
- Only new data is processed
  
Materialized Views
- Batch‑computed
- Exactly one flow
- Stored as a table
  
Temporary Views
- Execution‑scoped
- Used for intermediate transformations
- Not persisted outside the pipeline

### Pipelines
A pipeline is the primary unit of development and execution in SDP.
A pipeline:
- Contains flows, tables, and views
- Automatically resolves dependencies
- Orchestrates execution
- Supports parallelism
  
This is very similar to how Foundry pipelines automatically recompute downstream assets when upstream data changes.

### Pipeline Projects
A pipeline project consists of:
- Python and/or SQL files that define datasets
- A YAML pipeline specification

### Pipeline Specification (pipeline.yml)
```yaml
name: reinsurance_pipeline
definitions:
  - glob:
      include: transformations//.py
  - glob:
      include: transformations//.sql
database: reinsurance
configuration:
  spark.sql.shuffle.partitions: "1000"
```

This structure resembles Foundry pipeline configuration:
- Centralized configuration
- Clear code boundaries
- Predictable outputs

## The spark-pipelines CLI
SDP pipelines are executed using the spark-pipelines CLI, built on top of spark-submit.
### Initialize the Pipeline Project
```bash
spark-pipelines init --name reinsurance_pipeline
```

Creates:
- A simple pipeline project inside a directory named "reinsurance_pipeline"
- spec file
- example definitions
### Run the Pipeline
```bash
spark-pipelines run
```

Spark:
- Builds the dependency graph
- Executes flows in order
- Monitors execution
  

# Programming with SDP in SQL (Reinsurance Examples)
## Creating a Materialized View (Batch) 
```sql
CREATE MATERIALIZED VIEW policiesmv
AS
SELECT
  policyid,
  insuredname,
  lob,
  region,
  effectivedate,
  expirydate,
  limitamount,
  deductibleamount
FROM reinsurancesource.policies_curated;
```
 
## Creating a Temporary View (Intermediate)
```sql
CREATE TEMPORARY VIEW policytreatymaptv
AS
SELECT
  p.policyid,
  t.treatyid,
  p.region,
  p.lob
FROM policiesmv p
JOIN treaties_mv t
  ON p.region = t.region
AND p.lob    = t.lob;
```

## Creating a Streaming Table
```sql 
CREATE STREAMING TABLE rawclaimsst
AS
SELECT
  claimid,
  policyid,
  eventts,
  CAST(eventts AS DATE) AS lossdate,
  lossamountgross,
  region,
  lob
FROM STREAM reinsurancesource.claims_events;
```

## Querying Tables in the Pipeline — Enrich → Aggregate
### Enriched claims (batch MV consuming streaming):
```sql
CREATE MATERIALIZED VIEW claimsenrichedmv
AS
SELECT
  c.claimid,
  c.policyid,
  m.treatyid,
  c.lossdate,
  c.lossamountgross,
  c.region,
  c.lob
FROM rawclaimsst c
LEFT JOIN policytreatymaptv m
  ON c.policyid = m.policy_id
AND c.region    = m.region
AND c.lob       = m.lob;
```

### Treaty loss allocation (illustrative share):
```sql
CREATE MATERIALIZED VIEW treatyallocationsmv
AS
SELECT
  e.treatyid,
  e.lossdate,
  SUM(e.lossamountgross * COALESCE(t.share, 1.0)) AS treatyloss
FROM claimsenrichedmv e
LEFT JOIN treatiesmv t
  ON e.treatyid = t.treatyid
GROUP BY e.treatyid, e.lossdate;
```

### Daily treaty loss (final analytics):
```sql 
CREATE MATERIALIZED VIEW dailytreatylossesmv
AS
SELECT
  treatyid,
  lossdate,
  SUM(treatyloss) AS dailytreatyloss
FROM treatyallocationsmv
GROUP BY treatyid, lossdate;
```

## Using Multiple Flows to Write to a Single Target
``` sql
-- Unified streaming target
CREATE STREAMING TABLE claimsconsolidatedst;
 
-- Cedant A unified
CREATE FLOW appendcedanta
AS INSERT INTO claimsconsolidatedst
SELECT
  claimid,
  policyid,
  CAST(eventts AS DATE) AS lossdate,
  lossamountgross,
  region,
  lob
FROM STREAM cedantaclaimsst;
 
-- Cedant B unified
CREATE FLOW appendcedantb
AS INSERT INTO claimsconsolidatedst
SELECT
  claimid,
  policyid,
  CAST(eventts AS DATE) AS lossdate,
  lossamountgross,
  region,
  lob
FROM STREAM cedantbclaimsst;
```
