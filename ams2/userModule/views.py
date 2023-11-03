from django.shortcuts import render, redirect,HttpResponse

from adminModule.models import ProfessorsTable,StudentsTable,HajriTable,ProfessorsInfoTable
from . models import AdminCode
from django.core.mail import send_mail
from datetime import datetime,timedelta
from userModule.models import AttendanceLog
from django.db.models import Count, F, FloatField, Sum
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.utils import timezone


def error_404_view(request, exception):
   
    # we add the path to the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html')

#----LOGIN Manage start----
from django.template.loader import render_to_string
def login(request):
    if request.method == "POST":
        login_code = request.POST.get("login_code")
        user_codes = ProfessorsInfoTable.objects.values_list('code', flat=True)
        admin_codes =AdminCode.objects.values_list('code', flat=True)
        current_date_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
            

        if login_code in admin_codes:
     
            response = redirect("adminModule/")
            response.set_cookie('admin_id', login_code,secure=True, httponly=True)
            return response
        
        elif login_code in user_codes:
            response = redirect('/attendence/')
            info = ProfessorsInfoTable.objects.get(code=login_code)
            response.set_cookie('id', login_code, secure=True, httponly=True)
           
            return response
        else:
            return render(request, "loginPage.html", {"error": "Invalid Code!!"})
                
    return render(request, "loginPage.html")
#----LOGIN Manage over----
import pytz
#----ATTENDENCE Manage start----
def attendance_page(request):
    ist_timezone = pytz.timezone('Asia/Kolkata')
    

    current_time_in_ist = datetime.now(ist_timezone)


    formatted_time = current_time_in_ist.strftime('%Y-%m-%d %I:%M:%S %p')
    login_code = request.COOKIES.get('id')
    if login_code is None:
        return redirect('/')
    today = datetime.today()  
    prof_data = ProfessorsInfoTable.objects.get(code=login_code)
    professor_name_is_the=prof_data.professor_name
    
    
    courses = ProfessorsTable.objects.filter(pid=prof_data.pid).values_list('course_name', 'course_code', 'semester','course_num')
    
    selected_course = request.POST.get('selected_course', request.GET.get('course_dropdown'))
    
    
    if selected_course:
        data = ProfessorsTable.objects.filter(course_name=selected_course).first()
        
        
        
        if data:
            z = ProfessorsTable.objects.filter(course_code=data.course_code, semester=data.semester).values_list('semester', 'course_code')
            students_list = StudentsTable.objects.filter(student_semster=data.semester).exclude(i_grade=1).values_list('student_rollno', 'student_name').order_by('student_rollno')
            i_grade_students_list = StudentsTable.objects.filter(student_semster=data.semester, i_grade=1).values_list('student_rollno', 'student_name').order_by('student_rollno')
            if students_list:
                if request.method=="POST" and 'submit-btn' in request.POST:
                    attendance_list = request.POST.getlist('absentees[]')
                    absentee_numbers = [int(rno) for rno in attendance_list]
                    for student_rollno, student_name in students_list:
                        status = 0 if student_rollno in absentee_numbers else 1
                        stu_Info = StudentsTable.objects.filter(student_rollno=student_rollno, student_semster=data.semester).first()
                        att_date_str = request.POST.get('att_date') 

                        
                        att_date = datetime.strptime(att_date_str, '%Y-%m-%d').date()
                        
                        hajri = HajriTable(
                            att_date=att_date, 
                            stu_regno=stu_Info.regno,
                            stu_roll_no=stu_Info.student_rollno,
                            stu_name=stu_Info.student_name,
                            course=selected_course,
                            is_present=status
                        )
                        
                    
                        hajri.save()

                    attendance_log = AttendanceLog(
                    timestamp=formatted_time,
                    course_name=selected_course,
                    semester=data.semester,
                    professor_name=prof_data.professor_name,
                    
                    )
                    attendance_log.save()
                    
        
        attendance = HajriTable.objects.all().values()
            
        return render(request, "attendencePage.html", {'courses': courses,'professor_name_is_the':professor_name_is_the,'selected_course': selected_course, 'z': z, 'students_list': students_list, 'attendance_list': attendance,'today': today,'ig':i_grade_students_list})

    return render(request, "attendencePage.html", {'courses': courses, 'selected_course': selected_course,'today': today,'professor_name_is_the':professor_name_is_the})

       
#----LOGIN Manage over----


def view_attendance(request):
    login_code = request.COOKIES.get('id')
    if login_code is None:
        return redirect('/')
    prof_data = ProfessorsInfoTable.objects.get(code=login_code)
    courses = ProfessorsTable.objects.filter(pid=prof_data.pid).values_list('course_name', 'course_code', 'semester')
    if request.method == "POST":
        selected_course = request.POST.get('course_dropdown')
        selected_date = request.POST.get('date_field')
        selected_date_value = selected_date

        attendance_list = None
        if selected_course and selected_date:
            attendance_list = HajriTable.objects.filter(course=selected_course, att_date=selected_date).order_by('-att_date')
        elif selected_course:
            attendance_list = HajriTable.objects.filter(course=selected_course).order_by('-att_date')
        elif selected_date:
            attendance_list = HajriTable.objects.filter(att_date=selected_date).order_by('-att_date')
        else:
            attendance_list = HajriTable.objects.all().order_by('-att_date').values()


        
        return render(request, "attendanceView.html", {'courses': courses, 'selected_course': selected_course, 'selected_date': selected_date_value, 'attendance_list': attendance_list})
    return render(request, "attendanceView.html", {'courses': courses})


#----LOGOUT function----
def logout(request):
    response = redirect('/')
    response.delete_cookie('id')
    return response
#----LOGOUT function----

from django.utils import timezone
def reports(request):
    login_code = request.COOKIES.get('id')
    if login_code is None:
        return redirect('/')
    
    selected_filter = request.GET.get('filter')
    prof_data = ProfessorsInfoTable.objects.get(code=login_code)
    courses = ProfessorsTable.objects.filter(pid=prof_data.pid).values_list('course_name', 'course_code', 'semester')
    selected_course = request.POST.get('selected_course') or request.GET.get('course_dropdown')
    professor_name_is_the=prof_data.professor_name
    if selected_course:
        if selected_filter == 'weekly':
            # Calculate the start and end dates for the current week
            today = timezone.now()
            start_of_week = today - timezone.timedelta(days=today.weekday())
            end_of_week = start_of_week + timezone.timedelta(days=6)

            # Query for weekly attendance data within the current week
            attendance_data = (
                HajriTable.objects
                .filter(course=selected_course, att_date__range=[start_of_week, end_of_week])
                .values_list('stu_regno', 'stu_name','stu_roll_no')
                .annotate(attendance_percentage=(Sum(Cast('is_present', output_field=FloatField())) / Count('att_date')) * 100)
            ).order_by('stu_roll_no')
        
        elif selected_filter == 'monthly':
            # Calculate the start and end dates for the current month
            current_time = timezone.now()

            # Determine the start of the current month
            start_of_month = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Calculate the end of the current month
            next_month = start_of_month.replace(month=start_of_month.month + 1, day=1)
            end_of_month = next_month - timezone.timedelta(days=1, microseconds=1)

            # Query for monthly attendance data within the current month
            attendance_data = (
                HajriTable.objects
                .filter(course=selected_course, att_date__range=[start_of_month, end_of_month])
                .values_list('stu_regno', 'stu_name','stu_roll_no')
                .annotate(attendance_percentage=(Sum(Cast('is_present', output_field=FloatField())) / Count('att_date')) * 100)
            ).order_by('stu_roll_no')
        
        elif selected_filter == 'percent':

            attendance_data = (
                HajriTable.objects
                .filter(course=selected_course)
                .values_list('stu_regno', 'stu_name','stu_roll_no')
                .annotate(attendance_percentage=(Sum(Cast('is_present', output_field=FloatField())) / Count('att_date')) * 100)
            ).order_by('attendance_percentage')
        else:
            # Default to overall attendance
            attendance_data = (
                HajriTable.objects
                .filter(course=selected_course)
                .values_list('stu_regno', 'stu_name','stu_roll_no')
                .annotate(attendance_percentage=(Sum(Cast('is_present', output_field=FloatField())) / Count('att_date')) * 100)
            ).order_by('stu_roll_no')
        
        attendance_data_list = list(attendance_data)

        return JsonResponse(attendance_data_list, safe=False)
    else:
        return render(request, "Attreports.html", {'courses': courses, 'selected_course': selected_course,'professor_name_is_the':professor_name_is_the})

def assign_i_grade(request):
    regno = request.GET.get('regno')
    
    student = StudentsTable.objects.get(regno=regno)
    
    student.assign_i_grade()
    student.save()
    subject = 'I grade Alert⚠'
    message = render_to_string('I_grade.html', {'student': student})
    from_email = 'lms.cait@google.com'
    recipient_list = [student.student_email]
    
    send_mail(subject,'', from_email, recipient_list, html_message=message)
    return JsonResponse({'success': True})


def send_alert(request):
    student_rollNo = request.GET.get('student_rollNo')
    student_name = request.GET.get('student_name')
    attendance_percentage = request.GET.get('attendance')
    selected_course = request.GET.get('course')
  
    try:
        student=StudentsTable.objects.get(student_rollno=student_rollNo,student_name=student_name)
    except StudentsTable.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Student not found in the selected semester.'})
    
    
    subject = f'Attendance Alert⚠️'
    message = render_to_string('attalert.html',{'sc':selected_course,'stu':student,'per':attendance_percentage})

    
    from_email = 'lms.cait@google.com'
    recipient_list = [student.student_email]
    try:
        send_mail(subject, '', from_email, recipient_list, html_message=message)
        success = True
    except Exception as e:
        
        success = False
    
    return JsonResponse({'success': success})



def profile(request):
    students=StudentsTable.objects.values_list('student_name',flat=True).values()
    
    if request.method == "POST":
        query = request.POST.get('q', '')
        students = StudentsTable.objects.filter(Q(student_name__icontains=query) | Q(regno__icontains=query)) .values_list('regno', 'student_name', 'student_semster', 'student_rollno').order_by('student_name')
        
        num_matched_records = len(students)
        
        if num_matched_records > 0:
            return render(request, 'profile.html', {'stu': students, 'num_matched_records': num_matched_records})
        else:
            no_records_message = "No matching records found."
            return render(request, 'profile.html', {'no_records_message': no_records_message})
            
    return render(request, 'profile.html',{'students':students})

from django.db.models import Q

def special_attendence(request, regno):
    if request.method == "GET":
        login_code = request.COOKIES.get('id')
        prof_data = ProfessorsInfoTable.objects.get(code=login_code)
        student = StudentsTable.objects.get(regno=regno)
        courses = ProfessorsTable.objects.filter(pid=prof_data.pid, semester=student.student_semster).values_list('course_name', flat=True)
        return render(request, 'specialAtt.html', {'student': student, 'course': courses})
    
    if request.method == "POST" and 'insert_att' in request.POST:
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y')
        course = request.POST.get('course')
        name = request.POST.get('name')
        regno = request.POST.get('regno')
        rollno = request.POST.get('rno')
        
        current_date = start_date
       
        while current_date <= end_date:
            attendance_records = HajriTable.objects.filter(att_date=current_date, stu_regno=regno,course=course,stu_roll_no=rollno)
            
            for attendance_record in attendance_records:
                
                attendance_record.is_present=1
                attendance_record.save()
            else:
                pass
                
            current_date += timedelta(days=1)
        
        response = HttpResponse(
            '<script>alert("Attendance has been successfully taken or modified.");'
            'window.location.href = "/attendence/profile/";</script>'
        )
        
        return response
    
    return HttpResponse("Invalid request")
    

import random
def reset(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if ProfessorsInfoTable.objects.filter(email=email).exists():
            random_number = ''.join(str(random.randint(0, 9)) for _ in range(7))
            subject = "Verfication Alert"
            message = render_to_string('verificationalert.html',{'code':random_number})
            from_email = "lms.cait@google.com"
            recipient_list = [email]
            send_mail(
                subject,
                '',
                from_email,
                recipient_list,
                html_message=message
            )
            response = redirect("confirmcode")
            response.set_cookie('confirm_code', random_number, secure=True, httponly=True)
            response.set_cookie('profemail', email, secure=True, httponly=True)
            return response
        else:
            invalid_email = True
            return render(request, "reset.html",{'invalid_email': invalid_email})
    return render(request, "reset.html")

def confirm_code(request):
    con_code = request.COOKIES.get('confirm_code')
    if request.method == 'POST':
        code = request.POST.get('code')
        if con_code and int(con_code) == int(code):
            print("VALID CODE")
            response = redirect('reset_code')
            response.delete_cookie('confirm_code')
            return response
        else:
            invalid_code=True
            return render(request, "ConfirmCode.html",{'invalid_code': invalid_code})
    return render(request, "ConfirmCode.html")

def reset_code(request):
    prof_email = request.COOKIES.get('profemail')
    current_date_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')    
    
    if not prof_email :
        return redirect("/")

    if request.method == "POST":
        response = redirect("/")
        code1 = request.POST.get('code1')
        code2 = request.POST.get('code2')

        if code1 == code2:
            professor = ProfessorsInfoTable.objects.get(email=prof_email)
            professor.code = code1
            professor.save()
            subject = "Password Change Confirmation"
            message = render_to_string('codcgd.html',{'cd':code2,'dt':current_date_time})
            from_email = "lms.cait@google.com"
            recipient_list = [prof_email]
            send_mail(
                subject,
                '',
                from_email,
                recipient_list,
                html_message=message
                )
            response.delete_cookie('profemail')
            return  response
            
        else:
            
            return render(request, 'resetCode.html', {'codes_do_not_match': True})

    return render(request, 'resetCode.html')
