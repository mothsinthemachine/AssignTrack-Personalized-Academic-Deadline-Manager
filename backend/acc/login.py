#function to get user info when loging in
def get_user_from_db(username, password, verified=True):
    from backend.db_conn import connect_to_db
    from web.app import bcrypt

    try:
        conn = connect_to_db()
        cursor=conn.cursor()
        if verified:
            cursor.execute("""
                SELECT 
                    id, username, password, phone_number, email_address, school_id, created_date
                FROM users 
                WHERE username = %s
            """, (username,))
        else:
            cursor.execute("""
                SELECT 
                    id, username, password, phone_number, email_address, school_id, created_date
                FROM pending_users 
                WHERE username = %s
            """, (username,))    

        info=cursor.fetchone()

        if info is None:
            return None

        is_correct = bcrypt.check_password_hash(info[2], password) 
        #will check based off hash
        if not is_correct:
            return None

        
        return {
            'id':info[0],
            'username':info[1],
            'phone_number':info[3],
            'email_address':info[4],
            'school_id':info[5],
            'created_date':info[6]
        }
    except Exception as e:
        print(f'Error getting user from db {e}')
    
    finally:
        if conn:
            conn.close()
#function to get user info by their id
def get_user_from_db_by_id(user_id, verified=True):
    from backend.db_conn import connect_to_db

    try:
        conn = connect_to_db()
        cursor=conn.cursor()

        if verified:
            cursor.execute("""
                SELECT 
                    id, username, phone_number, email_address, school_id, created_date, password
                FROM users 
                WHERE id = %s
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT 
                    id, username, phone_number, email_address, school_id, created_date, password
                FROM pending_users 
                WHERE id = %s
            """, (user_id,)) 

        info = cursor.fetchone()
        
        if info is None:
            return None
        
        return {
            'id':info[0],
            'username':info[1],
            'phone_number':info[2],
            'email_address':info[3],
            'school_id':info[4],
            'created_date':info[5],
            'password':info[6]
        }
    except Exception as e:
        print(f'Error getting user from db by id {e}')
    
    finally:
        if conn:
            conn.close()


if __name__=='__main__':
    get_user_from_db(), get_user_from_db_by_id()