---
layout: default
title: "Data Preparation for AI"
---

# Data Preparation for AI
[[<img src="https://media.licdn.com/dms/image/v2/D4D12AQFOtVwp75w1bA/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1727859342774?e=2147483647&v=beta&t=bGPo320M-76P5KipNZ_E1GTFgCMWQGipWVNWJNsrYqY" alt="Data Preparation for AI" /> ](https://www.google.com/imgres?q=data%20preparation%20for%20ai%20images&imgurl=https%3A%2F%2Fwww.actian.com%2Fwp-content%2Fuploads%2F2023%2F12%2Fdata-preparation-for-AI.jpg&imgrefurl=https%3A%2F%2Fwww.actian.com%2Fdata-preparation-for-ai%2F&docid=Fg-Tr6vkts6ZiM&tbnid=aLWA-a297VupqM&vet=12ahUKEwj9-L6hzuCSAxVFzzgGHfBsBKEQnPAOegQIHxAB..i&w=815&h=500&hcb=2&ved=2ahUKEwj9-L6hzuCSAxVFzzgGHfBsBKEQnPAOegQIHxAB)](https://www.google.com/imgres?q=data%20preparation%20for%20ai%20images&imgurl=https%3A%2F%2Fwww.actian.com%2Fwp-content%2Fuploads%2F2023%2F12%2Fdata-preparation-for-AI.jpg&imgrefurl=https%3A%2F%2Fwww.actian.com%2Fdata-preparation-for-ai%2F&docid=Fg-Tr6vkts6ZiM&tbnid=aLWA-a297VupqM&vet=12ahUKEwj9-L6hzuCSAxVFzzgGHfBsBKEQnPAOegQIHxAB..i&w=815&h=500&hcb=2&ved=2ahUKEwj9-L6hzuCSAxVFzzgGHfBsBKEQnPAOegQIHxAB)

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
-	Numeric fields like price, quantity, and inventory must be non-negative
-	Age constrained to realistic human ranges
-	Core identifiers such as customer_id, product_id, and transaction_id must not be null
-	Type enforcement for numeric and date columns

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
-	Customer ← Customer dataset
-	Product ← Product Inventory dataset
-	Sales ← Sales Transactions dataset

Create them from **New** → **Object Type**

<img width="341" height="399" alt="image" src="https://github.com/user-attachments/assets/aca2d69e-ec3e-4725-af87-5ef9eb009ff9" />

#### Step 2 — Choose Stable Identifiers
Each object type must be anchored to a stable, globally unique identifier. These identifiers ensure that the same real-world entity is consistently recognized across datasets, pipelines, and applications. For example, Customer ID can serve as the primary key for the Customer object, while a human-readable attribute such as Last Name can be used as the display title.

<img width="939" height="607" alt="image" src="https://github.com/user-attachments/assets/12db3dfd-b55b-4a8c-a6c8-525101a6f34d" />

The same principle is applied across Product and Sales objects to maintain consistent identity and traceability across the ontology.

#### Step 3 — Model Properties (Strong Types & Units)
At this stage, technical columns are transformed into well-defined business attributes with strong data types, validation rules, and units. This ensures that downstream analytics and AI systems interpret values consistently and correctly.
-	Customer email (validated string format)
-	Product price (decimal with currency constraints)
-	Transaction date (timestamp with timezone handling)

#### Step 4 — Define Link Types (Relationships)
Beyond defining individual objects, Ontology captures how business entities relate to each other. These relationships create a connected semantic layer that enables richer analysis, traceability, and AI-driven reasoning
-	Customer -> Sales as one-to-many relationship
-	Sales -> Product as many-to-many relationship
-	Relationships are derived from foreign keys and join logic to maintain referential integrity across objects.

<img width="842" height="614" alt="image" src="https://github.com/user-attachments/assets/0f5bdfa0-c5b6-4ae9-8558-81c4fdd23f39" />

#### Step 5 — Attach Policies (Security & Sensitivity) 
Security and data sensitivity are embedded directly into the Ontology layer, ensuring that sensitive information is protected consistently across all applications and users. Instead of managing access separately in downstream systems, policies are defined at the data model level, making governance enforceable by design.
Sensitive attributes such as email and phone are marked as PII and configured for masking or encryption.

**PII Protection with Cipher**: 
-	Create a Cipher Channel and issue a Cipher Data Manager License. 

<img width="518" height="471" alt="image" src="https://github.com/user-attachments/assets/31962161-8f0f-44f6-8bf4-4a6839e11135" />

<img width="809" height="606" alt="image" src="https://github.com/user-attachments/assets/7d8bf675-0d07-4ecd-8c07-9a5d8c902dac" />

<img width="1141" height="627" alt="image" src="https://github.com/user-attachments/assets/413b6f3a-e038-4ee6-89f6-392846c32e14" />

-	Add the bellaso-python-lib to your code repository. (Add bellaso-python-lib in the requirements.run block in conda_recipe/meta.yml. You can also do this automatically by adding it in the Libraries panel of your Code Repository environment.)
-	Encrypt PII columns in your Python transform using Cipher operations as per the example shown:

```
from bellaso_python_lib.encryption.encrypter_input import EncrypterInput

@transform.spark.using(
   	encrypter=EncrypterInput("Cipher Customer Details"),
    	output=Output("Customer_Updated",
   	 customer_input=Input("Customer"),
)

```
-	Building encrypted datasets requires Admin or Data Manager permission.
-	Reference the encrypted dataset in Ontology Manager, set PII property type to CipherText, and assign the default Cipher Channel.


**Row-Level Security in Ontology Manager**
-	In Ontology Manager, navigate to the object type you want to secure.
-	Go to the **Security tab**.
-	Create a restricted view of the backing dataset and compose your row-level security policy (e.g., restrict access to rows where region = ‘EMEA’ to specific user groups).
-	Assign the policy to the appropriate user groups and save. Only users who meet the policy criteria will be able to view those rows

<img width="967" height="140" alt="image" src="https://github.com/user-attachments/assets/a72b9722-d337-4fcd-83ee-6144ad629308" />

<img width="976" height="430" alt="image" src="https://github.com/user-attachments/assets/4e8556f4-036c-4737-9149-cdbf0f1d4222" />

#### Step 6 — Create Derived Semantics
Ontology also supports derived attributes that encode business logic directly into the data model. These computed properties allow analytics and AI applications to use consistent, trusted metrics without recalculating logic in every downstream system.
Add computed attributes that capture business logic:
-	total_amount = quantity × unit_price
-	customer_lifetime_value based on historical transactions
-	product_velocity from inventory turnover rates

#### Step 7 — Publish & Version the Ontology
Once modeled, the ontology is published as a governed, versioned layer that serves as a consistent foundation for applications, analytics, and AI systems
-	Publish objects governed API-backed entities.
-	Maintain semantic versions and change notes.

#### Step 8 — Operationalize Consumption
The published ontology becomes the foundation for operational consumption across the enterprise. Applications, dashboards, and AI systems can interact with business objects directly instead of raw tables. Natural language interfaces and AIP integrations allow users to ask questions such as “Show customers with declining transactions in the last 90 days,” while governance, security, and audit controls operate seamlessly in the background.

**Structured Data: Traditional Tool vs Palantir Foundry**

| Capability        | Palantir Foundry        | Traditional Stack        |
|------------------|--------------------------|--------------------------|
| **Cleaning Reuse** | Shared utilities         | Rewritten per pipeline   |
| **Quality Checks** | Built-in expectations    | Custom scripts           |
| **Schema Control** | Enforced schema governance | Manual handling          |
| **Business Layer** | Business objects (ontology-driven) | Tables only             |
| **Relationships**  | Defined once (ontology relationships) | Query-level joins       |

This structured data approach from utility-driven cleaning through semantic ontology mapping creates the governed foundation that enterprise AI requires. Clean data evolves into business-intelligent, AI-ready assets with full lineage, security controls, and semantic relationships that enable reliable, scalable AI applications.
Next, we'll explore how this same principled approach extends to unstructured data, where documents and images present entirely different but equally critical challenges for AI readiness.

## Unstructured Data Preparation
In real-world scenarios, most data available for AI systems is **unstructured**. This includes text documents such as emails and articles, PDFs and PowerPoint files containing plain text, text and numeric tables, HTML documents, and system log files. Unlike structured datasets, unstructured data does not follow a predefined schema, making it significantly more challenging to process and prepare for modeling. Palantir Foundry offers two ways to work with the unstructured data 1.) Pipeline Builder   2.) Code Repository


**Pipeline Builder** is purpose‑built for AI‑driven unstructured data processing, unlike traditional no‑code tools designed for workflow automation. It natively understands PDFs, images, text, chunking, tokenization, and embeddings—making it the ideal engine for preparing insurance policies, contracts, KYC documents, and scanned archives.

**Code Repositories** are best for preparing unstructured data when you need custom code, advanced processing, or integration with AI/ML model training. They offer flexibility, version control, and access to file system APIs, making them ideal for complex workflows and large datasets.

### 1.) Unstructured Data Preparation Using Pipeline Builder

**Pipeline Builder Superpower**: Document → Page → Chunk → Embedding
 (Full lineage, high explainability, and AI‑ready outputs.)

 #### End‑to‑End Flow
```
Unstructured Data → Parsing → Extraction → Text → Chunking → Tokenization → Embeddings → Ontology

```

<img width="538" height="273" alt="image" src="https://github.com/user-attachments/assets/17e39c92-b2f2-4789-9d47-7bc0b5d29b35" />

#### STEP‑BY‑STEP PIPELINE
#### Step 1 — Upload Unstructured Files to a Media Set
Unstructured documents like **PDFs, PPTs, scanned pages, or images** are uploaded into a Media Set.
-	At this stage, files are still **raw binary data**.
-	No semantic meaning exists yet.
-	Pipeline Builder treats them as media assets awaiting parsing.

#### Step 2 — Create a Pipeline (Batch or Streaming)
Choose ingestion style:
**Batch Pipelines**
For historical or already‑ingested data.
**Streaming Pipelines**
For continuous incoming documents (real‑time ingestion).
Both modes apply the same transformations—only timing changes.

<img width="657" height="233" alt="image" src="https://github.com/user-attachments/assets/13cd9351-2b01-4068-b365-d29e73618c92" />

#### Step 3 — Document Nature Identification
Every document is either:
- Digitally Born PDFs
Contain embedded selectable text.<br>
 → Use **Raw Text Extraction** (more accurate, deterministic)
- Scanned PDFs / Images
Contains only pixel-level text.<br>
 → Use **OCR** (probabilistic, inference-based)

**Best Practice**:
- Always attempt raw extraction first
- Use OCR only if text is missing


<img width="663" height="230" alt="image" src="https://github.com/user-attachments/assets/b87493c2-41a6-4af6-a893-6b5a84eb3433" />

#### Step 4 — Parse & Extract Text
Start with:<br>

**Block: Convert Media Set to Table Rows**
 Transforms each file into a structured row.
Then apply:<br>

**Block: Extract Text from PDF (OCR)**
-	Used when raw text is not present
-	Output = Array of pages ([page_1_text, page_2_text, ...])

Normalize arrays via:
-	**Explode Array with Position**
-	**Extract Struct with Many Fields**

**Result**: Clean page-level text with file ID + page number.

<img width="600" height="250" alt="image" src="https://github.com/user-attachments/assets/19919302-d387-498b-a03d-bfbf09094288" />

#### Step 5 — Chunking the Extracted Text
Large text blocks are split into **semantically meaningful chunks** using **Chunk String**.

**Benefits**:
-	Higher semantic precision
-	Better embedding quality
-	Improved search relevance
-	Clause-level retrieval (critical for insurance/legal documents)

**Chunking Strategy**:
-	Length-based
-	Semantic based
-	Header/section-based
-	With controlled overlap to preserve context

<img width="400" height="250" alt="image" src="https://github.com/user-attachments/assets/2290b393-61c3-4f69-bafb-58f4eab938a2" />

#### Step 6 — Generate Embeddings

Using the **Text-to-Embedding** block, chunked text turns into numerical vectors.<br>

Embeddings capture:<br>
-	Meaning
-	Intent
-	Context
-	Topic
```Output → One vector per chunk → AI‑ready representation.```
