

from django.urls import path,include
from . import views
urlpatterns = [

        path("",views.login),

        #Link to take the attendence
        path("attendence/",views.attendance_page,name="attendance_page"),
        path("attendence/view_attendence/", views.view_attendance, name="view_attendance"),
        path("attendence/reports/", views.reports, name="view_reports"),
        path("attendence/profile/", views.profile, name="view_profile"),
        path("attendence/logout/", views.logout, name="logout"),
        path("reset/", views.reset, name="reset"),
        path("reset/confirm_code/", views.confirm_code, name="confirmcode"),
        path("resetCode/", views.reset_code, name="reset_code"),

        path('attendence/send_alert',views.send_alert,name="send_alert"),
        path("attendence/assign_i_grade/", views.assign_i_grade, name="assign_i_grade"),
        
    path('special_attendence/<str:regno>/', views.special_attendence, name='special_attendence'),
   
]
