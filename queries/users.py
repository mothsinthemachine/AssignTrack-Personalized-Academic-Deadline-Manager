def edit_phone_number(user_id, new_phone_number):
    conn = None
    try:
        from backend.db_conn import connect_to_db
        import psycopg2

        conn = connect_to_db()
        cursor = conn.cursor()

        # Query to update the user's phone number in the users table
        cursor.execute("""
            UPDATE users SET phone_number = %s WHERE id = %s
            """, (new_phone_number, user_id))
        
        # Check if any rows were affected by the update
        if cursor.rowcount == 0:
            return 'Invalid: user ID not found'
            
        conn.commit()
        return 'success'

    except psycopg2.errors.IntegrityError as e:
        if conn:
            conn.rollback()
        if 'reminders.user_id' in str(e):
            return 'Invalid: user ID not found in reminders table'
        if 'unique_phone' in str(e) or 'users_phone_number_key' in str(e):
            return 'Invalid: phone number has already been taken'
        return f'Database integrity error: {e}'
    except Exception as e:
        if conn:
            conn.rollback()
        return f"Unexpected error occurred when updating phone number: {e}"
    finally:
        if conn:
            conn.close()

def edit_user_email(user_id, new_email_address):
    conn = None
    try:
        from backend.db_conn import connect_to_db
        import psycopg2

        conn = connect_to_db()
        cursor = conn.cursor()

        # Query to update the user's email address in the users table
        cursor.execute("""
            UPDATE users SET email_address = %s WHERE id = %s
            """, (new_email_address, user_id))
        
        # Check if any rows were affected by the update
        if cursor.rowcount == 0:
            return 'Invalid: user ID not found'
            
        conn.commit()
        return 'success'

    except psycopg2.errors.IntegrityError as e:
        if conn:
            conn.rollback()
        if 'reminders.user_id' in str(e):
            return 'Invalid: user ID not found in reminders table'
        if 'unique_email' in str(e) or 'users_email_address_key' in str(e):
            return 'Invalid: email address has already been taken'
        # Handle other integrity constraint violations
        return f'Database integrity error: {e}'
    except Exception as e:
        if conn:
            conn.rollback()
        return f"Unexpected error occurred when updating email address: {e}"
    finally:
        if conn:
            conn.close()

#function that checks if input is already in the users table
def check_users_existing_info(info_type: str, to_check) -> str:
    # Validate allowed info types
    if info_type not in ["phone_number", "email_address", "username"]:
        return f'Invalid parameter got {info_type}'
    
    conn = None
    try:
        from backend.db_conn import connect_to_db
        conn = connect_to_db()
        cursor = conn.cursor()

        if info_type == "phone_number":
            column = "phone_number"
        elif info_type == "email_address":
            column = "email_address"
        else:
            return "Invalid parameter"
            
        #query to check if value exists
        query = f"SELECT COUNT(*) FROM users WHERE {column} = %s"
        cursor.execute(query, (to_check,))
        
        count = cursor.fetchone()[0]
        
        # Return result based on existence check
        if count > 0:
            return 'Invalid'  # Value already exists
        else:
            return 'Valid'    # Value doesn't exist
    
    except Exception as e:
        return f'Unexpected error occurred when checking users existing info: {e}'
    
    finally:
        if conn:
            conn.close()