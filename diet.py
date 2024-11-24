from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_openai import ChatOpenAI
from fpdf import FPDF
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from models import DietPlan

import os

os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = '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'
os.environ['OPENAI_API_KEY'] = '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'


# load the diet samples
loader = PyPDFDirectoryLoader("diet_samples/")
diet_samples = loader.load()

# AI prompt
template = """You are a vegan dietician assitant, the user will give you their calories and macros values.
    They may also give you a list of their favourite foods and foods they dont like. 
    You will generate a diet plan for them. 
    Make sure to include all favourite foods and not include the disliked foods.
    Your output will coonsist of a list of meals. Each meal has a list of ingredients. Each ingredient has the amount the user should eat, calories, carbohydrates, 
    fats and proteins. 

    Question: {question}
    """
prompt = ChatPromptTemplate.from_template(template)

# Don't write anything else in the output. Convert to json format. 
#     All fields are string.

# AI Model
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# llm_structured = llm.with_structured_output(DietPlan)

# chain
chain = prompt | llm


def generate_diet(question):
    return chain.invoke({"context": diet_samples, "question": question})

# def save_diet_to_pdf(diet_text, filename="diet_plan.pdf"):
#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.multi_cell(0, 10, diet_text)
#     pdf.output(filename)
#     return filename
