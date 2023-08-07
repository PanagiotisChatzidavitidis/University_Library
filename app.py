

from flask import Flask, render_template, request, make_response
#from dbconfig import get_mongo_connection
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

@app.route('/', methods=['GET', "POST"])
def hello():
    return render_template('./home.html')

# MongoDB connection settings
MONGO_HOST = 'localhost'  # Update with your MongoDB host
#MONGO_HOST = 'db'
MONGO_PORT = 27017  # Update with your MongoDB port
MONGO_DB = 'Library'  # Update with your MongoDB database name

connected='no one is connected'

def connect_to_db():
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return None

@app.route('/home')
def home():
    # Render the home
    return render_template('./home.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def register_form():
    return render_template('./sign_up.html')

@app.route('/sign_up2', methods=['GET', 'POST'])
def registerpage():
    # Gather inputs
    name = request.form.get('name')
    surname= request.form.get('surname')
    email = request.form.get('email')
    password = request.form.get('password')
    birthday = request.form.get('birthday')

    #MongoDB Connection
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['users']
        
        # User Creation
        user = {
            'name': name,
            'surname': surname,
            "email": email,
            'password': password,
            'birthday': birthday,
            'trait': "User" 
        }

        # Insert in users collection
        result = collection.insert_one(user)

        if result.inserted_id:
            return '<h4> Your account has been created successfully!</p><a href="sign_in"><button>Login</button></h4>'
        else:
            return 'Failed to create user'
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"
    
@app.route('/sign_in', methods=['GET', 'POST'])
def login_form():
    return render_template('./sign_in.html')
    
@app.route('/sign_in2', methods=['GET','POST'])
def crosscheck_login():
    global connected
    #MongoDB Connection
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['users']
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"
    
    email = request.form['email']
    password = request.form['password']
    
    exists = collection.find_one({'email':email,'password': password})
    if exists:

            return '<h4>Successful Authentication!</p><a href="user_home"><button>Continue</button></h4>'
    else:
            return "<h4>Authentication Failed<h4>!"
        
@app.route('/user_home', methods=['GET', 'POST'])
def user_page():
    return render_template('./user_home.html')