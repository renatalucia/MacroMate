import streamlit as st
from utils import calculate_bmr, calculate_tdee, adjust_calories_for_goal, calculate_macros

def macros_calculator_tab(tab):
    with tab:
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