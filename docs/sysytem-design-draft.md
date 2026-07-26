# System Design & Implementation (Draft)
*Living draft — covers the web application layer (Objective 1) built on top of the ML pipeline described in the Methodology chapter. Expand with architecture diagrams and screenshots before final submission.*

---

## 4.1 System Architecture

The system follows a three-service architecture, chosen to keep machine learning, application logic, and presentation concerns independently developable, testable, and — in line with Objective 8 — independently containerizable and deployable:

1. **`ml-service`** — a FastAPI application wrapping the trained XGBoost pipeline (Section 3.6–3.7). Exposes a single `/predict` endpoint accepting raw applicant fields and returning a default probability.
2. **`backend`** — a FastAPI application responsible for application lifecycle management: persisting applicant and application data, orchestrating calls to `ml-service`, and exposing endpoints for administrative review.
3. **`frontend`** — a React (Vite) single-page application providing two interfaces: an applicant-facing loan submission form, and an administrator dashboard.

Services communicate over HTTP rather than through shared code or a shared database connection from the frontend, so that in the eventual DevOps pipeline (Objective 8) each service can be built, tested, and deployed as an independent container.

```
[React Frontend] --HTTP--> [Backend API] --HTTP--> [ML Service API]
                                 |
                            [PostgreSQL]
```

## 4.2 Data Model

Four relational tables were designed to represent the loan lifecycle:

| Table | Purpose |
|---|---|
| `applicants` | Applicant identity/contact information |
| `applications` | A single loan request, including the financial and demographic fields used for prediction |
| `predictions` | The ML-generated default probability for a given application |
| `admin_reviews` | The administrative decision (approve/reject), reviewer, and notes |

This normalisation separates *who* applied, *what* they applied for, *what the model predicted*, and *what was decided* — allowing, for example, multiple applications to be tracked per applicant, and a full audit trail of predictions versus final human decisions to be retained (relevant to the transparency goals underpinning Objective 5).

## 4.3 ML Service Integration

A key design decision was how the `backend` should obtain predictions. Two approaches were considered: importing the trained model directly into the backend process, or calling a separate ML inference service over HTTP. The latter was chosen, for two reasons:

1. It mirrors realistic production architecture for ML systems, where model-serving infrastructure is commonly decoupled from application logic (allowing independent scaling, versioning, and redeployment of the model without redeploying the whole application).
2. It aligns directly with the project's DevOps objective — two services with different technology profiles (an ML-heavy service versus a general application service) benefit from separate containers, separate CI build steps, and potentially separate scaling policies.

At inference time, the `ml-service` reconstructs the same feature engineering steps applied during training (Section 3.2–3.3) — including the DAYS_EMPLOYED anomaly correction and behavioural feature defaulting for applicants with no prior payment history — ensuring the model receives input in a format consistent with what it was trained on, regardless of whether that input originates from the training pipeline or a live API request.

## 4.4 A Notable Integration Defect

During end-to-end testing, an integration defect was identified in which every submitted application received an identical predicted default probability, irrespective of the applicant's actual data. Root-cause analysis traced this to a naming convention mismatch: the backend's data model uses lowercase field names (matching its database schema), while the ML service's input schema uses uppercase field names (matching the original training dataset's column naming). Because the underlying validation library (Pydantic) silently discards unrecognised fields rather than raising an error, every field sent by the backend was effectively dropped, and every applicant was scored against empty input.

This defect is discussed here deliberately, rather than omitted, for two reasons. First, it illustrates a genuine and non-obvious failure mode in multi-service systems: both services returned successful HTTP responses throughout, and the defect was only detectable by comparing model outputs across meaningfully different inputs — a straightforward "does it return 200 OK" test would not have caught it. Second, resolving it (via an explicit field-mapping layer in the inter-service client) is a concrete, reusable pattern worth documenting for the DevOps/testing chapter: **schema consistency between independently-developed services cannot be assumed and should be validated automatically**, a consideration that will inform the design of integration tests in the CI pipeline (Objective 8).

## 4.5 Frontend

The frontend was built with React (via Vite) rather than server-rendered templates, prioritising a more contemporary development experience and portfolio presentation. Two views were implemented:

- **Application form**: collects applicant identity and financial/demographic fields, submits to the backend, and displays the returned risk prediction immediately upon submission.
- **Admin dashboard**: lists all submitted applications with a colour-coded risk indicator (derived from the predicted default probability) and provides inline approve/reject actions with an optional notes field.

**Environment note**: development required upgrading from Node.js 18 to Node.js 20, as the current Vite scaffolding tool depends on a Node.js standard library feature (`node:util`'s `styleText`) introduced after Node 18. This is recorded as a reproducibility note for anyone rebuilding the environment from scratch.

---

## Notes for later revision
- Add a proper architecture diagram (services, ports, data flow)
- Add dashboard and form screenshots
- Expand Section 4.4 once integration tests are added to the CI pipeline, cross-referencing the specific test that would have caught this defect
- Add authentication/authorization discussion once implemented
- Cross-reference Section 3.7 (SHAP) once explanations are surfaced in the dashboard UI
