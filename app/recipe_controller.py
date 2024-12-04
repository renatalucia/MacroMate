import json
import os
from langchain_community.document_loaders import WebBaseLoader
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import recipe
import requests


# Open and read the JSON file
with open('config.json', 'r') as file:
    env = json.load(file)


os.environ['LANGCHAIN_TRACING_V2'] = env['LANGCHAIN_TRACING_V2']
os.environ['LANGCHAIN_ENDPOINT'] = env['LANGCHAIN_ENDPOINT']
os.environ['LANGCHAIN_API_KEY'] = env['LANGCHAIN_API_KEY']
os.environ['OPENAI_API_KEY'] = env['OPENAI_API_KEY']

# LLM model
model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)


# Structure for LLM output
class RecipeStructure(BaseModel):
    name: str = Field(description="name")
    ingredients: str = Field(description="ingredients")
    instructions: str = Field(description="instructions to prepare the recipe")
    servings: str



def remove_non_food_items ( ingredients_list  ):
    template_nonfood_check = """
        Your task is to identify a list (separated by \',\') of items in {ingredients_list} that are not food.
        If none is found, return an empty string.
        Examples of items that are not food: pressed, diced, sliced, cut, peeled"""
    
    # Prompt
    prompt_nonfood_check = ChatPromptTemplate.from_template(template_nonfood_check)

    # Chain
    chain = prompt_nonfood_check | model

    non_food_list_str = chain.invoke({"ingredients_list": ", ".join(ingredients_list)})
    non_food_list = non_food_list_str.content.split(",")

    for item in non_food_list:
        item = item.strip()
        if item in ingredients_list:
            ingredients_list.remove(item)
    
    return ingredients_list

def remove_non_quantity_items (ingredients_list):
    print("remove_non_quantity_items")
    print(ingredients_list)
    
    template_ingredients_check = """
        Your task is to identify a list of ingredients in {ingredients_list} that do not have an associated quantity.
        If none is found, return an empty string \'\'.
        The items in the list should be separated by \',\'.
        """


    # Prompt
    prompt_ingredients_check = ChatPromptTemplate.from_template(template_ingredients_check)

    chain_ingredients_check = prompt_ingredients_check | model 

    non_qty_list_str = chain_ingredients_check.invoke({"ingredients_list": ", ".join(ingredients_list)})

    print(non_qty_list_str)
    non_qty_list = non_qty_list_str.content.split(",")

    print("Here")
    print(non_qty_list)

    for item in non_qty_list:
        item = item.strip()
        print(item)
        if item.lower() in ingredients_list:
            ingredients_list.remove(item)

    return ingredients_list




def get_nutritional_composition(recipe_link):
    # Prompt template
    template = """
    Your task is to identify the name, number of servings, the list (separated by \',\') of ingredients  with their quantities, and instructions of {input_recipe}.
    If you cannot identify any of these fields assign them the empty string \'\'.
    """

    # Prompt
    prompt = ChatPromptTemplate.from_template(template)

    structured_llm = model.with_structured_output(RecipeStructure)

    chain = prompt | structured_llm
    
    loader = WebBaseLoader(recipe_link)
    recipe_doc = loader.load()
    recipe_output = chain.invoke({"input_recipe":recipe_doc})

    
    ingredients_list = [ingr.strip().lower() for ingr in recipe_output.ingredients.split(",")]
    
    # Remove non-food items from the ingredients list
    # ingredients_list = remove_non_food_items(ingredients_list)

    ingredients_list = remove_non_quantity_items(ingredients_list)

    print(ingredients_list)

    # Request to Edamam API
    url = f"https://api.edamam.com/api/nutrition-details?app_id={env["EDAMAMA_ID"]}&app_key={env["EDAMAMA_KEY"]}&beta=true&kitchen=home"

    json_post = {
    "title": "string",
    "ingr": ingredients_list,
    "summary": "summary",
    "yield": "string",
    "time": "string",
    "img": "string",
    "prep": [
        "string"
    ]
    }

    try:
        response = requests.post(url=url, json=json_post)
        json_response = json.loads(response.text)
        composition = {}
        for values in json_response["totalNutrients"].values():
            composition[values['label']] = f"{int(values['quantity'])}{values['unit']}"  

        return  recipe.Recipe(
            recipe_output.name, 
            recipe_link, 
            recipe_output.instructions, 
            recipe_output.ingredients, 
            recipe_output.servings, 
            composition)   
    except requests.exceptions.RequestException as e:
        print("Error in request to Edamam API")
        raise e  
    
