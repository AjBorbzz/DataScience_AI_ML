import streamlit as st
import yfinance as yf
import pandas as pd
import schedule
import time
import ollama
from datetime import datetime, timedelta

prompt = "Create a step by step streamlit tutorial for getting started."
response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
response_text = response['message']['content'].strip()
print(response_text)