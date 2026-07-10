# Methodology (Draft)
*Living draft — expand as later phases (web application, DevOps pipeline) are completed. Sections below are ready for refinement/formatting into the final report.*

---

## 3.1 Dataset

The Home Credit Default Risk dataset (Kaggle) was selected for this project due to its scale, realism, and inclusion of both traditional application-level data and granular transaction-level history, which together make it suitable for engineering alternative behavioural features (Objective 3). The dataset comprises multiple relational tables; this project primarily draws on `application_train.csv` (307,511 applicant records, 122 features) as the core table, enriched with behavioural features derived from `installments_payments.csv` (13,605,401 records of historical installment payments).

The target variable, `TARGET`, is binary, indicating whether an applicant defaulted on their loan (1) or repaid without difficulty (0).

## 3.2 Exploratory Data Analysis

Initial exploratory analysis was conducted to characterise the dataset before any modelling decisions were made.

**Class distribution.** The target variable exhibits substantial class imbalance: 91.9% of applicants did not default, while 8.1% did. This imbalance directly informed the choice of evaluation metrics (Section 3.6), as plain classification accuracy would be a misleading indicator of model performance on this dataset — a naive classifier predicting "no default" for every applicant would achieve 91.9% accuracy while providing no practical value.

**Missing data.** Of the 122 original columns, 67 contained missing values, with 49 columns missing more than 40% of their entries. The most severely affected columns related to property and building characteristics of the applicant's residence (e.g., `COMMONAREA_AVG`, `NONLIVINGAPARTMENTS_MODE`, `LIVINGAPARTMENTS_MEDI`), with missingness concentrated in the 59–70% range. No column exceeded 70% missingness. Given the extent and apparent optionality of these fields, they were retained but handled via median/constant imputation within the modelling pipeline (Section 3.5) rather than dropped outright, preserving any residual signal while avoiding the need for manual per-column judgement calls across a large, homogeneous feature family.

**Data quality anomaly — DAYS_EMPLOYED.** A placeholder value of 365,243 (equivalent to approximately 1,000 years) was identified in the `DAYS_EMPLOYED` field, affecting 18.0% of applicants (55,374 records). Cross-tabulation against `NAME_INCOME_TYPE` confirmed this value corresponds almost exclusively to Pensioner (55,352 records) and Unemployed (22 records) applicants, indicating a deliberate encoding of "not currently employed" rather than a data entry error. This was addressed by (1) creating a binary indicator feature, `IS_RETIRED_OR_UNEMPLOYED`, to preserve the informational content of this status, and (2) replacing the placeholder with a null value in the underlying numeric field, allowing it to be handled through standard imputation without distorting numeric calculations (e.g., mean employment duration).

**Outlier treatment — AMT_INCOME_TOTAL.** The applicant income field exhibited a maximum value of 117,000,000 against a 99th-percentile value of only 472,500 — a discrepancy of approximately 250-fold. Inspection of the ten highest values revealed a full tail of extreme entries (117M, 18M, 13.5M, 9M, 6.75M, and a cluster near 4.5M) rather than a single anomalous record, indicating a genuine distributional skew rather than an isolated data entry error. A logarithmic transformation (`log1p`) was applied in preference to simple capping or winsorising, consistent with standard practice in credit risk modelling, where income effects on default probability are typically non-linear. The transformation reduced the feature's standard deviation from 237,123 to 0.489, substantially compressing the distribution while preserving the relative ordering and information content of all records.

## 3.3 Alternative Behavioural Feature Engineering

Objective 3 of this project required the derivation of behavioural indicators beyond those available in traditional application data. These were engineered from `installments_payments.csv`, which records one row per scheduled loan installment across applicants' prior credit history with the lender.

Two row-level indicators were first derived:
- **Payment delay**: the difference, in days, between the actual payment date and the scheduled due date (positive values indicating late payment).
- **Payment difference**: the difference between the amount actually paid and the amount due.

These were then aggregated to applicant level (grouped by `SK_ID_CURR`) into six behavioural features:

| Feature | Description |
|---|---|
| `avg_payment_delay` | Mean payment delay across all historical installments |
| `std_payment_delay` | Standard deviation of payment delay (payment consistency) |
| `pct_late_payments` | Proportion of installments paid after the due date |
| `avg_payment_diff` | Mean difference between amount paid and amount due |
| `std_payment_amount` | Standard deviation of installment amounts (spending regularity) |
| `num_installments` | Total number of historical installments on record |

The resulting applicant-level feature table (339,587 applicants) was merged into the main application dataset via a left join on `SK_ID_CURR`, preserving the original row count of 307,511 and confirming no duplication occurred during the merge.

**Coverage limitation.** 15,876 applicants (5.2%) had no prior installment history and therefore no computable behavioural features. This subgroup was flagged via a binary indicator, `NO_INSTALLMENT_HISTORY`, with behavioural feature values imputed to zero. This limitation is noted explicitly: applicants with no prior credit relationship with the lender — plausibly including genuinely "thin-file" individuals, i.e. the population this project's premise identifies as underserved by traditional credit scoring — cannot benefit from behavioural feature engineering derived solely from this lender's internal transaction history. The model therefore continues to rely on traditional application-level features (income, employment, demographic data) as a fallback for this subgroup, rather than behavioural features alone.

## 3.4 Feature Set Summary

Following data cleaning and feature engineering, the final feature set comprised 131 candidate features (115 numeric, 16 categorical) per applicant, combining original application fields, derived features (e.g., log-transformed income, employment tenure in years), and the six engineered behavioural indicators described above.

## 3.5 Preprocessing Pipeline

A `ColumnTransformer`-based preprocessing pipeline (scikit-learn) was constructed to handle numeric and categorical features separately, and was integrated directly into each model pipeline to prevent data leakage between training and test partitions:

- **Numeric features**: median imputation followed by standard scaling.
- **Categorical features**: constant-value imputation (missing category placeholder) followed by one-hot encoding, with unknown categories at inference time handled gracefully rather than raising an error.

One-hot encoding of the 16 categorical features expanded the total feature space to 261 dimensions.

Data was partitioned into training (80%) and test (20%) sets using stratified sampling on the target variable, ensuring both partitions preserved the original 91.9%/8.1% class distribution.

## 3.6 Model Development and Comparison

In line with Objective 4, three supervised classification algorithms were trained and compared under identical preprocessing and evaluation conditions:

1. **Logistic Regression**, with `class_weight='balanced'` to address class imbalance.
2. **Random Forest** (100 estimators), with `class_weight='balanced'`.
3. **XGBoost** (100 estimators), with `scale_pos_weight` set to the ratio of negative-to-positive class counts in the training data.

Given the class imbalance identified in Section 3.2, **AUC-ROC, precision, recall, and F1-score** were adopted as the primary evaluation metrics in preference to raw accuracy, which is not sufficiently discriminative on an imbalanced target.

**Results:**

| Model | AUC-ROC | Default Recall | Default Precision |
|---|---|---|---|
| Logistic Regression | 0.7526 | 0.68 | 0.16 |
| Random Forest | 0.7406 | 0.05 | 0.44 |
| XGBoost | **0.7560** | 0.63 | 0.18 |

Random Forest achieved the highest overall accuracy (92%) of the three models but the lowest recall on the default class (0.05), meaning it correctly identified only 5% of applicants who actually defaulted. This result provides a direct, empirical illustration of the limitations of accuracy as an evaluation metric under class imbalance: a model can appear strong by an accuracy measure while being functionally inadequate for the task it is intended to perform. XGBoost was selected as the primary model for the remainder of this project on the basis of its superior AUC-ROC and a more practically useful balance between precision and recall on the minority (default) class.

## 3.7 Explainable AI (SHAP)

To satisfy Objective 5, SHAP (SHapley Additive exPlanations) was integrated using `TreeExplainer`, an implementation providing fast and exact Shapley value computation for tree-based models such as XGBoost.

**Global feature importance.** SHAP values computed across a 1,000-record sample of the test set indicated that the three external credit bureau scores (`EXT_SOURCE_1`, `EXT_SOURCE_2`, `EXT_SOURCE_3`) and loan/goods amount fields (`AMT_GOODS_PRICE`, `AMT_CREDIT`, `AMT_ANNUITY`) were the most influential predictors overall, consistent with domain expectations. Notably, the engineered behavioural feature `pct_late_payments` ranked sixth in global importance — ahead of established demographic predictors such as `DAYS_BIRTH` (applicant age) — providing direct empirical support for the value of the alternative behavioural feature engineering undertaken in pursuit of Objective 3. A second engineered feature, `std_payment_amount`, also appeared within the top ten most influential features.

**Individual prediction explanations.** SHAP waterfall plots were generated to explain individual applicant predictions, decomposing each prediction into the additive contribution of each feature relative to the model's baseline (expected) output. This format is directly transferable to the administrative interface specified in Objective 6, enabling a loan officer to view not only an applicant's predicted default probability but a transparent, feature-level rationale for that prediction — for example, identifying that a below-average rate of late payments (`pct_late_payments`) contributed measurably to a lower predicted risk score for a given applicant.

---

## Notes for later revision
- Add methodology diagram (data flow: raw CSVs → cleaning → feature engineering → preprocessing pipeline → model → SHAP)
- Add confusion matrices alongside classification reports once finalised
- Expand Section 3.6 with hyperparameter tuning results once conducted
- Cross-reference Section 3.3's coverage limitation in the final Discussion/Limitations chapter
- Insert SHAP summary plot and waterfall plot figures (saved in `docs/`) with proper figure numbering
