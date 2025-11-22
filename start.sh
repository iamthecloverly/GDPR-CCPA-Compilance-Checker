#!/bin/bash

# Create a Streamlit config file
mkdir -p .streamlit
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > .streamlit/config.toml

# Start the Streamlit app
streamlit run app.py
