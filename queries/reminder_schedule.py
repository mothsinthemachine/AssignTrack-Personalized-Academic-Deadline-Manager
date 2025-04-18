#add or edit reminder schedule to the database
def add_or_edit_reminder_schedule(user_id : int, time : str, timezone : str) -> str:
    from backend.db_conn import connect_to_db


    try:

        conn=connect_to_db()
        cursor=conn.cursor()
        #query to add or edit the users info into the reminder schedule table
        cursor.execute("""
            INSERT INTO reminder_schedule(user_id, time, timezone)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET 
                time = EXCLUDED.time,
                timezone = EXCLUDED.timezone
        """, (user_id, time, timezone))
        
        conn.commit()

        return 'success'

    except Exception as e:
        if conn:
            conn.rollback()
        return f"Unexpected error occured when adding reminder {e}"

    finally:
        if conn:
            conn.close()

def get_reminder_schedule(user_id : int) -> dict:
    from backend.db_conn import connect_to_db


    try:

        conn=connect_to_db()
        cursor=conn.cursor()

        #gets time of school from its name
        cursor.execute("""
            SELECT time, timezone FROM reminder_schedule WHERE user_id = %s
        """,(user_id,))
        info = cursor.fetchall()

        time_str, timezone = info[0]
        hours, minutes_period = time_str.split(':')
        minutes, period = minutes_period.split(' ')

        info_dic={
            'hours':hours,
            'minutes':minutes,
            'period':period,
            'timezone':timezone
        }
        return info_dic

    except Exception as e:
        print(f' Unexpected Error Occured in function get_reminder_schedule {e}')
    finally:
        if conn:
            conn.close()

def get_all_reminder_schedule() -> list:
    from backend.db_conn import connect_to_db


    try:

        conn=connect_to_db()
        cursor=conn.cursor()

        #get all stored reminder_schedule
        cursor.execute("""
            SELECT user_id, time, timezone FROM reminder_schedule
        """)
        info = cursor.fetchall()

        return info

    except Exception as e:
        print(f' Unexpected Error Occured in function get_all_reminder_schedule {e}')
    finally:
        if conn:
            conn.close()