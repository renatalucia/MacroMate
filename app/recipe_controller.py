import json
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from gliner import GLiNER
import requests
import json
import pandas as pd


# Open and read the JSON file
with open('config.json', 'r') as file:
    env = json.load(file)


os.environ['LANGCHAIN_TRACING_V2'] = env['LANGCHAIN_TRACING_V2']
os.environ['LANGCHAIN_ENDPOINT'] = env['LANGCHAIN_ENDPOINT']
os.environ['LANGCHAIN_API_KEY'] = env['LANGCHAIN_API_KEY']
os.environ['OPENAI_API_KEY'] = env['OPENAI_API_KEY']

# LLM model
model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

# Name entity recognition model
ner_model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

# Labels for entity prediction
# Most GLiNER models should work best when entity types are in lower case or title case
ner_labels = ["quantity", "food"]


# Structure for LLM output
class Recipe(BaseModel):
    name: str = Field(description="name")
    ingredients: str = Field(description="ingredients")
    instructions: str = Field(description="instructions to prepare the recipe")
    servings: str



def read_recipe_from_web(recipe_link):

    print("----->>>>Reading recipe from the web")

    # Large language model to extract recipe information

    # Prmpt template
    template = """
    Your task is to identify the name, number of servings, the list (separated by \',\') of ingredients  with their quantities, and instructions of {input_recipe}.
    If you cannot identify any of these fields assign them the empty string \'\'.
    """
    # LLM Prompt
    prompt = ChatPromptTemplate.from_template(template)

    # Load Recipe from the web
    loader = WebBaseLoader(recipe_link)
    doc = loader.load() 

    # language model with structured output
    structured_llm = model.with_structured_output(Recipe)
    chain = prompt | structured_llm

    # Invoke  chain
    rec = chain.invoke({"input_recipe":doc})

    # Entity Recognition to extract food and quantiies for API request
    
    # Store entries for API call
    entity_ingredients = []

    print(rec.ingredients.split(","))

    # texts for entity prediction
    for text in rec.ingredients.split(","):
        # Perform entity prediction
        entities = ner_model.predict_entities(text, ner_labels, threshold=0.5)
        
        # Display predicted entities and their labels
        food = quantity = ""
        for entity in entities:
            # print(entity["text"], "=>", entity["label"])
            if (not food) and (entity["label"]=="food"):
                food = entity["text"]
            if (not quantity) and (entity["label"]=="quantity"):
                quantity = entity["text"]
        if food and quantity:
            entity_ingredients.append(f"{quantity} {food}")
        

    #print("************")
    #print(entity_ingredients)
    
    # Call nutritionix API for nutritional values
    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'

    headers = {
        'Content-Type': 'application/json',
        'x-app-id': env["x-app-id"],
        'x-app-key': env["x-app-key"]
    }

    nutritional_info = []
    recipe_totals = {
        "calories": 0,
        "total_fat": 0,
        "saturated_fat": 0,
        "total_carbohydrate": 0,
        "dietary_fiber": 0,
        "sugars": 0,
        "protein": 0
    }

    print("Before for ingredient in entity_ingredients")
    for ingredient in entity_ingredients:
        json_obj = {'query': ingredient}
        x = requests.post(url, headers = headers, json = json_obj)
        parsed = json.loads(x.text)

        url_alternatives = f'https://trackapi.nutritionix.com/v2/search/instant/?query={ingredient}'
        x_alternatives = requests.get(url_alternatives, headers = headers)
        parsed_alternatives = json.loads(x_alternatives.text)

        for food in parsed["foods"]:
            food_alternatives = [alt['food_name'] for alt in parsed_alternatives['common']]
            print(food["food_name"])
            print(food_alternatives)
            # get info for each food
            food_info = {}
            food_info["user_input"] = ingredient
            food_info["food_name"] = food["food_name"]
            food_info["food_alternatives"] = food_alternatives
            food_info["serving_qty"] = food["serving_qty"]
            food_info["serving_unit"] = food["serving_unit"]
            food_info["serving_weight_grams"] = food["serving_weight_grams"]
            food_info["nf_calories"] = food["nf_calories"]
            food_info["nf_total_fat"] = food["nf_total_fat"]
            food_info["nf_saturated_fat"] = food["nf_saturated_fat"]
            food_info["nf_total_carbohydrate"] = food["nf_total_carbohydrate"]
            food_info["nf_dietary_fiber"] = food["nf_dietary_fiber"]
            food_info["nf_sugars"] = food["nf_sugars"]
            food_info["nf_protein"] = food["nf_protein"]
            nutritional_info.append(food_info)

            # update recipe totals
            recipe_totals ["calories"] += food_info.get("nf_calories", 0) or 0
            recipe_totals ["total_fat"] += food_info.get("nf_total_fat", 0) or 0
            recipe_totals ["saturated_fat"] += food_info.get("nf_saturated_fat", 0) or 0
            recipe_totals ["total_carbohydrate"] += food_info.get("nf_total_carbohydrate", 0) or 0
            recipe_totals ["dietary_fiber"] += food_info.get("nf_dietary_fiber", 0) or 0
            recipe_totals ["sugars"] += food_info.get("nf_sugars", 0) or 0
            recipe_totals ["protein"] += food_info.get("nf_protein", 0) or 0


    return nutritional_info, recipe_totals

def food_nutritional_info (food_name):
    headers = {
        'Content-Type': 'application/json',
        'x-app-id': env["x-app-id"],
        'x-app-key': env["x-app-key"]
    }
    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
    json_obj = {'query': food_name}
    x = requests.post(url, headers = headers, json = json_obj)
    parsed = json.loads(x.text)
    food = parsed["foods"][0]
    food_info = {}
    food_info["food_name"] = food["food_name"]
    food_info["serving_qty"] = food["serving_qty"]
    food_info["serving_unit"] = food["serving_unit"]
    food_info["serving_weight_grams"] = food["serving_weight_grams"]
    food_info["nf_calories"] = food["nf_calories"]
    food_info["nf_total_fat"] = food["nf_total_fat"]
    food_info["nf_saturated_fat"] = food["nf_saturated_fat"]
    food_info["nf_total_carbohydrate"] = food["nf_total_carbohydrate"]
    food_info["nf_dietary_fiber"] = food["nf_dietary_fiber"]
    food_info["nf_sugars"] = food["nf_sugars"]
    food_info["nf_protein"] = food["nf_protein"]
    return food_info
    
