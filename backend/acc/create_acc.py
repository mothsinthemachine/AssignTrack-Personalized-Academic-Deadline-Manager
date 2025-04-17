def save_account(username, password, phone_number, email_address, school_name):

    try:
        import datetime as dt
        from backend.db_conn import connect_to_db

        
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

    except sqlite3.OperationalError as e:
        print(f'Sqlite Error {e}')
        return 'fail'

    except sqlite3.IntegrityError as e:
        if 'users.username' in str(e):
            return 'Invalid: username has been taken'
        if 'users.phone_number' in str(e):
            return 'Invalid: number has been taken'
        if 'users.email_address' in str(e):
            return 'Invalid: email address has been taken'
        return 'Invalid'
    except Exception as e:
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
