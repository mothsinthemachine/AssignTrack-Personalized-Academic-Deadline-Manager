#function to get user info when loging in
def get_user_from_db(username, password):
    from backend.db_conn import connect_to_db

    try:
        conn = connect_to_db()
        cursor=conn.cursor()

        cursor.execute("""
            SELECT 
                id, username, password, phone_number, email_address, school_id, created_date
            FROM users 
            WHERE username = %s
        """, (username,))

        info=cursor.fetchone()

        if info is None:
            return None
        
        #will check based off hash
        if password != info[2]:
            return None

        
        return {
            'id':info[0],
            'username':info[1],
            'password':info[2],
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
def get_user_from_db_by_id(user_id):
    from backend.db_conn import connect_to_db

    try:
        conn = connect_to_db()
        cursor=conn.cursor()

        cursor.execute("""
            SELECT 
                id, username, password, phone_number, email_address, school_id, created_date
            FROM users 
            WHERE id = %s
        """, (user_id,))

        info = cursor.fetchone()
        
        if info is None:
            return None
        
        return {
            'id':info[0],
            'username':info[1],
            'password':info[2],
            'phone_number':info[3],
            'email_address':info[4],
            'school_id':info[5],
            'created_date':info[6]
        }
    except Exception as e:
        print(f'Error getting user from db by id {e}')
    
    finally:
        if conn:
            conn.close()


if __name__=='__main__':
    get_user_from_db(), get_user_from_db_by_id()