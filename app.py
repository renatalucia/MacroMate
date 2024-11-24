import json
import os
import streamlit as st
from utils import calculate_bmr, calculate_tdee, adjust_calories_for_goal, calculate_macros
from diet import generate_diet
from models import DietPlan
from openai import OpenAI
from chat import open_chat
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import pandas as pd


os.environ['OPENAI_API_KEY'] = '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'


messages_container = None

st.title("Macro Mate")
tab1, tab2 = st.tabs(["Macro Calculator", "Diet Generator"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"


# Tab 1: Macro Calculator
with tab1:
    st.header("Daily Macronutrient Calculator")

    # Input fields for user data
    st.subheader("User Information")
    gender = st.radio("Gender", ["Male", "Female"], index=0)
    age = st.number_input("Age (years)", min_value=0, max_value=120, value=30, step=1)
    weight = st.number_input("Weight (kg)", min_value=0.0, value=70.0, step=0.1)
    height = st.number_input("Height (cm)", min_value=0.0, value=170.0, step=0.1)
    activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly active", "Moderately active", "Very active", "Super active"])

    # User goal selection
    st.subheader("Goal")
    goal = st.selectbox("Select your goal:", ["Maintenance", "Bulking", "Cutting"])

    # Macro split percentages
    st.subheader("Macronutrient Distribution")
    protein_pct = st.slider("Protein (%)", min_value=0, max_value=100, value=30, step=1)
    carb_pct = st.slider("Carbohydrates (%)", min_value=0, max_value=100, value=50, step=1)
    fat_pct = st.slider("Fats (%)", min_value=0, max_value=100, value=20, step=1)

    # Ensure percentages sum to 100%
    if protein_pct + carb_pct + fat_pct != 100:
        st.error("The total macronutrient percentage must equal 100%.")
    else:
        # Calculate BMR, TDEE, adjusted calories, and macros
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity_level)
        adjusted_calories = adjust_calories_for_goal(tdee, goal)
        protein, carbs, fats = calculate_macros(adjusted_calories, protein_pct, carb_pct, fat_pct)

        # Display results
        st.subheader("Results")
        st.write(f"**BMR**: {bmr:.2f} kcal")
        st.write(f"**TDEE (Unadjusted)**: {tdee:.2f} kcal")
        st.write(f"**Calories for {goal}:** {adjusted_calories:.2f} kcal")

        st.subheader("Macronutrient Breakdown")
        st.write(f"**Protein**: {protein:.2f} g")
        st.write(f"**Carbohydrates**: {carbs:.2f} g")
        st.write(f"**Fats**: {fats:.2f} g")

# Tab 2: Diet Generator
with tab2:
    
    # Input fields for user preferences
    st.subheader("Food Preferences")
    favorite_foods = st.text_area("Enter your favorite foods (comma-separated):", placeholder="e.g., tofu, broccoli, lentils, avocado")
    disliked_foods = st.text_area("Enter foods you dislike (comma-separated):", placeholder="e.g., mushrooms, spinach, brussels sprouts")

    # Input fields for macros and calories
    st.subheader("Macro and Calorie Goals")
    kcal = st.number_input("Target Calories (kcal):", min_value=0, value=2000, step=10)
    protein_pct = st.number_input("Protein (%)", min_value=0, max_value=100, value=30, step=1)
    fat_pct = st.number_input("Fats (%)", min_value=0, max_value=100, value=20, step=1)
    carb_pct = st.number_input("Carbohydrates (%)", min_value=0, max_value=100, value=50, step=1)

    if protein_pct + fat_pct + carb_pct != 100:
        st.error("The total macronutrient percentage must equal 100%.")
    else:
        if st.button("Generate Diet Plan"):
            question = f"""
                {kcal}kcal, {protein_pct}% from proteins, {fat_pct}% from fats, {carb_pct}% from carbohydrates.
                Favourite foods: {favorite_foods}.
                Dislike foods: {disliked_foods}.
                """
            diet_plan = generate_diet(question)
            # diet_plan = "Breakfast, lunch, dinner, snacks"
            st.session_state.diet_plan = diet_plan
 
            if "messages" not in st.session_state:
                st.session_state.messages = []
                 


    if "diet_plan" in st.session_state:
        # st.write("Diet Plan Generated:")
        st.write(st.session_state.diet_plan.content)
        #  for meal in st.session_state.diet_plan.meals:
        #     st.write(f"**{meal["meal"]}**")
        #     df = pd.DataFrame.from_records(meal["ingredients"])
        #     # df.set_index('ingredient', inplace=True)
        #     st.dataframe(df)

    if "messages" in st.session_state: 

        # Define the chatbot's custom prompt
        # custom_prompt = PromptTemplate(
        #     input_variables=["history", "diet_plan", "input"],
        template="""
            You are a dietitian assistant chatbot. You are helping a user with their diet plan.
            The diet plan is in the context.
            
            Conversation History:
            {history}

            Context: {diet_plan}

            Human: {input}
            AI:
            """
        # )
        custom_prompt = PromptTemplate.from_template(template).partial(diet_plan=st.session_state.diet_plan)

        # Initialize the LangChain chat model
        chat_model = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")

        # Add conversation memory to handle multi-turn conversations
        if not "memory" in st.session_state:
            st.session_state.memory = ConversationBufferMemory(memory_key="history", return_messages=True)
            
        # Initialize the conversation chain
        conversation = ConversationChain(
            llm=chat_model,
            memory=st.session_state.memory,
            prompt=custom_prompt,
            verbose=False
        )

        container = st.container()
        # Display chat messages 
        for message in st.session_state.messages:
            with container.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input("Hello! How can I assist you with your diet plan today?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with container.chat_message("user"):
                st.write(prompt)
            response = conversation.run({"input": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response})
            with container.chat_message("assistant"):
                st.write(response)

            st.session_state.memory.save_context({"input": prompt}, {"output": response})

  

        
   

        


        