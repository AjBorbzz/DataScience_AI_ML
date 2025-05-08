import streamlit as st
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
# from sklearn.metrics import plot_confusion_matrix, plot_roc_curve, plot_precision_recall_curve
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay, PrecisionRecallDisplay
from sklearn.metrics import precision_score, recall_score 

def main():
    st.title("Binary Classification Web App")
    st.sidebar.title("Binary Classification Web App")
    st.markdown("Are your mushrooms edible or poisonous? ")
    st.sidebar.markdown("Are your mushrooms edible or poisonous? ")

    @st.cache_data(persist=True)
    def load_data():
        data = pd.read_csv("./mushrooms.csv")
        label = LabelEncoder()
        for col in data.columns:
            data[col] = label.fit_transform(data[col])
        return data

    @st.cache_data(persist=True)
    def split(df):
        y = df['class']
        x = df.drop(columns=['class'])
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0)
        return x_train, x_test, y_train, y_test

    def plot_metrics(metrics_list):
        if 'Confusion Matrix' in  metrics_list:
            fig, ax = plt.subplots()
            st.subheader("Confusion Matrix")
            ConfusionMatrixDisplay.from_estimator(
            model, x_test, y_test, display_labels=class_names, ax=ax
                )
            st.pyplot(fig)

        if 'ROC Curve' in metrics_list:
            st.subheader("ROC Curve")
            fig, ax = plt.subplots()
            RocCurveDisplay.from_estimator(model, x_test, y_test, ax=ax)
            st.pyplot(fig)

        if 'Precision-Recall' in metrics_list:
            st.subheader("Precision-Recall Curve")
            fig, ax = plt.subplots()
            PrecisionRecallDisplay.from_estimator(model, x_test, y_test, ax=ax)
            st.pyplot(fig)

    def fit_and_plot(model):
        model.fit(x_train, y_train)
        accuracy = model.score(x_test, y_test)
        y_pred = model.predict(x_test)

        precision = precision_score(y_test, y_pred, labels=class_names)
        recall = recall_score(y_test, y_pred, labels=class_names)
        st.subheader("📊 Model Evaluation Metrics")

        # Layout in columns for better UI
        col1, col2, col3 = st.columns(3)

        col1.metric(label="🎯 Accuracy", value=f"{accuracy * 100:.2f}%")
        col2.metric(label="✅ Precision", value=f"{precision * 100:.2f}%")
        col3.metric(label="📥 Recall", value=f"{recall * 100:.2f}%")
        
        plot_metrics(metrics)

    df = load_data()    
    x_train, x_test, y_train, y_test = split(df)
    class_names = ['edible', 'poisonous']

    st.sidebar.subheader("Choose Classifier")
    classifier = st.sidebar.selectbox("Classifier", 
       ("Support Vector Machine (SVM)", 
        "Logistic Regression", 
        "Random Forest"))

    if classifier == "Support Vector Machine (SVM)":
        st.sidebar.subheader("Model Hyperparameters")
        C = st.sidebar.number_input("C (Regularization parameter)", 
                                    0.01,
                                    10.0,
                                    step=0.01,
                                    key='C')
        kernel = st.sidebar.radio("kernel",
                                  ("rbf", "linear"),
                                  key="kernel")
        gamma = st.sidebar.radio("Gamma (Kernel Coefficient)", 
                                 ("scale", "auto"),
                                 key="gamma")

        metrics = st.sidebar.multiselect("What metrics to plot?",
                  ("Confusion Matrix", "ROC Curve", "Precision-Recall"))

        if st.sidebar.button("Classify", key='classify'):
            st.subheader("Support Vector Machine (SVM) Results")
            model = SVC(C=C, kernel=kernel, gamma=gamma)
            fit_and_plot(model)

    if classifier == "Logistic Regression":
        st.sidebar.subheader("Model Hyperparameters")
        C = st.sidebar.number_input("C (Regularization parameter)", 
                                    0.01,
                                    10.0,
                                    step=0.01,
                                    key='C_LR')
        max_iter = st.sidebar.slider("Maximum number of iterations",
                                   100,500, key='max_iter')

        metrics = st.sidebar.multiselect("What metrics to plot?",
                  ("Confusion Matrix", "ROC Curve", "Precision-Recall"))

        if st.sidebar.button("Classify", key='classify'):
            st.subheader("Logistic Regression Results")
            model = LogisticRegression(C=C, max_iter=max_iter)
            fit_and_plot(model)

    if classifier == "Random Forest":
        st.sidebar.subheader("Model Hyperparameters")
        n_estimators = st.sidebar.number_input("The number of tress in the forest",
                                               100, 5000, step=10,
                                              key='n_estimators')

        max_depth = st.sidebar.number_input("The maximum depth of the tree", 
                                             1,
                                             20,
                                             step=1,
                                             key='max_depth')
        bootstrap = st.sidebar.radio("Bootstrap samples when building tree",
                                    ("True", "False"),
                                    key='bootstrap')

        metrics = st.sidebar.multiselect("What metrics to plot?",
                  ("Confusion Matrix", "ROC Curve", "Precision-Recall"))

        if st.sidebar.button("Classify", key='classify'):
            st.subheader("RandomForestClassifier Results")
            model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth,
                                    bootstrap=bootstrap, n_jobs=-1)
            fit_and_plot(model)

            
    if st.sidebar.checkbox("Show Raw Data", False):
        st.subheader("Mushroom Data Set (Classification)")
        st.write(df)

def test_env():
    data = pd.read_csv("./mushrooms.csv")
    label = LabelEncoder()
    for col in data.columns:
        data[col] = label.fit_transform(data[col])
    print(data.head())
    print(data['class'])

if __name__ == '__main__':
    main()
    # test_env()


