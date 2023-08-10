

from flask import Flask, render_template, request, make_response, session
#from dbconfig import get_mongo_connection
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "secret"

# MongoDB connection settings
MONGO_HOST = 'localhost'  # Update with your MongoDB host
#MONGO_HOST = 'db'
MONGO_PORT = 27017  # Update with your MongoDB port
MONGO_DB = 'UnipiLibrary'  # Update with your MongoDB database name


@app.route('/', methods=['GET', "POST"])
def hello():
    return render_template('./home.html')

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
    surname = request.form.get('surname')
    email = request.form.get('email')
    password = request.form.get('password')
    birthday = request.form.get('birthday')

    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['users']

        # Check if a user with the same email already exists
        existing_user = collection.find_one({'email': email})
        if existing_user:
            return 'A user with the same email already exists.</p><a href="sign_up"><button>Try Again</button><a href="sign_in"><button>sign-in</button></h4>'
        
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
            return '<h4> Your account has been created successfully!</p><a href="home"><button>return</button></h4>'
        else:
            return 'Failed to create user'
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"

    
@app.route('/sign_in', methods=['GET', 'POST'])
def login_form():
    return render_template('./sign_in.html')
    
@app.route('/sign_in2', methods=['GET','POST'])
def authentication():
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
        trait = exists.get('trait', 'default_trait_value')
        session["exists"] = True
        session["email"] = email  # Store the email in the session
        if trait == "User":
            return '<h4>Successful Authentication! You are an User</p><a href="user_home"><button>Continue</button></h4>'
        if trait == "Admin":
            return '<h4>Successful Authentication! You are an Admin</p><a href="admin_home"><button>Continue</button></h4>'
    else:
            return '<h4>Authentication Failed!</p></p><a href="sign_in"><button>Try Again</button><a href="home"><button>Return</button></h4>'
        
#end the session and send user to home page
@app.route('/sign_out', methods=['GET'])
def sign_out():
    # Clear the session and redirect to the home page
    session.clear()
    return render_template('/home.html')


#render user page template and make sesssion 
@app.route('/user_home', methods=['GET', 'POST'])
def user_page():
    if "email" in session:
        user_email = session["email"]
        return render_template('./user_home.html', user_email=user_email, session=session)
    else:
        return "User not authenticated."



#render admin page template
@app.route('/admin_home', methods=['GET', 'POST'])
def admin_page():
    return render_template('./admin_home.html')



@app.route('/book_insert_route', methods=['GET', 'POST'])
def admin_page_book():
    return render_template('./book_insert.html')



@app.route('/insert_book', methods=['POST'])
def create_book():
    # Get user inputs
    title = request.form.get('title')
    author = request.form.get('author')
    ISBN = request.form.get('ISBN')
    description = request.form.get('description')
    num_pages = request.form.get('num_pages')
    due_date = request.form.get('due_date')

    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['books']

        # Check if a book with the same ISBN already exists
        existing_book = collection.find_one({'ISBN': ISBN})
        if existing_book:
            return '<h4>A book with the same ISBN already exists<a href="book_insert_route"></p><button>Try Again</button></h4>'
        
        # Create a new book
        book = {
            'title': title,
            'author': author,
            'ISBN': ISBN,
            'description': description,
            'num_pages': num_pages,
            'due_date': due_date,
            'status' :  'Available'
        }
        
        # Insert the book document into the 'books' collection
        result = collection.insert_one(book)

        if result.inserted_id:
            success_message = f"Book '{title}' has been added successfully!"
            return f'<h4>{success_message}<a href="admin_home"></p><button>Return</button></h4>'        
        else:
            return 'Failed to create book'
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"
