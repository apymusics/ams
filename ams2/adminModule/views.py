from django.core.mail import send_mail,send_mass_mail
from django.shortcuts import render,redirect,HttpResponse
from . models import ProfessorsTable,StudentsTable,HajriTable,ProfessorsInfoTable
from django.db.models import Count, FloatField, Sum
from django.db.models.functions import Cast
from django.http import JsonResponse
from userModule.models import AdminCode,LoginCode
import datetime,random
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
import random
from .forms import ExcelImportForm
import uuid
import pandas as pd
import uuid
from datetime import datetime
from django.template.loader import render_to_string

def index(request):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    
    return redirect('/../adminModule/prof_view')



#-----COURSE ASSIGNMANET----
def professorsPanel(request):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    
    profdata = ProfessorsTable.objects.all().order_by('semester').values()
    profdata2 = ProfessorsInfoTable.objects.all().order_by('professor_name').values()
    
    semesters = sorted(set(ProfessorsTable.objects.values_list('semester',flat=True)))
    professors= sorted(set(ProfessorsTable.objects.values_list('professor_name',flat=True)))
    professors2= ProfessorsInfoTable.objects.all()
    
    filter_prof = request.GET.get('prof_filter')
    filter_sem = request.GET.get('sem_filter')
    result = profdata  
    duplicate=0
    if filter_prof and filter_sem:
        result = ProfessorsTable.objects.filter(professor_name=filter_prof, semester=filter_sem)
    
    elif filter_prof :
        result = ProfessorsTable.objects.filter(professor_name=filter_prof)
    
    elif filter_sem:
        result = ProfessorsTable.objects.filter(semester=filter_sem)
    
    if request.method=="POST" and 'course_assignment' in request.POST:
         
        p_id = str(request.POST.get('professor_name'))
        course_code = str(request.POST.get('course_code'))
        course_num=str(request.POST.get('course_number'))
        course_name = str(request.POST.get('course_name'))
        semester = str(request.POST.get('semester'))
        
        p_name=ProfessorsInfoTable.objects.get(pid=p_id)
        
        if ProfessorsTable.objects.filter(
            Q(course_code=course_code, course_num=course_num, course_name=course_name) |
            Q(course_code=course_code, course_num=course_num) |
            Q(course_name=course_name)
        ).exists():
            duplicate=1
        else:
            now = datetime.now()

# Extract the components: year, date, time, and seconds
            year = now.year
            date = now.strftime("%Y%m%d")
            time = now.strftime("%H%M%S")
            seconds = now.second


            unique_id = f"{year}{date}{time}{seconds}AIT"
            professor = ProfessorsTable(
            cid=unique_id,
            pid=p_id,
            professor_name=p_name.professor_name,
            course_code=course_code,
            course_name=course_name,
            course_num=course_num,
            semester=semester,
        )
            professor.save()
           

        
        messages.success(request, "Record added successfully.")


        profdata = ProfessorsTable.objects.all().values()
  
  #REGISTERING FOR A PROFESSOR----------------
         
        return render(request,'CoursesPage.html',{"pd":profdata,"pd2":profdata2,"sem":semesters,"pro":professors,"pro2":professors2,'duplicate':duplicate})
    
    return render(request, 'CoursesPage.html', {"pd": result,"pd2":profdata2, "sem": semesters, "pro": professors,"pro2":professors2,'duplicate':duplicate})








#ADD PROFESSOR
def prof_detail(request):
    professors = sorted(set(ProfessorsInfoTable.objects.values_list('professor_name', flat=True)))
    filter_prof = request.GET.get('prof_filter')
    result = ProfessorsInfoTable.objects.values().all()

    if filter_prof:
        result = ProfessorsInfoTable.objects.filter(professor_name=filter_prof).all()

    if request.method == 'POST' and 'add_professor' in request.POST:
        professor_name = request.POST.get('professor_name')
        ph_no = request.POST.get('phone_number')
        email = request.POST.get('email')

        # Generate unique_id and unique_code
        seconds = datetime.now().strftime("%S") + str(random.randint(1, 9999))
        random_number = str(random.randint(1, 100))
        unique_id = seconds + "AIT" + random_number
        unique_code = str(uuid.uuid4())[:7]

        if not ProfessorsInfoTable.objects.filter(phone_number=ph_no).exists() and not ProfessorsInfoTable.objects.filter(email=email).exists():
            duplicate=0
            professorInfo = ProfessorsInfoTable(
                pid=unique_id,
                professor_name=professor_name,
                phone_number=ph_no,
                email=email,
                code=unique_code
            )
            professorInfo.save()

            # Send email to the professor
            subject = "Welcome"
            message = f"Dear Professor {professor_name},\n\nWe hope this email finds you well. As a valued member of our faculty at College of AIT, we are delighted to provide you with your unique login code.\n\nYour Login Code: {unique_code}\n\nWith this code, you will have secure access to our attendance management system within our portal.\n\nIf you encounter any issues during the login process or have any questions, please feel free to reach out to our IT support team.\n\nThank you for your dedication to our institution, and we are looking forward to an exceptional academic journey with you.\n\nBest regards,\nCollege of AIT"
            from_email = "sapanlily123@student.aau.in"
            recipient_list = [email]

            email_sent = send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )

            if not email_sent:
                return render(request, 'professorView.html', {"result": result, "pro": professors,'duplicate':duplicate,'error_send_email':1})

        else:
            duplicate=1
        
        return render(request, 'professorView.html', {"result": result, "pro": professors,'duplicate':duplicate})
    return render(request, 'professorView.html', {"result": result, "pro": professors})


def prof_delete(request,uid):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    
    value=ProfessorsTable.objects.filter(cid=uid)

    value.delete()
    return redirect("/../adminModule/prof")



def prof_info_delete(request,uid):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    professors2= ProfessorsInfoTable.objects.exclude(pid=uid)
    value=ProfessorsInfoTable.objects.filter(pid=uid)
    prof_courses=ProfessorsTable.objects.filter(pid=uid)

    if request.method=="POST":
        print("in POST")

        pid =  request.POST.getlist("professor_name[]")
        course_codes = request.POST.getlist("course_code[]")
        course_numbers = request.POST.getlist("course_number[]")
        course_names = request.POST.getlist("course_name[]")
        semesters = request.POST.getlist("semester[]")
        
        for i in range(len(pid)):
            

           
            existing_record=ProfessorsTable.objects.filter(course_code=course_codes[i],course_num=course_numbers[i],course_name=course_names[i],semester=semesters[i])
            
            for j in existing_record:
                j.pid=pid[i]
                j.professor_name=ProfessorsInfoTable.objects.get(pid=pid[i]).professor_name
                j.course_code=course_codes[i]
                j.course_num=course_numbers[i]
                j.course_name=course_names[i]
                j.semester=semesters[i]
                j.save()

                print("SUCCESS")
                
                
        
        value.delete()
        return redirect("/../adminModule/prof")    

     



    # value.delete()
    return render(request,"afterDelete.html",{'courses_list':prof_courses,"pro2":professors2})




def mprof_delete(request):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    
    selected_students = request.POST.getlist('delete_list[]')
    ProfessorsInfoTable.objects.filter(pid__in=selected_students).delete()
    
    return redirect("/../adminModule/prof_view")

def prof_edit(request,uid):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    
    member =ProfessorsTable.objects.filter(cid=uid)
    professors = ProfessorsInfoTable.objects.values_list('pid','professor_name')
    return render(request,"editCourses.html",{'c':member,'pro':professors})


#EDIT PROFESOR
def prof_info_edit(request,uid):
    
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    
    member =ProfessorsInfoTable.objects.filter(pid=uid)
    return render(request,"editProfInfo.html",{'c':member})
#-----PROFESSOR panel Manage Over----

#-----STUDENT panel Manage Start----
def stu_edit(request,uid):
    
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    
    member =StudentsTable.objects.filter(regno=uid)

    
    return render(request,"editStudent.html",{'c':member})

def edit_stu_record(request, uid):

    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    member =StudentsTable.objects.get(uid=uid)
    member.regno =request.POST.get('regno')
    member.student_rollno =request.POST.get('roll_no')
    member.student_name =request.POST.get('student_name')
    member.student_semster =request.POST.get('semester')
    member.student_email =request.POST.get('email')
    member.save()
    
    hajri_records = HajriTable.objects.filter(stu_regno=member.regno)

    # Update the student's name in HajriTable records
    for hajri_record in hajri_records:
    
        hajri_record.stu_name = request.POST.get('student_name')
        hajri_record.stu_regno = request.POST.get('regno')
        hajri_record.stu_roll_no = request.POST.get('roll_no')
        hajri_record.save()
    
        

    
    return redirect("/../adminModule/stu") 



#COURSE EDIT
def edit_prof_record(request, uid):
    
    
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    member =ProfessorsTable.objects.get(cid=uid)

    member.professor_name =ProfessorsInfoTable.objects.get(pid=request.POST.get('prof_name')).professor_name
    
    member.semester=request.POST.get('semester')
    member.cid=member.pid =request.POST.get('prof_name')
    member.course_code =request.POST.get('course_code')
    member.course_num=request.POST.get('course_number')
    member.course_name =request.POST.get('course_name')
    member.save()
    return redirect("/../adminModule/prof") 






#PROFESSOR EDITR
def edit_info_prof_record(request, uid):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    member =ProfessorsInfoTable.objects.get(pid=uid)
    
    member.professor_name =request.POST.get('professor_name')
    member.code =request.POST.get('code')
    member.phone_number =request.POST.get('phno')
    member.email =request.POST.get('professor_email')
    member.save()

    member2 =ProfessorsTable.objects.filter(pid=member.pid)
    
    for prof_name in member2:
    
        prof_name.professor_name = request.POST.get('professor_name')
        prof_name.save()
    

    return redirect("/../adminModule/prof_view") 





def studentsPanel(request):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    excel_form = ExcelImportForm()
    studata = StudentsTable.objects.all().order_by('student_semster')
    semesters = sorted(set(StudentsTable.objects.values_list('student_semster', flat=True)))
    filter_sem = request.GET.get('sem_filter')
    result = studata

    if filter_sem:
        if filter_sem.isnumeric():
            result = StudentsTable.objects.filter(student_semster=filter_sem)
    else:
        result = StudentsTable.objects.all().order_by('student_semster')
    
    
    if request.method == 'POST' and 'student_search_button' in request.POST:

        
        search_query_st_name = request.POST['student_name_search']
        result = StudentsTable.objects.filter(Q(student_name__icontains=search_query_st_name)).order_by('student_semster')

        

        return render(request, 'studentsPanel.html', {"sd": result, "sem": semesters, "excel_form": excel_form,'search_query_st_name':search_query_st_name})
        
    if request.method == 'POST' and 'multiple_insert_button' in request.POST :
        
        form_type = request.POST.get('form_type')
        if form_type == 'multiple':
            successfully_inserted = []
            duplicate_entries = []

            for i in range(0, 10):
                student_regno = request.POST.get(f'entry[{i}][regno]')
                student_name = request.POST.get(f'entry[{i}][student_name]')
                student_rollno = request.POST.get(f'entry[{i}][roll_number]')
                student_semester = request.POST.get(f'entry[{i}][semester]')
                student_email = request.POST.get(f'entry[{i}][email]')
                
                if student_name is not None and student_rollno is not None and student_semester is not None:
                    response_data = handle_single_entry(request, student_regno, student_name, student_rollno, student_semester, student_email)
                    
                    successfully_inserted.extend(response_data['successfully_inserted'])
                    duplicate_entries.extend(response_data['duplicate_entries'])
            
            duplicate_entries_found=0
            k=0
            duplicate_entries_dict = []
            if duplicate_entries:
                duplicate_entries_found=1
                 
                for entry in duplicate_entries:
                    k+=1
                    duplicate_entry = {
                        'regno': entry['regno'],
                        'name': entry['student_name'],
                        'rollno': entry['student_rollno'],
                        'sem': entry['student_semester'],
                        'email': entry['student_email'],
                    }
                    duplicate_entries_dict.append(duplicate_entry)
            duplicate_records=len(duplicate_entries_dict)
        return render(request, 'studentsPanel.html', {"sd": result, "sem": semesters, "excel_form": excel_form, "duplicate_entries_dict": duplicate_entries_dict,"duplicate_entries_found":duplicate_entries_found,'duplicate_records':duplicate_records})            

        # Add the Excel import handling here
    elif request.method == 'POST' and 'import_excel' in request.POST:
        excel_form = ExcelImportForm(request.POST, request.FILES)
        if excel_form.is_valid():
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            
            successfully_inserted = []
            duplicate_entries = []
            
            for index, row in df.iterrows():
                student_regno = str(row[0])
                student_name = str(row[1])
                student_semester = str(row[2])
                student_rollno = str(row[3])
                student_email = str(row[4])
                
                response_data = handle_single_entry(request, student_regno, student_name, student_rollno, student_semester, student_email)
                
                successfully_inserted.extend(response_data['successfully_inserted'])
                duplicate_entries.extend(response_data['duplicate_entries'])
                
            if successfully_inserted:
                alert_message_success = "Successfully inserted records:\n"
                for entry in successfully_inserted:
                    alert_message_success += f"RegNo: {entry['regno']}, Name: {entry['student_name']}\n"
                
            
            duplicate_entries_found=0
        duplicate_entries_dict = []
        if duplicate_entries:
            duplicate_entries_found=1
            k=0    
            for entry in duplicate_entries:
                k+=1
                duplicate_entry = {
                    'regno': entry['regno'],
                    'name': entry['student_name'],
                    'rollno': entry['student_rollno'],
                    'sem': entry['student_semester'],
                    'email': entry['student_email'],
                }
                duplicate_entries_dict.append(duplicate_entry)
        duplicate_records=len(duplicate_entries_dict)
        return render(request, 'studentsPanel.html', {"sd": result, "sem": semesters, "excel_form": excel_form, "duplicate_entries_dict": duplicate_entries_dict,"duplicate_entries_found":duplicate_entries_found,'duplicate_records':duplicate_records})            
            


    # No Excel file found
        
    
    
    
    return render(request, 'studentsPanel.html', {"sd": result, "sem": semesters, "excel_form": excel_form})

def handle_single_entry(request, student_regno, student_name, student_rollno, student_semester, student_email):
    seconds = datetime.now().strftime("%S")
    random_number1 = str(random.randint(1, 100))
    random_number2 = str(random.randint(101, 999))
    unique_id = seconds + "stu" + random_number1 + random_number2

    # Initialize lists to store successfully inserted and duplicate entries
    successfully_inserted = []
    duplicate_entries = []

    # Check for duplicate entries
    if StudentsTable.objects.filter(regno=student_regno, student_rollno=student_rollno, student_semster=student_semester, student_email=student_email).exists() \
            or StudentsTable.objects.filter(regno=student_regno, student_rollno=student_rollno, student_semster=student_semester).exists() \
            or StudentsTable.objects.filter(student_semster=student_semester, student_email=student_email).exists() \
            or StudentsTable.objects.filter(student_semster=student_semester, student_email=student_email).exists() \
            or StudentsTable.objects.filter(regno=student_regno, student_semster=student_semester).exists() \
            or StudentsTable.objects.filter(regno=student_regno, student_name=student_name).exists() \
            or StudentsTable.objects.filter(regno=student_regno, student_email=student_email).exists() \
            or StudentsTable.objects.filter(student_name=student_name,student_email=student_email).exists() \
            or StudentsTable.objects.filter(student_email=student_email).exists() \
            or StudentsTable.objects.filter(regno=student_regno).exists():
        
        duplicate_entries.append({
            'regno': student_regno,
            'student_name': student_name,
            'student_rollno': student_rollno,
            'student_semester': student_semester,
            'student_email': student_email
        })
    else:
        student = StudentsTable(
            uid=unique_id,
            regno=student_regno,
            student_rollno=student_rollno,
            student_name=student_name,
            student_semster=student_semester,
            student_email=student_email
        )
        student.save()
        
        successfully_inserted.append({
            'regno': student_regno,
            'student_name': student_name,
            'student_rollno': student_rollno,
            'student_semester': student_semester,
            'student_email': student_email
        })

    # Prepare a response JSON with both types of entries
    response_data = {
        'successfully_inserted': successfully_inserted,
        'duplicate_entries': duplicate_entries
    }

    return response_data

#-----STUDENT panel Manage Over----
def stu_delete(request,uid):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    value=StudentsTable.objects.filter(regno=uid)
    value.delete()
    return redirect("/../adminModule/stu")

def mstu_delete(request):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    
    selected_students = request.POST.getlist('delete_list[]')
    
    StudentsTable.objects.filter(regno__in=selected_students).delete()
    
    return redirect("/../adminModule/stu")

def admin(request):

    
    admindata = AdminCode.objects.all()  
    if request.method == 'POST':
        name = str(request.POST.get('admin_name'))
        admin_login_code = str(request.POST.get('admin_code'))
        
        if AdminCode.objects.filter(admin_name=name, code=admin_login_code).exists():
            messages.warning(request, "Duplicate entry. Please try again.")
        else:
            admin = AdminCode(admin_name=name, code=admin_login_code)
            admin.save()
            messages.success(request, "Record added successfully.")
    
        admindata = AdminCode.objects.all()  
    
        return render(request, 'Admin.html', {"admindata": admindata})
    return render(request, 'Admin.html', {"admindata": admindata})

def admin_delete(request,code):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    value=AdminCode.objects.filter(code=code)
    value.delete()
    return redirect("/../adminModule/adminSettings")

def admin_edit(request,code):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
    member =AdminCode.objects.filter(code=code)
    return render(request,"editAdmin.html",{'c':member})

def edit_admin_record(request, code):
    login_code = request.COOKIES.get('admin_id')
    if login_code is None:
        return redirect('/')
  
    member =AdminCode.objects.get(code=code)
    member.admin_name =request.POST.get('admin_name')
    member.code =request.POST.get('admin_code')
  
    member.save()
    return redirect("/../adminModule/adminSettings") 



def reports(request):
    sem_filter = request.GET.get('sem_filter')
    course_filter = request.GET.get('course_filter')

    semesters = ['1', '2', '3', '4', '5', '6', '7']  

    courses_info = None
    if sem_filter:
        courses_info = ProfessorsTable.objects.filter(semester=sem_filter).values_list('course_name', 'course_code', 'professor_name')
        
    attendance_data = None
    if course_filter:
        attendance_data = HajriTable.objects.filter(course=course_filter).values_list('stu_regno','stu_roll_no', 'stu_name').annotate(attendance_percentage=(Sum(Cast('is_present', output_field=FloatField())) / Count('att_date')) * 100).order_by('stu_roll_no')
        
        
        

    return render(request, 'reports.html', {'sem': semesters,'sem_filter': sem_filter,'info': courses_info,'attendence': attendance_data,'selected_course': course_filter})




from django.db.models import Sum, Count, Case, When, FloatField

from django.db.models import Sum, Count, FloatField
from django.http import JsonResponse

from django.db.models import Sum, Count, FloatField
from django.http import JsonResponse

def send_alert_to_multiple(request):
    selected_course = request.GET.get('course')
    semesters_for_course = ProfessorsTable.objects.filter(course_name=selected_course).values('semester')
    semester_values = [semester_entry['semester'] for semester_entry in semesters_for_course]
    semester_value = semester_values[0]
    
    eligible_students = StudentsTable.objects.filter(student_semster=semester_value).values()
    
    attendance_data = (
        HajriTable.objects
        .filter(course=selected_course, stu_roll_no__in=[student['student_rollno'] for student in eligible_students])
        .values('stu_roll_no','stu_name')
        .annotate(
            total_classes=Count('att_date'),
            present_classes=Sum('is_present', output_field=FloatField())
        )
    )

    alert_data = []
    for data in attendance_data:
        attendance_percentage = (data['present_classes'] / data['total_classes']) * 100 if data['total_classes'] > 0 else 0
        alert_data.append({
            'stu_name':data['stu_name'],
            'stu_roll_no': data['stu_roll_no'],
            'attendance_percentage': attendance_percentage
        })
    email_messages = [] 
    for data in attendance_data:
            student_roll_no = data['stu_roll_no']
            total_classes = data['total_classes']
            present_classes = data['present_classes']
            
            attendance_percentage = (present_classes / total_classes) * 100 if total_classes > 0 else 0
            
            if attendance_percentage < 75:
                student = StudentsTable.objects.get(student_rollno=student_roll_no)
                email_message = create_email_message(student, attendance_percentage, selected_course)
                email_messages.append(email_message)
    
    
    count = len(email_messages)
    send_mass_mail(email_messages, fail_silently=True)
    
    return JsonResponse({'success': True, 'message': f'Successfully sent alerts to {count} students.','progress': count})

def create_email_message(student, attendance_percentage, selected_course):
    subject = 'Attendance Aler⚠️'
    message = f"""\
    {student.student_name}
    Your attendance percentage is {attendance_percentage:.2f}% in {selected_course}, which is below 75%. Please improve your attendance in order to maintain regularity and eligibility for examinations.
    Sincerely,<br>The Attendance System
    """
    from_email = 'lms.cait@gmail.com'
    recipient_list = [student.student_email]
    
    return (subject, message, from_email, recipient_list)


#-----REPORTS panel Manage Over----
def get_courses(request):

    selected_prof = request.GET.get('prof_list')
    
    if selected_prof:
        prof_data = LoginCode.objects.get(teacher_name=selected_prof)
        courses_list = ProfessorsTable.objects.filter(professor_name=prof_data.teacher_name).values('course_name', 'course_code', 'semester')
        
        return JsonResponse(list(courses_list), safe=False)
    return JsonResponse([], safe=False)

def get_attendance(request):
    selected_prof = request.GET.get('prof_list')
    selected_course = request.GET.get('course_list')
    if selected_prof and selected_course:
        attendance_data = HajriTable.objects.filter(course=selected_course).values('stu_roll_no', 'stu_name').annotate(
            attendance_percentage=(Sum(Cast('is_present', output_field=FloatField())) / Count('att_date')) * 100
        )
        return JsonResponse(list(attendance_data), safe=False)
    return JsonResponse([], safe=False)

    

#----LOGOUT function----
def logout(request):
    response = redirect('/')
    response.delete_cookie('admin_id')
    return response
#----LOGOUT function----




from datetime import timedelta,date
def add(request):
    if request.method == 'POST':
        sem = request.POST.get('sem')
        courses = ProfessorsTable.objects.filter(semester=sem).values_list('course_name', flat=True)
        students = StudentsTable.objects.filter(student_semster=sem).values_list('regno', 'student_name', 'student_rollno')

        today = date.today()
        end_date = today + timedelta(days=120)
        current_date = today

        if 'takeatt' in request.POST:
            selected_course = request.POST.get('course')
            while current_date <= end_date:
                for student in students:
                    is_present = random.randint(0, 1)
                    regno, student_name, student_rollno = student
                    attendance_record = HajriTable(
                        att_date=current_date,
                        stu_regno=regno,
                        stu_name=student_name,
                        stu_roll_no=student_rollno,
                        course=selected_course,
                        is_present=is_present
                    )
                    attendance_record.save()
                current_date += timedelta(days=1)

        return render(request, "abTakeatt.html", {'courses': courses,'taken':"Yes"})
    
    return render(request, "abTakeatt.html")

from userModule.models import AttendanceLog 
def attendance_logs(request):
    # Fetch all attendance logs from the database
    logs = AttendanceLog.objects.all().order_by('-serial_number')  # Order by timestamp in descending order

    return render(request, "attendance_logs.html", {'logs': logs})


