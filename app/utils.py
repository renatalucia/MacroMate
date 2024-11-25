def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:  # Female
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity_level):
    activity_factors = {
        "Sedentary": 1.2,
        "Lightly active": 1.375,
        "Moderately active": 1.55,
        "Very active": 1.725,
        "Super active": 1.9,
    }
    return bmr * activity_factors[activity_level]

def adjust_calories_for_goal(tdee, goal):
    if goal == "Bulking":
        return tdee * 1.1  # Increase by 10%
    elif goal == "Cutting":
        return tdee * 0.9  # Decrease by 10%
    return tdee  # Maintenance

def calculate_macros(calories, protein_pct, carb_pct, fat_pct):
    protein = (protein_pct / 100) * calories / 4
    carbs = (carb_pct / 100) * calories / 4
    fats = (fat_pct / 100) * calories / 9
    return protein, carbs, fats