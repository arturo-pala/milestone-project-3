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

@app.route('/register')
def register():
    return render_template('register.html', recipes=recipes.find(), 
        recipeCategory=recipeCategory.find(), page=1, page_title='Register at Lemon & Ginger, Recipe Finder')


@app.route('/signup', methods=['POST'])
def signup():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    author_name = request.form.get('author_name')
    username = request.form.get('username').lower()
    password = generate_password_hash(request.form.get('password'))    
    session['username'] = username
    user = userDB.find_one({'username' : username})
    
    if user is None:
        userDB.insert_one({
            'author_name': author_name,
            'username': username,
            'password': password,
            'recipes_rated':[]
        })
        session['logged_in'] = True
        flash('Welcome to Lemon & Ginger ' + author_name)
        return signin()
    else:
        session['logged_in'] = False
        flash('Username already exists, please try again.')
    return register()


@app.route('/signin')
def signin():
    tags = recipes.distinct("recipe_tags")
    random.shuffle(tags)
    #Count the number of recipes for the featured slider
    featured_recipes = recipes.find({'featured_recipe': 'on'})
    count_featured_recipes = featured_recipes.count() 
    if not session.get('logged_in'):
        return render_template('login.html', recipeCategory=recipeCategory.find(), tags=tags, page=1, 
        page_title='Login at Lemon & Ginger Recipe Finder', count_featured_recipes=count_featured_recipes)
    else:
        return render_template('index.html', recipes=recipes.find().sort('date_time',pymongo.DESCENDING), 
        recipeCategory=recipeCategory.find(), tags=tags, page=1, page_title='Login at Lemon & Ginger, Recipe Finder', 
        count_featured_recipes=count_featured_recipes)

    @app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].lower()
    password = request.form['password']
    session['username'] = username
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    user = userDB.find_one({'username' : username})
    tags = recipes.distinct("recipe_tags")
    random.shuffle(tags)
    #Count the number of recipes for the featured slider
    featured_recipes = recipes.find({'featured_recipe': 'on'})
    count_featured_recipes = featured_recipes.count() 
    
    if not user:
        session['logged_in'] = False
        flash('User ' + session['username'] + ' cannot be found on our system. Please try again.')
        return signin()
    elif not check_password_hash(user['password'],password):
        session['logged_in'] = False
        flash('Incorrect Password, please try again.')
        return signin()   
    else:
        session['logged_in'] = True
        flash('Welcome ' + user['author_name'].capitalize())
        return render_template('index.html', recipes=recipes.find().sort('date_time',pymongo.DESCENDING), 
        recipeCategory=recipeCategory.find(), author=user['author_name'], tags=tags, page=1, 
        page_title='Welcome to Lemon & Ginger, Recipe Finder', count_featured_recipes=count_featured_recipes)        

    
@app.route('/logout')
def logout():
    session['logged_in'] = False
    tags = recipes.distinct("recipe_tags")
    random.shuffle(tags)
    #Count the number of recipes for the featured slider
    featured_recipes = recipes.find({'featured_recipe: 'on'})
    count_featured_recipes = featured_recipes.count()     
    return render_template('index.html', recipes=recipes.find().sort('date_time',pymongo.DESCENDING), 
    recipeCategory=recipeCategory.find(),tags = tags, page=1, page_title='Logout of Lemon & Ginger, Recipe Finder',
    count_featured_recipes=count_featured_recipes)  
    
@app.route('/all_recipes/<page>', methods=['GET'])
def all_recipes(page):
    tags = recipes.distinct("recipe_tags")
    random.shuffle(tags)
    #Count the number of recipes in the Database
    all_recipes = recipes.find().sort([('date_time', pymongo.DESCENDING), ('_id', pymongo.ASCENDING)]) 
    count_recipes = all_recipes.count()
    
    #Variables for Pagination
    offset = (int(page) - 1) * 6
    limit = 6
    
    recipe_pages = recipes.find().sort([("date_time", pymongo.DESCENDING), 
                    ("_id", pymongo.ASCENDING)]).skip(offset).limit(limit)
    total_no_of_pages = int(math.ceil(count_recipes/limit))
   
    return render_template('all_recipes.html',
    recipes=recipe_pages, recipeCategory=recipeCategory.find(),count_recipes=count_recipes, total_no_of_pages=total_no_of_pages, 
    page=page, page_title='All Recipes at Lemon & Ginger, Recipe Finder', tags=tags)

    @app.route('/browse_recipes/<recipe_category_name>/<page>', methods=['GET'])
def browse_recipes(recipe_category_name, page):
    tags = recipes.distinct("recipe_tags")
    random.shuffle(tags)    
    #Count the number of recipes in the Database
    all_recipes = recipes.find({'recipe_category_name': recipe_category_name}).sort([('date_time', pymongo.DESCENDING), 
    ('_id', pymongo.ASCENDING)]) 
    count_recipes = all_recipes.count()
    
    #Variables for Pagination
    offset = (int(page) - 1) * 6
    limit = 6
    
    recipe_pages = recipes.find({'recipe_category_name': recipe_category_name}).sort([("date_time", pymongo.DESCENDING), 
                    ("_id", pymongo.ASCENDING)]).skip(offset).limit(limit)
    total_no_of_pages = int(math.ceil(count_recipes/limit))
   
    return render_template('browse_recipes.html',
    recipes=recipe_pages, recipeCategory=recipeCategory.find(),count_recipes=count_recipes, total_no_of_pages=total_no_of_pages, 
    page=page, recipe_category_name=recipe_category_name, page_title='Lemon & Ginger, Recipe Finder', tags=tags)
    
