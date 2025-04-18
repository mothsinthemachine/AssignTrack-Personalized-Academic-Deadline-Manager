#adds token for user
def add_token(user_id, token):
    try:
        from backend.db_conn import connect_to_db
        import psycopg2

        conn=connect_to_db()
        cursor=conn.cursor()

        #query to add the users info into the tokens table
        cursor.execute("""
            INSERT INTO tokens(user_id, token)
            VALUES (%s,%s)
            """,(user_id, token))
        
        conn.commit()

        return 'success'

    except psycopg2.errors.IntegrityError as e:
        if conn:
            conn.rollback()
        if 'token.user_id' in str(e):
            return 'Invalid, user already have a token'
        # Handle other integrity constraint violations
        return f'Database integrity error: {e}'
    except Exception as e:
        if conn:
            conn.rollback()
        return f"Unexpected error occured when adding token {e}"

    finally:
        if conn:
            conn.close()

#edits token for user
def edit_token(user_id, token):
    try:
        from backend.db_conn import connect_to_db
        import psycopg2

        conn=connect_to_db()
        cursor=conn.cursor()

        #query to edit the users info into the tokens table
        cursor.execute("""
            UPDATE tokens SET token = %s WHERE user_id = %s
            """,(token, user_id))
        
        conn.commit()

        return 'success'

    except psycopg2.errors.IntegrityError as e:
        if conn:
            conn.rollback()
        if 'token.user_id' in str(e):
            return 'Invalid, user have yet to add a token to edit'
        # Handle other integrity constraint violations
        return f'Database integrity error: {e}'
    except Exception as e:
        if conn:
            conn.rollback()
        return f"Unexpected error occured when editting token {e}"

    finally:
        if conn:
            conn.close()

#checks if user already have a token
def check_user_token_status(user_id):
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to edit the users info into the tokens table
        cursor.execute("""
            SELECT token FROM tokens WHERE user_id = %s
            """,(user_id,))

        info=cursor.fetchone()

        conn.commit()
        conn.close()

        if info is None:
            return False
        else:
            return info[0]

    except Exception as e:
        raise Exception(f'Unexpected error occured when checking user token status {e}')

#delete reminders for user
def rem_token(user_id):
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to remove the users info from the reminders table
        cursor.execute("""
            DELETE FROM tokens WHERE user_id = %s
            """,(user_id, ))
        
        conn.commit()

        # Check if any row was deleted
        if cursor.rowcount == 0:
            return f"Invalid: No token found for user"

        return 'success'
        
    except Exception as e:
        if conn:
            conn.rollback()
        return f"Unexpected error occured when removing token {e}"

    finally:
        if conn:
            conn.close()

if __name__=='__main__':
    check_user_token_status()
    edit_token()
    add_token()
    rem_token()