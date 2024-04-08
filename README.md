# Web Application README

## Overview
This Flask-based web application provides a user-friendly platform for event management. With features like user authentication, event creation, update, and visualization on a calendar, it's designed to enhance productivity and organization. The application leverages Flask extensions such as Flask-Login for handling user sessions, Flask-Migrate for database migrations, and Flask-Bcrypt for secure password hashing.

## Features
- **User Authentication**: Sign up and Sign in.
- **Event Management**: Users can add, update, or delete events.
- **Calendar View**: Events are displayed on a monthly calendar, with the ability to view details for each day.

## Technology Stack
- **Flask**: A micro web framework written in Python.
- **Flask Extensions**: Flask-Login, Flask-Migrate, Flask-Bcrypt.
- **Database**: SQLAlchemy ORM for data management.

## Deployment on Render.com
### Prerequisites
- A Render account.
- Application source code hosted on GitHub.

### Steps
1. **Log In to Render**
   - Navigate to [Render.com](https://render.com) and sign in.
2. **Create a New Web Service**
   - From your Render dashboard, select the "New +" button, then choose "Web Service".
3. **Connect Your Repository**
   - Connect to the Git provider and select the repository that contains the Flask application.
4. **Configure Your Web Service**
   - **Environment**: Select Python.
   - **Branch**: Choose the branch you want to deploy.
   - **Build Command**: Enter the command to install your dependencies, typically `pip install -r requirements.txt`.
   - **Start Command**: Use `gunicorn app:app` to start the Flask application.
   - **Environment Variables**: Add all necessary environment variables, such as `SECRET_KEY`, `DATABASE_URL`, etc.
     - `DATABASE_URL` is the internal URL from the PostgreSQL instance created on Render. Make sure to replace `postgres` with `postgresql` in the URL.
5. **Deploy**
   - Click the "Create Web Service" button. Render will automatically deploy your application.

### Accessing the Application
- Once the deployment is successful, Render will provide a `.onrender.com` subdomain to access your web app.
- Navigate to the provided URL to access your Flask application live on Render.

## Local Development
To run the application locally, ensure you have Python installed and follow these steps:
1. **Clone the Repository**
   - `git clone <repository-url>`
2. **Create a Virtual Environment**
   - `python -m venv venv`
3. **Activate the Virtual Environment**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. **Install Dependencies**
   - `pip install -r requirements.txt`
5. **Run the Application**
   - `flask run`
   - Visit `http://127.0.0.1:5000` in your web browser to access the application.

## Setting Up PostgreSQL on Render.com
This application uses PostgreSQL as its database. Render allows you to set up and connect to a PostgreSQL database.
1. **Create a PostgreSQL Database**
   - **Navigate to Your Render Dashboard**: Log in to your Render account and go to the dashboard.
   - **Add a New Database**: Click on the "New +" button at the top of the dashboard, then select "Database".
   - **Configure Your Database**: Name your database and select the appropriate region.
2. **Database Settings**
   - Once your database is created, Render will provide you with an internal connection string.
   - Modify the provided URL by replacing `postgres://` with `postgresql://`.

## Connecting to Your Database with pgAdmin4
1. **Launch pgAdmin4**
   - Open pgAdmin4 and add a new server.
   - Configure the connection with the external URL and your credentials.
2. **Creating the Database Tables**
   - Use the Query Tool to create the `users`, `events`, and `last_viewed` tables.
   - Execute the query to create the tables.

```sql
-- Create Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
);

-- Create Events Table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    end_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create LastViewed Table
CREATE TABLE last_viewed (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## UI Design and Navigation
### Calendar View UI
- **Date Navigation**: Provides a clear view of the current month and year.
- **Daily Events**: Days with events show a numeric indicator.
- **Interactive Elements**: Add events via the plus symbol (+).
- **Navigation Arrows**: Navigate between months.

### Day View UI
- **Concurrent Events**: Arrange overlapping events in adjacent columns.
- **Auto-scrolling**: Scrolls to the first event of the day.
- **Modifying Events**: Click on events to edit details.

## Resources Used
- **Tailwind Components**: Utilized for styling with Tailwind CSS.
- **fffuel.co**: Used for the background image for the login page.

## Additional Links
- **GitHub Repository**: [github.com/omarbaker8/calendar](https://github.com/omarbaker8/calendar)
- **Live Application**: [calendar-1-qcai.onrender.com](https://calendar-1-qcai.onrender.com)
