def adjust_last_saved_reminder(users_dic: dict) -> str:
    """
    Adds or edits reminder schedules in the database based on the provided users dictionary.
    
    Args:
        users_dic: Dictionary containing user IDs as keys and their reminder details as values
        
    Returns:
        str: Success message or error description
    """
    
    conn = None
    try:
        from datetime import datetime
        from backend.db_conn import connect_to_db

        
        conn = connect_to_db()
        cursor = conn.cursor()

        date = datetime.today().date()

        #resets last_saved_reminders table
        cursor.execute("""
                    DELETE FROM last_saved_reminder
                    """)
                
        def get_users_with_reminders():
            """Fetch all users with reminders from the database"""
            try:
                # Query to see only users with saved information
                cursor.execute("""
                    SELECT id from users_schools_tokens_reminders_view
                    """)
                
                info = cursor.fetchall()
                return [] if info is None else [user_id[0] for user_id in info]  # Extract IDs from tuples
                
            except Exception as e:
                raise Exception(f'Unexpected error occurred when getting users with reminders: {e}')

        users_id = get_users_with_reminders()

        # Part that adjusts the last saved table
        for user_id in users_id:
            if user_id in users_dic:
                list_details = users_dic[user_id] 
                details=''.join([item for detail in list_details for item in detail])
                # Query to add or edit the users info into the reminder schedule table
                cursor.execute("""
                    INSERT INTO last_saved_reminder(user_id, details, date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id)
                    DO UPDATE SET 
                        details = EXCLUDED.details,
                        date = EXCLUDED.date
                """, (user_id, details, date))
            else:
                # Query to delete the users info from the reminder schedule table
                cursor.execute("""
                    DELETE FROM last_saved_reminder WHERE user_id = %s
                    """, (user_id,))
                
        conn.commit()
        
        return 'success'
    
    except Exception as e:
        if conn:
            conn.rollback()
        return f"Unexpected error occurred when adjusting last saved reminder: {e}"
    
    finally:
        if conn:
            conn.close()