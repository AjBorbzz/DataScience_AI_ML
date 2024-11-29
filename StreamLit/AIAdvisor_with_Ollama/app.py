import streamlit as st
import yfinance as yf
import pandas as pd
import schedule
import time
import ollama
from datetime import datetime, timedelta

stock = yf.Ticker("AAPL")
dow_jones = yf.Ticker("^DJI")
data = stock.history(period="1d", interval="1m")
dow_data = dow_jones.history(period="1d", interval="1m")

print(dow_data)