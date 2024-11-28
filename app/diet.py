from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import os
import requests

# Load json config variables
with open('config.json', 'r') as file:
    env = json.load(file)

os.environ['LANGCHAIN_TRACING_V2'] = env['LANGCHAIN_TRACING_V2']
os.environ['LANGCHAIN_ENDPOINT'] = env['LANGCHAIN_ENDPOINT']
os.environ['LANGCHAIN_API_KEY'] = env['LANGCHAIN_API_KEY']
os.environ['OPENAI_API_KEY'] = env['OPENAI_API_KEY']

edamama_url = f"https://api.edamam.com/api/nutrition-details?app_id={env["EDAMAMA_ID"]}&app_key={env["EDAMAMA_KEY"]}&beta=true&kitchen=home"


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

# Prompt 2: Takes a diet plan and modifies it to meet the user's daily calorie intake
prompt2 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a vegan diet assistant. The user will tell you their daily calories intake.
            Your  task is to adapt {user_diet_plan} to meet the the user's daily callories intake
            of {input} by changing the amount of the foods. The total calories can NEVER be more than
            {input}.
            
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
            "prefered_foods": prefered_foods,
            "dislike_foods": dislike_foods
        }
    )

    return chain2.invoke(
        {
            "user_diet_plan": user_diet_plan,
            "input": calories
        }
    )

def get_meal_computed_composition_values(ingredients):
    json_input = {
        "title": "string",
        "ingr": [
            "2 tbsp olive oil", "225g block smoked firm tofu, cut into small cubes", "3 tbsp chipotles in adobo", "0.5 tsp sea salt", "3 spring onions", "Tacos or toast to serve", "Grated zest and juice 1 lime", "Garlic cloves", "Chilli oil or Korean chilli flakes", "Chilli oil or Korean chilli flakes",  "Drizzle of tahini", "10g IsoPure Protein Powder"],
        "summary": "summary",
        "yield": "string",
        "time": "string",
        "img": "string",
        "prep": [
            "string"
        ],
    }
    
    response = requests.post(url=edamama_url, json=json_input)
    response_json = json.loads(response.text)
    composition_values = {}
    for key, values in response_json["totalNutrients"].items():
        composition_values[values["label"]] = f"{round(values["quantity"])}{values["unit"]}"    



# def save_diet_to_pdf(diet_text, filename="diet_plan.pdf"):
#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.multi_cell(0, 10, diet_text)
#     pdf.output(filename)
#     return filename
