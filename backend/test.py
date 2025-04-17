from notify import number_notify
from upcoming import Upcoming
from twilio.rest import Client
import os
from dotenv import load_dotenv

try:
    load_dotenv()
    twilio_sid=os.getenv('twilio_sid')
    twilio_token=os.getenv('twilio_token')
    twilio_number=os.getenv('number')
    canvas_token=os.getenv('canvas_token')
    school_url='https://mdc.instructure.com/'
    upcoming_assighnment_list=Upcoming(school_url, canvas_token, 5)
    message=''.join(upcoming_assighnment_list)

    #runs the functions
    number_notify(twilio_sid, twilio_token, message, twilio_number)
except Exception as e:
    print(f'Unexpected Error occured {e}')


