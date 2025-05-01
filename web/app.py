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
from queries.users import edit_user_email, edit_phone_number, check_users_existing_info
from backend.user_input_check import is_valid_email, is_valid_username, is_valid_token, is_valid_phone, is_valid_password
from queries.sessions import create_session_for_user, get_user_id_from_session, rem_session_from_db
from queries.reminder_schedule import add_or_edit_reminder_schedule, get_reminder_schedule
import uuid
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
from backend.verification.verify import send_verification_code, check_verification_code
from queries.pending_users import unverified_to_verified_user



load_dotenv()  # Load environment variables from .env file

#check if app is in demo mode
is_demo_mode = os.environ.get('demo_mode', 'false').lower() in ('true', '1', 'yes')
token_encryption_key=os.getenv('token_encryption_key')
fernet=Fernet(token_encryption_key)
app_secret_key=os.getenv('app_secret_key')

app=Flask(__name__)
app.secret_key = app_secret_key
app.permanent_session_lifetime = timedelta(minutes=300)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    session.clear() #clears sessions before loging in
    username=request.form.get('username').strip().lower()
    password=request.form.get('password')
    user = get_user_from_db(username, password)
    unverified_user=get_user_from_db(username, password, verified=False)

    #stores information into cookie and session
    if user:
        session_id = str(uuid.uuid4())  # Generate a random session ID
        create_session_for_user(user['id'], session_id, expiry_time=300)#stores session in database
        session['session_id'] = session_id
        return redirect(url_for('profile'))
    
    elif unverified_user:
        # Create a pending session
        pending_session_id = str(uuid.uuid4())
        user_id=unverified_user['id']
        create_session_for_user(user_id=user_id, session_id=pending_session_id, expiry_time=1800, verified=False)  # 30 minutes
        session['pending_session_id'] = pending_session_id
        session['is_pending'] = True

        user=get_user_from_db_by_id(user_id, verified=False)
        email=user['email_address']
        # Redirect to verification page
        return render_template('acc_creation_verify.html', email=email)

    else:
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    cookie=session.get('session_id')
    user_id=get_user_id_from_session(cookie)
    if cookie and user_id:
        invalid_token=request.args.get('invalid_token')
        invalid_phone_number=request.args.get('invalid_phone_number')
        invalid_email=request.args.get('invalid_email')
        user=get_user_from_db_by_id(user_id)
        selected_reminder_schedule = get_reminder_schedule(user['id'])
        #work with later
        school_names=school_name_list()
        selected_school=get_user_school_name(user['school_id'])
        has_token_encrypted=check_user_token_status(user['id'])

        if has_token_encrypted:
            has_token=fernet.decrypt(has_token_encrypted.encode()).decode()
        else:
            has_token=False


        check_reminders_dict=check_user_reminders(user['id'])
        last_sent=check_last_sent_noti(user['id'])
        noti_preference=check_notification_preferences(user['id'])
        return render_template('profile.html', user=user, has_token=has_token, check_reminders_dict=check_reminders_dict, last_sent=last_sent, noti_preference=noti_preference, school_names=school_names, selected_school=selected_school, srs=selected_reminder_schedule, invalid_token=invalid_token, invalid_phone_number=invalid_phone_number, invalid_email=invalid_email)
        
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
    #dont need to add phone number when creating account
    phone_number=None
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
    db_add_user=save_account(username, hashed_password, email_address, school_name=school_name)

    #show error message for invalid information
    if 'INVALID' in db_add_user.upper():
        return redirect(url_for('create_account', error=db_add_user))
    #send first verification
    send_verification_code(email_address, 'email')

    # Create a pending session
    unverified_user=get_user_from_db(username, password, verified=False)
    pending_session_id = str(uuid.uuid4())
    user_id=unverified_user['id']
    create_session_for_user(user_id=user_id, session_id=pending_session_id, expiry_time=1800, verified=False)  # 30 minutes
    session['pending_session_id'] = pending_session_id
    session['is_pending'] = True

    return redirect(url_for('account_creation_verify_page', email=email_address))

@app.route('/edit_token_redirect', methods=['POST'])
def edit_token_redirect():
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    new_token=request.form.get('editToken')
    school_id=request.form.get('school_id')

    school_url=get_school_url(school_id)

    #sanitize for input accidents
    new_token=new_token.strip(" '\"")


    #check if user token input is valid
    if is_valid_token(new_token, school_url) is False:
        invalid_token_str = 'Invalid token or school: make sure the token and school is correct'
        return redirect(url_for('profile', invalid_token=invalid_token_str))

    #encrypt the token
    encrypted_new_token=fernet.encrypt(new_token.encode()).decode()

    try_edit_token=edit_token(user_id, encrypted_new_token)

    if try_edit_token == 'success':
        return redirect(url_for('profile'))
    
    #return error the try_edit_token raises
    else:
        return try_edit_token


@app.route('/add_token_redirect', methods=['POST'])
def add_token_redirect():
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    new_token=request.form.get('newToken')
    school_id=request.form.get('school_id')

    school_url=get_school_url(school_id)

    #sanitize for input accidents
    new_token=new_token.strip(" '\"")


    #check if user token input is valid
    if is_valid_token(new_token, school_url) is False:
        invalid_token_str = 'Invalid token or school: make sure the token and school is correct'
        return redirect(url_for('profile', invalid_token=invalid_token_str))
    
    encrypted_new_token=fernet.encrypt(new_token.encode()).decode()
    #adds token to the databse if token is correct
    add_token(user_id, encrypted_new_token)
    return redirect(url_for('profile'))

@app.route('/add_reminder_redirect', methods=['POST'])
def add_reminder_redirect():
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
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
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
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
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    reminder_number=request.form.get('reminder_number')
    #deletes reminder from database
    rem_reminder(user_id, reminder_number)
    return redirect(url_for('profile'))

@app.route('/remove_token_redirect', methods=['POST'])
def remove_token_redirect():
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    #deletes token from database
    rem_token(user_id)
    return redirect(url_for('profile'))

@app.route('/noti_preference_redirect', methods=['POST'])
def noti_preference_redirect():
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    text_notifications = 'Text' in request.form  
    email_notifications = 'Email' in request.form

    update_notification_preference(email_notifications, text_notifications, user_id)
    return redirect(url_for('profile'))

@app.route('/edit_email_redirect', methods=['POST'])
def edit_email_redirect():
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    new_email_address=request.form.get('new_email_address')
    
    if is_demo_mode:
        return redirect(url_for('profile'))

    #check if user email inputs is valid
    if is_valid_email(new_email_address) is False:
        invalid_email="Invalid email format"
        return redirect(url_for('profile', invalid_email=invalid_email))
    
    edit_user_email(user_id, new_email_address)

    return redirect(url_for('profile'))

@app.route("/edit_phone_number_redirect", methods=['POST'])
def edit_phone_number_redirect():
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    new_phone_number=request.form.get('new_phone_number')

    if is_demo_mode:
        return redirect(url_for('profile'))

    #check if user phone number input is valid
    if is_valid_phone(new_phone_number) is False:
        invalid_phone_number='Invalid phone number format'
        return redirect(url_for('profile', invalid_phone_number=invalid_phone_number)) 

    edit_phone_number(user_id, new_phone_number)

    return redirect(url_for('profile'))

@app.route('/choose_school_redirect', methods=['POST'])
def choose_school_redirect():
    school_name=request.form.get('schools')
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)

    print(edit_user_school(user_id, school_name))

    return redirect(url_for('profile'))

@app.route('/choose_schedule_redirect', methods=['POST'])
def choose_schedule_redirect():
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    hours=request.form.get('hours')
    minutes=request.form.get('minutes')
    period=request.form.get('period')
    timezone=request.form.get('timezone')
    time=f'{hours}:{minutes} {period}'

    add_or_edit_reminder_schedule(user_id, time, timezone)

    return redirect(url_for('profile'))

@app.route('/phone_number_edit_page', methods=['POST', 'GET'])
def phone_number_edit_page():
    # Initialize these variables to avoid UnboundLocalError
    phone_number_check = None
    verify_code = None
    send_code=None

    new_phone_number=request.form.get('new_phone_number')
    verify_code=request.form.get('verify_code')
    send_code=request.form.get('send_code')
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    phone_number_check=new_phone_number

    if request.method=='POST':
        
        if new_phone_number is not None:
            #check if user phone number input is valid
            if is_valid_phone(new_phone_number) is False:
                phone_number_check='Invalid: phone number format'
                return render_template('phone_number_verify.html', phone_number_check=phone_number_check)
            else:
                #function that checks if the info is already in the database
                if check_users_existing_info('phone_number', new_phone_number) == "Valid":
                    if (send_code is not None and send_code=='True'):
                        send_verification_code(new_phone_number, 'sms')
                        return render_template('phone_number_verify.html', phone_number_check=phone_number_check)
                else:
                    phone_number_check='Invalid: phone number has already been taken'
                    return render_template('phone_number_verify.html', phone_number_check=phone_number_check)
                
        if verify_code is not None:
            if check_verification_code(new_phone_number, verify_code, 'sms'):
                #edit user phone number
                edit_phone_number(user_id, new_phone_number)
                return redirect(url_for('profile'))
            else:
                return render_template('phone_number_verify.html', phone_number_check=phone_number_check)


    return render_template('phone_number_verify.html', phone_number_check=phone_number_check)

    
@app.route('/email_edit_page', methods=['POST', 'GET'])
def email_edit_page():
    # Initialize these variables to avoid UnboundLocalError
    email_check = None
    verify_code = None
    send_code=None

    new_email=request.form.get('new_email')
    verify_code=request.form.get('verify_code')
    send_code=request.form.get('send_code')
    cookie=session.get('session_id')
    user_id = get_user_id_from_session(cookie)
    email_check=new_email

    if request.method=='POST':
        
        if new_email is not None:
            #check if user phone number input is valid
            if is_valid_email(new_email) is False:
                email_check='Invalid: email format'
                return render_template('email_verify.html', email_check=email_check, user_id=user_id)
            else:
                #function that checks if the info is already in the database
                if check_users_existing_info('email_address', new_email) == "Valid":
                    if (send_code is not None and send_code=='True'):
                        send_verification_code(new_email, 'email')
                        return render_template('email_verify.html', email_check=email_check, user_id=user_id)
                else:
                    email_check='Invalid: Email has already been taken'
                    return render_template('email_verify.html', email_check=email_check, user_id=user_id)
                
        if verify_code is not None:
            if check_verification_code(new_email, verify_code, 'email'):
                #edit user email
                print(user_id)
                edit_user_email(user_id, new_email)
                return redirect(url_for('profile'))
            else:
                return render_template('email_verify.html', email_check=email_check, user_id=user_id)


    return render_template('email_verify.html', email_check=email_check, user_id=user_id)

@app.route('/account_creation_verify_page', methods=['POST', 'GET'])
def account_creation_verify_page():
    cookie=session.get('pending_session_id')
    user_id=get_user_id_from_session(cookie, verified=False)
    user=get_user_from_db_by_id(user_id, verified=False)

    # Initialize these variables to avoid UnboundLocalError
    send_code=None

    verify_code=request.form.get('verify_code')
    send_code=request.form.get('send_code')

    #add part to get email from session
    email=user['email_address']
    if (send_code is not None and send_code=='True'):
        send_verification_code(email, 'email')
        return render_template('acc_creation_verify.html', email=email)

    if verify_code is not None:
        if check_verification_code(email, verify_code, 'email'):
            rem_session_from_db(user_id, verified=False)
            ##function that transfers unverified user to verified user
            print(unverified_to_verified_user(user_id))
            session.clear()
            return redirect(url_for('login'))
        else:
            return render_template('acc_creation_verify.html', email=email)
    return render_template('acc_creation_verify.html', email=email)


if __name__=='__main__':
    app.run(debug=True, port=5001)
