# Complaint Management API

A lightweight Flask-based API that receives, stores, and tracks user complaints with email ticket confirmation. Designed for integration with a frontend like [ComplainForm](https://complainform.vercel.app) and suitable for small businesses, internal tools, or customer feedback systems.

## ✨ Features

- Submit and store complaints in PostgreSQL
- Generates a unique ticket number for each submission
- Sends confirmation emails to users
- CORS enabled for frontend integration
- Basic status tracking for complaints

## 🔧 Technologies Used

- Python + Flask
- PostgreSQL + SQLAlchemy
- Flask-Mail (SMTP email service)
- Flask-Migrate (database migrations)
- Flask-CORS (CORS handling)
- dotenv for environment variable management

## 🚀 Getting Started

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/complaint-management-api.git
cd complaint-management-api
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/your_db
MAIL_SERVER=smtp.yourmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
```

### Step 4: Initialize the Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Step 5: Run the Server

```bash
python app.py
```

API will be available at `http://localhost:5000`.

## 🧪 API Endpoints

### `GET /`

Returns a basic message to confirm the server is up.

```json
{ "message": "Complaint Management System is running!" }
```

---

### `POST /submit_complaint`

Submit a new complaint.

#### Request Body (JSON):

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "complaint": "My product arrived damaged."
}
```

#### Response:

```json
{
  "message": "Complaint submitted successfully",
  "ticket_number": "a3f6d29c"
}
```

Also sends a confirmation email to the user with the ticket number.

## 🌍 CORS

CORS is explicitly enabled for:

```
https://complainform.vercel.app
```

Add other domains as needed in the CORS config section of `app.py`.

## 📁 Project Structure

```
.
├── app.py
├── .env
├── requirements.txt
└── migrations/  # Flask-Migrate migration history
```

## 📦 Deployment Notes

- For production, consider:
  - Running behind Gunicorn or uWSGI
  - Using Nginx as a reverse proxy
  - Setting up TLS (HTTPS)
  - Keeping secrets outside version control
  - Adding logging and rate-limiting

## 💡 Future Improvements

- Add an admin dashboard or endpoints to view and resolve complaints
- Add token authentication for admin routes
- Add complaint categorization (e.g., product, service, delivery)
- Integrate SMS notifications

---

**Developed by Olatunji Olayide Nelson**  
Making customer feedback management easier with clean APIs.
