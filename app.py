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
        return jsonify({"error": "Missing data or email"}), 400

    # Check if the email already exists in the database
    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Add the chat data to the new user document
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
        "notice_period": data.get('notice_period'),
        "chat_data": data.get('chat_data')  # Add chat data here
    }

    # Insert the new user document into the database along with chat data
    try:
        mongo.db.users.insert_one(new_user)
        logging.info(f"User {email} added to MongoDB with chat data")
    except Exception as e:
        logging.error(f"Error inserting document into MongoDB: {e}")
        return jsonify({"error": "Database insertion error"}), 500

    # Send an email with the new user's details and chat data
    try:
        msg = Message("New User Details with Chat Data", recipients=[app.config['MAIL_USERNAME']])
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
        
        Chat Data: {new_user['chat_data']}
        """
        mail.send(msg)
        logging.info(f"Email sent to {app.config['MAIL_USERNAME']} with chat data")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return jsonify({"error": "Email sending error"}), 500

    return jsonify({"message": "Details submitted successfully with chat data"}), 200

@app.route('/get_candidate_details', methods=['POST'])
def get_candidate_details():
    email = request.json.get('email')
    if not email:
        return jsonify({"error": "Email is required to fetch candidate details"}), 400

    # Fetch candidate details from MongoDB based on email
    candidate = mongo.db.CandidateDetails.find_one({"email": email})

    if not candidate:
        return jsonify({"error": "Candidate details not found for the provided email"}), 404

    # Prepare response with Candidate_Name and Phone Number
    response = {
        "Candidate_Name": candidate.get("Candidate_Name"),
        "Phone_Number": candidate.get("Phone_Number")
    }

    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
