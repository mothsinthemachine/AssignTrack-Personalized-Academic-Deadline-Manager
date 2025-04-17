def constant_save_reminder():
    from upcoming import Upcoming
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
    from queries.last_saved_reminder import adjust_last_saved_reminder


    #gets information from users_schools_tokens_reminders_view VIEW
    def constant_to_be_reminded():
        try:
            from db_conn import connect_to_db


            conn=connect_to_db()
            cursor=conn.cursor()

            #query to get the users_schools_tokens_reminders_view 'VIEW' to input into upcoming
            cursor.execute("""
                SELECT id, school_url, token, days_ahead, special from users_schools_tokens_reminders_view
                """)
            info=cursor.fetchall()

            if info is None:
                return False
            else:
                return info

        except Exception as e:
            raise Exception(f'Unexpected error occured when trying to access the view named users_schools_tokens_reminders_view {e}')

    def constant_save_to_be_reminded():
        from collections import defaultdict

        users_reminders_dict=defaultdict(list)

        #look for reminders for user
        users_reminders=constant_to_be_reminded()
        
        for user_remind in users_reminders:
            user_id=user_remind[0]
            school_url=user_remind[1]
            token=user_remind[2]
            days_ahead=user_remind[3]
            is_special=user_remind[4]

            detail = Upcoming(school_url, token, days_ahead, is_special)
            if detail is not None:
                if len(detail)>0:
                    users_reminders_dict[user_id].append(detail)
        adjust_last_saved_reminder(users_reminders_dict)

    constant_save_to_be_reminded()


if __name__ == '__main__':                  
    constant_save_reminder()
