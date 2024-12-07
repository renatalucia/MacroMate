import json
import os
import streamlit as st
from utils import calculate_bmr, calculate_tdee, adjust_calories_for_goal, calculate_macros
from diet import generate_diet
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import pandas as pd
import json
import recipe_controller
import nutritional_info_sample as nutritional_info

with open('config.json', 'r') as file:
    env = json.load(file)

os.environ['LANGCHAIN_TRACING_V2'] = env['LANGCHAIN_TRACING_V2']
os.environ['LANGCHAIN_ENDPOINT'] = env['LANGCHAIN_ENDPOINT']
os.environ['LANGCHAIN_API_KEY'] = env['LANGCHAIN_API_KEY']
os.environ['OPENAI_API_KEY'] = env['OPENAI_API_KEY']

messages_container = None

st.title("Macro Mate")
tab1, tab2, tab3 = st.tabs(["Macros Calculator", "Diet Generator", "Food Composition Analyzer"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# def update_quantity(df, edited_df):
#     print("update_quantity")
#     for index, row in edited_df.iterrows():
#         factor = row["Quantity"]/df.loc[index, "Quantity"]
#         row["Calories"] = df.loc[index, "Calories"] * factor
#     return edited_df

def get_exapnd_text(ingredient_details):
    return f"{ingredient_name} - {ingredient_quantity} ({ingredient_details["Calories"]}kcal)"

def update_nutritional_values(edited_df):
    print("update_nutritional_values")
    for index, row in edited_df.iterrows():
        print(row["Quantity"])
        print(st.session_state.df.loc[index, "Quantity"])
        factor = row["Quantity"]/st.session_state.df.loc[index, "Quantity"]
        print(factor)
        edited_df.loc[index, "Calories"] = st.session_state.df.loc[index, "Calories"] * factor
        edited_df.loc[index, "Calories"] = st.session_state.df.loc[index, "Calories"] * factor
    print(edited_df["Calories"])
    st.session_state.df = edited_df
    # st.rerun()


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
            calories = f"{kcal}calories"
            print(calories)
            prefered_foods = favorite_foods
            disliked_foods = disliked_foods
       
            diet_plan = generate_diet(calories, prefered_foods, disliked_foods)
            print(diet_plan)
            # diet_plan = "Breakfast, lunch, dinner, snacks"
            st.session_state.diet_plan = diet_plan
 
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            st.session_state.messages.append({"role": "assistant", "content": diet_plan.content})
            
            # Add conversation memory to handle multi-turn conversations
            if not "memory" in st.session_state:
                st.session_state.memory = ConversationBufferMemory(memory_key="history", return_messages=True)
            st.session_state.memory.save_context({"input": "question"}, {"output": diet_plan.content})

    if "messages" in st.session_state: 

        # Define the chatbot's custom prompt
        # custom_prompt = PromptTemplate(
        #     input_variables=["history", "diet_plan", "input"],
        template="""
            You are a dietitian assistant chatbot. You are helping a user with their diet plan.
            The user will tell me the changes they want to make to their diet plan. Every time the you change the diet make sure the daily amount of calories, carbohydrates, fats and protein stay close to the amounts of the diet_plan.
            . When the user asks to add or change some food make only minimal changes to the diet plan.

            Conversation History:
            {history}

            DIET PLAN:
            {diet_plan}

            Human: {input}
            AI:
            """
        # )
        custom_prompt = PromptTemplate.from_template(template).partial(diet_plan=st.session_state.diet_plan)

        # Initialize the LangChain chat model
        chat_model = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")

        

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

# Tab 3: Recipe Analyzer
with tab3:

    # Input fields for web data source
    st.header("Get Nutritional Information for your Recipe")
    recipe_link = st.text_area("Enter the link to your recipe:",
        placeholder="e.g., https://nutritionfacts.org/recipe/chickpea-chili/")
    
    
    get_info_btn = st.button("Get Nutritional Information")
    
    if get_info_btn:
        try:
            recipe_info, recipe_totals = recipe_controller.read_recipe_from_web(recipe_link)
            # print(recipe_info)
            # st.write(recipe_info)

            st.session_state.df = pd.DataFrame(
                # nutritional_info.format_nutritional_info(nutritional_info.nutritional_info)
                nutritional_info.format_nutritional_info(recipe_info)
            )

        except Exception as e:
            print(e)
            st.error("""Error in request to  API.
                   \nPlease check the recipe link and try again.""")  
    
    if "df" in st.session_state:

        st.subheader("Recipe Ingredients")

        # Loop through the ingredients and create an expander for each one
        for idx, row in st.session_state.df.iterrows():
            print(row)
            ingredient_name = row["Food"]
            ingredient_quantity = row["Quantity"]

            # Use st.expander to simulate a popover
            with st.expander(get_exapnd_text(row), expanded=False):
                # Dropdown to replace ingredient
                new_ingredient = st.selectbox(
                    f"Replace with:", 
                    row["Food_alternative"],
                    key=f"{ingredient_name}_dropdown"
                )

                # Textbox to edit the quantity
                new_quantity = st.text_input(
                    f"Edit quantity of {ingredient_name}:",
                    value=ingredient_quantity,
                    key=f"{ingredient_name}_quantity"
                )

                # Update the ingredient and quantity in session_state
                if new_ingredient != "Select":
                    st.session_state.df.loc[idx, 'Food'] = new_ingredient
                if new_quantity != ingredient_quantity:
                    st.session_state.df.loc[idx, 'Quantity'] = new_quantity

                # Display the selected options
                if new_ingredient != "Select":
                    st.write(f"Replacement: {st.session_state.df.loc[idx, 'Food']}")
                if new_quantity != ingredient_quantity:
                    st.write(f"New Quantity: {st.session_state.df.loc[idx, 'Quantity']}")

                # Trigger a re-run to reflect the changes
                if new_ingredient != "Select" and new_ingredient != ingredient_name or new_quantity != ingredient_quantity:
                    st.rerun()

                

                       
  

 
    
    


                            


  

        
   

        


        