from django.db import models
class AdminCode(models.Model):
    code = models.CharField(max_length=7, unique=True)
    admin_name = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    
class LoginCode(models.Model):
    code = models.CharField(max_length=7, unique=True)
    teacher_name = models.CharField(max_length=40)
    email = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

class AttendanceLog(models.Model):
    serial_number = models.AutoField(primary_key=True) 
    timestamp = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255)
    semester = models.CharField(max_length=50)
    professor_name = models.CharField(max_length=255)
    


