from django.urls import path
from . import views
# from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from .views import register, CustomLoginView
from .views import admin_dashboard, staff_dashboard,register_daycare,daycare_detail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='index'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile, name='profile'),    
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', staff_dashboard, name='staff_dashboard'),
    path('register_daycare/', register_daycare, name='register_daycare'),
    path('daycare/<int:daycare_id>/', daycare_detail, name='daycare_detail'),
    path('children/register/<int:daycare_id>/', views.register_child, name='children_register'),
    path('staff/register/<int:daycare_id>/', views.register_staff, name='register_staff'),
    path('accounts/assign_group_ajax/<int:child_id>/', views.assign_group_ajax, name='assign_group_ajax'),
    path('accounts/schedule_list/', views.schedule_list, name='schedule_list'),
    path('parent/enroll/', views.enroll_child_dashboard, name='enroll_child_dashboard'),
    path('parent/schedule/', views.parent_schedule_view, name='parent_schedule'),
    path('accounts/schedule/edit/<int:activity_id>/', views.edit_activity, name='edit_activity'),
    path('schedule/delete/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('update_status/', views.update_status, name='update_status'),
    path('get_participants/', views.get_participants, name='get_participants'),
    path('save_evaluation/', views.save_evaluation, name='save_evaluation'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('report/<str:period>/', views.attendance_report, name='attendance_report'),
    path('attendance_report/<int:child_id>/<int:month>/<int:year>/', views.attendance_report_for_child, name='attendance_report_for_child'),


    # Meal Plan (NEW)
    path('mealplan/create/', views.create_mealplan, name='create_mealplan'),
    path('mealplan/view/<int:mealplan_id>/', views.view_mealplan, name='view_mealplan'),

    path('health-incident/', views.record_health_incident, name='record_health_incident'),
    path('medication-record/', views.record_medication, name='record_medication'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('view-feedback/', views.view_feedback, name='view_feedback'),
    path('emergency-contacts/', views.emergency_contacts, name='emergency_contacts'),
    path('child-development/', views.child_development, name='child_development'),
    path('add-milestone/', views.add_milestone, name='add_milestone'),
    path('add-activity/', views.add_activity_summary, name='add_activity'),







]

