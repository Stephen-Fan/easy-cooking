import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate
from flask import render_template, make_response
from easy_cooking.models import db, Recipe, Cart, CartItem, nutritions
from easy_cooking.nutrition import get_nutrition_by_id, update_nutrition_by_id

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = env.get('DATABASE_URL')
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
#     'connect_args': {
#         'sslmode': 'require'
#     },
#     'pool_pre_ping': True
# }
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) 

# Initialize Flask-Migrate to handle database migrations, linking the app and the database
migrate = Migrate(app, db)

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


with app.app_context():
    db.create_all()

# @app.before_first_request
# def init_db():
#     db.create_all()


# Define the home route, render the 'home.html' template, and pass the active page, user session, 
# and a pretty-printed version of the session data to the template
@app.route('/')
def home():
    return render_template('home.html', active_page='home', session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


# Define the recipes route, query all recipes from the database, and render the 'recipes.html' template.
# Pass the active page, the list of all recipes, user session, and a pretty-printed version of the session data to the template.
@app.route('/recipes')
def recipes():
    all_recipes = Recipe.query.all()
    return render_template('recipes.html', active_page='recipes', recipes=all_recipes, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


# Define the recipe detail route, filter the Recipe by the recipe_name from the URL.
# If the recipe is not found, return a 404 error.
@app.route('/recipe/<recipe_name>')
def recipe_detail(recipe_name):
    recipe = Recipe.query.filter_by(name=recipe_name).first()
    
    # print(data)
    if not recipe:
        return "Recipe not found", 404
    
    # try:
    nutrition = get_nutrition_by_id(recipe.rid)
        # print("start")
        # print(nutrition)
        # print("end")
    # except KeyError:
    #     nutritions.add_new_nutrition(recipe.rid, {"alert": "The given ingredients do not support nutrition analysis"})
    #     nutrition = {"alert": "The given ingredients do not support nutrition analysis"}

     # Get the current user's ID from the session if logged in
    user_id = session.get('user', {}).get('userinfo', {}).get('sub') if 'user' in session else None
    
    # Check if the recipe is already in the user's shopping cart
    is_in_cart = False
    if user_id:
        cart = Cart.query.filter_by(uid=user_id).first()
        if cart:
            cart_item = CartItem.query.filter_by(cart_id=cart.id, recipe_id=recipe.rid).first()
            if cart_item:
                is_in_cart = True

    # Pass the zip function to the template for usage in recipe detail rendering
    return render_template('recipe_detail.html', recipe=recipe, nutrition=nutrition, session=session.get('user'), is_in_cart=is_in_cart, zip=zip)


# Define the search route to handle GET requests.
# Get the search query from the URL parameters and convert it to lowercase.
# If no query is provided, render the 'search.html' template with no recipes.
# If a query is present, search the Recipe model for matches in name, category, difficulty, spiciness, description, or ingredients.
# Render the 'search.html' template, passing the matching recipes, active page, user session, and a pretty-printed session data to the template.
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()  # Get search query

    if not query:
        return render_template(
            'search.html',
            recipes=None, 
            active_page='search',
            session=session.get('user'),
            pretty=json.dumps(session.get('user'), indent=4)
        )

    matching_recipes = Recipe.query.filter(
        or_(
            Recipe.name.ilike(f'%{query}%'),
            Recipe.category.ilike(f'%{query}%'),
            Recipe.difficulty.ilike(f'%{query}%'),
            Recipe.spiciness.ilike(f'%{query}%'),
            Recipe.description.ilike(f'%{query}%'),
            Recipe.ingredients.any(query)  # Search within array of ingredients
        )
    ).all()

    return render_template(
        'search.html',
        recipes=matching_recipes,
        active_page='search',
        session=session.get('user'),
        pretty=json.dumps(session.get('user'), indent=4)
    )


# Define the portal route, query all recipes from the database, and render the 'portal.html' template.
# Pass the active page, the list of all recipes, user session, and a pretty-printed version of the session data to the template.
@app.route('/portal')
def portal():
    user_id = session.get('user', {}).get('userinfo', {}).get('name')
    # print(user_id)
    all_recipes = Recipe.query.filter_by(uid=user_id).all()
    return render_template('portal.html', active_page='portal', recipes=all_recipes, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


# Define the route to display recipes by category.
# Filter the recipes by either the category or difficulty matching the provided category from the URL.
# Render the 'recipes.html' template, passing the filtered recipes, category, user session, and a pretty-printed version of the session data to the template.
@app.route('/recipes/<category>')
def recipes_by_category(category):
    filtered_recipes = Recipe.query.filter((Recipe.category == category) | (Recipe.difficulty == category)).all()
    return render_template('recipes.html', category=category, recipes=filtered_recipes, session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))


# Define the route to add a new recipe, handling both GET and POST requests.
# If the request method is POST, collect form data for the new recipe, including author, name, category, difficulty, spiciness, and dietary options.
# Retrieve lists for ingredients, quantities, measurements, and instructions, as well as any image or video link provided.
# Create a new Recipe object with the provided data and add it to the database.
# After committing the changes, redirect the user to the portal page.
# If the request method is GET, render the 'new_recipe.html' template, passing user session and a pretty-printed version of session data.
@app.route('/add_new_recipe', methods=['GET', 'POST'])
def add_new_recipe():
    if request.method == 'POST':
        uid = request.form['author']
        name = request.form['recipe_name']
        category = request.form['stacked-category']
        difficulty = request.form['stacked-difficulty']
        spiciness = request.form['stacked-spiciness']
        nut_free = True if request.form.get('nut') else False
        vegan = True if request.form.get('vegetarian') else False
        dairy_free = True if request.form.get('dairy') else False
        description = request.form['description']
        ingredients = request.form.getlist('ingredients[]')
        quantity = request.form.getlist('quantity[]')
        measurement = request.form.getlist('measurement[]')
        instructions = request.form.getlist('instructions[]')
        image = request.form['recipe_image']
        video_link = request.form['recipe_video']

        response = Recipe(
            uid = uid,
            name = name,
            category = category,
            difficulty = difficulty,
            spiciness = spiciness,
            nut_free = nut_free,
            vegan = vegan,
            dairy_free = dairy_free,
            description = description,
            ingredients = ingredients,
            quantity = quantity,
            measurement = measurement,
            instructions = instructions,
            image = image,
            video_link = video_link
        )

        db.session.add(response)
        db.session.commit()

        return redirect(url_for('portal'))

    return render_template('new_recipe.html', session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))
    

# Define the route to edit an existing recipe, handling both GET and POST requests.
# If the request method is POST, update the existing recipe's fields with new form data from the user.
# After committing the changes, redirect the user to the portal page.
# If the request method is GET, retrieve the recipe by name and prepare the recipe's current details to be pre-filled in the edit form.
# Pass the recipe data, available categories, spiciness levels, difficulties, and dietary options (nut-free, vegan, dairy-free) to the template for rendering.
# Also pass user session data and pretty-printed session details, along with the zip function to iterate through lists in the template.
@app.route('/edit_recipe/<recipe_name>', methods=['GET', 'POST'])
def edit_recipe(recipe_name):
    user_id =  session.get('user', {}).get('userinfo', {}).get('sub')
    print(user_id)
    
    if request.method == 'POST':
        recipe = Recipe.query.filter_by(name=recipe_name).first()

        if recipe:
            # Update the recipe's fields with new form data
            recipe.name = request.form['recipe_name']
            recipe.category = request.form['stacked-category']
            recipe.difficulty = request.form['stacked-difficulty']
            recipe.spiciness = request.form['stacked-spiciness']
            recipe.nut_free = True if request.form.get('nut') else False
            recipe.vegan = True if request.form.get('vegetarian') else False
            recipe.dairy_free = True if request.form.get('dairy') else False
            recipe.description = request.form['description']
            recipe.ingredients = request.form.getlist('ingredients[]')
            recipe.quantity = request.form.getlist('quantity[]')
            recipe.measurement = request.form.getlist('measurement[]')
            recipe.instructions = request.form.getlist('instructions[]')
            recipe.image = request.form['recipe_image']
            recipe.video_link = request.form['recipe_video']

            db.session.commit()
            update_nutrition_by_id(recipe.rid)
            return redirect(url_for('portal')) 

    else:
        recipe = Recipe.query.filter_by(name=recipe_name).first()
        if recipe:
            categories = ['Chinese', 'Japanese', 'Korean', 'Vietnamese', 'Thai', 'American', 'Mexican', 'Italian', 'England', 'Spanish']
            selected_category = recipe.category
            spiciness = ['None', 'Mild', 'Medium', 'Hot', 'Extra Hot', 'Extreme Hot']
            selected_spiciness = recipe.spiciness
            difficulties = ['Easy', 'Medium', 'Hard']
            selected_difficulty = recipe.difficulty
            nut_free = recipe.nut_free
            vegan = recipe.vegan
            dairy_free = recipe.dairy_free
            description = recipe.description
            ingredients = recipe.ingredients
            quantities = recipe.quantity
            measurements = recipe.measurement
            instructions = recipe.instructions

            return render_template(
                'edit_recipe.html',
                recipe=recipe,
                categories=categories,
                selected_category=selected_category,
                spiciness=spiciness,
                selected_spiciness=selected_spiciness,
                difficulties=difficulties,
                selected_difficulty=selected_difficulty,
                nut_free=nut_free,
                vegan=vegan,
                dairy_free=dairy_free,
                description=description,
                ingredients=ingredients,
                quantities=quantities,
                measurements=measurements,
                instructions=instructions,
                session=session.get('user'),
                pretty=json.dumps(session.get('user'), indent=4),
                zip=zip
            )
        

# Define the route to delete a recipe, handling POST requests only.
# Get the recipe by its ID from the database.
# If the recipe exists, attempt to delete it from the database.
# If an exception occurs during the deletion process, roll back the transaction.
# After successfully deleting the recipe, redirect the user to the portal page.
@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    # print("start1")
    # print(recipe_id)
    # print("end1")
    if request.method == 'POST':
        recipe = Recipe.query.get(recipe_id)
    
    if recipe:
        # print("start2")
        # print(recipe)
        # print("end2")
        try:
            db.session.delete(recipe)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
    
    return redirect(url_for('portal'))


# Define the cart route to display the user's shopping cart.
# Get the user's ID from the session. If the user is not logged in, redirect to the login page.
@app.route('/cart')
def cart():
    user_id = session.get('user', {}).get('userinfo', {}).get('sub')
    if not user_id:
        return redirect(url_for('login'))

    # Retrieve the cart associated with the user
    cart = Cart.query.filter_by(uid=user_id).first()

    cart_items = []

    if cart:
        # Query all cart items, joining with the Recipe model to get related recipe details
        cart_items = CartItem.query.filter_by(cart_id=cart.id).join(Recipe).all()
        # for cart_item in cart_items:
        #     cart_item.

        # 清空购物车中的所有项目
        # CartItem.query.filter_by(cart_id=cart.id).delete()
        # db.session.commit()

        # Convert the ingredient string in each cart item to a list
        # for item in cart_items:
        #     if item.ingredient:
        #         item.ingredient = item.ingredient.split(', ')  # Convert stored string into a list of ingredients
        
     # Render the 'cart.html' template and pass the cart items and user session data
    for each in cart_items:
        print(each.ingredient)
        print(each.checking)

    return render_template('cart.html', cart_items=cart_items, session=session.get('user'))


# Define the route to add a recipe to the shopping cart, handling POST requests.
# Get the current user's ID from the session to ensure they are logged in. If not, redirect to the login page.
@app.route('/add_to_cart/<int:recipe_id>', methods=['POST'])
def add_to_cart(recipe_id):
    user_id = session.get('user', {}).get('userinfo', {}).get('sub')
    if not user_id:
        return redirect(url_for('login'))

    # Find the specified recipe by recipe_id
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return "Recipe not found.", 404

    # print(request.form)
    # print("--"*50)

    # 获取所有提交的成分，去除空格
    # submitted_ingredients = [ingredient.strip() for ingredient in request.form.getlist('selected_ingredients') and request.form.getlist('None_selected_ingredients')]
    # print("All submitted ingredients:", submitted_ingredients)

    #  # Get the ingredients selected by the user and clean them up by removing whitespace
    # selected_ingredients = [ingredient.strip() for ingredient in request.form.getlist('selected_ingredients')]
    # print("Selected ingredients:", selected_ingredients)

    # # Get the ingredients that were not selected by the user
    # non_selected_ingredients = [ingredient.strip() for ingredient in request.form.getlist('None_selected_ingredients')]
    # print("Non-selected ingredients:", non_selected_ingredients)

    # # Sort the ingredients with non-selected ingredients first and selected ingredients last
    # sorted_ingredients = non_selected_ingredients + selected_ingredients
    # print("Sorted ingredients:", sorted_ingredients)

    # Query or create the user's cart
    selected_ingredients = [ingredient for ingredient in request.form.getlist('selected_ingredients')]
    
    cart = Cart.query.filter_by(uid=user_id).first()
    if not cart:
        cart = Cart(uid=user_id)
        db.session.add(cart)
        db.session.commit()

    # Check if a cart item for the given recipe already exists in the user's cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, recipe_id=recipe_id).first()

    # print("form: ",request.form)


    # If the cart item already exists, update its ingredient list

    if cart_item:
        all_ingredients= cart_item.ingredient
        checking = []
        
        # print("all ingredientdsd:",all_ingredients)
        # print("selected ingredientdsd:",selected_ingredients)
        
        for each in all_ingredients:
            if each in selected_ingredients:
                checking.append(True)
            else:
                checking.append(False)


        # cart_item.ingredient = recipe.ingredients  # Update the ingredient list
        cart_item.checking = checking
        db.session.commit()

    else:
        # If the cart item does not exist, create a new one with the sorted ingredients
        checking = [False] * len(recipe.ingredients)
        new_item = CartItem(cart_id=cart.id, recipe_id=recipe_id, ingredient=recipe.ingredients, checking=checking)
        db.session.add(new_item)
        db.session.commit()

    # Redirect the user to the cart page after adding or updating the cart item
    return redirect('/cart')


# Define the route to remove a recipe from the user's shopping cart, handling POST requests.
# Get the user's ID from the session to ensure they are logged in. If not, redirect them to the login page.
@app.route('/remove_from_cart/<int:recipe_id>', methods=['POST'])
def remove_from_cart(recipe_id):
    user_id = session.get('user', {}).get('userinfo', {}).get('sub')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login page if the user is not logged in

    # Retrieve the user's cart
    cart = Cart.query.filter_by(uid=user_id).first()

    if not cart:
        return "No cart found.", 404  # Return a 404 error if no cart is found for the user

    # Find the specific cart item based on the recipe_id and the user's cart_id
    cart_item = CartItem.query.filter_by(cart_id=cart.id, recipe_id=recipe_id).first()

    # Check if the cart item exists and belongs to the user's cart
    if cart_item:
        try:
            db.session.delete(cart_item)  # Delete the cart item
            db.session.commit()  # Commit the changes to the database
        except Exception as e:
            db.session.rollback()
            return f"Error removing item from cart: {str(e)}", 500
    else:
        return "Item not found or you don't have permission to remove it.", 404

    return redirect(url_for('cart'))  # Redirect the user back to the cart page


# Define the login route to initiate OAuth login using Auth0.
# Redirect the user to the Auth0 login page, specifying the callback URL once authenticated.
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )    


# Define the callback route to handle the response after successful authentication.
# Retrieve the access token from Auth0 and store the user's token in the session.
# Redirect the user to the home page after login.
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    print(token)
    return redirect("/")


# Define the logout route to clear the session and log the user out from Auth0.
# Redirect the user back to the home page after logging out.
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

if __name__ == '__main__':
     app.run(host="0.0.0.0", port=env.get("PORT", 5000))
