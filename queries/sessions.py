def create_session_for_user(user_id, session_id, expiry_time):
    from backend.db_conn import connect_to_db
    from datetime import datetime, timedelta


    conn = connect_to_db()
    cursor = conn.cursor()
    
    expiry = datetime.now() + timedelta(minutes=expiry_time)
    
    cursor.execute("""
        INSERT INTO sessions (session_id, user_id, expiry) 
        VALUES (%s, %s, %s)
        ON CONFLICT (session_id) 
        DO UPDATE SET 
            user_id = EXCLUDED.user_id,
            expiry = EXCLUDED.expiry
    """, (session_id, user_id, expiry))
    
    conn.commit()
    conn.close()
    return session_id

def get_user_id_from_session(session_id):
    from backend.db_conn import connect_to_db
    from datetime import datetime


    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM sessions WHERE session_id = %s AND expiry > %s", 
                  (session_id, datetime.now()))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]  # Return the user_id
    return None

#delete session for user
def rem_session_from_db(user_id):
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to remove the users info from the sessions table
        cursor.execute("""
            DELETE FROM sessions WHERE user_id = %s
            """,(user_id,))
        
        conn.commit()

        # Check if any row was deleted
        if cursor.rowcount == 0:
            return f"Invalid: No session found for user"

        return 'success'
        
    except Exception as e:
        if conn:
            conn.rollback()
        return f"Unexpected error occured when removing session {e}"

    finally:
        if conn:
            conn.close()