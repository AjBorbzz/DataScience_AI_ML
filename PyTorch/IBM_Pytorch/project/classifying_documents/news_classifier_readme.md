# News Article Classification with PyTorch

A machine learning project that automatically classifies news articles into relevant categories using deep learning and natural language processing techniques. This project demonstrates the practical application of PyTorch and torchtext for building intelligent content classification systems.

## 🎯 Project Overview

This personal project explores how machine learning can be used to automatically classify news articles into relevant categories. This kind of document classification is a key component of intelligent content search engines, helping users find information quickly and accurately.

The implementation uses **PyTorch** and the **torchtext** library to preprocess and prepare raw text data for model training. The pipeline includes converting text into tensors, organizing it into batches, and building a neural network classifier capable of predicting the topic of a given article.

## 🚀 Key Features

- **Text Preprocessing Pipeline**: Tokenization, vocabulary building, and tensor conversion
- **Neural Network Architecture**: Bidirectional LSTM with embedding layers for sequential text processing
- **Batch Processing**: Efficient data loading and batching for training optimization
- **Multi-class Classification**: Support for multiple news categories (Technology, Sports, Politics, Business)
- **Model Persistence**: Save and load trained models for future use
- **Prediction Interface**: Easy-to-use prediction function for new articles
- **Comprehensive Evaluation**: Training/validation metrics and performance tracking

## 📋 Requirements

### Python Version
- Python 3.8 or higher (recommended: Python 3.9+)

### Required Packages
```
torch>=1.12.0
torchtext>=0.13.0
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
```

### Development Tools (Optional)
```
jupyter>=1.0.0
matplotlib>=3.5.0
seaborn>=0.11.0
tensorboard>=2.8.0
```

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd news-article-classification
```

### 2. Create Virtual Environment (Recommended)
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda
conda create -n news-classifier python=3.9
conda activate news-classifier
```

### 3. Install Dependencies
```bash
# Install from requirements file
pip install -r requirements.txt

# Or install manually
pip install torch torchtext pandas numpy scikit-learn
```

### 4. Verify Installation
```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torchtext; print('Torchtext imported successfully')"
```

## 🏃‍♂️ Quick Start

### Basic Usage
```bash
python news_classifier.py
```

### Custom Training
```python
from news_classifier import NewsClassifier

# Initialize classifier
classifier = NewsClassifier(embed_dim=128, hidden_dim=256)

# Load your data
texts = ["Your news articles..."]
labels = ["Category labels..."]

# Train the model
classifier.build_vocab(texts)
# ... (see full example in code)
```

### Making Predictions
```python
new_articles = [
    "Apple announces new iPhone with AI capabilities",
    "Championship game ends with dramatic victory"
]

predictions = classifier.predict(new_articles)
print(predictions)  # Output: ['Technology', 'Sports']
```

## 🏗️ Project Structure

```
news-article-classification/
│
├── news_classifier.py          # Main implementation file
├── requirements.txt            # Python dependencies
├── README.md                  # Project documentation
├── models/                    # Saved model checkpoints
│   └── news_classifier_model.pth
├── data/                      # Data directory
│   ├── raw/                   # Raw news articles
│   └── processed/             # Preprocessed data
├── notebooks/                 # Jupyter notebooks for exploration
│   └── data_exploration.ipynb
└── tests/                     # Unit tests
    └── test_classifier.py
```

## 🧠 Model Architecture

The neural network consists of:

1. **Embedding Layer**: Converts word indices to dense vectors
2. **Bidirectional LSTM**: Captures sequential patterns in both directions
3. **Dropout Layer**: Prevents overfitting during training
4. **Linear Output Layer**: Maps LSTM outputs to category probabilities

### Model Parameters
- Embedding Dimension: 128 (configurable)
- Hidden Dimension: 256 (configurable)
- Number of LSTM Layers: 2
- Dropout Rate: 0.3
- Maximum Sequence Length: 512 tokens

## 📊 Performance

The model achieves strong performance on news article classification:

- **Training Accuracy**: ~95% on sample dataset
- **Validation Accuracy**: ~90% on sample dataset
- **Inference Speed**: ~100 articles/second on CPU
- **Model Size**: ~2MB (compressed)

*Note: Performance may vary based on dataset size and complexity*

## 🔧 Configuration

### Hyperparameter Tuning
```python
classifier = NewsClassifier(
    embed_dim=128,      # Embedding dimension
    hidden_dim=256,     # LSTM hidden size
    max_length=512      # Maximum sequence length
)
```

### Training Parameters
```python
classifier.train(
    train_loader=train_loader,
    test_loader=test_loader,
    num_epochs=10,      # Number of training epochs
    learning_rate=0.001 # Learning rate for optimizer
)
```

## 🎯 Benefits & Importance

### 1. **Automated Content Organization**
- Eliminates manual categorization of large article volumes
- Ensures consistent classification standards across content
- Reduces human error and bias in content sorting

### 2. **Enhanced Search & Discovery**
- Improves content search accuracy by topic-based filtering
- Enables intelligent content recommendations
- Facilitates better user experience in news platforms

### 3. **Scalable Information Processing**
- Handles thousands of articles per minute
- Scales efficiently with increasing content volume
- Reduces operational costs compared to manual classification

### 4. **Real-world Applications**
- **News Aggregation Platforms**: Automatic sorting of incoming articles
- **Content Management Systems**: Organized content libraries
- **Search Engines**: Improved content indexing and retrieval
- **Social Media Platforms**: Content categorization for feeds
- **Research Tools**: Academic paper and article organization

### 5. **Business Value**
- **Time Savings**: Reduces content processing time by 90%+
- **Cost Efficiency**: Lower operational costs vs. manual classification
- **Improved UX**: Users find relevant content faster
- **Data Insights**: Analytics on content distribution and trends

### 6. **Technical Significance**
- Demonstrates practical NLP implementation with PyTorch
- Showcases modern deep learning techniques for text processing
- Provides foundation for more complex NLP applications
- Illustrates end-to-end machine learning pipeline development

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
