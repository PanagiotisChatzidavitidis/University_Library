

from flask import Flask, render_template, request, make_response, session
#from dbconfig import get_mongo_connection
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from functools import wraps


app = Flask(__name__)
app.secret_key = "secret"

# MongoDB connection settings
MONGO_HOST = 'localhost'  # Update with your MongoDB host
#MONGO_HOST = 'db'
MONGO_PORT = 27017  # Update with your MongoDB port
MONGO_DB = 'UnipiLibrary'  # Update with your MongoDB database name

access = "guest"  # Initialize the access value

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
    global access
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
        access=trait
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
    global access
    access = "guest"
    session.clear()
    return render_template('./home.html')


# Define user traits and their corresponding authorized routes
USER_TRAITS_ROUTES = {
    "User": ["user_home", "user_book_display", "user_search", "user_view_book","user_return_books","user_book_selection","user_rents","user_delete_account"],
    "Admin": ["admin_home", "admin_book_insert_route", "admin_delete_book", "admin_update_due_date","insert_book","admin_display_books"],
}



# Middleware function to check access
def check_access(route):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if access in USER_TRAITS_ROUTES:
                if route in USER_TRAITS_ROUTES[access]:
                    return view_func(*args, **kwargs)
                else:
                    return render_template('unauthorized_access.html', access=access)
            else:
                return render_template('unauthorized_access.html', access=access)
        return wrapper
    return decorator

# Apply the middleware to routes
@app.route('/user_home')
@check_access("user_home")
def user_page():
    if "email" in session:
        user_email = session["email"]
        return render_template('./user_home.html', user_email=user_email, session=session)
    else:
        return "User not authenticated."

@app.route('/admin_home')
@check_access("admin_home")
def admin_page():
    return render_template('./admin_home.html')


@app.route('/admin_book_insert_route', methods=['GET', 'POST'])
@check_access("admin_book_insert_route")
def admin_page_book():
    return render_template('./admin_book_insert.html')



@app.route('/insert_book', methods=['POST'])
@check_access("insert_book")
def create_book():
    # Get user inputs
    title = request.form.get('title')
    author = request.form.get('author')
    release_date = request.form.get('release_date')
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
            return '<h4>A book with the same ISBN already exists<a href="admin_book_insert_route"></p><button>Try Again</button></h4>'
        
        # Create a new book
        book = {
            'title': title,
            'author': author,
            'release_date': release_date,
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

#Display books
@app.route('/user_book_display')
@check_access("user_book_display")

def display_books():
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['books']

        books = collection.find({})  # Fetch all books from the collection

        return render_template('./user_book_display.html', books=books)
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"
    
@app.route('/user_view_book/<isbn>')
def user_view_book(isbn):
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['books']

        book = collection.find_one({'ISBN': isbn})  # Fetch the selected book

        return render_template('./user_view_book.html', book=book)
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"

#render view books
@app.route('/user_book_display', methods=['GET', 'POST'])
@check_access("user_book_display")
def user_book_display():
    return render_template('./user_book_display.html')

#render search page
@app.route('/user_search')
@check_access("user_search")
def search_form():
    return render_template('./user_search.html')
#render search bar funtionality
@app.route('/user_search_results', methods=['GET'])

def user_search_results():
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['books']

        search_query = request.args.get('search_query')

        # Search for books by title, author, ISBN, and availability
        books = collection.find({
            '$or': [
                {'title': {'$regex': search_query, '$options': 'i'}},
                {'author': {'$regex': search_query, '$options': 'i'}},
                {'ISBN': {'$regex': search_query, '$options': 'i'}},
                {'status': {'$regex': search_query, '$options': 'i'}}
            ]
        })

        return render_template('./user_search.html', books=books)
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"
    
    
    # Display book selection
@app.route('/user_book_selection')
@check_access("user_book_selection")
def user_book_selection():
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['books']

        books = collection.find({})  # Fetch all books from the collection

        return render_template('./user_book_selection.html', books=books)
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"


# Rent Book
@app.route('/user_rent_book/<isbn>', methods=['GET'])
def user_rent_book(isbn):
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['books']

        book = collection.find_one({'ISBN': isbn})
        if not book:
            return 'Book not found'

        return render_template('./user_rent_book.html', book=book)
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"



# Confirm Rent
@app.route('/user_confirm_rent/<isbn>', methods=['POST'])
def user_confirm_rent(isbn):
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        books_collection = db['books']
        rents_collection = db['rents']

        book = books_collection.find_one({'ISBN': isbn})
        if not book:
            return 'Book not found'

        contact_phone = request.form.get('contact_phone')

        if book['status'] == 'Available':
            user_email = session['email']
            user = db['users'].find_one({'email': user_email})

            if user:
                user_name = user['name']
                user_surname = user['surname']

                due_date = int(book['due_date'])  # Replace 'due_date' with the actual field name

                # Calculate return date based on rent date and due date
                rent_date = datetime.now()
                return_date = rent_date + timedelta(days=due_date)

                rental_record = {
                    'user_email': user_email,
                    'user_name': user_name,
                    'user_surname': user_surname,
                    'book_ISBN': isbn,
                    'rent_date': rent_date,
                    'return_date': return_date,  # Store the calculated return date
                    'contact_phone': contact_phone,
                    'rent_status': 'holding'
                }

                rents_collection.insert_one(rental_record)
                books_collection.update_one({'ISBN': isbn}, {'$set': {'status': 'Unavailable'}})

                return render_template('user_rent_result.html', result_message='Book successfully rented!')
            else:
                return render_template('user_rent_result.html', result_message='User not found')
        else:
            return render_template('user_rent_result.html', result_message='Book is not available for rent')
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"




# Display User Rents
@app.route('/user_rents')
@check_access("user_rents")
def user_rents():
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        rents_collection = db['rents']

        user_email = session['email']
        user_rents = rents_collection.find({'user_email': user_email})

        return render_template('user_rents.html', user_rents=user_rents)
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"
    

# Delete User Account
@app.route('/user_delete_account', methods=['GET', 'POST'])
@check_access("user_delete_account")
def user_delete_account():
    if "email" in session:
        if request.method == 'POST':
            try:
                client = MongoClient(MONGO_HOST, MONGO_PORT)
                db = client[MONGO_DB]
                users_collection = db['users']

                user_email = session['email']

                # Delete user account
                result = users_collection.delete_one({'email': user_email})

                if result.deleted_count > 0:
                    # Clear session and redirect to the home page after successful deletion
                    session.clear()
                    return render_template('user_delete_account.html', message='Your account has been deleted.')
                else:
                    return render_template('user_delete_account.html', message='Failed to delete your account.')
            except Exception as e:
                return f"Error connecting to MongoDB: {str(e)}"
        else:
            return render_template('user_delete_account_confirmation.html')
    else:
        return "User not authenticated."


@app.route('/admin_delete_book', methods=['GET', 'POST'])
@check_access("admin_delete_book")
def admin_delete_book():
    if request.method == 'POST':
        isbn = request.form.get('isbn')

        try:
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            collection = db['books']

            book = collection.find_one({'ISBN': isbn})
            if not book:
                return 'Book not found</p><a href="admin_delete_book"><button>Delete another book</button><a href="admin_home"><button>Return</button>'

            if book['status'] == 'Unavailable':
                return 'Book has not been returned yet. Try again later.</p><a href="admin_delete_book"><button>Delete another book</button><a href="admin_home"><button>Return</button>'

            # Delete the book from the collection
            result = collection.delete_one({'ISBN': isbn})
            if result.deleted_count > 0:
                return 'Book deleted successfully</p><a href="admin_delete_book"><button>Delete another book</button><a href="admin_home"><button>Return</button>'
            else:
                return 'Failed to delete book'
        except Exception as e:
            return f"Error connecting to MongoDB: {str(e)}"
    else:
        try:
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            collection = db['books']

            # Fetch available books from the collection
            available_books = collection.find({'status': 'Available'})

            return render_template('admin_delete_book.html', available_books=available_books)
        except Exception as e:
            return f"Error connecting to MongoDB: {str(e)}"


# Update Due Date with Dropdown
@app.route('/admin_update_due_date', methods=['GET', 'POST'])
@check_access("admin_update_due_date")
def admin_update_due_date():
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['books']

        available_books = collection.find({'status': 'Available'})  # Fetch available books from the collection

        if request.method == 'POST':
            isbn = request.form.get('isbn')
            new_due_date = int(request.form.get('due_date'))
            
            book = collection.find_one({'ISBN': isbn})
            if not book:
                return 'Book not found'

            # Update the due_date of the book
            result = collection.update_one({'ISBN': isbn}, {'$set': {'due_date': new_due_date}})
            if result.modified_count > 0:
                return 'Rent days updated successfully</p><a href="admin_update_due_date"><button>Update Another Book</button><a href="admin_home"><button>Return</button>'
            else:
                return 'Failed to update rent days</p><a href="admin_update_due_date"><button>Update Another Book</button><a href="admin_home"><button>Return</button>'

        return render_template('admin_update_due_date.html', available_books=available_books)
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"

#display books for admin
@app.route('/admin_display_books')
@check_access("admin_display_books")
def admin_display_books():
    try:
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['books']
        rents_collection = db['rents']

        books = collection.find({})  # Fetch all books from the collection

        book_data = []

        for book in books:
            book_entry = {
                'title': book['title'],
                'author': book['author'],
                'release_date': book['release_date'],
                'ISBN': book['ISBN'],
                'description': book['description'],
                'num_pages': book['num_pages'],
                'due_date': book['due_date'],
                'status': book['status']
            }

            if book['status'] == 'Unavailable': # if somebody has rented this book fetch their rent details
                rent = rents_collection.find_one({'book_ISBN': book['ISBN']})
                if rent:
                    rent_details = {
                        'user_name': rent['user_name'],
                        'user_surname': rent['user_surname'],
                        'user_email': rent['user_email'],
                        'rent_date': rent['rent_date'],
                        'return_date': rent['return_date'],
                        'contact_phone': rent['contact_phone']
                    }
                    book_entry['rent_details'] = rent_details

            book_data.append(book_entry)

        return render_template('admin_display_books.html', books=book_data)
    except Exception as e:
        return f"Error connecting to MongoDB: {str(e)}"

#return book 
@app.route('/user_return_books', methods=['GET', 'POST'])
@check_access("user_return_books")
def user_return_books():
    if "email" in session:
        user_email = session["email"]
        try:
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            rents_collection = db['rents']
            books_collection = db['books']

            # Fetch rents with rent_status 'holding' for the logged-in user
            user_rents = rents_collection.find({'user_email': user_email, 'rent_status': 'holding'})

            if request.method == 'POST':
                rent_id = request.form.get('rent_id')

                # Update the rent_status to 'returned' in rents collection
                result = rents_collection.update_one({'_id': ObjectId(rent_id)}, {'$set': {'rent_status': 'returned'}})

                if result.modified_count > 0:
                    # Get the book ISBN from the rent
                    rent = rents_collection.find_one({'_id': ObjectId(rent_id)})
                    if rent:
                        book_isbn = rent['book_ISBN']

                        # Update the book status to 'Available' in books collection
                        books_collection.update_one({'ISBN': book_isbn}, {'$set': {'status': 'Available'}})
                        return 'Book returned successfully</p><a href="user_return_books"><button>Return another book</button><a href="user_home"><button>Return home</button>'
                    else:
                        return 'Failed to find book information'
                else:
                    return 'Failed to return book'

            return render_template('user_return_books.html', user_rents=user_rents)
        except Exception as e:
            return f"Error connecting to MongoDB: {str(e)}"
    else:
        return "User not authenticated."

