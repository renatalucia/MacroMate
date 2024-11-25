from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import os

with open('config.json', 'r') as file:
    env = json.load(file)

os.environ['LANGCHAIN_TRACING_V2'] = env['LANGCHAIN_TRACING_V2']
os.environ['LANGCHAIN_ENDPOINT'] = env['LANGCHAIN_ENDPOINT']
os.environ['LANGCHAIN_API_KEY'] = env['LANGCHAIN_API_KEY']
os.environ['OPENAI_API_KEY'] = env['OPENAI_API_KEY']

# load the diet samples
loader = PyPDFDirectoryLoader("diet_samples/")
diet_samples = loader.load()

# LLM model
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# AI prompts

# Prompt 1: Takes a a base diet and modifies it to meet the user's food preferences
prompt1 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a vegan diet assistant. 
            Take the {input_diet_plan} and replace Clif Builder Bar with Bread or Vegetables and Hummus.
            Now your first task is to adapt {input_diet_plan} to meet The user food preferences.
            Remove {dislike_foods}. Add {prefered_foods}. Add or remove other foods accoordingly such that 
            the amount of calories in each meal of the {input_diet_plan} stays the same."""
           
        ),
        ("human", "{prefered_foods}"),
    ]
)

#Prompt 2: Takes a diet plan and modifies it to meet the user's daily calorie intake
prompt2 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a vegan diet assistant. The user will tell you their daily calories intake.
            Your  task is to adapt {user_diet_plan} to meet the the user's daily callories intake
            of {input} by changing the amount of the foods. The total calories of the diet have be {input}.
            
            Start your response with "This is
            your persinalised vegan meal plan"
            """
        ),
        ("human", "{input}"),
    ]
)

chain1 = prompt1 | llm
chain2 = prompt2 | llm




def generate_diet(calories, prefered_foods, dislike_foods):
    user_diet_plan = chain1.invoke(
    {
        "input_diet_plan": diet_samples[0],
        "prefered_foods" : prefered_foods,
        "dislike_foods": dislike_foods
    }
    )
    print(user_diet_plan.content)
    print(calories)
    return  chain2.invoke(
    {
        "user_diet_plan": user_diet_plan,
        "input": calories
    }
)

# def save_diet_to_pdf(diet_text, filename="diet_plan.pdf"):
#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.multi_cell(0, 10, diet_text)
#     pdf.output(filename)
#     return filename
