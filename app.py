from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, current_user, LoginManager
from flask_migrate import Migrate
from config import Config
from models import db, User, LastViewed, Event
from flask import jsonify
import datetime
import calendar
from math import floor
from collections import defaultdict

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/form', methods=['GET', 'POST'])
def home_form():


    if request.method == 'POST':
        action = request.form['action']
        
        email = request.form['email']
        password = request.form['password']
        print(f'Email: {email}, Password: {password}')
        user = User.query.filter_by(email=email).first()
        print(f'User: {user}')
        
        if action == 'sign_in':
            
            if current_user.is_authenticated:
                logout_user()


            if user and bcrypt.check_password_hash(user.password_hash, password):
                print('Login Successful')
                login_user(user)
                return jsonify(success=True, redirect_url=url_for('welcome')), 200  # Or your desired page
            else:
                print('Login Unsuccessful')
                return jsonify({"error": "invalid_credentials"}), 401
        elif action == 'sign_up':
            if user:
                print('Email already registered')
                return jsonify({"error": "email_exists"}), 409
            else:
                print('Signup action')
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                new_user = User(email=email, password_hash=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return jsonify(success=True, redirect_url=url_for('welcome')), 200  # Or your desired page
               
                
    return render_template('login.html')


@app.route('/welcome', methods=['GET'])
def welcome():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    now = datetime.datetime.now()
    query_month = request.args.get('month', type=int)
    query_year = request.args.get('year', type=int)

    # Fetch or initialize the last_viewed record
    last_viewed = LastViewed.query.filter_by(user_id=current_user.id).first()
    if last_viewed is None:
        # If there's no last_viewed record for this user, create one with either the query params or current date
        last_viewed = LastViewed(user_id=current_user.id, month=query_month or now.month, year=query_year or now.year)
        db.session.add(last_viewed)
    elif last_viewed and query_month and query_year:
        # If query params are provided, update the last_viewed record
        print('Updating last_viewed record')
        last_viewed.month = query_month
        last_viewed.year = query_year
    else:
        # If no query params provided, use the month and year from the last_viewed record
        query_month = last_viewed.month
        query_year = last_viewed.year

    db.session.commit()

    # Use either the updated/created last_viewed record or the current date if no params were provided
    month = query_month if query_month else now.month
    year = query_year if query_year else now.year

    print(f'Month: {month}, Year: {year}')
    data = get_month_details(year, month)
    # Fetch count of events for the current user for the month and year grouped by day
    events = Event.query.filter_by(user_id=current_user.id).filter(Event.date.cast(db.Text).like(f'{year}-{month:02}%')).all()

    # Initialize a dictionary to hold event counts per day
    month_events = {}

    for event in events:
        day = event.date.day  # Assuming 'date' is a datetime.date object
        if day in month_events:
            month_events[day] += 1
        else:
            month_events[day] = 1

    print(month_events)


        
    return render_template('calendar.html', data=data, month=month, year=year, month_events=month_events)




def get_month_details(year, month):
    padding_start_of_month, number_of_days = calendar.monthrange(year, month)
    padding_end_of_month = (6 - (number_of_days + padding_start_of_month - 1) % 7)

    # Adjust for January
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    day_start_of_cal = calendar.monthrange(prev_year, prev_month)[1] - padding_start_of_month + 1
    return day_start_of_cal, padding_start_of_month, number_of_days, padding_end_of_month

# Add additional routes as needed

@app.route('/addEvent', methods=['POST'])
def add_event():
    if request.method == 'POST':
        data = request.get_json()  # Correct way to get JSON data
        
        # Access the JSON data using keys directly
        title = data.get('title')
        date = data.get('date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        print(f'Title: {title}, Date: {date}, Start Time: {start_time}, End Time: {end_time}')
        # Add the event to the database
        event = Event(user_id=current_user.id, title=title, date=date, start_time=start_time, end_time=end_time)
        db.session.add(event)
        db.session.commit()

        # Return a JSON response or redirect as needed
        return jsonify(success=True, redirect_url=url_for('welcome')), 200
    


@app.route('/dayView', methods=['GET'])
def day_view():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    date = request.args.get('date')
    if date:
        original_events = Event.query.filter_by(user_id=current_user.id, date=date).all()
        events_with_grid_and_col = []

        # Track the start times and assign columns
        start_time_to_col_start = defaultdict(lambda: 1)  # Default to column 1

        for event in sorted(original_events, key=lambda e: (e.start_time, e.end_time)):
            start_hour = event.start_time.hour
            start_minute = event.start_time.minute
            end_hour = event.end_time.hour
            end_minute = event.end_time.minute

            start_grid = int((start_hour * 12) + floor(start_minute / 5) + 2)
            end_grid = int((end_hour * 12) + floor(end_minute / 5) + 2)
            duration = end_grid - start_grid
            
            # Determine column start based on previous events at this time
            start_time_str = f"{start_hour:02d}:{start_minute:02d}"
            col_start = start_time_to_col_start[start_time_str]
            start_time_to_col_start[start_time_str] += 1  # Increment for the next event at this time

            events_with_grid_and_col.append({
                'event': event,
                'start_grid': start_grid,
                'end_grid': end_grid,
                'duration': duration,
                'col_start': col_start  # New property to indicate which column to start in
            })

        return render_template('dayView.html', events=events_with_grid_and_col, date=date)
    else:
        return redirect(url_for('welcome'))

@app.route('/updateEvent', methods=['POST'])
def update_event():
    if request.method == 'POST':
        data = request.get_json()
        event_id = data.get('event_id')
        title = data.get('title')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        print(f'Event ID: {event_id}, Title: {title}, Start Time: {start_time}, End Time: {end_time}')
        # // Update the event in the database if action is update
        if data.get('action') == 'update':
            event = Event.query.get(event_id)
            event.title = title
            event.start_time = start_time
            event.end_time = end_time
            db.session.commit()

            return jsonify(success=True), 200
        # // Delete the event from the database if action is delete
        elif data.get('action') == 'delete':
            event = Event.query.get(event_id)
            db.session.delete(event)
            db.session.commit()

            return jsonify(success=True), 200



if __name__ == '__main__':
    app.run(debug=True)


