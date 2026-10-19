# Master's Thesis — Introduction

**Working thesis title:** Development of an AI-Powered Credit Scoring and Loan Management System Based on Alternative Behavioural Data, Explainable Machine Learning and DevOps Practices

**Programme:** Master's in Modern Software Development, Southern Federal University

**Author:** Afosi Muideen Olawale

## Contents

- [Research relevance](#research-relevance-актуальность-исследования)
- [What has already been done](#what-has-already-been-done-степень-изученности-проблемы)
- [Research objective](#research-objective-цель-исследования)
- [Research tasks](#research-tasks-задачи-исследования)
- [Research object](#research-object-объект-исследования)
- [Research subject](#research-subject-предмет-исследования)
- [Research hypothesis](#research-hypothesis-гипотеза-исследования)
- [Research methodology](#research-methodology-методология-исследования)
- [Scientific novelty](#scientific-novelty-научная-новизна)
- [Theoretical significance](#theoretical-significance-теоретическая-значимость)
- [Practical significance](#practical-significance-практическая-значимость)
- [Results validation](#results-validation-апробация-результатов)
- [Publications on the research topic](#publications-on-the-research-topic-публикации-по-теме-исследования)
- [Structure of the thesis](#structure-of-the-thesis)
- [References](#references)

## Research relevance (Актуальность исследования)

Credit is one of the main channels through which households and small businesses invest, smooth consumption and absorb financial shocks. The decision to grant or refuse a loan therefore has direct economic and social consequences, both for the borrower and for the lender, whose solvency depends on the quality of its loan portfolio. Credit scoring — the quantitative estimation of the probability that a borrower will default — sits at the centre of this decision and has become one of the most widespread applications of statistical modelling and machine learning in industry.

The relevance of the topic is determined by several converging trends.

First, a large share of the world's population remains outside traditional credit assessment. According to the World Bank's Global Findex 2025 report, based on surveys of about 145,000 adults in 141 economies conducted in 2024, roughly 1.3 billion adults still have no account at a financial institution or mobile money provider, and borrowing, insurance and pensions lag behind account ownership. Many more people hold accounts but have a "thin" or non-existent credit file. Classical scorecards built on bureau history cannot assess such applicants reliably, so they are either rejected or priced as high risk. Methods that extract predictive signals from alternative and behavioural data — for example, how consistently a person repays instalments — are therefore of direct practical and social value.

Second, the quality of credit risk prediction affects lender stability. Loan default data are strongly imbalanced: defaulters typically form a small minority of applicants. Under such imbalance, a model can achieve high overall accuracy while failing to identify most actual defaulters. Choosing appropriate algorithms and evaluation metrics (AUC-ROC, recall on the default class, precision–recall trade-offs) is not a technical detail but a condition for financially sound decisions.

Third, the shift from transparent statistical scorecards to complex ensemble models such as Random Forest and gradient boosting has created an explainability problem. These models are often more accurate than logistic regression, but their internal logic is opaque to loan officers, applicants and supervisors. At the same time, regulation is moving towards mandatory transparency. The EU Artificial Intelligence Act (Regulation (EU) 2024/1689) classifies AI systems used to evaluate the creditworthiness of natural persons as high-risk, requiring transparency, human oversight and documentation. The GDPR (Article 22) restricts purely automated decisions with significant effects on individuals. In the Russian Federation, the National Strategy for the Development of Artificial Intelligence (Presidential Decree No. 490 of 10 October 2019, as amended in 2024) emphasises the trustworthy and safe use of AI in the economy. A credit model that cannot explain its decisions is increasingly difficult to deploy.

Fourth, most research on machine-learning credit scoring stops at the level of an experimental model in a notebook. In practice, a model creates value only when it is integrated into a working information system: an application that collects borrower data, calls the model, stores the decision and its explanation, and allows administrators to manage loans. Such a system must also be built, tested, deployed and monitored reliably. Industry studies of machine-learning systems show that the model code is only a small fraction of a production ML system, and that most of the engineering effort and technical risk lie in data pipelines, integration, deployment and monitoring. The discipline that addresses this — DevOps and its ML-specific extension, MLOps — is still rarely treated as part of credit scoring research.

The main difficulties that hinder a solution are therefore: (1) the scarcity of informative features for applicants with limited credit history; (2) severe class imbalance and anomalous, incomplete records in real credit data; (3) the trade-off between predictive accuracy and interpretability; and (4) the gap between an experimental model and a reliable, maintainable software system.

Addressing these difficulties within one integrated solution matters for the development of the field. It shows how alternative behavioural features, multi-algorithm comparison and explainable AI can be combined in a system that is not only accurate but also transparent, auditable and deployable with modern software engineering practices. This is consistent with the aims of the Modern Software Development programme, which treats software as a product that must be engineered across its whole life cycle, from requirements to operation.

## What has already been done (Степень изученности проблемы)

Credit scoring is a mature research field, but the literature has developed along four largely separate lines: statistical scoring, machine-learning scoring, alternative data, and explainability. Engineering and operation of scoring systems form a fifth, much less studied line.

**Statistical foundations.** The quantitative approach to credit risk goes back to D. Durand [1], who applied discriminant analysis to consumer instalment loans, and to E. Altman [2], whose Z-score model predicted corporate bankruptcy from financial ratios. L. Thomas, D. Edelman and J. Crook [3] systematised the theory and practice of application and behavioural scorecards, and D. Hand and W. Henley [4] reviewed statistical classification methods in consumer credit. Logistic regression became the industry standard because it is stable, well understood and easy to explain to regulators.

**Machine-learning scoring.** B. Baesens and co-authors [5] carried out one of the first large benchmarks of classification algorithms for credit scoring. S. Lessmann, B. Baesens, H.-V. Seow and L. Thomas [6] updated this benchmark with 41 classifiers on several data sets and concluded that ensemble methods, particularly heterogeneous ensembles and random forests, generally outperform logistic regression. The ensemble techniques themselves were developed by L. Breiman (Random Forest) [7] and by T. Chen and C. Guestrin (XGBoost) [8], whose gradient boosting implementation has become a de facto standard for tabular data. E. Dumitrescu and co-authors [9] showed that logistic regression enriched with non-linear tree-based effects can narrow the gap with ensembles while keeping interpretability.

**Class imbalance.** I. Brown and C. Mues [10] compared classifiers on imbalanced credit data sets and showed that performance differences grow as the share of defaulters falls. N. Chawla and co-authors proposed SMOTE oversampling [11]; class weighting and threshold tuning are common alternatives. This line established that accuracy is a misleading metric for default prediction and that AUC-ROC and minority-class recall must be reported.

**Alternative and behavioural data.** M. Óskarsdóttir, C. Bravo and co-authors [12] demonstrated that mobile phone usage and social network data improve scoring and can support financial inclusion. T. Berg, V. Burg, A. Gombović and M. Puri [13] showed that simple digital footprints carry predictive power comparable to bureau scores. The public Home Credit Default Risk data set [14] made rich alternative data, including instalment payment histories, available for open research, and was used in a large number of competition solutions. However, most of this work treats features as inputs to maximise leaderboard scores, without analysing their behavioural meaning or their contribution to individual decisions.

**Explainable AI.** M. Ribeiro, S. Singh and C. Guestrin introduced LIME [15], and S. Lundberg and S.-I. Lee proposed SHAP, a unified approach based on Shapley values from cooperative game theory [16]. Lundberg and co-authors later developed TreeSHAP, an exact and fast algorithm for tree ensembles [17]. N. Bussmann, P. Giudici and co-authors [18] applied SHAP to credit risk in peer-to-peer lending and showed that explanations can group borrowers by similar risk drivers. These results make it possible to use accurate ensembles while still explaining each decision.

**Engineering and operation of ML systems.** D. Sculley and co-authors [19] described the "hidden technical debt" of ML systems, showing that model code is a small part of a production system. D. Kreuzberger, N. Kühl and S. Hirschl [20] defined MLOps and its reference architecture, and G. Kim, J. Humble and co-authors [21] codified DevOps practices of continuous integration, delivery and monitoring.

**Gaps in existing research.** The review shows several unexplored or weakly explored aspects:

1. Most credit scoring studies end with an offline model evaluation; few describe a complete, working loan management system in which the model, its explanations and the business process are integrated.
2. Alternative behavioural features are usually engineered for accuracy alone; their interpretability for loan officers and applicants is rarely examined together with SHAP explanations.
3. Explainability is mostly analysed at the global level (feature importance plots); delivery of per-applicant explanations through an application interface is seldom addressed.
4. DevOps and MLOps literature is largely domain-agnostic, while credit scoring literature rarely considers CI/CD, containerisation and monitoring. Practical integration defects — for example, silent data loss at service boundaries — are almost never documented.

This thesis addresses these gaps by combining behavioural feature engineering, comparative modelling, SHAP-based explanation and a DevOps-oriented software architecture in one system.

## Research objective (Цель исследования)

The objective of this research is **to develop and evaluate an AI-powered credit scoring and loan management system** that predicts the probability of borrower default using alternative behavioural features, explains each prediction to its users, and is engineered and delivered with DevOps practices.

## Research tasks (Задачи исследования)

To achieve this objective, the following tasks are solved. Each task corresponds to a chapter or section of the thesis.

1. **To analyse the theoretical foundations** of credit scoring, machine-learning classification under class imbalance, explainable AI and DevOps/MLOps practices (Chapter 1). This task is necessary to justify the choice of methods and to locate the gaps that the thesis addresses.
2. **To explore and prepare the Home Credit Default Risk data** and to engineer alternative behavioural features from instalment payment histories (Chapter 2). This task is necessary because raw credit data contain anomalies, outliers and missing values, and because applicants with limited credit history can only be assessed through additional behavioural signals.
3. **To build and compare predictive models** — Logistic Regression, Random Forest and XGBoost — using metrics suited to imbalanced data, and to select the primary model (Chapter 2). This task is necessary because model choice determines both the financial quality of decisions and the feasibility of explanation.
4. **To integrate SHAP-based explanations** into the model service so that every prediction is returned with its most influential factors and their direction of effect (Chapters 2–3). This task is necessary to make decisions transparent for loan officers, applicants and supervisors.
5. **To design and implement the loan management system** — a web platform with a database, a backend API, a separate ML service, a user interface and administrative tools (Chapter 3). This task is necessary because a model only creates value when embedded in a working business process.
6. **To design and implement a DevOps pipeline** for continuous integration, containerised deployment and monitoring of the system, and to evaluate the system as a whole (Chapter 4). This task is necessary to show that the solution is reproducible, maintainable and fit for operation, not only for experimentation.

## Research object (Объект исследования)

The object of the research is **the process of assessing the creditworthiness of individual borrowers and making lending decisions** in consumer lending.

This process generates the problem situation: the lender must decide under uncertainty, with incomplete and imbalanced information, and must be able to justify the decision. The boundaries of the object are set as follows. The research covers retail (consumer) loans to individuals, from the submission of an application to the scoring decision and its administration. It does not cover corporate lending, collateral valuation, loan pricing, collection of overdue debts or macro-prudential portfolio risk.

This object was chosen because consumer creditworthiness assessment is high-volume, data-rich and directly affects access to finance, and because it is the area where regulators now explicitly require automated decisions to be transparent.

## Research subject (Предмет исследования)

The subject of the research is **the methods, models and software architecture for machine-learning prediction of borrower default probability with explainable outputs, delivered as an integrated, continuously deployed information system**.

Within the object, the thesis directly examines:

- the relationship between alternative behavioural features derived from instalment payment history and the probability of default;
- the comparative predictive quality of Logistic Regression, Random Forest and XGBoost under a class imbalance of roughly 91% non-defaulters to 9% defaulters;
- the relationship between model inputs and individual predictions, as quantified by SHAP values;
- the interaction between system components — database, backend API, ML service and user interface — and the data contracts between them;
- the processes of building, testing, deploying and monitoring the system.

This subject was selected because the gaps identified in the literature lie precisely at the junction of these elements: accuracy, explanation and engineering are usually studied separately, while the research objective requires them to work together.

## Research hypothesis (Гипотеза исследования)

The research proceeds from the hypothesis that a gradient-boosted ensemble model trained on application data enriched with behavioural features from instalment repayment history achieves higher discriminative ability (AUC-ROC) and better recall of the default class than logistic regression and random forest on the same data. It is further assumed that SHAP explanations of this model identify behavioural repayment indicators, in particular the share of late payments, among the leading drivers of predicted risk. Finally, it is assumed that integrating the model and its explanations into a containerised, service-oriented system with an automated CI/CD pipeline makes scoring decisions reproducible and transparent without reducing predictive quality.

The key variables are: the feature set (with and without behavioural features), the algorithm, the discriminative quality metrics (AUC-ROC, recall, precision, F1), the SHAP contribution of each feature, and the reproducibility of system builds and deployments.

## Research methodology (Методология исследования)

The research combines general scientific methods with specific methods of data science and software engineering.

**General scientific methods:** analysis and synthesis of scientific literature, regulatory documents and industry practice; comparison and generalisation of existing approaches; abstraction and modelling of the lending process; experiment as the main method of testing the hypothesis.

**Theoretical approaches:** statistical learning theory and the theory of classification under class imbalance; ensemble learning (bagging and gradient boosting); cooperative game theory as the basis of Shapley-value explanations; systems analysis and service-oriented architecture; the DevOps and MLOps life-cycle models of continuous integration, delivery and monitoring.

**Empirical methods:**

- exploratory data analysis (EDA) of the Home Credit Default Risk data set, including detection of anomalies (such as the placeholder value in the employment duration field, which affects mostly pensioners) and treatment of extreme income outliers by logarithmic transformation;
- feature engineering of six behavioural indicators aggregated from instalment payment records;
- supervised classification with Logistic Regression, Random Forest and XGBoost, with stratified validation and metrics suited to imbalanced data (AUC-ROC, recall, precision, F1, confusion matrices);
- model explanation with SHAP TreeExplainer at global (feature importance) and local (per-applicant) levels;
- software design and prototyping: relational data modelling (PostgreSQL, SQLAlchemy), REST API development (FastAPI), a separate ML inference service, a React/Vite client;
- integration testing and defect analysis of service boundaries;
- DevOps engineering: containerisation (Docker), CI/CD (Jenkins) and monitoring (Prometheus, Grafana);
- system evaluation against functional and non-functional requirements.

The research tools are Python, scikit-learn, XGBoost, SHAP, pandas, FastAPI, SQLAlchemy, PostgreSQL, React, Docker, Jenkins, Prometheus, Grafana and Git/GitHub.

## Scientific novelty (Научная новизна)

The scientific novelty of the research lies in the following results obtained by the author:

1. **An integrated architecture** of a credit scoring and loan management system is proposed in which the predictive model, its per-applicant SHAP explanations and the lending business process are linked through separated services and explicit data contracts. Unlike most studies, which end with an offline model, the thesis treats explanation as a stored and displayed part of each lending decision.
2. **A set of six interpretable behavioural features** derived from instalment repayment history is developed and its contribution to default risk is quantified with SHAP. It is shown that repayment behaviour, in particular the share of late payments, ranks among the leading global risk factors, supporting the use of such features for applicants with limited bureau history.
3. **A comparative evaluation** of Logistic Regression, Random Forest and XGBoost under strong class imbalance is carried out, demonstrating that a model with high overall accuracy can fail to identify defaulters, and justifying AUC-ROC and default-class recall as primary selection criteria.
4. **A DevOps/MLOps delivery model** for an explainable credit scoring system is designed, including a CI/CD pipeline, containerised deployment and monitoring, and a documented class of integration defects — silent discarding of fields at the API validation layer caused by naming mismatches — together with a method of preventing it through explicit field mapping.

## Theoretical significance (Теоретическая значимость)

The theoretical significance of the research is that it extends the concept of credit scoring from a model-centred to a system-centred view, in which predictive quality, explainability and operational reliability are treated as interdependent properties of one information system.

The results supplement existing theory in three ways. They add evidence on the predictive and explanatory value of behavioural repayment features. They refine the understanding of how evaluation metrics should be chosen for imbalanced credit data. They bring DevOps and MLOps concepts into the domain of credit risk modelling and describe failure modes at service boundaries that are absent from the scoring literature.

The findings can be used in further research on fairness and bias in credit models, on monitoring of model drift in production, on the use of other alternative data sources, and on methods of presenting explanations to non-expert users.

## Practical significance (Практическая значимость)

The practical significance lies in a working software prototype and reusable engineering artefacts that can be applied directly.

The target audience includes:

- **microfinance organisations, credit cooperatives and digital lenders**, which need affordable, transparent scoring for applicants with thin credit files;
- **risk analysts and loan officers**, who receive not only a default probability but also the top factors behind it and their direction of effect;
- **compliance and audit specialists**, for whom stored explanations support documentation and review requirements for high-risk AI systems;
- **software and DevOps engineers**, who can reuse the modular ML pipeline (data loading, feature engineering, preprocessing, training, prediction), the service architecture and the CI/CD and monitoring design;
- **universities**, where the system and its documentation can serve as teaching material for courses on machine learning, software engineering and DevOps.

Examples of application include automated pre-screening of loan applications, decision support with explanations for manual review, and a reference implementation for organisations moving credit models from experimental notebooks into production.

## Results validation (Апробация результатов)

The software prototype was validated in a local deployment environment (Docker on WSL2 Ubuntu), where the ML service, backend API and web client were integrated and tested end to end. The source code and project documentation are maintained on GitHub ([github.com/KingWhales](https://github.com/KingWhales)).

The results of the research are being prepared for presentation at the department and at scientific conferences.

## Publications on the research topic (Публикации по теме исследования)

At the time of writing, the results of the research are being prepared for publication.

## Structure of the thesis

The thesis consists of an introduction, four chapters, a conclusion, a list of references and appendices. Chapter 1 presents the theoretical foundations of credit scoring, machine learning under class imbalance, explainable AI and DevOps/MLOps. Chapter 2 describes the data, behavioural feature engineering, model comparison and SHAP analysis. Chapter 3 presents the design and implementation of the loan management system. Chapter 4 describes the DevOps pipeline and the evaluation of the system. The conclusion summarises the results and outlines directions for further research.

## References

1. Durand D. Risk Elements in Consumer Instalment Financing. — New York: National Bureau of Economic Research, 1941.
2. Altman E. I. Financial ratios, discriminant analysis and the prediction of corporate bankruptcy // The Journal of Finance. — 1968. — Vol. 23, No. 4. — P. 589–609.
3. Thomas L. C., Edelman D. B., Crook J. N. Credit Scoring and Its Applications. — Philadelphia: SIAM, 2002.
4. Hand D. J., Henley W. E. Statistical classification methods in consumer credit scoring: a review // Journal of the Royal Statistical Society: Series A. — 1997. — Vol. 160, No. 3. — P. 523–541.
5. Baesens B., Van Gestel T., Viaene S., Stepanova M., Suykens J., Vanthienen J. Benchmarking state-of-the-art classification algorithms for credit scoring // Journal of the Operational Research Society. — 2003. — Vol. 54, No. 6. — P. 627–635.
6. Lessmann S., Baesens B., Seow H.-V., Thomas L. C. Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research // European Journal of Operational Research. — 2015. — Vol. 247, No. 1. — P. 124–136.
7. Breiman L. Random Forests // Machine Learning. — 2001. — Vol. 45, No. 1. — P. 5–32.
8. Chen T., Guestrin C. XGBoost: A scalable tree boosting system // Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. — 2016. — P. 785–794.
9. Dumitrescu E., Hué S., Hurlin C., Tokpavi S. Machine learning for credit scoring: Improving logistic regression with non-linear decision-tree effects // European Journal of Operational Research. — 2022. — Vol. 297, No. 3. — P. 1178–1192.
10. Brown I., Mues C. An experimental comparison of classification algorithms for imbalanced credit scoring data sets // Expert Systems with Applications. — 2012. — Vol. 39, No. 3. — P. 3446–3453.
11. Chawla N. V., Bowyer K. W., Hall L. O., Kegelmeyer W. P. SMOTE: Synthetic Minority Over-sampling Technique // Journal of Artificial Intelligence Research. — 2002. — Vol. 16. — P. 321–357.
12. Óskarsdóttir M., Bravo C., Sarraute C., Vanthienen J., Baesens B. The value of big data for credit scoring: Enhancing financial inclusion using mobile phone data and social network analytics // Applied Soft Computing. — 2019. — Vol. 74. — P. 26–39.
13. Berg T., Burg V., Gombović A., Puri M. On the rise of FinTechs: Credit scoring using digital footprints // The Review of Financial Studies. — 2020. — Vol. 33, No. 7. — P. 2845–2897.
14. Home Credit Default Risk [Data set] // Kaggle. — 2018. — URL: [kaggle.com/c/home-credit-default-risk](https://www.kaggle.com/c/home-credit-default-risk)
15. Ribeiro M. T., Singh S., Guestrin C. "Why should I trust you?": Explaining the predictions of any classifier // Proceedings of the 22nd ACM SIGKDD Conference. — 2016. — P. 1135–1144.
16. Lundberg S. M., Lee S.-I. A unified approach to interpreting model predictions // Advances in Neural Information Processing Systems 30 (NeurIPS). — 2017. — P. 4765–4774.
17. Lundberg S. M., Erion G., Chen H. et al. From local explanations to global understanding with explainable AI for trees // Nature Machine Intelligence. — 2020. — Vol. 2. — P. 56–67.
18. Bussmann N., Giudici P., Marinelli D., Papenbrock J. Explainable machine learning in credit risk management // Computational Economics. — 2021. — Vol. 57. — P. 203–216.
19. Sculley D., Holt G., Golovin D. et al. Hidden technical debt in machine learning systems // Advances in Neural Information Processing Systems 28 (NeurIPS). — 2015. — P. 2503–2511.
20. Kreuzberger D., Kühl N., Hirschl S. Machine Learning Operations (MLOps): Overview, definition, and architecture // IEEE Access. — 2023. — Vol. 11. — P. 31866–31879.
21. Kim G., Humble J., Debois P., Willis J. The DevOps Handbook. — Portland: IT Revolution Press, 2016.
22. World Bank. The Global Findex Database 2025: Connectivity and Financial Inclusion in the Digital Economy. — Washington, DC, 2025. — URL: [openknowledge.worldbank.org](https://openknowledge.worldbank.org/entities/publication/8b9002b6-d8dd-426c-aa7c-6d7d16902cd7)
23. Regulation (EU) 2024/1689 of the European Parliament and of the Council laying down harmonised rules on artificial intelligence (Artificial Intelligence Act). — URL: [eur-lex.europa.eu](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
24. Decree of the President of the Russian Federation No. 490 of 10.10.2019 "On the Development of Artificial Intelligence in the Russian Federation" (as amended).
