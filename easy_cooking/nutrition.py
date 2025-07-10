import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
from easy_cooking.models import db, Recipe, nutritions


def get_nutrition_by_id(id):
    nutrition = None

    nutrition = nutritions.get_nutrition(id)
    if nutrition:
        print("nutrition is in the database")
        print(nutrition.nutrition_data)

        # print(type(nutrition))
        # print(type(nutrition.nutrition_data))
        nutrition = nutrition.nutrition_data
    if not nutrition:
        target = Recipe.get_recipe_by_id(id)
        nutrition = get_nutrition_from_api(target)
        if nutrition:
            nutritions.add_new_nutrition(id, nutrition)
            print(nutrition)
            
    return nutrition


def update_nutrition_by_id(id):
    print("updating nutrition")

    target = Recipe.get_recipe_by_id(id)
    nutrition = get_nutrition_from_api(target)

    # print("start")
    # print(nutrition)
    # print("end")
    
    cart_item = nutritions.query.filter_by(rid=id).first()
    cart_item.nutrition_data = nutrition
    db.session.commit()


def get_nutrition_from_api(target):
    title = target.name
    ingredients = target.ingredients
    quantity = target.quantity
    measurements = target.measurement

    print(f"api called for {title}")

    splited_ingredients = []
    for ingredient in ingredients:
        temp = ingredient.split(", ")
        splited_ingredients.append(temp[0])

    splited_measurement = []
    for measurement in measurements:
        if measurement == " ":
            splited_measurement.append("whole")
        else:
            splited_measurement.append(measurement)
    
    print(splited_ingredients)
    print(quantity)
    print(splited_measurement)

    nutrition_api = os.getenv("NUTRITION_API")
    app_id = os.getenv("NUTRITION_API_ID")

    url = "https://api.edamam.com/api/nutrition-details"

    parameters = {"app_id": app_id, "app_key": nutrition_api, "beta": "false"}

    body = {
        "title": title,
        "ingr": []
    }
    
    for i in range(len(splited_ingredients)):
        body["ingr"].append(f"{quantity[i]} {splited_measurement[i]} {splited_ingredients[i]}")

    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    try:
        r = requests.post(url, params=parameters, data=json.dumps(body), headers=headers)
    except:
        print(f"Error occur when fetch api for {title}")
        return None

    overall_dict = {}
    # print("start")
    # print(r.json())
    # print("end")
    try:
        nutrition_dict = (r.json())["totalNutrients"]
    except KeyError:
        overall_dict = {"alert": "The given ingredients do not support nutrition analysis"}
        return overall_dict
    
    nutrition_perc_dict = (r.json())["totalDaily"]

    overall_dict["calories"] = {
        "quantity":nutrition_dict["ENERC_KCAL"]["quantity"],
        "unit": nutrition_dict["ENERC_KCAL"]["unit"],
        "percentage": nutrition_perc_dict["ENERC_KCAL"]["quantity"]
    }

    overall_dict["total_fat"] = {
        "quantity": nutrition_dict["FAT"]["quantity"],
        "unit": nutrition_dict["FAT"]["unit"],
        "percentage": nutrition_perc_dict["FAT"]["quantity"]
    }

    overall_dict["saturated_fat"] = {
        "quantity": nutrition_dict["FASAT"]["quantity"],
        "unit": nutrition_dict["FASAT"]["unit"],
        "percentage": nutrition_perc_dict["FASAT"]["quantity"]
    }

    overall_dict["trans_fat"] = {
        "quantity": nutrition_dict["FATRN"]["quantity"],
        "unit": nutrition_dict["FATRN"]["unit"],
        "percentage": None
    }

    overall_dict["cholesterol"] = {
        "quantity": nutrition_dict["CHOLE"]["quantity"],
        "unit": nutrition_dict["CHOLE"]["unit"],
        "percentage": nutrition_perc_dict["CHOLE"]["quantity"]
    }

    overall_dict["sodium"] = {
        "quantity": nutrition_dict["NA"]["quantity"],
        "unit": nutrition_dict["NA"]["unit"],
        "percentage": nutrition_perc_dict["NA"]["quantity"]
    }

    overall_dict["total_carbohydrates"] = {
        "quantity": nutrition_dict["CHOCDF"]["quantity"],
        "unit": nutrition_dict["CHOCDF"]["unit"],
        "percentage": nutrition_perc_dict["CHOCDF"]["quantity"]
    }

    overall_dict["dietary_fiber"] = {
        "quantity": nutrition_dict["FIBTG"]["quantity"],
        "unit": nutrition_dict["FIBTG"]["unit"],
        "percentage": nutrition_perc_dict["FIBTG"]["quantity"]
    }

    overall_dict["total_sugar"] = {
        "quantity": nutrition_dict["SUGAR"]["quantity"],
        "unit": nutrition_dict["SUGAR"]["unit"],
        "percentage": None
    }

    overall_dict["protein"] = {
        "quantity": nutrition_dict["PROCNT"]["quantity"],
        "unit": nutrition_dict["PROCNT"]["unit"],
        "percentage": nutrition_perc_dict["PROCNT"]["quantity"]
    }

    overall_dict["vitamin_d"] = {
        "quantity": nutrition_dict["VITD"]["quantity"],
        "unit": nutrition_dict["VITD"]["unit"],
        "percentage": nutrition_perc_dict["VITD"]["quantity"]
    }

    overall_dict["calcium"] = {
        "quantity": nutrition_dict["CA"]["quantity"],
        "unit": nutrition_dict["CA"]["unit"],
        "percentage": nutrition_perc_dict["CA"]["quantity"]
    }

    overall_dict["iron"] = {
        "quantity": nutrition_dict["FE"]["quantity"],
        "unit": nutrition_dict["FE"]["unit"],
        "percentage": nutrition_perc_dict["FE"]["quantity"]
    }

    overall_dict["Potassium"] = {
        "quantity": nutrition_dict["K"]["quantity"],
        "unit": nutrition_dict["K"]["unit"],
        "percentage": nutrition_perc_dict["K"]["quantity"]
    }


    nut_free = False
    dairy_free = False
    Vegetarian = False
    
    health_labels = (r.json())["healthLabels"]
    if ("PEANUT_FREE" in health_labels) and ("TREE_NUT_FREE" in health_labels):
        nut_free = True
    if "DAIRY_FREE" in health_labels:
        dairy_free = True
    if "VEGETARIAN" in health_labels:
        Vegetarian = True

    overall_dict["nut_free"] = nut_free
    overall_dict["dairy_free"] = dairy_free
    overall_dict["Vegetarian"] = Vegetarian

    return overall_dict
