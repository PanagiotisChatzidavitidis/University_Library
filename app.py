''' 

Τρεψω την εντολη
.venv\Scripts\activate
και την
set FLASK_APP=app

Για να την τρεξω
flask run


'''



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

x=''

def connect_to_db():
    try:
        #print(pymongo.__version__)
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return None

@app.route('/home')
def home():
    # Render the home page template
    return render_template('./home.html')

@app.route('/register', methods=['GET', 'POST'])
def register_form():
    return render_template('./register.html')

@app.route('/register_complete', methods=['GET', 'POST'])
def registerpage():
    # Get user inputs from the request form data
    name = request.form.get('name')
    surname= request.form.get('surname')
    email = request.form.get('email')
    password = request.form.get('password')
    birthday = request.form.get('birthday')


    # Connect to MongoDB
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['users']

        # Create a new user document
        user = {
            'name': name,
            'surname': surname,
            "email": email,
            'password': password,
            'birthday': birthday
            
        }

        # Insert the user document into the 'users' collection
        result = collection.insert_one(user)

        if result.inserted_id:
            return '<p> User created successfully </p><a href="login_form"><button>Login</button></a>'
        else:
            return 'Failed to create user'
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"
    
@app.route('/login_form', methods=['GET', 'POST'])
def login_form():
    return render_template('./login_form.html')
    
@app.route('/login', methods=['GET','POST'])
def crosscheck_login():
    global x
    # Connect to MongoDB
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['users']
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"
    
    email = request.form['email']
    password = request.form['password']
        
    if ((email == 'Admin') and (password == "Admin")):
        x='a'
        return render_template('./admin_page.html')
    else:

        result = collection.find_one({'email':email,'password': password})
        if result:
            x='u'
            return render_template('./user_page.html')
        else:
            return "Invalid username or password."
        
@app.route('/flight_creation_form', methods=['GET', 'POST'])
def flight_creation_form():
    if (x =='a'):
        return render_template('./flight_creation.html')
    else:
        print(x)
        # Render the template
        rendered_template = render_template('hackerman.html')

         # Create a response with the rendered template
        response = make_response(rendered_template)

        # Set the HTTP status code
        response.status_code = 401  # Replace with the desired status code

        # Return the response
        return response
        
@app.route('/flight_creation', methods=['POST'])
def flight_creation():
    # Get user inputs from the request form data
    start = request.form.get('start')
    stop = request.form.get('stop')
    flight_date = request.form.get('flight_date')
    business_price = request.form.get('business_price')
    economy_price = request.form.get('economy_price')
    business_seats = request.form.get('business_seats')
    economy_seats = request.form.get('economy_seats')

    # Connect to MongoDB
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['flights']

        # Create a new user document
        flight = {
            'start': start,
            'stop': stop,
            'flight_date': flight_date,
            'business_price': business_price,
            'economy_price': economy_price,
            'economy_seats':economy_seats,
            'business_seats': business_seats
            
        }

        # Insert the user document into the 'users' collection
        result = collection.insert_one(flight)

        if result.inserted_id:
            return render_template('./admin_page.html')        
        else:
            return 'Failed to create user'
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"

@app.route('/view_flights')
def view_flights():
    if request.method == 'POST':
        if 'update' in request.form:
            # Retrieve updated values from the form
            flight_id = request.form.get('flight_id')
            business_price = float(request.form.get('business_price'))
            economy_price = float(request.form.get('economy_price'))

            # Update the flight document in MongoDB
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            collection = db['flights']

            # Update the "business_price" and "economy_price" fields
            collection.update_one({'_id': flight_id}, {'$set': {'business_price': business_price, 'economy_price': economy_price}})
        
        elif 'delete' in request.form:
            # Retrieve flight ID to delete
            flight_id = request.form.get('flight_id')
            
            # Delete the flight document from MongoDB
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            collection = db['flights']
            collection.delete_one({'_id': flight_id})

    # Retrieve all documents from the "flights" collection
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    collection = db['flights']
    flights = collection.find()

    if(x !=''):
        return render_template('flights.html', flights=flights)
    else:
        # Render the template
        rendered_template = render_template('hackerman.html')

         # Create a response with the rendered template
        response = make_response(rendered_template)

        # Set the HTTP status code
        response.status_code = 401  # Replace with the desired status code

        # Return the response
        return response
    
@app.route('/flight_delete_form', methods=['GET', 'POST'])
def flight_delete_form():
    if(x =='a'):
        return render_template('./flight_delete.html')
    else:
        # Render the template
        rendered_template = render_template('hackerman.html')

         # Create a response with the rendered template
        response = make_response(rendered_template)

        # Set the HTTP status code
        response.status_code = 401  # Replace with the desired status code

        # Return the response
        return response
    
@app.route('/flight_delete', methods=['POST'])
def flight_delete():
        # Retrieve all documents from the "flights" collection
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    collection = db['flights']
    flights = collection.find()
    
    flight_id = request.form.get('flight_id')

    collection.delete_one({'_id': ObjectId(flight_id)})
    return render_template('./admin_page.html')

@app.route('/modifyprice_form', methods=['GET' ,'POST'])
def modifyform():
    if(x !=''):
        return render_template('./modifyprice.html')
    else:
        # Render the template
        rendered_template = render_template('hackerman.html')

         # Create a response with the rendered template
        response = make_response(rendered_template)

        # Set the HTTP status code
        response.status_code = 401  # Replace with the desired status code

        # Return the response
        return response
    
@app.route('/modifyprice', methods=['POST'])
def modify_price():
    if request.method == 'POST':
        # Retrieve the new economy_price value from the form
        flight_id = request.form.get('flight_id')
        new_business_price= float(request.form.get('new_business_price'))
        new_economy_price = float(request.form.get('new_economy_price'))
        
        # Connect to MongoDB
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['flights']
        if (new_economy_price != ""):
            # Update the document with the specified ID
            result = collection.update_one(
                {'_id': ObjectId(flight_id)},
                {'$set': {'economy_price': new_economy_price}}
            )
            
        if(new_business_price != ""):
            # Update the document with the specified ID
            result = collection.update_one(
                {'_id': ObjectId(flight_id)},
                {'$set': {'business_price': new_business_price}}
            )
        return render_template('./admin_page.html')

@app.route('/find_flight_form', methods=['GET', 'POST'])
def find_flight_form():
    if(x !=''):
        return render_template('./find_flight.html')
    else:
        # Render the template
        rendered_template = render_template('hackerman.html')

         # Create a response with the rendered template
        response = make_response(rendered_template)

        # Set the HTTP status code
        response.status_code = 401  # Replace with the desired status code

        # Return the response
        return response
    
@app.route('/find_flight', methods=['GET','POST'])
def find_flight():
    # Connect to MongoDB
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    collection = db['flights']

    if request.method == 'POST':
        # Get the start and stop values from the form
        start = request.form.get('start')
        stop = request.form.get('stop')
        flight_date= request.form.get('flight_date')
        
        # Perform the search query
        if (flight_date == ''):
            flights = collection.find({'start': start, 'stop': stop })
            return render_template('find_flight.html', flights=flights, start=start, stop=stop)
        elif(stop==''):
            flights = collection.find({'start': start, 'flight_date': flight_date })
            return render_template('find_flight.html', flights=flights, start=start, flight_date=flight_date)
        else:
            flights = collection.find({'start': start, 'stop': stop, 'flight_date': flight_date, })
            return render_template('find_flight.html', flights=flights, start=start, stop=stop , flight_date=flight_date)

@app.route('/delete_account_form', methods=['GET', 'POST'])
def delete_account_form():
    if(x =='u'):
        return render_template('./account_delete.html')
    else:
        # Render the template
        rendered_template = render_template('hackerman.html')

         # Create a response with the rendered template
        response = make_response(rendered_template)

        # Set the HTTP status code
        response.status_code = 401  # Replace with the desired status code

        # Return the response
        return response

@app.route('/account_delete', methods=['POST'])
def account_delete():
        # Retrieve all documents from the "flights" collection
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    collection = db['users']
    
    email = request.form.get('email')
    password = request.form.get('password')
    result = collection.find_one({'email':email,'password': password})
    if result:
        collection.delete_one({'email': email})
    return render_template('./home.html')

@app.route('/user_find_flight_form', methods=['GET', 'POST'])
def user_find_flight_form():
    if(x =='u'):
        return render_template('./user_find_flight.html')
    else:
        # Render the template
        rendered_template = render_template('hackerman.html')

         # Create a response with the rendered template
        response = make_response(rendered_template)

        # Set the HTTP status code
        response.status_code = 401  # Replace with the desired status code

        # Return the response
        return response
    
@app.route('/user_find_flight', methods=['GET','POST'])
def user_find_flight():
    # Connect to MongoDB
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    collection = db['flights']

    if request.method == 'POST':
        # Get the start and stop values from the form
        start = request.form.get('start')
        stop = request.form.get('stop')
        flight_date= request.form.get('flight_date')
        
        # Perform the search query
        if (flight_date == ''):
            flights = collection.find({'start': start, 'stop': stop })
            return render_template('user_find_flight.html', flights=flights, start=start, stop=stop)
        elif(stop==''):
            flights = collection.find({'start': start, 'flight_date': flight_date })
            return render_template('user_find_flight.html', flights=flights, start=start, flight_date=flight_date)
        else:
            flights = collection.find({'start': start, 'stop': stop, 'flight_date': flight_date, })
            return render_template('user_find_flight.html', flights=flights, start=start, stop=stop , flight_date=flight_date)