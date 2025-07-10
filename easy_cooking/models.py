from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from datetime import datetime

db = SQLAlchemy()

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key for the recipe table
    uid = db.Column(db.String(100), nullable=False)  # User ID of the person who created the recipe
    time = db.Column(db.DateTime, default=datetime.now)  # Timestamp when the recipe was created
    name = db.Column(db.String(100), nullable=False)  # Name of the recipe
    category = db.Column(db.String(100), nullable=False)  # Recipe category (e.g., Chinese, Italian)
    difficulty = db.Column(db.String(50), nullable=False)  # Difficulty level of the recipe (e.g., Easy, Medium)
    spiciness = db.Column(db.String(50), nullable=False)  # Spiciness level of the recipe
    nut_free = db.Column(db.Boolean, default=False)  # Whether the recipe is nut-free
    vegan = db.Column(db.Boolean, default=False)  # Whether the recipe is vegan
    dairy_free = db.Column(db.Boolean, default=False)  # Whether the recipe is dairy-free
    description = db.Column(db.String(500), nullable=True)  # A brief description of the recipe
    ingredients = db.Column(ARRAY(db.String), nullable=False)  # List of ingredients required for the recipe
    quantity = db.Column(ARRAY(db.String), nullable=False)  # List of quantities corresponding to each ingredient
    measurement = db.Column(ARRAY(db.String), nullable=False)  # List of measurement units for the ingredients
    instructions = db.Column(ARRAY(db.String), nullable=False)  # Step-by-step instructions for preparing the recipe
    image = db.Column(db.String(255), nullable=True)  # URL or path to an image of the recipe
    video_link = db.Column(db.String(255), nullable=True)  # URL to a video tutorial for the recipe

    # Static method to get a recipe by its ID
    @staticmethod
    def get_recipe_by_id(recipe_id):
        return Recipe.query.get(recipe_id)

    # Static method to retrieve all recipes from the database
    @staticmethod
    def get_all_recipes():
        return Recipe.query.all()

    # Static method to filter and retrieve recipes by category
    @staticmethod
    def get_recipes_by_category(category):
        return Recipe.query.filter_by(category=category).all()



class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key for the cart table
    uid = db.Column(db.String(100), nullable=False)  # User ID associated with the cart
    created_at = db.Column(db.DateTime, default=datetime.now)  # Timestamp for when the cart was created
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # Timestamp for when the cart was last updated
    
    # Establish a one-to-many relationship with CartItem, allowing the cart to have multiple items
    items = db.relationship('CartItem', backref='cart', lazy=True)

    # Static method to add an item to the cart
    @staticmethod
    def add_to_cart(user_id, recipe_id, ingredient):
        try:
            # Query for the user's cart; if it doesn't exist, create a new cart
            cart = Cart.query.filter_by(uid=user_id).first()
            if not cart:
                cart = Cart(uid=user_id)
                db.session.add(cart)
                db.session.commit()

            # Check if the item already exists in the cart for the given recipe and ingredient
            cart_item = CartItem.query.filter_by(cart_id=cart.id, recipe_id=recipe_id, ingredient=ingredient).first()
            if not cart_item:
                # If the item doesn't exist, create a new CartItem and add it to the cart
                new_item = CartItem(
                    cart_id=cart.id, 
                    recipe_id=recipe_id, 
                    ingredient=ingredient
                )
                db.session.add(new_item)
                db.session.commit()
        except Exception as e:
            db.session.rollback()  # Roll back the transaction if any error occurs
            print(f"Error adding item to cart: {e}")

    # Static method to retrieve the user's cart and return all items
    @staticmethod
    def get_cart(user_id):
        # Query for the user's cart
        cart = Cart.query.filter_by(uid=user_id).first()
        if cart:
            return cart.items  # Return all items in the cart
        return []  # If no cart exists, return an empty list



class CartItem(db.Model):
    __tablename__ = 'cart_item'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)  # Foreign key linking to the user's cart
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.rid'), nullable=False)  # Foreign key linking to the related recipe

    # Store ingredient details as a string (e.g., "Tomato, Onion, Garlic")
    ingredient = db.Column(ARRAY(db.String), nullable=False)
    checking = db.Column(ARRAY(db.Boolean), nullable=False)  # Step-by-step instructions for preparing the recipe

    # Establish a relationship with the Recipe model, allowing access to the related recipe from the cart item
    recipe = db.relationship('Recipe', backref='cart_items')


class nutritions(db.Model):
    __tablename__ = 'nutritions'

    nid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rid = db.Column(db.Integer, db.ForeignKey('recipes.rid', ondelete='CASCADE'), nullable=False)
    nutrition_data = db.Column(JSON, nullable=False)

    @staticmethod
    def add_new_nutrition(recipe_id, overall_dict):
        new_nutrition = nutritions(rid=recipe_id, nutrition_data=overall_dict)
        db.session.add(new_nutrition)
        db.session.commit()
    
    @staticmethod
    def get_nutrition(recipe_id):
        nutrition = nutritions.query.filter_by(rid=recipe_id).first()
        if nutrition:
            return nutrition
        else:
            None



