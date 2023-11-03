"""
URL configuration for ams project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    
    path('adminModule/', views.index, name='index_Page'),
    path('add/', views.add, name='add'),
   
    #Links related CRUD opertaions of professors ----DO NOT TOUCH----
    path('adminModule/prof', views.professorsPanel, name='professors_Page'),
    path('adminModule/logs', views.attendance_logs, name='attendance_logs'),
    path('adminModule/prof_view', views.prof_detail, name='professors_View'),
    path('adminModule/prof/pdelete/<str:uid>', views.prof_delete, name='professor_delete'),
    path('adminModule/prof/pinfodelete/<str:uid>', views.prof_info_delete, name='professor_info_delete'),
    path('adminModule/prof/mdelete', views.mprof_delete, name='mp_delete'),
    path("adminModule/prof/pedit/<str:uid>",views.prof_edit,name="edit_professor"),
    path('adminModule/prof/pedit/pedit2/<str:uid>', views.edit_prof_record, name='edit_professor_record'),

    path("adminModule/prof/piedit/<str:uid>",views.prof_info_edit,name="edit_professor_info"),
    path('adminModule/prof/piedit/piedit2/<str:uid>', views.edit_info_prof_record, name='edit_professor_record_info'),

    #Links related CRUD opertaions of students ----DO NOT TOUCH----
    path('adminModule/stu',views.studentsPanel,name="students_Page"),
    path('adminModule/stu/sdelete/<str:uid>', views.stu_delete, name='student_delete'),
    path("adminModule/stu/sedit/<str:uid>",views.stu_edit,name="edit_student"),
    path('adminModule/stu/sedit/sedit2/<str:uid>', views.edit_stu_record, name='edit_student_record'),
    path('adminModule/stu/mdelete', views.mstu_delete, name='m_delete'),
    




    #Links related to CRUD of admin ----DO NOT TOUCH----
    path('adminModule/adminSettings',views.admin,name="admin_settings"),
    path('adminModule/adminSettings/admin_delete/<str:code>', views.admin_delete, name='admin_delete'),
    path("adminModule/adminSettings/admin_edit/<str:code>",views.admin_edit,name="edit_admin"),
    path('adminModule/adminSettings/admin_edit/admin_edit_2/<str:code>', views.edit_admin_record, name='edit_admin_record'),



    #Links related to reports ----DO NOT TOUCH----
    path('adminModule/reports',views.reports,name="admin_reports_page"),
    
    path('adminModule/send_alert_to_multiple/', views.send_alert_to_multiple, name='send_alert_to_multiple'),
    

    path('logout',views.logout,name="logout"),
    path('adminModule/logout',views.logout,name="logout")


]
