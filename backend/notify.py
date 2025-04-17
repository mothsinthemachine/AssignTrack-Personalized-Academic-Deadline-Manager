def number_notify(twilio_sid, twilio_token, message, phone_number):
    from twilio.rest import Client
    

    if len(message)==0:
        return 'no message were added to number_notify'
    try:
        client = Client(twilio_sid, twilio_token)

        message = client.messages.create(
            from_='+18886190127',
            body=f'{message}',
            to='+1' + phone_number)
        
    except Exception as e:
        print(f'Unexpected Error occured in number_notify {e}')



def email_notify(sendgrid_email, sendgrid_token, user_email, message):
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
 
    try:
        message_obj = Mail(
            from_email=sendgrid_email,
            to_emails=user_email,
            subject='Assignment Reminder',
            html_content=message
        )

        sg = SendGridAPIClient(sendgrid_token)
        response = sg.send(message_obj)

    except Exception as e:
        print(f'Error in email_notify: {e}')

if __name__=='__main__':
    import os
    from dotenv import load_dotenv


    #send email message with sendgrid
    load_dotenv()
    send_email=os.getenv('send_email')
    sendgrid_token=os.getenv('sendgrid_token')
    user_email=os.getenv('user_email')
    message = "<p>hey this is a test please dont block</p>"
    email_notify(send_email, sendgrid_token, user_email, message)

    #send text message with twillio
    twilio_sid=os.getenv('twilio_sid')
    twilio_token=os.getenv('twilio_token')
    phone_number=os.getenv('number')
    message='hi'
    number_notify(twilio_sid, twilio_token, message, phone_number)
