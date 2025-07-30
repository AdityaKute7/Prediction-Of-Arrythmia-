# Arrhythmia Prediction Using Deep Learning (B.E. Final year project)

A deep learning-based ECG arrhythmia prediction system leveraging Convolutional Neural Networks (1D-CNN) for early and accurate diagnosis of cardiac irregularities. The project is deployed via a Flask web app, enabling real-time prediction from ECG input data.

---

##  Project Overview

Cardiovascular diseases, particularly arrhythmias, are a major cause of global mortality. This project aims to automate arrhythmia detection using deep learning, reducing reliance on manual ECG interpretation and enabling early intervention through:

- A CNN-based classifier trained on ECG features
- A user-friendly web interface for real-time prediction
- Integration of patient symptom data for enhanced accuracy

---

##  Features

-  **1D Convolutional Neural Network (CNN)** for ECG signal classification
-  Accuracy of **92–95%** on testing data
-  Flask-based web application with secure user login
-  CSV-based ECG input format with preprocessing pipeline
-  Real-time prediction with visual results and healthcare suggestions
-  Symptom analysis through pre-diagnostic questionnaire

---
## Model Architecture

- **Input**: ECG values (RR interval, P-wave, QRS complex, T-wave, QT interval)
- **CNN Layers**: Conv1D → MaxPooling → Dropout → Flatten → Dense → Dropout → Output
- **Output**: Binary classification → `Normal (0)` or `Arrhythmia (1)`

---

##  Performance Metrics

| Metric      | Value       |
|-------------|-------------|
| Accuracy    | 92–95%      |
| Precision   | >90%        |
| Recall      | >90%        |
| F1-Score    | High        |

---

##  Tools & Libraries

- **Python**
- **TensorFlow / Keras**
- **Scikit-learn**
- **Pandas, NumPy**
- **Flask (Web Interface)**
- **Google Colab / Jupyter for training**
- **Matplotlib / Seaborn for visualization**

---

##  References
The model is built and validated using well-established datasets and methodologies such as:

MIT-BIH Arrhythmia Database

CNN architectures inspired by Acharya et al., Rajpurkar et al.

Research references listed in the thesis document

##  Author
Aditya Kute – Final Year Project
© 2025 Aditya Kute. All rights reserved.
