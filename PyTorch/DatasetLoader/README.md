#  Dataset Loader Utility

> A modular and extensible dataset loading utility for PyTorch-based projects, created as a personal initiative to simplify and standardize how datasets are accessed, preprocessed, and reused across machine learning experiments.

##  Project Goal

This project is designed to serve as a **production-grade utility** for loading and managing datasets across various domains, such as:
- **Text classification** (e.g., news, reviews)
- **Image recognition** (e.g., CIFAR, MNIST)
- **Audio analysis** (e.g., SpeechCommands)

The aim is to **reduce boilerplate**, promote **clean code practices**, and provide a **centralized interface** to dynamically load datasets depending on your use case.

## Why I Built This

As someone who frequently works on diverse AI/ML projects, I often found myself repeating the same steps to:
- Locate datasets
- Write download and transform logic
- Test each loader manually

This project automates that process and allows for scalable and clean integration into different machine learning workflows.

## Key Features

-  Dynamic dataset loader via domain registry
-  Support for TorchText, TorchVision, and Torchaudio datasets
-  Unit-testable components
-  Easily extendable for custom datasets or domains

##  Project Structure
dataset_loader/
├── core/ # Domain-specific loaders (text, vision, audio)
├── config/ # Registry for mapping domain + dataset
├── utils/ # Common preprocessing utilities
├── tests/ # Unit tests for dataset loading
├── main.py # Example usage
└── requirements.txt



## Proposed Project Structure
dataset_loader/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── base.py          # Common logic and utilities
│   ├── text_loader.py   # Text-specific dataset loading
│   ├── vision_loader.py # Vision-specific dataset loading
│   ├── audio_loader.py  # Audio-specific dataset loading
├── config/
│   └── registry.py       # Maps dataset names to classes
├── utils/
│   ├── __init__.py
│   └── transforms.py    # Common transforms/preprocessing
├── main.py              # Entry point for testing loader
├── requirements.txt     # Dependencies
└── tests/
    ├── __init__.py
    ├── test_loader.py   # Unit tests for dataset loading
