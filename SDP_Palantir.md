---
layout: default
title: "Spark Declarative Pipelines: A Palantir Foundry Perspective"
---




# Spark Declarative Pipelines: A Palantir Foundry Perspective                                      
                                        
<img src="./images/02-01-spark-declarative-pipelines.png" width="95%" align="center" alt="Spark Declarative Pipelines: A Palantir Foundry Perspective" />                                    
          
## Collab          
1. [Ankita Hatibaruah](https://github.com/Ahb98), [LinkedIn](http://linkedin.com/in/ankita-hatibaruah-bb2a62218)          
2. [Pavithra Ananthakrishnan](https://github.com/Pavi-245), [LinkedIn](https://www.linkedin.com/in/pavithra-ananthakrishnan-552416244/)          
3. [Sree Bhavya Kanduri](https://github.com/sreebhavya10), [LinkedIn](https://www.linkedin.com/in/kanduri-sree-bhavya-4001a6246)                         
          
## Overview          
Data engineering is moving from imperative, job-centric orchestration to dataset-centric systems. SDP formalizes this in core Spark: you specify what datasets should exist and how they’re derived; Spark plans the graph, retries, and incremental updates for you. Foundry embodies the same philosophy: you declare Transforms that read inputs and write outputs (datasets); Pipelines schedule execution; and Lineage tracks the DAG across your enterprise.          
## TL;DR          
Spark 4.1’s Spark Declarative Pipelines (SDP) popularize a dataset-centric approach, declare the datasets and queries; let the engine plan and run the graph. In Palantir Foundry, you build the same kind of pipelines using Transforms (@transform, @transform_df, @incremental) that materialize datasets and are orchestrated by Pipelines with scheduling, lineage, and governance built-in.           
          
## What SDP Is (and how it maps)          
- SDP introduces flows, datasets (streaming tables, materialized views, temporary views), and a pipeline spec to run.          
- Foundry maps naturally:          
    - SDP flow → Foundry Transform reading Inputs and writing one or more Outputs.          
	- SDP materialized view → Persisted transform output dataset (the canonical way to “materialize” in Foundry).          
	- SDP temporary view → Intermediate dataset (or a Foundry View if you want read-time union/dedup without storing new files).          
	- SDP graph execution → Foundry Pipelines + schedules + Lineage to monitor dependencies and impact.          
	- For incremental behavior, Foundry provides the @incremental() decorator.          
          
## Why this matters (especially for Foundry)          
Foundry emphasizes dataset lineage, governed modeling (Ontology), incremental recomputation, and separation between what data represents and how it’s computed. The dataset centric style you learn from SDP aligns naturally with Foundry’s core apps and best practices,only here you also get enterprise-grade lineage, access control, checks, and auditing as first-class.          
          
## The Dataflow Graph (in Foundry)          
In Foundry, the DAG is explicit in Data Lineage: transforms (nodes) consume input datasets and produce output datasets; lineage updates as you build. You can explore ancestor/descendant relationships, see schemas and last build times, and color or snapshot parts of the graph for collaboration.          
          
## Key Concepts (SDP → Foundry)          
- Transforms (Foundry) = flows (SDP): a unit of compute that reads Inputs and writes Outputs, defined with @transform / @transform_df. Use multiple outputs when needed.          
- Datasets (Foundry) = persisted outputs. Use Views when you want a union or primary-key dedup at read time without writing new files.          
- Pipelines (Foundry) = orchestration + schedules, with native lineage and governance.          
- Incremental: add @incremental() when inputs and logic meet constraints so only new data is processed.          
          
## Pipeline Project (Foundry)          
- Author Python transforms in a Code Repository.          
- Declare Inputs/Outputs in decorators; write a DataFrame to each Output.          
- Register transforms in a Pipeline, set schedules, and monitor Lineage.          
## Programming with Foundry in Python (Reinsurance Examples)          
          
These examples demonstrate how to build data pipelines for reinsurance analytics using **Palantir Foundry**. The examples show how to define persisted outputs, materialized datasets, incremental transforms, and multi-output pipelines to handle both batch and streaming data sources.          
          
The pipeline ingests raw claims and cessions from Kafka/EventHub/S3, enriches them with policy and treaty reference data, and then aggregates losses at the treaty and regional levels. It also illustrates how multiple cedant flows can be consolidated into a unified curated dataset.          
          
In essence, these examples walk through the end-to-end process of transforming raw insurance event streams into curated, queryable datasets that support reinsurance reporting and loss allocation.          
          
---          
          
### Curated Materialized Views (Batch)          
#### This example demonstrates creating stable, curated reference datasets for policies and treaties.          
```python          
from transforms.api import transformdf, Input, Output          
          
@transformdf(          
    Output("/reinsurance/reference/policiesmv"),          
    policiesraw=Input("/reinsurance/reference/policies")          
)          
def policiesmv(policiesraw):          
    return policiesraw          
          
@transformdf(          
    Output("/reinsurance/reference/treatiesmv"),          
    treatiesraw=Input("/reinsurance/reference/treaties")          
)          
def treatiesmv(treatiesraw):          
    return treatiesraw          
```          
          
---          
          
### Claims Enrichment (Parse + Join with Policy Context)          
#### This example parses raw claims and enriches them with policy reference data.          
```python          
from transforms.api import transformdf, Input, Output          
from pyspark.sql.functions import col, to_date, from_json          
from pyspark.sql.types import StructType, StructField, StringType, DoubleType          
          
schema = StructType([          
    StructField("claimid", StringType()),          
    StructField("policyid", StringType()),          
    StructField("eventts", StringType()),          
    StructField("lossamount", DoubleType()),          
    StructField("region", StringType()),          
    StructField("lob", StringType())          
])          
          
@transformdf(          
    Output("/reinsurance/curated/claimsenrichedds"),          
    rawclaims=Input("/reinsurance/raw/claimsingested"),          
    policiesmv=Input("/reinsurance/reference/policiesmv")          
)          
def claimsenrichedds(rawclaims, policiesmv):          
    parsed = (          
        rawclaims          
        .selectExpr("CAST(value AS STRING) AS payload")          
        .select(from_json(col("payload"), schema).alias("r"))          
        .select("r.*")          
    )          
    return (          
        parsed.join(policiesmv, "policyid", "left")          
              .select(          
                  "claimid", "policyid",          
                  to_date(col("eventts")).alias("lossdate"),          
                  col("lossamount").alias("grossloss"),          
                  "region", "lob"          
              )          
    )          
```          
          
---          
          
### Exposure Schedules (Batch Reads)          
#### This example materializes exposure schedules from CSV inputs.          
```python          
from transforms.api import transformdf, Input, Output          
          
@transformdf(          
    Output("/reinsurance/reference/exposureschedulesmv"),          
    exposures=Input("/reinsurance/exposure/schedules")          
)          
def exposureschedules(exposures):          
    return exposures          
```          
          
---          
          
### Map Claims → Treaties → Compute Daily Treaty Loss          
#### This example attaches treaties to claims and computes daily treaty losses.          
```python          
from transforms.api import transformdf, Input, Output          
from pyspark.sql.functions import col, sum as ssum, coalesce, lit          
          
@transformdf(          
    Output("/reinsurance/curated/claimswithtreatiesmv"),          
    claimsenriched=Input("/reinsurance/curated/claimsenrichedds"),          
    treatiesmv=Input("/reinsurance/reference/treatiesmv"),          
    mapdf=Input("/reinsurance/reference/policytreatymapping")          
)          
def claimswithtreatiesmv(claimsenriched, treatiesmv, mapdf):          
    return (          
        claimsenriched          
        .join(mapdf, ["policyid", "region", "lob"], "left")          
        .join(treatiesmv, "treatyid", "left")          
        .select(          
            "claimid", "policyid", "treatyid", "lossdate",          
            col("grossloss"),          
            coalesce(col("share"), lit(1.0)).alias("treatyshare")          
        )          
    )          
          
@transformdf(          
    Output("/reinsurance/analytics/dailytreatylossesmv"),          
    claimswithtreaties=Input("/reinsurance/curated/claimswithtreatiesmv")          
)          
def dailytreatylossesmv(claimswithtreaties):          
    return (          
        claimswithtreaties          
        .withColumn("treatyloss", col("grossloss") * col("treatyshare"))          
        .groupBy("treatyid", "lossdate")          
        .agg(ssum("treatyloss").alias("dailytreatyloss"))          
    )          
```          
### Multiple Cedant Streams → Single Consolidated Target          
#### This example consolidates multiple cedant claim streams into one curated dataset.          
```python          
from transforms.api import transformdf, Input, Output          
          
@transformdf(          
    Output("/reinsurance/curated/claimsconsolidated"),          
    cedanta=Input("/reinsurance/raw/cedantaclaimsnorm"),          
    cedantb=Input("/reinsurance/raw/cedantbclaimsnorm"),          
)          
def claimsconsolidated(cedanta, cedantb):          
    return cedanta.unionByName(cedantb, allowMissingColumns=False)          
```          
          
---          
          
### Incremental Processing          
#### This example demonstrates incremental transforms to process only new data each run.          
```python          
from transforms.api import transform, incremental, Input, Output          
from pyspark.sql.functions import to_date, col          
          
@incremental()          
@transform(          
    raw=Input("/reinsurance/raw/claimsingested"),          
    enrichedout=Output("/reinsurance/curated/claimsenrichedinc")          
)          
def claimsenrichedincremental(raw, enrichedout):          
    df = raw.dataframe(mode="added")          
    cleaned = df.select(          
        "claimid", "policyid",          
        to_date(col("eventts")).alias("lossdate"),          
        col("lossamount").alias("grossloss"),          
        "region", "lob"          
    )          
          
    enrichedout.write_dataframe(cleaned)          
          
```          
          
          
                
          
    
   
---
		   
# [Back to Rocket Ship front page](https://shauryashaurya.github.io/rocket-ship/)            