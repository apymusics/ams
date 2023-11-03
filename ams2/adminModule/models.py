from django.db import models
from django.utils import timezone

#COURSES TABLE
class ProfessorsTable(models.Model):
    cid = models.CharField(max_length=50, primary_key=True,unique=True)
    pid = models.CharField(max_length=40)
    professor_name = models.CharField(max_length=40)
    course_code = models.CharField(max_length=8)
    course_num = models.CharField(max_length=8)
    course_name = models.CharField(max_length=50)
    semester = models.CharField(max_length=1)
       
#ADD PROFESSOR TABLE
class ProfessorsInfoTable(models.Model):
    pid = models.CharField(max_length=50, primary_key=True,unique=True)
    professor_name = models.CharField(max_length=40)
    email= models.CharField(max_length=30)
    phone_number= models.CharField(max_length=10)
    code= models.CharField(max_length=7)
    

class StudentsTable(models.Model):
    
    regno = models.CharField(max_length=50, unique=True)
    uid = models.CharField(max_length=50,primary_key=True, unique=True)
    student_rollno = models.IntegerField()
    student_name = models.CharField(max_length=40)
    student_semster = models.CharField(max_length=1)
    student_email = models.CharField(max_length=30)
    i_grade = models.CharField(max_length=1,default="0")

    def assign_i_grade(self):
        self.i_grade = "1"
        self.save()

class HajriTable(models.Model):
    
    att_date = models.DateField(default=timezone.now)
    stu_regno= models.CharField(max_length=15)
    stu_name = models.CharField(max_length=40)
    stu_roll_no = models.IntegerField()
    course = models.CharField(max_length=40)
    is_present = models.CharField(max_length=1,default="1")

    