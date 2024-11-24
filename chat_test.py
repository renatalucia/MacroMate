from chat import open_chat
import json
import os
import streamlit as st
from utils import calculate_bmr, calculate_tdee, adjust_calories_for_goal, calculate_macros
from diet import generate_diet
from models import DietPlan
from openai import OpenAI
from chat import open_chat
import time


tab1, tab2 = st.tabs(["Macro Calculator", "Diet Generator"])
with tab1:
    st.header("Daily Macronutrient Calculator")
with tab2:
    st.header("Diet Generator")
    messages = st.container(height=300)
    if prompt := st.chat_input("Say something"):
        messages.chat_message("user").write(prompt)
        messages.chat_message("assistant").write(f"Echo: {prompt}")