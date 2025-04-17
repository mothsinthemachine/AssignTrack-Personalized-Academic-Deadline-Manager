def Upcoming(school_url, token, days_ahead, is_special) -> list:
    from canvasapi import Canvas
    import datetime as dt
    import pytz


    try:
        assighn_list=[]

        canvas=Canvas(school_url, token)
        user=canvas.get_current_user()
        courses=canvas.get_courses(enrollment_status='active')
        eastern_tz=pytz.timezone("America/New_York")

        if courses is not None:
            for course in courses:
                #stop adding assighnments at 10
                if len(assighn_list)>10:
                    break

                assignments=course.get_assignments()
                for assignment in assignments:

                    submission = assignment.get_submission(user.id)

                    #only check assighnments that have due dates
                    if assignment.due_at is not None:
                        # Check if the assignment hasn't been submitted yet
                        if submission.workflow_state == 'unsubmitted':  
                            due_at_date=assignment.due_at_date.astimezone(eastern_tz)
                            today_date=eastern_tz.localize(dt.datetime.today())
                            days_dif_datetime=due_at_date-today_date
                            days_dif=days_dif_datetime.days

                            course_code, course_name = str(course).split('|')
                            due_at_date_12hr_format = due_at_date.strftime("%Y-%m-%d %I:%M %p")

                            #does the check for is_special
                            if is_special==1:
                                if days_dif>0 and days_dif<=days_ahead:
                                    assighn_list.append(f'Due date: {due_at_date_12hr_format}/assignment name: {assignment}/Course name: {course_name}//')
                            else:
                                if days_dif==days_ahead:
                                    assighn_list.append(f'Due date: {due_at_date_12hr_format}/assignment name: {assignment}/Course name: {course_name}//')
        
        #makes the max amount of returnable assignments to 10
        return assighn_list[:10]

    except Exception as e:
        print(f'Unexpected Error from Upcoming function occured {e}')
                    
if __name__=='__main__':
    Upcoming()

