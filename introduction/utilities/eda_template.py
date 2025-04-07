# -------------------------
# 📊 Exploratory Data Analysis (EDA) Template
# -------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the data
def load_data(filepath):
    return pd.read_csv(filepath)  # Modify if using other formats

# 2. Basic Inspection
def basic_info(df):
    print("✅ Shape:", df.shape)
    print("\n📌 Columns & Types:\n", df.dtypes)
    print("\n🧠 Info:")
    df.info()
    print("\n📈 Summary Stats:\n", df.describe(include='all'))
    print("\n🔁 Duplicates:", df.duplicated().sum())

# 3. Missing Values
def missing_values(df):
    print("\n🕳️ Missing Values:\n", df.isnull().sum())
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
    plt.title("Missing Values Heatmap")
    plt.show()

# 4. Univariate Analysis
def univariate_analysis(df):
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(include='object').columns
    
    for col in num_cols:
        df[col].hist()
        plt.title(f'Distribution of {col}')
        plt.show()
    
    for col in cat_cols:
        sns.countplot(x=col, data=df)
        plt.title(f'Count Plot of {col}')
        plt.xticks(rotation=45)
        plt.show()

# 5. Bivariate / Multivariate Analysis
def multivariate_analysis(df):
    print("\n🔗 Correlation Matrix:")
    corr = df.select_dtypes(include=np.number).corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title("Correlation Heatmap")
    plt.show()

# 6. Outlier Detection (IQR method)
def detect_outliers(df):
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
        print(f"📌 Outliers in {col}: {outliers.shape[0]}")
        sns.boxplot(x=df[col])
        plt.title(f'Boxplot of {col}')
        plt.show()

# 7. Feature Engineering (basic placeholder)
def feature_engineering(df):
    print("\n🛠️ Placeholder: Add feature engineering logic here.")
    # Example:
    # df['new_feature'] = df['feature1'] / df['feature2']

# 8. Export Cleaned Data
def export_data(df, filename='cleaned_data.csv'):
    df.to_csv(filename, index=False)
    print(f"💾 Data exported to {filename}")

# Example usage
if __name__ == "__main__":
    df = load_data('your_dataset.csv')
    basic_info(df)
    missing_values(df)
    univariate_analysis(df)
    multivariate_analysis(df)
    detect_outliers(df)
    feature_engineering(df)
    export_data(df)
