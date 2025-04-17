def is_valid_email(email: str) -> bool:
    import re


    #Checks if the given email address is valid.
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def is_valid_username(name: str) -> bool:
    import re


    # Only letters and numbers, with no spaces or special characters
    name_regex = r'^[A-Za-z0-9]+$'
    return re.match(name_regex, name) is not None

def is_valid_phone(phone: str) -> bool:
    import re
    

    #checks if the phone number is correctly formatted
    phone_regex = r'^\d{10}$'
    return re.match(phone_regex, phone) is not None

def is_valid_password(password: str) -> bool:
    import re

    # Only letters and numbers, with no spaces or special characters
    password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,20}$'
    return re.match(password_regex, password) is not None



def is_valid_token(token: str, school_url: str) -> bool:
    from canvasapi.exceptions import InvalidAccessToken
    from canvasapi import Canvas

    try:
        canvas=Canvas(school_url, token)
        user=canvas.get_current_user()
        return True

    except InvalidAccessToken as e:
        return False
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return False

