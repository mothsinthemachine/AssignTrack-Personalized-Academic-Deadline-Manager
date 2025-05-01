#delete session for user
def rem_pending_user_from_db(user_id):
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to remove the users info from the pending users table
        cursor.execute("""
            DELETE FROM pending_users WHERE id = %s
            """,(user_id,))
        
        conn.commit()

        # Check if any row was deleted
        if cursor.rowcount == 0:
            return f"Invalid: No pending user found"

        return 'success'
        
    except Exception as e:
        if conn:
            conn.rollback()
        return f"Unexpected error occured when removing pending user {e}"

    finally:
        if conn:
            conn.close()

#transfer pending user to verified user
def unverified_to_verified_user(pending_user_id):
    try:
        from backend.db_conn import connect_to_db


        conn=connect_to_db()
        cursor=conn.cursor()

        #query to transfer the users from pending users table to verified users
        cursor.execute("""
            CALL promote_pending_user(%s);
            """,(pending_user_id,))
        
        conn.commit()

        return 'success'
        
    except Exception as e:
        if conn:
            conn.rollback()
        
        if "Verification expired" in str(e):
            return str(e)  # Return just the clean message from the stored procedure
        else:
            return f"Unexpected error occurred when transferring user from pending to verified: {e}"

    finally:
        if conn:
            conn.close()