'''
This code is a Flask web application that allows users to create accounts.

The application uses SQLite as the database and includes the necessary functions to handle database connections, errors, and queries.

The main functionality of the application is the ability for users to create accounts by submitting a form with their first name,
last name, email, password, and confirmation of password. 

If the passwords match and the email does not already exist in the database,
a new user is added to the database with a timestamp of when the account was created. 

The application also includes error handling and displays success or error messages to the user.
'''


# Neccessary Imports
import sqlite3
from flask import Flask, g, render_template, request, flash
import datetime

# Define Flask Application
app = Flask(__name__)

# Set a secret key for the app to use
app.secret_key = 'abcdef12345!@#$%'

# Set the database file name
DATABASE = 'Store.db'

# Define a function to get the database connection
def get_db():
    # Get the database connection from the app context
    db = getattr(g, '_database', None)
    if db is None:
        # Create a new database connection if one does not exist
        db = g._database = sqlite3.connect(DATABASE)
        # Set the row factory to sqlite3.Row to return rows as dictionaries
        db.row_factory = sqlite3.Row
    return db

# Define a function to close the database connection when the app context is torn down
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Define an error handler for database errors
@app.errorhandler(sqlite3.Error)
def handle_database_error(error):
    return 'A database error occurred: ' + str(error), 500

# Define the root route for the app
@app.route('/')
def index():
    try:
        # Get the database connection
        db = get_db()
        # Create a cursor to execute SQL statements
        cursor = db.cursor()
        # Create a users table if it does not exist
        cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT, password TEXT, created_at DATETIME)')
        # Commit the changes to the database
        db.commit()
        # Close the cursor
        cursor.close()
        # Return the index.html template
        return render_template('index.html')
    except sqlite3.Error as e:
        # Return an error message if a database error occurs
        return 'A database error occurred: ' + str(e), 500

# Define a route to create a new user
@app.route('/create_account', methods=['POST'])
def create_user():
    # Get the database connection
    db = get_db()
    # Get the form data from the request
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Check if the passwords match
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return render_template('index.html')

    # Create a cursor to execute SQL statements
    cursor = db.cursor()
    # Check if the email already exists in the database
    cursor.execute('SELECT email FROM users WHERE email=?', (email,))
    user = cursor.fetchone()
    if user:
        # Return an error message if the email already exists
        cursor.close()
        flash('User already exists', 'error')
        return render_template('index.html')

    # Insert the new user into the users table
    cursor.execute('INSERT INTO users (first_name, last_name, email, password, created_at) VALUES (?, ?, ?, ?, ?)',
                (first_name, last_name, email, password, datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
    # Commit the changes to the database
    db.commit()
    # Close the cursor
    cursor.close()

    # Return a success message
    flash('User created successfully', 'success')   
    return render_template('index.html')


# Run Flask Application
if __name__ == '__main__':
    app.run(debug=True)