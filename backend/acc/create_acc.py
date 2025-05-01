def save_account(username, password, email_address, phone_number=None, school_name='', school_id=1):
    conn = None
    try:
        import datetime as dt
        from backend.db_conn import connect_to_db
        import psycopg2
        
        conn = connect_to_db()
        cursor = conn.cursor()

        created_date = str(dt.date.today())
        if school_name!='':
            # gets the id of school from its name
            cursor.execute("""
                SELECT id FROM schools WHERE name = %s
            """, (school_name,))

            school_id = cursor.fetchone()

            if school_id is None:
                return "Invalid school couldn't be found"
            school_id = school_id[0]

        # Check if username, email, or phone already exists in users table
        # Only check phone if it's not None
        if phone_number is not None:
            cursor.execute("""
                SELECT 
                    CASE WHEN EXISTS(SELECT 1 FROM users WHERE username = %s) THEN 'username'
                         WHEN EXISTS(SELECT 1 FROM users WHERE email_address = %s) THEN 'email'
                         WHEN EXISTS(SELECT 1 FROM users WHERE phone_number = %s) THEN 'phone'
                         ELSE NULL
                    END as existing_field
            """, (username, email_address, phone_number))
        else:
            cursor.execute("""
                SELECT 
                    CASE WHEN EXISTS(SELECT 1 FROM users WHERE username = %s) THEN 'username'
                         WHEN EXISTS(SELECT 1 FROM users WHERE email_address = %s) THEN 'email'
                         ELSE NULL
                    END as existing_field
            """, (username, email_address))
        
        existing = cursor.fetchone()[0]
        
        if existing:
            if existing == 'username':
                return 'Invalid: username has been taken'
            elif existing == 'email':
                return 'Invalid: email address has been taken'
            elif existing == 'phone':
                return 'Invalid: phone number has been taken'
    
        # If no conflicts with users table, proceed with insertion into pending_users
        cursor.execute('INSERT INTO pending_users(username, password, phone_number, email_address, school_id, created_date) VALUES (%s,%s,%s,%s,%s,%s)',
                    (username, password, phone_number, email_address, school_id, created_date))       

        conn.commit()
        return 'success'

    except psycopg2.errors.OperationalError as e:
        if conn:
            conn.rollback()
        print(f'PostgreSQL Error: {e}')
        return 'fail'

    except psycopg2.errors.IntegrityError as e:
        if conn:
            conn.rollback()

        # Check unique constraint violations for pending users table
        if 'unique_username' in str(e) or 'pending_users_username_key' in str(e):
            return 'Invalid: username has been taken'
        if 'unique_email' in str(e) or 'pending_users_email_address_key' in str(e):
            return 'Invalid: email address has been taken'
        if 'unique_phone' in str(e) or 'pending_users_phone_number_key' in str(e):
            return 'Invalid: phone number has been taken'
        return 'Invalid'
          
    except Exception as e:
        if conn:
            conn.rollback()
        return f'Unexpected Error occurred in save account {e}'

    finally:
        if conn:
            conn.close()