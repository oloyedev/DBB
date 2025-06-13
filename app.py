import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_cors import CORS
from flask_migrate import Migrate

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Explicitly allow CORS for 'https://complainform.vercel.app'
CORS(app, resources={r"/*": {"origins": "https://complainform.vercel.app"}}, supports_credentials=True)

# PostgreSQL Connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Email Configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

db = SQLAlchemy(app)
migrate = Migrate(app, db) 
mail = Mail(app)

# Complaint Model
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    complaint = db.Column(db.Text, nullable=False)
    ticket_number = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.String(10), default="pending")  # 'pending' or 'resolved'

# Home Route
@app.route("/")
def home():
    return jsonify({"message": "Complaint Management System is running!"})

# Handle Preflight Requests explicitly
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS Preflight Request"})
        response.headers["Access-Control-Allow-Origin"] = "https://complainform.vercel.app"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 200

# Submit Complaint
@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    data = request.json
    ticket = os.urandom(4).hex()  # Generates an 8-character alphanumeric ticket

    new_complaint = Complaint(
        name=data["name"],
        email=data["email"],
        complaint=data["complaint"],
        ticket_number=ticket
    )
    db.session.add(new_complaint)
    db.session.commit()

    # Send Confirmation Email
    msg = Message("Complaint Received", sender=app.config["MAIL_USERNAME"], recipients=[data["email"]])
    msg.body = f"Dear {data['name']},\n\nYour complaint has been received.\nYour Ticket Number: {ticket}.\nWe will update you once it is resolved.\n\nThank you."
    mail.send(msg)

    # Respond with appropriate CORS headers
    response = jsonify({"message": "Complaint submitted successfully", "ticket_number": ticket})
    response.headers["Access-Control-Allow-Origin"] = "https://complainform.vercel.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response, 200

if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))
