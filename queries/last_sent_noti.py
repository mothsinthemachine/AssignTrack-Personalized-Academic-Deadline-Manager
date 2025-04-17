def save_last_sent_noti(user_id, details):
    import datetime as dt
    from backend.db_conn import connect_to_db

    date = dt.datetime.today() 
    conn = None

    try:
        # Step 1: Connect to the database
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
        except Exception as e:
            return f"Error connecting to database: {e}"

        # Step 2: Check if the user is already in the last_sent_noti table
        try:
            cursor.execute("SELECT id FROM last_sent_noti WHERE user_id = %s", (user_id,))
            has_noti = cursor.fetchone()
        except Exception as e:
            return f"Error checking user in last_sent_noti table: {e}"

        if has_noti:
            # Step 3: Update the existing notification
            try:
                cursor.execute(
                    "UPDATE last_sent_noti SET date = %s, details = %s WHERE user_id = %s",
                    (date, details, user_id),
                )
                conn.commit()
                return "Success: Updated existing notification"
            except Exception as e:
                return f"Error updating last_sent_noti: {e}"

        else:
            # Step 4: Insert new notification
            try:
                cursor.execute(
                    "INSERT INTO last_sent_noti (user_id, date, details) VALUES (%s, %s, %s)",
                    (user_id, date, details)
                )
                conn.commit()
                return "Success: Added new notification"
            except Exception as e:
                return f"Error inserting new notification: {e}"

    finally:
        if conn:
            conn.close()
#checks if user already have a token
def check_last_sent_noti(user_id):
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to see the users last sent notification
        cursor.execute("""
            SELECT details, date FROM last_sent_noti WHERE user_id = %s
            """,(user_id,))

        info=cursor.fetchone()

        conn.commit()
        conn.close()

        if info is None:
            return False
        else:
            return info[0]

    except Exception as e:
        raise Exception(f'Unexpected error occured when checking user last sent noti {e}')