# Progress Log

*Running log of project milestones, decisions, and key findings. Updated at the end of each significant work session — not every single step.*

---

## Setup — Environment & Repo

- Dev environment: Windows + WSL2 (Ubuntu 24.04) + Docker Desktop with WSL integration enabled
- Git and Python confirmed working in WSL; switched primary workflow from raw terminal to VS Code connected via WSL Remote extension
- GitHub repo created (`KingWhales/ai-credit-scoring-system`), authenticated via Personal Access Token (GitHub no longer supports password auth for git operations)
- Repo skeleton created: `backend/`, `ml-service/`, `frontend/`, `infra/`, `tests/`, `docs/`
- Home Credit Default Risk dataset (Kaggle) downloaded: `application_train.csv`, `application_test.csv`, `bureau.csv`, `bureau_balance.csv`, `installments_payments.csv`, `previous_application.csv`
- Python venv created in `ml-service/`; core packages installed (pandas, numpy, matplotlib, seaborn, jupyter, scikit-learn)
- **Decision**: local-first development approach — build and test everything on WSL/Docker before committing to a cloud provider, to avoid getting blocked on card/billing issues (AWS and Oracle both require a card even for free tier; no card currently available). Migration path kept simple by containerizing everything from the start.

---

## EDA & Data Cleaning

- Loaded `application_train.csv`: 307,511 rows × 122 columns
- **Target imbalance confirmed**: 91.9% no-default, 8.1% default (`TARGET`). Justifies using AUC-ROC, F1, and precision-recall as primary evaluation metrics instead of plain accuracy.
- **Missing data mapped**: 67 of 122 columns have missing values; 49 columns exceed 40% missing; 0 columns exceed 70% missing. Heaviest missingness concentrated in property/building-related columns (`COMMONAREA_*`, `NONLIVINGAPARTMENTS_*`, `LIVINGAPARTMENTS_*`, `FLOORSMIN_*`, `YEARS_BUILD_*`) — likely candidates to drop or heavily simplify.
- **Column types**: 65 float64, 41 int64, 16 categorical (object) — most features already numeric; only 16 columns need categorical encoding.
- **DAYS_EMPLOYED anomaly found and fixed**: placeholder value `365243` present in 18% of applicants (55,374 rows), confirmed via cross-tab to correspond almost entirely to Pensioners (55,352) and Unemployed (22) applicants — not random noise. Handled by:
  1. Creating a binary flag `IS_RETIRED_OR_UNEMPLOYED`
  2. Replacing the placeholder with `NaN` in the numeric column
  - **Gotcha encountered**: using `pd.NA` initially converted the column to `object` dtype, silently breaking downstream numeric calculations. Fixed using `pd.to_numeric(..., errors='coerce')` to force proper numeric dtype and convert unparseable values to `NaN`.
- **AMT_INCOME_TOTAL outlier investigated**: max value of 117,000,000 vs. 99th percentile of only 472,500 (~250x gap) — confirmed as a genuine data quality issue via a full tail of extreme values, not a single freak entry. Applied `np.log1p` log-transformation rather than simple capping, since credit scoring literature treats income effects on default risk as non-linear; log-transform compresses the distribution (std reduced from 237,123 to 0.489) without discarding data.
- **First behavioral feature prototype**: `INCOME_PER_EMPLOYED_YEAR` (income relative to employment tenure) as an initial income stability proxy.

---

## Behavioral Feature Engineering (Objective 3)

- Loaded `installments_payments.csv`: 13,605,401 rows (one row per installment payment across all applicants' loan history)
- Derived row-level signals:
  - `PAYMENT_DELAY_DAYS` = actual payment date − due date (positive = late, negative = early)
  - `PAYMENT_DIFF` = amount paid − amount due
- Aggregated to one row per applicant (`groupby('SK_ID_CURR')`) into six behavioral features:
  - `avg_payment_delay`, `std_payment_delay`, `pct_late_payments`
  - `avg_payment_diff`, `std_payment_amount`, `num_installments`
- Result: 339,587 applicants with computed behavioral features
- Merged into main applicant table via left join — row count preserved at 307,511 (confirmed no duplication)
- **5.2% of applicants (15,876) had no installment history** — likely genuinely thin-file/new applicants, i.e. exactly the population this project aims to serve better. Flagged via `NO_INSTALLMENT_HISTORY` binary column; behavioral features imputed to 0 for this group. Noted as an honest limitation: engineered behavioral features can't help applicants with zero prior loan history — traditional features (income, employment) still needed for this subgroup.

---

## Baseline Model Comparison (Objective 4)

- Built a `ColumnTransformer` preprocessing pipeline: median imputation + standard scaling for numeric features, constant imputation + one-hot encoding for categorical features (131 total input features → 261 after encoding)
- Train/test split: 80/20, stratified on `TARGET` to preserve class balance in both sets
- Trained and compared three algorithms, all with class imbalance handling enabled:

| Model | AUC-ROC | Default Recall | Default Precision |
|---|---|---|---|
| Logistic Regression (`class_weight='balanced'`) | 0.7526 | 0.68 | 0.16 |
| Random Forest (`class_weight='balanced'`) | 0.7406 | 0.05 | 0.44 |
| **XGBoost** (`scale_pos_weight`) | **0.7560** | 0.63 | 0.18 |

- **Key finding**: Random Forest achieved 92% overall accuracy but only 5% recall on the default class — despite looking strong on accuracy alone, it fails to catch the vast majority of actual defaulters, making it the weakest model for the actual use case. This is a concrete, evidenced example of why accuracy is a misleading metric for imbalanced classification problems, directly justifying the AUC-ROC/precision/recall metric choice made during EDA.
- **XGBoost selected as primary model** going forward — best AUC-ROC and a reasonable precision/recall balance.

---

## Explainable AI — SHAP Integration (Objective 5)

- Installed SHAP; resolved a NumPy/Numba version conflict (`numba` required NumPy ≤2.4, environment had 2.5.1) by pinning `numpy<2.5`
- Set up `shap.TreeExplainer` on the fitted XGBoost classifier (fast, exact method for tree-based models)
- Computed SHAP values on a 1,000-row sample of the test set (261 features post-encoding)
- Generated global feature importance summary plot. Key findings:
  - Top predictors are external credit bureau scores (`EXT_SOURCE_1/2/3`) and loan amount fields (`AMT_GOODS_PRICE`, `AMT_CREDIT`, `AMT_ANNUITY`) — consistent with domain expectations
  - **`pct_late_payments` (engineered behavioral feature) ranked 6th in global importance**, ahead of `DAYS_BIRTH` (age) and `DAYS_EMPLOYED` — direct evidence that the alternative behavioral feature engineering (Objective 3) contributes meaningfully to model predictions, not just as a token addition
  - `std_payment_amount` (engineered) also appeared in the top 10 features

---

## Next Steps

- [ ] Single-applicant SHAP explanations (force plot / waterfall) — the format an admin dashboard would realistically display
- [ ] Consider incorporating `bureau.csv` / `previous_application.csv` for additional behavioral signal (optional — current feature set already defensible for Objective 3)
- [ ] Light XGBoost hyperparameter tuning
- [ ] Save/serialize the final trained pipeline for use by `ml-service` API
- [ ] Refactor notebook logic into reusable `.py` modules ahead of Phase 2 (web application)
