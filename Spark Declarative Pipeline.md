---
layout: default
title: "Spark Declarative Pipelines (Spark 4.1.1)"
---



            
# Spark Declarative Pipelines (Spark 4.1.1)                                     
                                        
<img src="./images/02-01-spark-declarative-pipelines.png" width="95%" align="center" alt="Spark Declarative Pipelines (Spark 4.1.1)" />                                    
          

## Collab
1. [Ankita Hatibaruah](https://github.com/Ahb98), [LinkedIn](http://linkedin.com/in/ankita-hatibaruah-bb2a62218)
2. [Pavithra Ananthakrishnan](https://github.com/Pavi-245), [LinkedIn](https://www.linkedin.com/in/pavithra-ananthakrishnan-552416244/)
3. [Sree Bhavya Kanduri](https://github.com/sreebhavya10), [LinkedIn](https://www.linkedin.com/in/kanduri-sree-bhavya-4001a6246?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)

## TL;DR   
This document provides a structured, end‑to‑end overview of Spark Declarative Pipelines (SDP) introduced in Apache Spark 4.1.1 released on January 09, 2026, using examples to illustrate how to describe datasets and transformations declaratively. With SDP, you define what tables/views should exist and how they’re computed, and Spark builds and runs the dependency graph (ordering, parallelism, retries, and incremental updates).

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
  
## Programming with SDP in Python (Reinsurance Examples)
These examples demonstrates how to build data pipelines for reinsurance analytics using Spark Data Pipelines (SDP). The examples show how to define different types of views and tables, materialized views, temporary views, and streaming tables, to handle both batch and streaming data sources.

The pipeline ingests raw claims and cessions from Kafka, enriches them with policy and treaty reference data, and then aggregates losses at the treaty and regional levels. It also illustrates how multiple data flows can be consolidated into a unified streaming target.

In essence, these examples walk through the end to end process of transforming raw insurance event streams into curated, queryable datasets that support reinsurance reporting and loss allocation.
### Import the pipelines API from PySpark to use SDP decorators for defining tables and views.
```bash
from pyspark import pipelines as sdp
```
### Creating a Materialized View (Batch)
#### Policies master (batch): This creates a stable, curated materialized view of policy data from Parquet files.
```bash
@sdp.materializedview
def policiesmv():
    return spark.read.format("parquet").load("/reinsurance/reference/policies")
```
### Creating a Materialized View (Batch) — With Name
#### Treaties master (batch) with explicit name: This defines a materialized view named "treatiesmv" that loads treaty reference data from Delta format.
```bash
@sdp.materializedview(name="treatiesmv")
def treaties():
    return spark.read.format("delta").load("/reinsurance/reference/treaties")
```
### Creating a Temporary View — Intermediate Enrichment
#### Claims enriched with policy context (execution‑scoped): This temporary view parses raw claims from Kafka, enriches them with policy data, and prepares them for downstream processing.
```bash
from pyspark.sql.functions import col, to_date, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

@sdp.temporaryview
def claimsenrichedtv():
    schema = StructType([
        StructField("claimid", StringType()),
        StructField("policyid", StringType()),
        StructField("eventts", StringType()),
        StructField("lossamount", DoubleType()),
        StructField("region", StringType()),
        StructField("lob", StringType())
    ])

    return (
        spark.table("rawclaimsst")
        .selectExpr("CAST(value AS STRING) AS payload")
        .select(from_json(col("payload"), schema).alias("r"))
        .select("r.*")
        .join(spark.table("policiesmv"), "policyid", "left")
        .select(
            "claimid",
            "policyid",
            to_date(col("eventts")).alias("lossdate"),
            col("lossamount").alias("gross_loss"),
            "region", "lob"
        )
    )
```
### Creating a Streaming Table  
#### Raw Claims: This streaming table ingests raw claims events from Kafka into Spark.
```bash
@sdp.table(name="rawclaimsst")
def rawclaims():
    return (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "broker1:9092,broker2:9092")
        .option("subscribe", "claimsevents")
        .option("startingOffsets", "latest")
        .load()
    )
```
### Loading from a Streaming Source 
#### Cessions: This streaming table ingests raw cession events from Kafka into Spark.
```bash
@sdp.table(name="rawcessionsst")
def rawcessions():
    return (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "broker:9092")
        .option("subscribe", "cessionsevents")
        .load()
    )
```
### Batch Reads
#### Exposure Schedules: This materialized view loads exposure schedules from CSV files with headers.
```bash
@sdp.materializedview(name="exposureschedulesmv")
def exposureschedules():
    return (
        spark.read.format("csv")
        .option("header", True)
        .load("/reinsurance/exposure/schedules")
    )
```
### Querying Tables Defined in Your Pipeline
#### Stream claims → enrich → allocate to treaty → daily treaty loss
#### These materialized views map claims to treaties and compute daily treaty losses.
```bash
from pyspark.sql.functions import col, sum as ssum, coalesce, lit

@sdp.materializedview(name="claimswithtreatiesmv")
def claimswithtreaties():
    mapdf = spark.read.format("delta").load("/reinsurance/reference/policytreatymapping")

    return (
        spark.table("claimsenrichedtv")
        .join(mapdf, ["policyid", "region", "lob"], "left")
        .join(spark.table("treatiesmv"), "treatyid", "left")
        .select(
            "claimid",
            "policyid",
            "treatyid",
            "lossdate",
            col("gross_loss"),
            coalesce(col("share"), lit(1.0)).alias("treatyshare")
        )
    )

@sdp.materializedview(name="dailytreatylossesmv")
def dailytreatylosses():
    return (
        spark.table("claimswithtreatiesmv")
        .withColumn("treatyloss", col("gross_loss") * col("treatyshare"))
        .groupBy("treatyid", "lossdate")
        .agg(ssum("treatyloss").alias("dailytreatyloss"))
    )
```
### Creating Tables in a For Loop
#### This loop dynamically creates region-specific materialized views of daily treaty losses.
```bash
from pyspark.sql.functions import collect_list

@sdp.temporaryview
def regionstv():
    return spark.read.format("delta").load("/reinsurance/reference/regions")

regionlist = (
    spark.table("regionstv")
    .select(collect_list("regionname"))
    .collect()[0][0]
)

for region in regionlist:
    safe = region.lower().replace(" ", "")

    @sdp.materializedview(name=f"dailytreatylosses{safe}mv")
    def perregiondailylosses(regionfilter=region):
        return (
            spark.table("dailytreatylossesmv")
            .join(spark.table("treatiesmv"), "treatyid")
            .filter(f"region = '{regionfilter}'")
        )
```
### Using Multiple Flows to Write to a Single Target
#### This example demonstrates appending multiple cedant claim streams into a single consolidated streaming table.
```bash
sdp.createstreamingtable("claimsconsolidatedst")

@sdp.appendflow(target="claimsconsolidatedst")
def cedantaappend():
    return spark.readStream.table("cedantaclaimsst")  # already normalized schema

@sdp.appendflow(target="claimsconsolidatedst")
def cedantbappend():
    return spark.readStream.table("cedantbclaimsst")
```
## Programming with SDP in SQL (Reinsurance Examples)
### Creating a Materialized View (Batch) 
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

### Creating a Temporary View (Intermediate)
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
AND p.lob    = t.lob;
```

### Creating a Streaming Table
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

### Querying Tables in the Pipeline — Enrich → Aggregate
#### Enriched claims (batch MV consuming streaming):
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
AND c.region    = m.region
AND c.lob       = m.lob;
```
#### Treaty loss allocation (illustrative share):
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
#### Daily treaty loss (final analytics):
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

### Using Multiple Flows to Write to a Single Target
```sql
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
    
   
---
		   
# [Back to Rocket Ship front page](https://shauryashaurya.github.io/rocket-ship/)            