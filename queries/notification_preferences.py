#function that tells you which notification preference a users have
def check_notification_preferences(user_id) -> dict:
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to check for notification preference
        cursor.execute("""
            SELECT email_preference, phone_preference FROM notification_preferences WHERE user_id = %s
            """,(user_id,))

        info=cursor.fetchall()


        conn.commit()
        conn.close()

        reminders_status_dict={
            'email_preference':False,
            'phone_preference':False,
        }

        if info[0][0]==1:
            reminders_status_dict['email_preference']=True
        if info[0][1]==1:
            reminders_status_dict['phone_preference']=True

        return reminders_status_dict
    
    except Exception as e:
        print(info)
        print(f'Unexpected error occured when checking user stored notification preference {e}')

        return f'Unexpected error occured when checking user stored notification preference {e}'

def update_notification_preference(email_preference, phone_preference, user_id):
    try:
        from backend.db_conn import connect_to_db

        conn=True
        if email_preference==True:
            email_preference=1
        else:
            email_preference=0
        if phone_preference==True:
            phone_preference=1
        else:
            phone_preference=0

        conn=connect_to_db()
        cursor=conn.cursor()

        #query to edit the users info into the notification_preferences table
        cursor.execute("""
            UPDATE notification_preferences SET email_preference = %s, phone_preference = %s WHERE user_id = %s
            """,(email_preference, phone_preference, user_id))
        
        conn.commit()

        return 'success'

    except sqlite3.IntegrityError as e:
        if 'notification_preferences.user_id' in str(e):
            return 'Invalid, user have yet have a notifcation preference to edit'

    except Exception as e:
        return f"Unexpected error occured when editting notification_preferences {e}"

    finally:
        if conn:
            conn.close()