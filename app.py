from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
import random
import string
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)

CORS(app)
# PostgreSQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

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

# Generate Ticket Number
def generate_ticket():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# Create Tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return jsonify({"message": "Complaint Management System is running!"})

# Submit Complaint
@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    data = request.json
    ticket = generate_ticket()
    
    new_complaint = Complaint(
        name=data["name"],
        email=data["email"],
        complaint=data["complaint"],
        ticket_number=ticket
    )
    db.session.add(new_complaint)
    db.session.commit()

    # Send Confirmation Email
    msg = Message("Complaint Received", sender=app.config['MAIL_USERNAME'], recipients=[data["email"]])
    msg.body = f"Dear {data['name']},\n\nYour complaint has been received.\nYour Ticket Number: {ticket}.\nWe will update you once it is resolved.\n\nThank you."
    mail.send(msg)

    return jsonify({"message": "Complaint submitted successfully!", "ticket_number": ticket})

# ✅ Check Complaint Status
@app.route("/check_status/<ticket_number>", methods=["GET"])
def check_status(ticket_number):
    complaint = Complaint.query.filter_by(ticket_number=ticket_number).first()
    if not complaint:
        return jsonify({"message": "Ticket not found"}), 404
    return jsonify({
        "ticket_number": complaint.ticket_number,
        "status": complaint.status,
        "name": complaint.name,
        "email": complaint.email,
        "complaint": complaint.complaint
    })

# ✅ Mark Complaint as Resolved
@app.route("/resolve_complaint/<ticket_number>", methods=["PUT"])
def resolve_complaint(ticket_number):
    complaint = Complaint.query.filter_by(ticket_number=ticket_number).first()
    if not complaint:
        return jsonify({"message": "Ticket not found"}), 404

    complaint.status = "resolved"
    db.session.commit()

    # Send Resolution Email
    msg = Message("Complaint Resolved", sender=app.config['MAIL_USERNAME'], recipients=[complaint.email])
    msg.body = f"Dear {complaint.name},\n\nYour complaint with Ticket Number {ticket_number} has been resolved.\n\nThank you for your patience!"
    mail.send(msg)

    return jsonify({"message": "Complaint resolved and email sent!"})

if __name__ == "__main__":
    app.run(debug=True)
