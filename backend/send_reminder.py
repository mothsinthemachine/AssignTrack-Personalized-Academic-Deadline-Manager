def constant_check_reminder_schedule():
    from datetime import datetime
    import pytz
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
    from queries.reminder_schedule import get_all_reminder_schedule

    
    users_schedule=get_all_reminder_schedule()
    triggered=[]

    # Map timezone string to pytz timezone
    tz_map = {
        'utc': 'UTC',
        'edt': 'US/Eastern',  # During daylight saving
        'est': 'US/Eastern',  # Standard time
        'cdt': 'US/Central',  # During daylight saving
        'cst': 'US/Central',  # Standard time
        'mdt': 'US/Mountain', # During daylight saving
        'mst': 'US/Mountain', # Standard time
        'pdt': 'US/Pacific',  # During daylight saving
        'pst': 'US/Pacific',  # Standard time
        'akdt': 'US/Alaska',  # During daylight saving
        'akst': 'US/Alaska',  # Standard time
        'hst': 'US/Hawaii'    # Hawaii doesn't use daylight saving
    }

    for user_id, time, timezone_str in users_schedule:
        
        if timezone_str.lower() in tz_map:
            # Get current time in the specified timezone
            tz = pytz.timezone(tz_map[timezone_str.lower()])
            current_time = datetime.now(tz).time().replace(second=0, microsecond=0)
            
            # Parse the user's scheduled time
            user_time_obj = datetime.strptime(time, '%I:%M %p').time().replace(second=0, microsecond=0)
            
            if current_time == user_time_obj:
                triggered.append(user_id)
    
    return triggered

def constant_send_reminder():
    from notify import number_notify, email_notify
    from queries.last_sent_noti import save_last_sent_noti
    import os
    from dotenv import load_dotenv
    from db_conn import connect_to_db


    load_dotenv()
    #twilio credentials
    twilio_sid=os.getenv('twilio_sid')
    twilio_token=os.getenv('twilio_token')

    #sendgrid credentials
    send_email=os.getenv('send_email')
    sendgrid_token=os.getenv('sendgrid_token')


    triggered_users=constant_check_reminder_schedule()
    if len(triggered_users)!=0:
        conn=connect_to_db()
        cursor=conn.cursor()

        for user_id in triggered_users:
            try:

                #query to get the users_np_lsr_view 'VIEW' to input into upcoming
                cursor.execute("""
                    SELECT details, email_preference, phone_preference, phone_number, email_address  FROM users_np_lsr_view
                    WHERE id = %s
                    """,(user_id,))

                info=cursor.fetchone()

                if info is None:
                    continue
                else:
                    details=info[0]
                    email_preference=info[1]
                    phone_preference=info[2]
                    phone_number=info[3]
                    email_address=info[4]
                    save_last_sent_noti(user_id, details)
                    #formated to be sent as text
                    text_message=details.replace('/', '\n')
                    #formated to be sent as email
                    email_message=details.replace('/', '<br>')


                    #send users their email notification based on their preference
                    if email_preference==1:
                        email_notify(send_email, sendgrid_token, email_address, email_message)
                    if (phone_preference==1 and phone_number is not None):
                        number_notify(twilio_sid, twilio_token, text_message, phone_number)
            except Exception as e:
                return f'Unexpected Error Occured on constant send reminder function {e}'
                
            finally:
                if conn:
                    conn.close()

if __name__ == '__main__':                  
    constant_send_reminder()
