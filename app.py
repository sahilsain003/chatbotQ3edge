import os
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
import urllib.parse
from werkzeug.exceptions import BadRequest, InternalServerError
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure MongoDB URI using environment variables
username = urllib.parse.quote_plus(os.getenv('MONGO_USERNAME'))
password = urllib.parse.quote_plus(os.getenv('MONGO_PASSWORD'))
app.config['MONGO_URI'] = (
    f"mongodb+srv://{username}:{password}@sahilsain.8c2dtu8.mongodb.net/"
    f"Chatbot?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
)

# Configure Flask-Mail using environment variables
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mongo = PyMongo(app)
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    email = data.get('email')

    if not data or not email:
        raise BadRequest("Missing data or email")

    # Check MongoDB connection
    try:
        mongo.cx.admin.command('ping')
        logging.info("MongoDB connection successful")
    except Exception as e:
        logging.error(f"MongoDB connection error: {e}")
        raise InternalServerError("Database connection error")

    # Check if the email already exists in the database
    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        raise BadRequest("Email already registered")

    # Create a new user document
    new_user = {
        "name": data.get('name'),
        "email": email,
        "qualification": data.get('qualification'),
        "linkedin": data.get('linkedin'),
        "last_company": data.get('last_company'),
        "years_experience": data.get('years_experience'),
        "unique_code": data.get('unique_code'),
        "expected_salary": data.get('expected_salary'),
        "key_skills": data.get('key_skills'),
        "notice_period": data.get('notice_period')
    }

    # Insert the new user document into the database
    try:
        mongo.db.users.insert_one(new_user)
        logging.info(f"User {email} added to MongoDB")
    except Exception as e:
        logging.error(f"Error inserting document into MongoDB: {e}")
        raise InternalServerError("Database insertion error")

    # Send an email with the new user's details
    try:
        msg = Message("New User Details", recipients=[app.config['MAIL_USERNAME']])
        msg.body = f"""
        Name: {new_user['name']}
        Email: {new_user['email']}
        Qualification: {new_user['qualification']}
        LinkedIn: {new_user['linkedin']}
        Last Company: {new_user['last_company']}
        Years of Experience: {new_user['years_experience']}
        Unique Code: {new_user['unique_code']}
        Expected Salary: {new_user['expected_salary']}
        Key Skills: {new_user['key_skills']}
        Notice Period: {new_user['notice_period']}
        """
        mail.send(msg)
        logging.info(f"Email sent to {app.config['MAIL_USERNAME']}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise InternalServerError("Email sending error")

    return jsonify({"message": "Details submitted successfully"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
