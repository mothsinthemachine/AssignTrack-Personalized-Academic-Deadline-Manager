def school_name_list() -> list:
    try:
        from backend.db_conn import connect_to_db

        conn=connect_to_db()
        cursor=conn.cursor()

        #gets the id of school from its name
        cursor.execute("""
            SELECT name FROM schools
        """)
        school_names=cursor.fetchall()

        return school_names

    except Exception as e:
        print(f' Unexpected Error Occured in function school_name_list {e}')


#edits school for user
def edit_user_school(user_id, school_name):
    from backend.db_conn import connect_to_db

    conn = None

    try:
        # Step 1: Connect to the database
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
        except Exception as e:
            return f"Error connecting to database: {e}"

        # Step 2: Check if the school exists
        try:
            cursor.execute("SELECT id FROM schools WHERE name = %s", (school_name,))
            school_id = cursor.fetchone()
        except Exception as e:
            return f"Error getting the school id: {e}"

        if school_id:
            school_id = school_id[0]  # Extract the ID from the tuple

            # Step 3: Update the user's school_id
            try:
                cursor.execute(
                    "UPDATE users SET school_id = %s WHERE id = %s",
                    (school_id, user_id)
                )
                conn.commit()
                return "Success: Updated existing user school"
            except Exception as e:
                return f"Error updating user school: {e}"
        else:
            return "Error: Could not find a school with that name"

    finally:
        if conn:
            conn.close()

def get_school_url(school_id) -> str:
    try:
        from backend.db_conn import connect_to_db

        conn=connect_to_db()
        cursor=conn.cursor()

        #gets url of school from its name
        cursor.execute("""
            SELECT canvas_link FROM schools WHERE id = %s
        """,(school_id,))
        school_url=cursor.fetchone()

        return school_url[0]

    except Exception as e:
        print(f' Unexpected Error Occured in function get_school_url {e}')
    finally:
        if conn:
            conn.close()

def get_user_school_name(school_id) -> str:
    try:
        from backend.db_conn import connect_to_db

        conn=connect_to_db()
        cursor=conn.cursor()

        #gets url of school from its name
        cursor.execute("""
            SELECT name FROM schools WHERE id = %s
        """,(school_id,))
        school_url=cursor.fetchone()

        return school_url[0]

    except Exception as e:
        print(f' Unexpected Error Occured in function get_school_name {e}')
        
    finally:
        if conn:
            conn.close()
if __name__=='__main__':
    school_name_list()