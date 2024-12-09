import streamlit as st
from diet import generate_diet
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

def diet_generator_tab(tab):
    with tab:
        st.subheader("Food Preferences")
        favorite_foods = st.text_area("Enter your favorite foods (comma-separated):", placeholder="e.g., tofu, broccoli, lentils, avocado")
        disliked_foods = st.text_area("Enter foods you dislike (comma-separated):", placeholder="e.g., mushrooms, spinach, brussels sprouts")

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
                prefered_foods = favorite_foods
                disliked_foods = disliked_foods

                diet_plan = generate_diet(calories, prefered_foods, disliked_foods)
                st.session_state.diet_plan = diet_plan

                if "messages" not in st.session_state:
                    st.session_state.messages = []

                st.session_state.messages.append({"role": "assistant", "content": diet_plan.content})

                if not "memory" in st.session_state:
                    st.session_state.memory = ConversationBufferMemory(memory_key="history", return_messages=True)
                st.session_state.memory.save_context({"input": "question"}, {"output": diet_plan.content})

        if "messages" in st.session_state:
            template = """
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
            custom_prompt = PromptTemplate.from_template(template).partial(diet_plan=st.session_state.diet_plan)
            chat_model = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")
            conversation = ConversationChain(llm=chat_model, memory=st.session_state.memory, prompt=custom_prompt, verbose=False)

            container = st.container()
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