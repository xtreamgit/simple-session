# Author: Hector DeJesus
# Date: May 19, 2024
# Simple Session Example using Flask, PyMongo, and flask_session.
# Created as a simple session building block.
# Tested and working fine with the current requirements.txt.
# The session ID only changes if there is no other session ID. 
# User must logout and login to change the session ID.
# If there is no logged in user, the session is empty.

from flask import Flask, session, redirect, url_for, request, render_template_string, g
from flask_session import Session
from pymongo import MongoClient
import os
from custom_session_interface import CustomSessionInterface  # Import the custom session interface

app = Flask(__name__)

# Configure the secret key for session management
app.config['SECRET_KEY'] = 'supersecretkey'

# Configure the session to use MongoDB
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_PERMANENT'] = False
app.config["SESSION_MONGODB"] = MongoClient('mongodb://localhost:27017/')
app.config['SESSION_MONGODB_DB'] = 'mySessionDB'
app.config['SESSION_MONGODB_COLLECT'] = 'sessions'
app.config['SESSION_COOKIE_NAME'] = 'simple-user-session'

# Create a custom session interface instance
app.session_interface = CustomSessionInterface(
    uri='mongodb://localhost:27017/',
    db='mySessionDB',  # Corrected to match the configuration
    collection='sessions'
)

# Initialize the session with the app
Session(app)

# Simple login page template
login_page = """
<!doctype html>
<html>
<head><title>Login</title></head>
<body>
<h2>Login</h2>
<form action="/login" method="post">
  <p><input type=text name=username>
  <p><input type=submit value=Login>
</form>
</body>
</html>
"""

@app.before_request
def before_request():
    # Retrieve the session ID from the cookies and store it in the global object
    g.session_id = request.cookies.get(app.config['SESSION_COOKIE_NAME'])

@app.route('/')
def index():
    # Debug print to show the current session ID
    print(f"Current session ID: {g.session_id}")
    # Check if 'username' is in the session and return the appropriate response
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Clear the existing session data
        session.clear()
        # Set the 'username' in the session
        session['username'] = request.form['username']
        # Mark the session as modified to reset the session ID
        session.modified = True
        # Debug print to show the new session ID after login
        print(f"New session ID after login: {request.cookies.get(app.config['SESSION_COOKIE_NAME'])}")
        return redirect(url_for('index'))
    # Render the login page template
    return render_template_string(login_page)

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Debug print to confirm the session is cleared
    print("Session cleared")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True)
