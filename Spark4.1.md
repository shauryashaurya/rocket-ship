---
layout: default
title: "More notes on the Apache Spark 4.1 release"
---




# More notes on the Apache Spark 4.1 release                                     
                                        
<img src="./images/02-02-spark-4-1-release.png" width="95%" align="center" alt="More notes on the Apache Spark 4.1 release" />      

## Collab
1. [Ankita Hatibaruah](https://github.com/Ahb98), [LinkedIn](http://linkedin.com/in/ankita-hatibaruah-bb2a62218)
2. [Pavithra Ananthakrishnan](https://github.com/Pavi-245), [LinkedIn](https://www.linkedin.com/in/pavithra-ananthakrishnan-552416244/)
3. [Sree Bhavya Kanduri](https://github.com/sreebhavya10), [LinkedIn](https://www.linkedin.com/in/kanduri-sree-bhavya-4001a6246?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)

## Apache Spark 4.1 — Introduction
Apache Spark 4.1, released in December 2025, is a major update in the Spark 4.x series that enhances performance, usability, and developer productivity. Spark continues to serve as a unified analytics engine for large-scale, distributed data processing.
This release brings faster Python execution, improved SQL and streaming engines, better error handling, and lower-latency processing, making Spark 4.1 well-suited for both batch processing and real-time analytics.

## Key Highlights in Spark 4.1

### 1.Spark Declarative Pipelines (SDP)
A new declarative framework where users define what datasets and queries should exist, and Spark manages how they execute.

#### Key capabilities:
- Define datasets and transformations declaratively
- Automatic execution graph & dependency ordering
- Built-in parallelism, checkpoints, and retries
- Author pipelines in Python and SQL
- Compile and run pipelines via CLI
- Integrates with Spark Connect for multi-language clients

#### Value:
Reduces orchestration complexity and boilerplate, enabling reliable, production-grade pipelines with minimal effort.

For detailed overview of SDP, refer to the document linked [Spark Declarative Pipeline](https://github.com/Ahb98/rocket-ship/blob/main/Spark%20Declarative%20Pipeline.md)

### 2. Structured Streaming – Real-Time Mode (RTM)

First official support for real-time Structured Streaming with sub-second latency.

#### What’s supported in 4.1:
- Stateless, single-stage Scala queries
- Kafka sources
- Kafka and foreach sinks
- Continuous processing with single-digit millisecond latency for eligible workloads

#### Why it matters:
Enables near-instant data processing for use cases like fraud detection, monitoring, and alerting. Spark 4.1 establishes the foundation for broader RTM support in future releases.


### 3. PySpark UDFs & Python Data Sources

Significant performance and observability improvements for Python workloads.

#### Enhancements include:
##### Arrow-native UDF & UDTF decorators
- Executes directly on PyArrow
- Avoids Pandas conversion overhead

##### Python Data Source filter pushdown
- Reduces data movement
- Improves query efficiency

##### Python worker logging
- Captures logs from UDF execution
- Exposed via a built-in table-valued function

#### Outcome:
Faster execution, lower memory usage, and better debugging for PySpark applications.


### 4. Spark Connect Improvements

Spark Connect continues to mature as the default client-server architecture.

#### What’s new:

##### Spark ML on Connect is GA for Python
- Smarter model caching
- Improved memory management

##### Better stability for large workloads:
- Zstandard (zstd) compressed protobuf plans
- Chunked Arrow result streaming
- Improved handling of large local relations

#### Benefit:
More reliable and scalable remote execution for notebooks, services, and multi-language clients.


### 5. SQL Enhancements

Spark SQL sees major usability and performance upgrades.

#### Highlights:

##### SQL Scripting(enabled by default)
- Cleaner variable declarations
- Improved error handling

##### VARIANT data type
- Efficient shredding
- Faster reads for semi-structured data (JSON-like)

##### Recursive CTE support

#####  New approximate data sketches
- KLL sketches
- Theta sketches

#### Impact:
More expressive SQL, better support for semi-structured data, and advanced analytical capabilities.






    
   
---
		   
# [Back to Rocket Ship front page](https://shauryashaurya.github.io/rocket-ship/)            


