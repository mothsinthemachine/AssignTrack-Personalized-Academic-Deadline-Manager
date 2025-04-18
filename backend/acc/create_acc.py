def save_account(username, password, phone_number, email_address, school_name):
    conn = None
    try:
        import datetime as dt
        from backend.db_conn import connect_to_db
        import psycopg2
        
        conn = connect_to_db()
        cursor = conn.cursor()

        created_date = str(dt.date.today())

        # gets the id of school from its name
        cursor.execute("""
            SELECT id FROM schools WHERE name = %s
        """, (school_name,))

        school_id = cursor.fetchone()

        if school_id is None:
            return "Invalid school couldn't be found"
        school_id = school_id[0]

        cursor.execute('INSERT INTO users(username, password, phone_number, email_address, school_id, created_date) VALUES (%s,%s,%s,%s,%s,%s)',
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
        # Check unique constraint violations
        if 'unique_username' in str(e) or 'users_username_key' in str(e):
            return 'Invalid: username has been taken'
        if 'unique_phone' in str(e) or 'users_phone_number_key' in str(e):
            return 'Invalid: number has been taken'
        if 'unique_email' in str(e) or 'users_email_address_key' in str(e):
            return 'Invalid: email address has been taken'
        return 'Invalid'
        
    except Exception as e:
        if conn:
            conn.rollback()
        return f'Unexpected Error occurred in save account {e}'

    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # Example usage with dummy data
    result = save_account(
        username="johndoe123",
        password="password123",
        phone_number="123-456-7890",
        email_address="johndoe@example.com",
        school_name="mdc"
    )
