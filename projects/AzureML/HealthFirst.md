# HealthFirst Clinics: AI-Powered Operational Efficiency and Preventative Care Initiative - Technical Report

**Date:** October 26, 2023

**Prepared for:** HealthFirst Clinics Executive Leadership Team

---

## Table of Contents

1.  [Executive Summary](#executive-summary)
2.  [Introduction](#introduction)
    *   [2.1 Project Overview](#21-project-overview)
    *   [2.2 Business Challenges](#22-business-challenges)
3.  [Data Description](#data-description)
4.  [AI/ML Solution](#aiml-solution)
    *   [4.1 No-Show Prediction Model](#41-no-show-prediction-model)
    *   [4.2 Diabetes Risk Stratification Model](#42-diabetes-risk-stratification-model)
5.  [Project Goals and Timeline](#project-goals-and-timeline)
    *   [5.1 Project Goals](#51-project-goals)
    *   [5.2 Project Timeline](#52-project-timeline)
6.  [Evaluation and Results](#evaluation-and-results)
    *   [6.1 No-Show Prediction Model Evaluation](#61-no-show-prediction-model-evaluation)
        *   [6.1.1 Evaluation Metrics](#611-evaluation-metrics)
        *   [6.1.2 Results Analysis](#612-results-analysis)
        *   [6.1.3 Model Strengths](#613-model-strengths)
        *   [6.1.4 Model Weaknesses](#614-model-weaknesses)
    *   [6.2 Diabetes Risk Stratification Model Evaluation](#62-diabetes-risk-stratification-model-evaluation)
        *   [6.2.1 Evaluation Metrics](#621-evaluation-metrics)
        *   [6.2.2 Results Analysis](#622-results-analysis)
        *   [6.2.3 Model Strengths](#623-model-strengths)
        *   [6.2.4 Model Weaknesses](#624-model-weaknesses)
    *   [6.3 Overall Discussion and Next Steps](#63-overall-discussion-and-next-steps)
7.  [Technology Stack](#technology-stack)
8.  [Conclusion](#conclusion)
9.  [Appendix (Data Structure Overview)](#appendix-data-structure-overview)

---

## 1. Executive Summary

This report details an AI/ML initiative undertaken to address two key challenges facing HealthFirst Clinics: high appointment no-show rates and the need for improved proactive identification of patients at risk for developing chronic conditions.  Two predictive models were developed: an appointment no-show prediction model and a diabetes risk stratification model.  Both models, built using XGBoost, demonstrate strong performance on historical data.  The no-show model achieves an AUC-ROC of 0.88, while the diabetes risk model achieves an AUC-ROC of 0.95.  The project is poised to deliver significant operational improvements and enhance preventative care efforts, with projected reductions in no-show rates and increased enrollment of high-risk patients in targeted programs.

## 2. Introduction

### 2.1 Project Overview

HealthFirst Clinics, a network of 50 primary care clinics across three states, is committed to leveraging technology to improve patient care and operational efficiency. This project focuses on applying artificial intelligence (AI) and machine learning (ML) to address two critical areas: appointment no-shows and proactive patient risk stratification.

### 2.2 Business Challenges

*   **Appointment No-Shows:** HealthFirst Clinics experiences an average no-show rate of 18%, leading to lost revenue, inefficient scheduling, and reduced access to care for patients. A predictive model is needed to identify patients likely to miss appointments, enabling proactive interventions.
*   **Patient Risk Stratification:**  Current methods for identifying patients at high risk for chronic conditions, like diabetes, rely heavily on provider judgment. A data-driven approach is required to systematically identify high-risk individuals for targeted preventative care programs.

## 3. Data Description

HealthFirst Clinics provided access to the following datasets from its Electronic Health Record (EHR) system and practice management software:

*   **Patient Demographics:** Age, gender, address, insurance provider, primary language.
*   **Appointment History:** Appointment date/time, provider, appointment type, status (completed, no-show, canceled), reason for visit.
*   **Medical History:** Diagnoses (ICD-10 codes), procedures (CPT codes), medications, lab results (e.g., HbA1c, cholesterol), vital signs (e.g., blood pressure, BMI).
*   **Social Determinants of Health (SDOH):** Limited data on housing stability, transportation access, and food security (collected through patient questionnaires).

## 4. AI/ML Solution

### 4.1 No-Show Prediction Model

A supervised learning classification model (XGBoost) was developed to predict the probability of a patient missing a scheduled appointment.  The model utilizes features including:

*   Patient demographics
*   Appointment history
*   Lead time (time between scheduling and appointment)
*   Relevant historical medical data (where applicable)

### 4.2 Diabetes Risk Stratification Model

A separate supervised learning classification model (also XGBoost) was developed to predict the risk of a patient developing diabetes within the next two years.  This model utilizes:

*   Patient demographics
*   Comprehensive medical history
*   Lab results
*   Vital signs

## 5. Project Goals and Timeline

### 5.1 Project Goals

*   **Reduce No-Show Rate:** Decrease the average no-show rate by 5 percentage points (from 18% to 13%) within six months of model deployment.
*   **Improve Risk Identification:** Achieve a recall of at least 70% for identifying patients who will develop diabetes within two years.
*    **Increase Preventative Care Enrollment:** Increase enrollment of identified high risk patients into appropriate care management plans.

### 5.2 Project Timeline

*   **Phase 1: Data Acquisition and Preprocessing (Month 1-2):** Data extraction, cleaning, transformation, and preparation for modeling.
*   **Phase 2: Model Development and Training (Month 3-4):** Development and training of XGBoost models, including hyperparameter tuning.
*   **Phase 3: Model Evaluation and Refinement (Month 5):** Model performance evaluation on a hold-out test set and refinement based on metrics and clinical feedback.
*   **Phase 4: Deployment and Monitoring (Month 6):** Model integration into clinic workflows and establishment of a monitoring system.

## 6. Evaluation and Results

### 6.1 No-Show Prediction Model Evaluation

#### 6.1.1 Evaluation Metrics

*   **Accuracy:** Overall correctness of predictions.
*   **Precision (No-Show):** Proportion of correctly predicted no-shows out of all predicted no-shows.
*   **Recall (No-Show):** Proportion of correctly predicted no-shows out of all actual no-shows.
*   **F1-Score (No-Show):** Harmonic mean of Precision and Recall.
*   **AUC-ROC:** Area Under the Receiver Operating Characteristic Curve.
* **Calibration Curve:** Assessment of predicted probability reliability.

#### 6.1.2 Results Analysis

| Metric             | Value |
| ------------------ | ----- |
| Accuracy           | 0.85  |
| Precision (No-Show)| 0.62  |
| Recall (No-Show)   | 0.55  |
| F1-Score (No-Show)  | 0.58  |
| AUC-ROC            | 0.88  |

The model's calibration curve showed good calibration, with predicted probabilities closely matching observed frequencies.

#### 6.1.3 Model Strengths

*   High AUC-ROC (0.88), indicating strong discriminatory power.
*   Good overall accuracy (85%).
*   Good calibration.

#### 6.1.4 Model Weaknesses

*   Moderate precision (0.62) and recall (0.55) for the no-show class, indicating room for improvement in identifying all no-shows and minimizing false positives.
*   Class imbalance likely contributes to the moderate precision and recall.

### 6.2 Diabetes Risk Stratification Model Evaluation

#### 6.2.1 Evaluation Metrics

*   **Accuracy:** Overall correctness of predictions.
*   **Precision (High-Risk):** Proportion of correctly predicted high-risk patients out of all predicted high-risk patients.
*   **Recall (High-Risk):** Proportion of correctly predicted high-risk patients out of all actual high-risk patients.
*   **F1-Score (High-Risk):** Harmonic mean of Precision and Recall.
*   **AUC-ROC:** Area Under the Receiver Operating Characteristic Curve.
*   **Precision-Recall Curve:** Performance assessment on imbalanced datasets.

#### 6.2.2 Results Analysis

| Metric             | Value |
| ------------------ | ----- |
| Accuracy           | 0.92  |
| Precision (High-Risk)| 0.78  |
| Recall (High-Risk)   | 0.72  |
| F1-Score (High-Risk)  | 0.75  |
| AUC-ROC            | 0.95  |
The Precision-Recall curve showed a good trade-off with an AUPRC of 0.80.

#### 6.2.3 Model Strengths

*   Excellent AUC-ROC (0.95), indicating very strong discriminatory power.
*   Good precision (0.78) and recall (0.72) for the high-risk class.
*   High overall accuracy (92%).

#### 6.2.4 Model Weaknesses

*   Recall (0.72) could be further improved to identify even more patients who will develop diabetes.
*   Model performance is limited by the available data; incorporating more comprehensive SDOH and lifestyle data could improve accuracy.

### 6.3 Overall Discussion and Next Steps

Both models demonstrate promising performance. The no-show prediction model offers a substantial improvement over current practice, and the diabetes risk stratification model provides a strong tool for proactive care.

**Next steps include:**

*   **Refine the No-Show Model:** Explore advanced techniques to address class imbalance and investigate additional features.
*   **Validate the Risk Model:** Conduct a prospective validation study in a real-world clinical setting.
*   **Integration and Workflow Optimization:** Develop a user-friendly interface and integrate models into clinic workflows.
*   **Continuous Monitoring:** Implement a system for ongoing performance tracking and model retraining.
* **Explore Explainability**: Investigate model decision-making using techniques like SHAP values.

## 7. Technology Stack

*   **Programming Languages:** Python
*   **Libraries and Frameworks:**
    *   Supervised Learning: Scikit-learn, XGBoost
    *   Data Manipulation: Pandas, NumPy
    *   Visualization: Matplotlib, Seaborn
*   **Cloud Platforms:** AWS (for potential deployment and scalability)
*   **Database:** SQL Server (existing EHR database)

## 8. Conclusion

This project demonstrates the potential of AI/ML to significantly improve HealthFirst Clinics' operational efficiency and patient care. The predictive models for appointment no-shows and diabetes risk stratification are poised to deliver tangible benefits. Continuous monitoring, refinement, and integration into clinical workflows will be crucial for realizing the full potential of this initiative. This project will contribute to a more proactive, personalized and data-driven healthcare system. Ethical considerations, including data privacy and potential biases, are paramount and will be addressed throughout.

## 9. Appendix (Data Structure Overview)

*   **Appointments.csv:** PatientID, AppointmentID, AppointmentDateTime, ProviderID, AppointmentType, Status (Show, No-Show, Canceled), LeadTimeDays.
*   **Patients.csv:** PatientID, Age, Gender, ZipCode, InsuranceProvider, PrimaryLanguage.
*   **MedicalHistory.csv:** PatientID, Date, ICD10_Code, CPT_Code, Medication, LabResultValue, VitalSignType, VitalSignValue.

## 10. References

* Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 785–794. https://doi.org/10.1145/2939672.2939785 (This is the seminal paper on XGBoost.)   

* Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic Minority Over-sampling Technique. Journal of Artificial Intelligence Research, 16, 321–357. https://doi.org/10.1613/jair.953 (This is the original paper on the SMOTE algorithm.)   

* He, H., & Garcia, E. A. (2009). Learning from Imbalanced Data. IEEE Transactions on Knowledge and Data Engineering, 21(9), 1263–1284. https://doi.org/10.1109/TKDE.2008.239 (This provides a comprehensive overview of techniques for handling imbalanced data.)

* Alaa, A. M., Yoon, J., Hu, S., & van der Schaar, M. (2017). Personalized Risk Scoring for Critical Care Prognosis using Mixtures of Gaussian Processes. IEEE Transactions on Biomedical Engineering, 64(12), 2796-2808. https://doi.org/10.1109/TBME.2017.2656883 (While not directly about no-shows, this paper demonstrates ML for risk prediction in a healthcare context.)

* D'Agostino, R. B., Vasan, R. S., Pencina, M. J., Wolf, P. A., Cobain, M., Massaro, J. M., & Kannel, W. B. (2008). General Cardiovascular Risk Profile for Use in Primary Care: The Framingham Heart Study. Circulation, 117(6), 743–753. https://doi.org/10.1161/CIRCULATIONAHA.107.699579 (This is a classic paper on risk scoring, relevant to the diabetes prediction aspect.)   

* Daghistani, T. A., Elshawi, R., Sakr, S., Ahmed, N., Al-Mallah, M. H., & Bakhsh, H. (2023). Predicting appointment no-show using machine learning: Towards an understanding of drivers and reasons. Health Informatics Journal, 29(2). https://doi.org/10.1177/14604582231183. (This is directly relevant literature, that talks about no-show predictions)

* Kavakiotis, I., Tsave, O., Salifoglou, A., Maglaveras, N., Vlahavas, I., & Chouvarda, I. (2017). Machine Learning and Data Mining Methods in Diabetes Research. Computational and Structural Biotechnology Journal, 15, 104–116. https://doi.org/10.1016/j.csbj.2016.12.005 (This is a review paper on machine learning in diabetes research.)   

