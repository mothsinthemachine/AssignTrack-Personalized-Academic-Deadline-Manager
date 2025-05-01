from twilio.rest import Client
from dotenv import load_dotenv
import os


load_dotenv()
#twilio credentials
twilio_sid = os.getenv('twilio_sid')
twilio_token = os.getenv('twilio_token')
phone_number=os.getenv('number')
messaging_service_sid = os.getenv('messaging_service_sid')

client = Client(twilio_sid, twilio_token)

def send_verification_code(to, channel='sms'):
    if channel == 'sms':
        to = '+1' + to
    elif channel == 'email':
        # No modification needed for email
        pass
    else:
        return f'Incorrect parameter "channel" can only be sms or email, got: {channel}'
    
    try:
        """
        Send a verification code to the specified phone number or email
        """
        verification = client.verify.v2.services(
            messaging_service_sid
        ).verifications.create(channel=channel, to=to)
        print(verification.status)
        return 'success'
    except Exception as e:
        print(f'Unexpected Error occured when sending verification code {e}') 

def check_verification_code(to, code, channel='sms'):
    if channel == 'sms':
        to = '+1' + to
    elif channel == 'email':
        # No modification needed for email
        pass
    else:
        return f'Incorrect parameter "channel" can only be sms or email, got: {channel}'
        
    try:
        """
        Check if the verification code is valid
        """

        verification_check = client.verify.v2.services(
            messaging_service_sid
        ).verification_checks.create(to=to, code=code)


        print(verification_check.status)
        
        print(f"Verification check status: {verification_check.status}")
        return verification_check.status == 'approved'
    except Exception as e:
        print(f'Unexpected Error occured when checking {channel} verification code {e}') 


if __name__ == "__main__":
    phone_number=os.getenv('number')
    send_verification_code(to=phone_number, channel='sms')
    verification_code = input("Enter the verification code: ")
    # Step 3: Verify the code
    if check_verification_code(to=phone_number,code=verification_code, channel='sms'):
        print("Phone number verified successfully!")
    else:
        print("Invalid verification code.")