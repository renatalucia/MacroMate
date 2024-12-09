import streamlit as st
import pandas as pd
import recipe_controller
import nutritional_info_sample as nutritional_info

def get_expand_text(ingredient_details):
    return f"""***{ingredient_details["Food"]} - {ingredient_details["Quantity"]} 
        {ingredient_details["Unit"]}***
        ({ingredient_details["Calories"]}kcal, 
        {ingredient_details["Protein"]}g Protein, {ingredient_details["Total Carbs"]}g Total Carbs,
        {ingredient_details["Fiber"]}g Fiber, {ingredient_details["Sugars"]}g Sugars, 
        {ingredient_details["Total Fat"]}g Total Fat,
        {ingredient_details["Saturated Fat"]}g Saturated Fat)
        """

def update_quantity(index, new_quantity):
    factor = float(new_quantity)/float(st.session_state.df.loc[index, "Quantity"])
    st.session_state.df.loc[index, "Calories"] = st.session_state.df.loc[index, "Calories"] * factor
    st.session_state.df.loc[index, "Total Fat"] = st.session_state.df.loc[index, "Total Fat"] * factor
    st.session_state.df.loc[index, "Saturated Fat"] = st.session_state.df.loc[index, "Saturated Fat"] * factor
    st.session_state.df.loc[index, "Protein"] = st.session_state.df.loc[index, "Protein"] * factor
    st.session_state.df.loc[index, "Total Carbs"] = st.session_state.df.loc[index, "Total Carbs"] * factor
    st.session_state.df.loc[index, "Fiber"] = st.session_state.df.loc[index, "Fiber"] * factor
    st.session_state.df.loc[index, "Sugars"] = st.session_state.df.loc[index, "Sugars"] * factor
    st.session_state.df.loc[index, 'Quantity'] = new_quantity

    st.session_state.recipe_totals = recipe_controller.calculate_totals(st.session_state.df)

def update_ingredient(idx, new_ingredient):
    query = f"{st.session_state.df.loc[idx, 'Quantity']} {st.session_state.df.loc[idx, 'Unit']} {new_ingredient}"   
    nutritional_values = recipe_controller.food_nutritional_info(query)
    st.session_state.df.loc[idx, 'Food'] = nutritional_values["food_name"]
    st.session_state.df.loc[idx, 'Calories'] = nutritional_values["nf_calories"]
    st.session_state.df.loc[idx, 'Total Fat'] = nutritional_values["nf_total_fat"]
    st.session_state.df.loc[idx, 'Saturated Fat'] = nutritional_values["nf_saturated_fat"]
    st.session_state.df.loc[idx, 'Protein'] = nutritional_values["nf_protein"]
    st.session_state.df.loc[idx, 'Total Carbs'] = nutritional_values["nf_total_carbohydrate"]
    st.session_state.df.loc[idx, 'Fiber'] = nutritional_values["nf_dietary_fiber"]
    st.session_state.df.loc[idx, 'Sugars'] = nutritional_values["nf_sugars"]
    st.session_state.df.loc[idx, 'Quantity'] = nutritional_values["serving_qty"]
    st.session_state.df.loc[idx, 'Unit'] = nutritional_values["serving_unit"]

    st.session_state.recipe_totals = recipe_controller.calculate_totals(st.session_state.df)

def recipe_analyzer_tab(tab):
    print(recipe_analyzer_tab)
    with tab:
        st.header("Get Nutritional Information for your Recipe")
        recipe_link = st.text_area("Enter the link to your recipe:", placeholder="e.g., https://nutritionfacts.org/recipe/chickpea-chili/")
        get_info_btn = st.button("Get Nutritional Information")

        print("*****Heerrreeee!!!!!")
        if get_info_btn:
            try:
                # recipe_info, recipe_totals = recipe_controller.read_recipe_from_web(recipe_link)
                print("*****Heerrreeee")
                recipe_info = nutritional_info.nutritional_info
                recipe_totals = nutritional_info.recipe_totals
                
                st.session_state.df = pd.DataFrame(nutritional_info.format_nutritional_info(recipe_info))
                st.session_state.recipe_totals = recipe_totals
            except Exception as e:
                st.error(e)
                st.error("Error in request to API. Please check the recipe link and try again.")

        if "df" in st.session_state:
            st.subheader("Recipe Nutritional Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<h3 style='font-size:16px;'>Total Calories: {st.session_state.recipe_totals['calories']:.2f} kcal</h3>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='font-size:16px;'>Total Protein: {st.session_state.recipe_totals['protein']:.2f} g</h3>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<h3 style='font-size:16px;'>Total Carbs: {st.session_state.recipe_totals['total_carbs']:.2f} g</h3>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='font-size:16px;'>Fiber: {st.session_state.recipe_totals['fiber']:.2f} g</h3>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='font-size:16px;'>Sugar: {st.session_state.recipe_totals['sugar']:.2f} g</h3>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<h3 style='font-size:16px;'>Total Fat: {st.session_state.recipe_totals['total_fat']:.2f} g</h3>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='font-size:16px;'>Saturated Fat: {st.session_state.recipe_totals['saturated_fat']:.2f} g</h3>", unsafe_allow_html=True)

            st.subheader("Recipe Ingredients")
            for idx, row in st.session_state.df.iterrows():
                ingredient_name = row["Food"]
                ingredient_quantity = row["Quantity"]
                with st.expander(get_expand_text(row), expanded=False):
                    new_ingredient = st.selectbox(f"Replace with:", row["Food_alternatives"], key=f"{ingredient_name}_dropdown")
                    new_quantity = st.text_input(f"Edit quantity of {ingredient_name}:", value=ingredient_quantity, key=f"{ingredient_name}_quantity")
                    if new_ingredient != "Select":
                        update_ingredient(idx, new_ingredient)
                    if new_quantity != ingredient_quantity:
                        update_quantity(idx, new_quantity)
                    if new_ingredient != "Select" and new_ingredient != ingredient_name or new_quantity != ingredient_quantity:
                        st.rerun()