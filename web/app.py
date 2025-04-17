from flask import Flask, render_template, request, session, redirect, url_for
import hashlib
from datetime import timedelta

import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
from backend.acc.login import get_user_from_db, get_user_from_db_by_id
from backend.acc.create_acc import save_account
from queries.schools import school_name_list, get_school_url, edit_user_school, get_user_school_name
from queries.tokens import add_token, edit_token, check_user_token_status, rem_token
from queries.reminders import add_reminder, check_user_reminders, edit_reminder, rem_reminder
from queries.last_sent_noti import check_last_sent_noti
from queries.notification_preferences import check_notification_preferences, update_notification_preference
from queries.users import edit_user_email, edit_phone_number
from backend.user_input_check import is_valid_email, is_valid_username, is_valid_token, is_valid_phone, is_valid_password
from queries.sessions import create_session_for_user, get_user_id_from_session, rem_session_from_db
from queries.reminder_schedule import add_or_edit_reminder_schedule, get_reminder_schedule
import uuid
from flask_bcrypt import Bcrypt


load_dotenv()  # Load environment variables from .env file

#check if app is in demo mode
is_demo_mode = os.environ.get('demo_mode', 'false').lower() in ('true', '1', 'yes')


app=Flask(__name__)
app.secret_key = '4@6daf8#ga1z6a)ySdg1%Av87'
app.permanent_session_lifetime = timedelta(minutes=300)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    username=request.form.get('username').strip().lower()
    password=request.form.get('password')
    user = get_user_from_db(username, password)

    #stores information into cookie and session
    if user:
        session_id = str(uuid.uuid4())  # Generate a random session ID
        create_session_for_user(user['id'], session_id, expiry_time=300)#stores session in database
        session['session_id'] = session_id
        return redirect(url_for('profile'))

    else:
        return 'Invalid user', 401

@app.route('/profile')
def profile():
    cookie=session.get('session_id')
    user_id=get_user_id_from_session(cookie)
    if cookie and user_id:
        user=get_user_from_db_by_id(user_id)
        selected_reminder_schedule = get_reminder_schedule(user['id'])
        #work with later
        school_names=school_name_list()
        selected_school=get_user_school_name(user['school_id'])
        has_token=check_user_token_status(user['id'])
        check_reminders_dict=check_user_reminders(user['id'])
        last_sent=check_last_sent_noti(user['id'])
        noti_preference=check_notification_preferences(user['id'])
        return render_template('profile.html', user=user, has_token=has_token, check_reminders_dict=check_reminders_dict, last_sent=last_sent, noti_preference=noti_preference, school_names=school_names, selected_school=selected_school, srs=selected_reminder_schedule)
        
    return redirect(url_for('home'))

@app.route('/logout', methods=['POST'])
def logout():
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    rem_session_from_db(user_id)
    session.clear()
    return redirect(url_for('home'))

@app.route('/create_account', methods=['POST', 'GET'])
def create_account():
    if is_demo_mode:
        return redirect(url_for('home'))

    error=request.args.get('error')
    school_names=school_name_list()
    return render_template('create-acc.html', error=error, school_names=school_names)

@app.route('/process_create_account', methods=['POST'])
def process_create_account():
    username=request.form.get('username')
    password=request.form.get('password')
    phone_number=request.form.get('phone_number')
    email_address=request.form.get('email_address')
    school_name=request.form.get('schools')
    
    #check if user email inputs is valid
    if is_valid_email(email_address) is False:
        invalid_email_str = 'Invalid Email: wrong format'
        return redirect(url_for('create_account', error=invalid_email_str))

    #check if user username inputs is valid
    if is_valid_username(username) is False:
        invalid_username_str = 'Invalid Username: only letters and numbers, with no spaces or special characters'
        return redirect(url_for('create_account', error=invalid_username_str))

    #check if user phone number input is valid
    if is_valid_phone(phone_number) is False:
        invalid_phone_str = 'Invalid Phone number: needs to be nine numbers'
        return redirect(url_for('create_account', error=invalid_phone_str)) 

    if is_valid_password(password) is False:
         invalid_password_str = (
                                "Invalid password: Password must meet the following requirements:\n"
                                "- At least 8 characters long\n"
                                "- At least one uppercase letter\n"
                                "- At least one lowercase letter\n"
                                "- At least one number\n"
                                "- At least one special character (e.g., !@#$%^&*)"
                            )
         return redirect(url_for('create_account', error=invalid_password_str)) 
    
    # Store hashed_password in database
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')


    #try to add the user to the database
    db_add_user=save_account(username, hashed_password, phone_number, email_address, school_name)

    #show error message for invalid information
    if 'INVALID' in db_add_user.upper():
        return redirect(url_for('create_account', error=db_add_user))
    return redirect(url_for('home'))

@app.route('/edit_token_redirect', methods=['POST'])
def edit_token_redirect():
    user_id=request.form.get('user_id')
    new_token=request.form.get('editToken')
    school_id=request.form.get('school_id')

    school_url=get_school_url(school_id)

    #sanitize for input accidents
    new_token=new_token.strip(" '\"")


    #check if user token input is valid
    if is_valid_token(new_token, school_url) is False:
        invalid_token_str = 'Invalid token or school: make sure the token and school is correct'
        return redirect(url_for('profile', error=invalid_token_str))

    try_edit_token=edit_token(user_id, new_token)

    if try_edit_token == 'success':
        return redirect(url_for('profile'))
    
    #return error the try_edit_token raises
    else:
        return try_edit_token


@app.route('/add_token_redirect', methods=['POST'])
def add_token_redirect():
    user_id=request.form.get('user_id')
    new_token=request.form.get('newToken')
    school_id=request.form.get('school_id')

    school_url=get_school_url(school_id)

    #sanitize for input accidents
    new_token=new_token.strip(" '\"")


    #check if user token input is valid
    if is_valid_token(new_token, school_url) is False:
        invalid_token_str = 'Invalid token or school: make sure the token and school is correct'
        return redirect(url_for('profile', error=invalid_token_str))

    #adds token to the databse if token is correct
    add_token(user_id, new_token)
    return redirect(url_for('profile'))

@app.route('/add_reminder_redirect', methods=['POST'])
def add_reminder_redirect():
    user_id=request.form.get('user_id')
    first_reminder_days=request.form.get('first_reminder')
    second_reminder_days=request.form.get('second_reminder')
    third_reminder_days=request.form.get('third_reminder')
    special_reminder_days=request.form.get('special_reminder')

    print(first_reminder_days)
    if first_reminder_days != '' and first_reminder_days is not None:
        add_reminder(user_id, first_reminder_days, 1)
        return redirect(url_for('profile'))
    
    if second_reminder_days != '' and second_reminder_days is not None:
        add_reminder(user_id, second_reminder_days, 2)
        return redirect(url_for('profile'))
    
    if third_reminder_days != '' and third_reminder_days is not None:
        add_reminder(user_id, third_reminder_days, 3)
        return redirect(url_for('profile'))
    
    if special_reminder_days != '' and special_reminder_days is not None:
        print(add_reminder(user_id, special_reminder_days, 4))
        return redirect(url_for('profile'))
    

    return redirect(url_for('profile'))

@app.route('/edit_reminder_redirect', methods=['POST'])
def edit_reminder_redirect():
    user_id=request.form.get('user_id')
    days_ahead=request.form.get('daysAhead')
    reminder_number=request.form.get('reminder_number')

    #make sure user inputs a valid reminder include more validations later
    try:
        if int(days_ahead) < 0:
            return redirect(url_for('profile'))
    except ValueError:
        return redirect(url_for('profile'))

    try_edit_reminder=edit_reminder(user_id, days_ahead, reminder_number)

    if try_edit_reminder == 'success':
        return redirect(url_for('profile'))
    
    #return error the try_edit_reminder raises
    else:
        return try_edit_reminder

@app.route('/remove_reminder_redirect', methods=['POST'])
def remove_reminder_redirect():
    user_id=request.form.get('user_id')
    reminder_number=request.form.get('reminder_number')
    #deletes reminder from database
    rem_reminder(user_id, reminder_number)
    return redirect(url_for('profile'))

@app.route('/remove_token_redirect', methods=['POST'])
def remove_token_redirect():
    user_id=request.form.get('user_id')
    #deletes token from database
    rem_token(user_id)
    return redirect(url_for('profile'))

@app.route('/noti_preference_redirect', methods=['POST'])
def noti_preference_redirect():
    user_id=request.form.get('user_id')
    text_notifications = 'Text' in request.form  
    email_notifications = 'Email' in request.form

    update_notification_preference(email_notifications, text_notifications, user_id)
    return redirect(url_for('profile'))

@app.route('/edit_email_redirect', methods=['POST'])
def edit_email_redirect():
    user_id=request.form.get('user_id')
    new_email_address=request.form.get('new_email_address')
    
    if is_demo_mode:
        return redirect(url_for('profile'))

    #check if user email inputs is valid
    if is_valid_email(new_email_address) is False:
        return redirect(url_for('profile'))

    edit_user_email(user_id, new_email_address)

    return redirect(url_for('profile'))

@app.route("/edit_phone_number_redirect", methods=['POST'])
def edit_phone_number_redirect():
    user_id=request.form.get('user_id')
    new_phone_number=request.form.get('new_phone_number')

    if is_demo_mode:
        return redirect(url_for('profile'))

    #check if user phone number input is valid
    if is_valid_phone(new_phone_number) is False:
        return redirect(url_for('profile')) 

    edit_phone_number(user_id, new_phone_number)

    return redirect(url_for('profile'))

@app.route('/choose_school_redirect', methods=['POST'])
def choose_school_redirect():
    school_name=request.form.get('schools')
    user_id=request.form.get('user_id')

    print(edit_user_school(user_id, school_name))

    return redirect(url_for('profile'))

@app.route('/choose_schedule_redirect', methods=['POST'])
def choose_schedule_redirect():
    user_id=request.form.get('user_id')
    hours=request.form.get('hours')
    minutes=request.form.get('minutes')
    period=request.form.get('period')
    timezone=request.form.get('timezone')
    time=f'{hours}:{minutes} {period}'

    add_or_edit_reminder_schedule(user_id, time, timezone)

    return redirect(url_for('profile'))

if __name__=='__main__':
    app.run(debug=True, port=5000)
