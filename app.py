from flask import Flask, session, redirect, url_for, request, render_template_string, g
from flask_session import Session
from pymongo import MongoClient
from datetime import timedelta  # Import the timedelta module
from custom_session_interface import CustomSessionInterface  # Import the custom session interface

app = Flask(__name__)

# Configure the secret key for session management
app.config['SECRET_KEY'] = 'supersecretkey'

# Configure session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Configure the session to use MongoDB
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_MONGODB'] = MongoClient('mongodb://localhost:27017/')
app.config['SESSION_MONGODB_DB'] = 'mySessionDB'
app.config['SESSION_MONGODB_COLLECT'] = 'sessions'
app.config['SESSION_COOKIE_NAME'] = 'simple-user-session'

# Create a custom session interface instance
app.session_interface = CustomSessionInterface(
    uri='mongodb://localhost:27017/',
    db=app.config['SESSION_MONGODB_DB'],
    collection=app.config['SESSION_MONGODB_COLLECT']
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
        # Check if there is a session ID assigned
        if 'username' in session:
            # Print the current logged-in username
            print(f"Current logged-in user: {session['username']}")
            # Clear the existing session data
            session.clear()
            # Invalidate the session ID
            response = redirect(url_for('login'))
            response.delete_cookie(app.config['SESSION_COOKIE_NAME'])
            print("Previous user logged out and session invalidated")
            return response

        # Set the 'username' in the session
        session['username'] = request.form['username']
        # Mark the session as modified to ensure a new session ID is generated
        session.modified = True
        
        # Print the new logged-in user and session ID after login
        print(f"New logged-in user: {session['username']}")
        print(f"New session ID after login: {session.sid if session.sid else 'None'}")
        
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
