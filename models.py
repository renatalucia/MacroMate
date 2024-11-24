from pydantic import BaseModel, Field

class Macro(BaseModel):
    calories: str = Field(description="calories")
    carbohydrates : str = Field(description="calories")
    fats: str = Field(description="fats")
    proteins: str = Field(description="proteins")

class Ingredient(BaseModel):
    ingredient: str = Field(description="name of ingredient")
    amount: str = Field(description="amount the user should eat")
    calories: str = Field(description="calories")
    carbohydrates : str = Field(description="calories")
    fats: str = Field(description="fats")
    proteins: str = Field(description="proteins")

    class Config:
        arbitrary_types_allowed = True

class Meal(BaseModel):
    name: str = Field(description="meal name")
    ingredients: [Ingredient] = Field(description="list of ingredients")

    class Config:
        arbitrary_types_allowed = True

class DietPlan(BaseModel):
    meals: [Meal] = Field(description="list of ingredients")

    class Config:
        arbitrary_types_allowed = True