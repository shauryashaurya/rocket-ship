---
layout: default
title: "MLOps in Palantir Foundry"
---




# MLOps in Palantir Foundry                             
                              
<img src="./images/03-mlops-foundry.png" width="95%" align="center" alt="MLOps in Palantir Foundry" />                          
                          
                          
---                          
                          
## Introduction                          
                          
MLOps (Machine Learning Operations) refers to the set of practices that automate and standardize the end-to-end machine learning lifecycle—data preparation, feature engineering, experimentation, training, validation, deployment, monitoring, and governance. The goal is to enable reliable, scalable, and auditable ML systems in production.                          
                          
Palantir Foundry is an enterprise data, analytics, and AI platform that provides a tightly integrated MLOps experience. Unlike tool-chain-based MLOps stacks, Foundry unifies data pipelines, feature engineering, experimentation, model lifecycle management, deployment, and governance on a single platform, reducing operational friction and improving reproducibility and compliance.                          
                          
                          
---                          
                          
## Key Challenges in MLOps                          
                          
- Feature inconsistency: Training-serving skew caused by mismatched feature logic across environments.                          
                          
- Experiment tracking at scale: Difficulty comparing experiments, datasets, and feature versions.                          
                          
- Model and data versioning: Ensuring reproducibility across changing data and code.                          
                          
- Fragmented tooling: Separate tools for features, experiments, registry, deployment, and monitoring.                          
                          
- Governance and compliance: Auditable lineage across data → features → models → predictions.                          
                          
                          
Foundry addresses these challenges by embedding feature engineering, experimentation, model registry, and governance directly into the platform’s data and ontology layer.                          
                          
                          
---                          
                          
## MLOps Architecture in Foundry                          
                          
Foundry’s MLOps architecture is data-centric and ontology-driven.                          
                          
Core Architectural Elements:                          
                          
- Ontology: A semantic abstraction layer defining business entities, relationships, and actions. Models consume ontology-aligned data, ensuring consistent interpretation across analytics, ML, and operations.                          
                          
- Versioned Data & Features: Every dataset and transformation (including features) is versioned with full lineage.                          
                          
- Model Artifacts + Adapters: Models are packaged with metadata and adapters that standardize inference and deployment.                          
                          
- Modeling Objectives: Serve as the control plane for experimentation, evaluation, promotion, and deployment of models tied to business objectives.                          
![Modelling Objective](https://anudeepchatradi.github.io/rocket-ship/images/Screenshot%202026-02-03%20214523.png)                          
                          
This architecture tightly couples features, experiments, models, and deployments into a single lifecycle.                          
                            
---                          
                          
## Data Management                          
                          
Data management in Foundry directly supports feature engineering and reproducibility:                          
                          
- Versioned Datasets: Point-in-time snapshots allow models to be trained and re-evaluated on identical data.                          
                          
- Feature Engineering Pipelines: Features are created as standard Foundry transformations (Spark / SQL / Python), inheriting versioning, lineage, and access controls.                          
                          
- Feature Reuse: Engineered features can be reused across multiple models without duplication.                          
                          
- Training–Serving Consistency: The same feature logic is used for batch scoring and live inference, minimizing skew.                          
                          
- Ontology Integration: Features can be mapped to business entities, enabling semantic consistency and governance.                          
                          
                          
Foundry does not rely on an external feature store; instead, the platform itself acts as a governed feature layer.                          
                          
                          
---                          
                          
## Model Development                          
                          
Foundry supports flexible and collaborative model development:                          
                          
Frameworks & Packages                          
                          
- palantir_models (primary): Standard library for packaging models, defining inference interfaces, and integrating with Foundry deployments.                          
                          
- Common ML frameworks: scikit-learn, XGBoost, LightGBM, TensorFlow, PyTorch, and custom containers.                          
                          
- Spark ML: Supported for training, but not recommended for low-latency REST inference.                          
                          
                          
Experimentation                          
                          
- Experiment Tracking: Training runs are tied to specific data versions, feature versions, code, and parameters.                          
                          
- Metric Comparison: Modeling Objectives allow side-by-side evaluation of model submissions using standardized metrics.                          
                          
- Reproducibility: Every experiment can be reproduced exactly due to immutable data and transformation lineage.                           
                          
                          
Model Registry                          
                          
Approved models are stored as versioned artifacts within Modeling Objectives.                          
                          
Each version contains:                          
                          
- Training data references                          
                          
- Feature definitions                          
                          
- Evaluation metrics                          
                          
- Deployment readiness status                          
                          
                          
Promotion from experimentation → staging → production is governed and auditable.                          
                          
                          
                          
---                          
                          
## Deployment                          
                          
Foundry supports both batch and real-time deployment:                          
                          
- Live Models: Deployed as REST endpoints with version control and rollback.                          
                          
- Batch Scoring: Scheduled or triggered inference pipelines.                          
                          
- Environment Promotion: Explicit promotion across environments (Dev / Staging / Prod).                          
                          
- Objective-Driven Releases: Only models approved within Modeling Objectives can be deployed.                          
                          
- External Models: Integration with externally hosted models (e.g., AWS SageMaker) is supported when required.                          
                          
                          
Deployment is tightly coupled with governance and lineage.                          
                          
                          
---                          
                          
## Monitoring & Observability                          
                          
Monitoring in Foundry focuses on traceability and feedback loops:                          
                          
- Performance Metrics: Ongoing evaluation of prediction quality using defined metrics.                          
                          
- Data & Feature Drift Awareness: Changes in upstream data or feature distributions are traceable through lineage.                          
                          
- Operational Feedback: Predictions and outcomes can be written back into Foundry datasets to retrain or recalibrate models.                          
                          
- Auditability: Every prediction can be traced back to a model version, feature set, and data snapshot.                          
                          
                          
While Foundry does not expose standalone drift-detection libraries like some cloud tools, its lineage-first design enables deep root-cause analysis.                          
                          
                          
---                          
                          
## Governance & Compliance                          
                          
Governance is a core strength of Foundry MLOps:                          
                          
- Fine-grained Access Control: Permissions enforced at dataset, feature, model, and deployment levels.                          
                          
- End-to-End Lineage: Automatic tracking from raw data → features → experiments → models → predictions.                          
                          
- Approval Workflows: Controlled promotion of models into production.                          
                          
- Enterprise Compliance: Designed for regulated industries requiring explainability, audit trails, and policy enforcement.                          
                          
                          
                          
---                          
                          
## Packages & Tools in Foundry for MLOps                          
Palantir Foundry provides native components and libraries that collectively enable end-to-end MLOps without requiring a fragmented external toolchain.                          
                          
| Component                 | Purpose                                                       |                          
|---------------------------|---------------------------------------------------------------|                          
| **palantir_models**       | Model packaging, inference interfaces, deployment integration |                          
| **Modeling Objectives**   | Experiment tracking, evaluation, model registry, promotion   |                          
| **Foundry Transformations** | Feature engineering with versioning and lineage              |                          
| **Ontology**              | Semantic consistency across data, features, and models       |                          
| **Foundry DevOps (Beta)** | CI/CD and release management for ML workflows                |                          
| **External Integrations** | Optional integration with external model hosting             |                          
                          
---                          
## Example how to do                          
Say we have a example model like                           
```python                          
import pandas as pd                          
import numpy as np                          
from sklearn.model_selection import train_test_split                          
from sklearn.preprocessing import StandardScaler, OneHotEncoder                          
from sklearn.compose import ColumnTransformer                          
from sklearn.pipeline import Pipeline                          
from sklearn.ensemble import RandomForestRegressor                          
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error                          
import joblib                          
                          
                          
                          
# Display basic info                          
print("Dataset shape:", df.shape)                          
print("\nFirst few rows:")                          
print(df.head())                          
print("\nData types:")                          
print(df.dtypes)                          
print("\nBasic statistics:")                          
print(df.describe())                          
                          
# Separate features and target                          
X = df.drop('charges', axis=1)                          
y = df['charges']                          
                          
# Split the data                          
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)                          
                          
# Define numerical and categorical features                          
numerical_features = ['age', 'bmi', 'children']                          
categorical_features = ['sex', 'smoker', 'region']                          
                          
# Create preprocessing pipelines for both numerical and categorical data                          
numerical_transformer = StandardScaler()                          
categorical_transformer = OneHotEncoder(drop='first', sparse_output=False)                          
                          
# Combine preprocessing steps                          
preprocessor = ColumnTransformer(                          
    transformers=[                          
        ('num', numerical_transformer, numerical_features),                          
        ('cat', categorical_transformer, categorical_features)                          
    ])                          
                          
# Create the complete pipeline with Random Forest                          
pipeline = Pipeline(steps=[                          
    ('preprocessor', preprocessor),                          
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10))                          
])                          
                          
print("\n" + "="*60)                          
print("Training the model...")                          
print("="*60)                          
                          
# Train the model                          
pipeline.fit(X_train, y_train)                          
                          
# Make predictions                          
y_pred_train = pipeline.predict(X_train)                          
y_pred_test = pipeline.predict(X_test)                          
                          
# Evaluate the model                          
print("\n" + "="*60)                          
print("MODEL PERFORMANCE")                          
print("="*60)                          
                          
print("\nTraining Set:")                          
print(f"  R² Score: {r2_score(y_train, y_pred_train):.4f}")                          
print(f"  RMSE: ${np.sqrt(mean_squared_error(y_train, y_pred_train)):,.2f}")                          
print(f"  MAE: ${mean_absolute_error(y_train, y_pred_train):,.2f}")                          
                          
print("\nTest Set:")                          
print(f"  R² Score: {r2_score(y_test, y_pred_test):.4f}")                          
print(f"  RMSE: ${np.sqrt(mean_squared_error(y_test, y_pred_test)):,.2f}")                          
print(f"  MAE: ${mean_absolute_error(y_test, y_pred_test):,.2f}")                          
                          
# Show sample predictions                          
print("\n" + "="*60)                          
print("SAMPLE PREDICTIONS (First 10 from test set)")                          
print("="*60)                          
comparison_df = pd.DataFrame({                          
    'Actual': y_test.values[:10],                          
    'Predicted': y_pred_test[:10],                          
    'Difference': y_test.values[:10] - y_pred_test[:10]                          
})                          
print(comparison_df.to_string(index=False))                          
```                          
Now since we have the model ready we need to tell palantir how this model acessed and needs to be used for which we need a adapter code like following                           
```python                          
import palantir_models as pm                          
                          
                          
class InsuranceModelAdapter(pm.ModelAdapter):                          
    @pm.auto_serialize(                          
        model=pm.serializers.DillSerializer()                          
    )                          
    def __init__(self, model):                          
        self.model = model                          
                          
    @classmethod                          
    def api(cls):                          
        columns = [('age', int), ('sex', str), ('bmi', float), ('children', int), ('smoker', str), ('region', str)]                          
        return {"df_in":pm.Pandas(columns)},{"df_out": pm.Pandas(columns+[("chargeAmnt",float)])}                          
                          
    def predict(self, df_in):                          
        numerical_features = ['age', 'bmi', 'children']                          
        categorical_features = ['sex', 'smoker', 'region']                          
                          
        prediction_features = numerical_features+categorical_features                          
        df_in["chargeAmnt"] = self.model.predict(df_in[prediction_features])                          
                          
        return df_in                          
```                          
Once both of them are ready this means we are ready to register the model                          
                          
```python                          
# Load the autoreload extension and automatically reload all modules                          
%load_ext autoreload                          
%autoreload 2                          
from palantir_models.code_workspaces import ModelOutput                          
from insurance_model_adapter import InsuranceModelAdapter # Update if class or file name changes                          
                          
# Wrap the trained model in a model adapter for Foundry                          
insurance_model_adapter = InsuranceModelAdapter(pipeline)                          
                          
# Get a writable reference to your model resource.                          
model_output = ModelOutput("insurance_model")                          
model_output.publish(insurance_model_adapter) # Publishes the model to Foundry                          
```                          
Once the model registration is sucessful  we can move to modelling to deploy it.                          
Like following we can directly run the model and check the values ![Deploy](https://anudeepchatradi.github.io/rocket-ship/images/Screenshot%202026-02-04%20000524.png)                          
We can also check the deployement logs like following ![deployment logs](https://anudeepchatradi.github.io/rocket-ship/images/Screenshot%202026-02-04%20000542.png)                          
We can set checks and evaluation metrics so that any new model gets released, we run a evaluation on a data and check if the values are within our said threshold ![Evaluation Metrics](https://anudeepchatradi.github.io/rocket-ship/images/Screenshot%202026-02-04%20001017.png)                          
                          
Once deployed with proper configurations it can be accessed as api ![Container Details](https://anudeepchatradi.github.io/rocket-ship/images/Screenshot%202026-02-04%20002132.png)                          
otherwise it can also be published as a function in ontology manager ![Model in Ontology Manager](https://anudeepchatradi.github.io/rocket-ship/images/Screenshot%202026-02-04%20001659.png)                          
or imported in typescript repository ![Palantir TS repository](https://anudeepchatradi.github.io/rocket-ship/images/Screenshot%202026-02-04%20001939.png)                          
                          
---                          
                          
## Comparison with Other MLOps Tools                          
The table below compares Palantir Foundry with common MLOps tools, including MLflow, across core lifecycle capabilities.                          
![Comparison Chart](https://anudeepchatradi.github.io/rocket-ship/images/comparison_chart.jpg)                          
                          
Key Insight:                          
                          
MLflow excels at experiment tracking and lightweight model registry, but relies on external systems for features, governance, and deployment.                          
                          
Foundry provides a fully integrated enterprise MLOps platform, prioritizing governance, lineage, and operationalization over standalone experimentation flexibility.                          
                          
---                          
                          
## Conclusion                          
                          
Palantir Foundry delivers an end-to-end, governance-first MLOps platform that unifies data management, feature engineering, experimentation, model registry, deployment, and monitoring under a single architecture. By embedding MLOps directly into the data and ontology layer, Foundry minimizes tool fragmentation and ensures reproducibility, compliance, and operational trust.                          
                          
While tools like MLflow or Kubeflow are strong in modular or research-oriented environments, Foundry is particularly well-suited for large enterprises and regulated industries where traceability, control, and integration with business operations are critical.                          
                          
                          
---                          
## Authors                          
1. [Anudeep Chatradi](https://github.com/anudeepchatradi), [LinkedIn](https://www.linkedin.com/in/anudeep-chatradi-78757298/)                          
2. [Abhishek Narayan Chaudhury](https://github.com/achaudhury7378), [LinkedIn](https://www.linkedin.com/in/abhishek-chaudhury-07422b191/)                          
    
   
---
		   
# [Back to Rocket Ship front page](https://shauryashaurya.github.io/rocket-ship/)            