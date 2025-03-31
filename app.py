import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS to allow your frontend
CORS(app, resources={r"/*": {"origins": ["https://complainform.vercel.app/", "http://127.0.0.1:5500"]}}, supports_credentials=True)

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

# Handle CORS Preflight Request for POST
@app.route('/submit_complaint', methods=['OPTIONS'])
def handle_options():
    response = jsonify({"message": "CORS Preflight Handled"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "OPTIONS, POST")
    return response, 204

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

    # Include CORS headers in response
    response = jsonify({"message": "Complaint submitted successfully!", "ticket_number": ticket})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "OPTIONS, POST")
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render uses assigned port
    app.run(host="0.0.0.0", port=port)

