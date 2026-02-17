---
layout: default
title: "Data Preparation for AI"
---

# Data Preparation for AI
<img src="https://media.licdn.com/dms/image/v2/D4D12AQFOtVwp75w1bA/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1727859342774?e=2147483647&v=beta&t=bGPo320M-76P5KipNZ_E1GTFgCMWQGipWVNWJNsrYqY" alt="Data Preparation for AI" /> 

## Collab     
1. [Pavan Kumar Busetty](https://github.com/pavankumarbusetty), [LinkedIn](https://www.linkedin.com/in/pavankumar-busetty/)
2. [Shivani Patil](), [LinkedIn]()
3. [Shruthi Raj](), [LinkedIn]()
4. [Jaya Chandran](), [LinkedIn]()
5. [Shaurya Agarwal](https://www.linkedin.com/in/shauryashaurya/)

## TL;DR
Built an end-to-end enterprise data preparation framework in Palantir Foundry covering structured and unstructured data.
Implemented reusable PySpark cleaning utilities, enforced data quality using Expectations, modeled business-aware Ontology objects with security controls (PII encryption + row-level policies), and operationalized semantic search using embeddings.
The result: messy enterprise data transformed into governed, AI-ready business assets with full lineage, traceability, and production-grade reliability.

## Introduction 
Everyone talks about AI models. In real world production systems, most of the effort still goes into data cleaning, especially when data appears structured but fails basic analytical and semantic expectations.

### Why Data Cleaning Is Mission-Critical
Poor data quality is the primary reason why 85% of AI projects fail in production. Even sophisticated algorithms cannot overcome fundamental data issues like inconsistent formats, missing values, and logical violations lead to unreliable models, biased predictions, and costly business failures. Organizations typically spend 70-80% of AI project time on data preparation rather than model development.

### Enterprise Data Types & Core Challenges
**Structured Data** (databases, spreadsheets, APIs): Format inconsistencies, missing values, logical violations, duplicate records
**Unstructured Data** (PDFs, documents, images, emails): Mixed digital/scanned formats, complex layouts, OCR requirements, content extraction complexity
**Semi-Structured Data** (JSON, XML, logs): Schema variations, nested hierarchies, encoding issues, format evolution over time

### The Foundry Advantage
This is where **Palantir Foundry** stands out. Rather than brittle, one-off scripts, Foundry provides a production-grade data operating system where **pipelines, governance, quality, security, and ontology are first-class citizens**. Using Pipeline Builder and Code Repositories, teams can transform messy datasets into AI-ready, ontology-aligned data with full lineage and traceability.


## Structured Data 
Enterprise structured data often looks clean in databases, but hidden quality issues silently break analytics and AI models in production. The real challenge isn’t just fixing individual records, it’s building reusable, governed processes that scale across enterprise datasets and prevent quality issues from derailing AI performance.

We demonstrate a comprehensive cleaning pipeline using three enterprise datasets: **Customer, Product Inventory, and Sales Transactions, processed via Code Repositories** with shared utilities for consistency and maintainability. This approach transforms problematic raw data into secure, semantic business assets ready for AI consumption. This is where Palantir Foundry moves beyond traditional data platforms — turning cleaned data into governed, reusable assets that AI systems can trust.

Raw Structured Data -> Data Issue Identification -> Standardized Cleaning & Validation -> Ontology Mapping -> Governed AI-Ready Business Data

### Step 1: Data Issue Identification

**Common Enterprise Data Quality Issues (with Examples & Resolution Strategies)**
In Palantir Foundry, identifying issues early helps define what cleaning logic, validation checks, and reusable transformations should be built into pipelines. Even structured tables develop recurring quality problems due to manual inputs, system migrations, and multiple source integrations.
Below are the most common issues specifically aligned to our datasets, along with resolution strategies. These recurring patterns allow us to design standardized, reusable cleaning logic in Foundry that can be applied consistently across pipelines instead of solving data quality issues in isolation each time.


| Issue Type | Example (as per Dataset) | Cleaning Approach |
|------------|--------------------------|-------------------|
| **Missing Values** | customer_age missing in Customer table;<br>unit_price null in Product Inventory;<br>quantity missing in Sales Transactions | • Impute numeric analytical fields using 0, mean, or median where appropriate<br>• Fill descriptive fields like region or sales_rep with placeholders such as "Unknown"<br>• Track null patterns using data quality checks to catch recurring source issues |
| **Inconsistent Formats** | transaction_date as "20/01/2024 10:30" vs "2024-01-20";<br>unit_price as "$99.99" vs 99.99 | • Standardize date columns into one timestamp format<br>• Remove currency symbols before casting to numeric<br>• Enforce consistent schema types during pipeline transformation |
| **Logically Invalid Values** | quantity = -2 in Sales Transactions;<br>quantity_in_stock = -10 in Product Inventory | • Apply validation rules to detect negative or unrealistic values<br>• Replace with 0 or flag for review based on business logic |
| **Identifier Issues** | Missing customer_id in Customer table;<br>invalid customer_email like "john@email";<br>duplicate product_code entries | • Enforce non-null primary keys for customer_id, product_code, transaction_id<br>• Validate email format using pattern checks<br>• Deduplicate records using business identifiers |
| **Duplicate Records** | Same customer_email appearing multiple times with different customer_id values | • Identify duplicates using email as a business key<br>• Retain the record with the most complete information<br>• Track merged records for auditability and traceability |
| **Whitespace & Hidden Characters** | product_code stored as " P001 ";<br>region as "North " | • Trim leading and trailing spaces across key columns<br>• Remove hidden/non-printable characters that break joins<br>• Standardize cleaned values before matching |
| **Data Type Drift** | quantity stored as "2" (string) in some rows and numeric in others | • Enforce consistent casting to integer/decimal types during transformation<br>• Validate schema consistency across pipeline runs<br>• Monitor for drift using automated data quality checks |

### Step 2: Data Cleaning & Quality Validation
**Reusable Transformation Architecture**
All datasets were processed using a shared utility.py module for consistent, reusable transformations. This utility layer provides standardized functions for null handling, format normalization, and business defaults, ensuring consistent, AI-ready data across all enterprise systems.

Example utility functions:

```
Import pyspark.sql.functions as F
Import pyspark.sql.types as T
def trim_column(df, col):
    return df.withColumn(col, F.trim(F.col(col)))

def clean_age(df, col="age", default=38, min_age=1, max_age=120):
    df = df.withColumn(col, F.col(col).cast(T.IntegerType()))
    df = df.withColumn(col, F.coalesce(F.col(col), F.lit(default)))
    return df.filter((F.col(col) >= min_age) & (F.col(col) <= max_age))

```
These reusable transformations standardize how data is cleaned across datasets. However, cleaning alone is not sufficient, and quality must also be enforced continuously as new data enters the system.

**Enforcing Quality: Data Health Checks & Expectations**
Cleaning existing data is only half the battle. The real value comes from preventing bad data from entering your AI pipeline. Foundry's expectation framework enables proactive quality enforcement during transformation, ensuring invalid records don't propagate downstream. This shift data quality from reactive fixing to proactive enforcement.

Validations included:
•	Numeric fields like price, quantity, and inventory must be non-negative
•	Age constrained to realistic human ranges
•	Core identifiers such as customer_id, product_id, and transaction_id must not be null
•	Type enforcement for numeric and date columns

These checks ensure that data quality rules are enforced during pipeline execution, preventing invalid records from flowing into downstream systems.
Example expectation checks applied on the product dataset:
```
from transforms.api import transform, Input, Output, Check
from transforms import expectations as E
@transform.spark.using(
    output=Output("clean_product_dataset", checks=[
        Check(E.col("quantity_in_stock").gte(0), "quantity_in_stock must be >= 0"),
        Check(E.col("price").gte(0), "price must be >= 0"),
        Check(E.col("weight_kg").gte(0), "weight_kg must be >= 0"),
    ]),
    product_input=Input("raw_product_dataset"),
)
```
Similarly, type enforcements checks were applied on the customer dataset:
```
from transforms.api import transform, Input, Output, Check
from transforms import expectations as E
@transform.spark.using(
    output=Output(
        " clean_customer_dataset ",
        checks=[
            Check(E.col("email").has_type(T.StringType()), "email must be string"),
            Check(E.col("phone").has_type(T.StringType()), "phone must be string"),
            Check(E.col("age").has_type(T.IntegerType()), "age must be integer"),
            Check(E.col("registration_date").has_type(T.TimestampType()), "registration_date must be timestamp"),
        ]
    ),
    customer_input=Input("raw_customer_dataset "),
)
```

### Step 3: Ontology Mapping

While most traditional data platforms stop at producing clean tables, Foundry extends this layer by turning structured datasets into business-aware objects with defined meaning, relationships, and governance. This semantic layer is what allows analytics and AI systems to interact with data in a more natural and consistent way.

**From Clean Data to Intelligent Business Assets**
Cleaning improves data quality, but clean tables alone still lack business context. This is where Foundry's Ontology becomes transformative by
converting clean datasets into governed business objects with meaning, relationships and security that AI and analytics systems can directly reason on
The ontology creation process transforms technical datasets into semantic business assets through strategic steps:

#### Step 1 — Identify Business Objects
Map cleaned datasets to core business entities (object types), not raw tables:
•	Customer ← Customer dataset
•	Product ← Product Inventory dataset
•	Sales ← Sales Transactions dataset

Create them from **New** → **Object Type**

<img width="341" height="399" alt="image" src="https://github.com/user-attachments/assets/aca2d69e-ec3e-4725-af87-5ef9eb009ff9" />

#### Step 2 — Choose Stable Identifiers
Each object type must be anchored to a stable, globally unique identifier. These identifiers ensure that the same real-world entity is consistently recognized across datasets, pipelines, and applications. For example, Customer ID can serve as the primary key for the Customer object, while a human-readable attribute such as Last Name can be used as the display title.

<img width="939" height="607" alt="image" src="https://github.com/user-attachments/assets/12db3dfd-b55b-4a8c-a6c8-525101a6f34d" />

The same principle is applied across Product and Sales objects to maintain consistent identity and traceability across the ontology.

