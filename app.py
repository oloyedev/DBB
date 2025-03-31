import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://complainform.vercel.app/"}})

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

  
if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))