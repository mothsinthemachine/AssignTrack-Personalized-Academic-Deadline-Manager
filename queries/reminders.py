#add reminder to the database
def add_reminder(user_id, days_ahead, reminder_number):

    #safeguard so users cant add more then 4 reminders
    if reminder_number not in range(1, 5):
        return 'Invalid reminder_number parameter for add_reminder must be between 1 and 4'
    
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()
        #query to add the users info into the reminders table
        cursor.execute("""
            INSERT INTO reminders(user_id, days_ahead, reminder_number)
            VALUES (%s,%s,%s)
            """,(user_id, days_ahead, reminder_number))
        
        conn.commit()

        return 'success'

    except sqlite3.IntegrityError as e:
        if 'reminders.reminder_number' in str(e):
            return 'Invalid, you already have a similar reminder'

    except Exception as e:
        return f"Unexpected error occured when adding reminder {e}"

    finally:
        if conn:
            conn.close()

#function that tells you which reminders a users have
def check_user_reminders(user_id) -> dict:
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to edit the users info into the access_token table
        cursor.execute("""
            SELECT reminder_number, days_ahead, special FROM reminders WHERE user_id = %s
            """,(user_id,))

        info=cursor.fetchall()

        conn.close()

        reminders_status_dict={
            'first_reminder_key':False,
            'second_reminder_key':False,
            'third_reminder_key':False,
            'special_reminder_key':False
        }

        for reminder_number, days_ahead, special in info:
            if reminder_number == 1:
                reminders_status_dict['first_reminder_key'] = days_ahead
            elif reminder_number == 2:
                reminders_status_dict['second_reminder_key'] = days_ahead
            elif reminder_number == 3:
                reminders_status_dict['third_reminder_key'] = days_ahead
            if special == 1:
                reminders_status_dict['special_reminder_key'] = days_ahead


        return reminders_status_dict


    except Exception as e:
        raise Exception(f'Unexpected error occured when checking user stored reminders status {e}')


#edits reminder for user
def edit_reminder(user_id, days_ahead, reminder_number):
    import sqlite3

    try:


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to edit the users info into the reminders table
        cursor.execute("""
            UPDATE reminders SET days_ahead = %s WHERE user_id = %s and reminder_number = %s
            """,(days_ahead, user_id, reminder_number))
        
        conn.commit()

        return 'success'

    except sqlite3.IntegrityError as e:
        if 'reminders.user_id' in str(e):
            return 'Invalid, user have yet to add a reminder to edit'

    except Exception as e:
        return f"Unexpected error occured when editting reminder {e}"

    finally:
        if conn:
            conn.close()

#delete reminders for user
def rem_reminder(user_id, reminder_number):
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to remove the users info from the reminders table
        cursor.execute("""
            DELETE FROM reminders WHERE user_id = %s and reminder_number = %s
            """,(user_id, reminder_number))
        
        conn.commit()

        # Check if any row was deleted
        if cursor.rowcount == 0:
            return f"Invalid: No reminder found for user with reminder number {reminder_number}"

        return 'success'
        
    except Exception as e:
        return f"Unexpected error occured when removing reminder {e}"

    finally:
        if conn:
            conn.close()

if __name__=='__main__':
    rem_reminder()
    check_user_reminders()
    add_reminder()
    edit_reminder()
