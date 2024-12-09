import os
import json
import streamlit as st
from config_loader import load_config
from macros_calculator import macros_calculator_tab
from diet_generator import diet_generator_tab
from recipe_analyzer import recipe_analyzer_tab

# Load configuration
env = load_config('config.json')

# Set environment variables
os.environ['LANGCHAIN_TRACING_V2'] = env['LANGCHAIN_TRACING_V2']
os.environ['LANGCHAIN_ENDPOINT'] = env['LANGCHAIN_ENDPOINT']
os.environ['LANGCHAIN_API_KEY'] = env['LANGCHAIN_API_KEY']
os.environ['OPENAI_API_KEY'] = env['OPENAI_API_KEY']

st.title("Macro Mate")
tab1, tab2, tab3 = st.tabs(["Macros Calculator", "Diet Generator", "Food Composition Analyzer"])

macros_calculator_tab(tab1)
diet_generator_tab(tab2)
recipe_analyzer_tab(tab3)