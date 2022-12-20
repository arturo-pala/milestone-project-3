import os, pymongo, math, random
from flask import Flask, render_template, redirect, request, url_for, request, session, g, abort, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'onlineCookbook'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost')

app.secret_key = os.getenv('SECRET', 'randomstring123')

mongo = PyMongo(app)

recipes = mongo.db.recipes
recipeCategory = mongo.db.recipeCategory
allergens = mongo.db.allergens
skillLevel = mongo.db.skillLevel
userDB = mongo.db.users

@app.route('/')
@app.route('/index/1')
def index():
    tags = recipes.distinct("recipe_tags")
    random.shuffle(tags)
    username=session.get('username')
    #Count the number of recipes for the featured slider
    featured_recipes = recipes.find({'featured_recipe': 'on'})
    count_featured_recipes = featured_recipes.count()    
    return render_template('index.html', recipes=recipes.find().sort('date_time',pymongo.DESCENDING), 
    recipeCategory=recipeCategory.find(), page=1, tags=tags, page_title='Lemon & Ginger, Recipe Finder', count_featured_recipes=count_featured_recipes)

@app.route('/get_recipes')
def get_recipes():
    return render_template('get_recipes.html', recipes = recipes.find().sort('date_time',pymongo.DESCENDING), 
                            recipeCategory=recipeCategory.find())
