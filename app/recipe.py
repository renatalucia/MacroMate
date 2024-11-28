class Recipe:

    def __init__(self, recipe_name: str, recipe_link: str,
                 recipe_instructions: str, recipe_ingredients: list,
                 recipe_servings: str, nutritional_info: dict):
        self.name = recipe_name
        self.instructions = recipe_instructions
        self.link = recipe_link
        self.ingredients = recipe_ingredients
        self.servings = recipe_servings
        self.nutritional_info = nutritional_info