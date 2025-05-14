from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ParentRegisterForm
from .forms import ParentUpdateForm,DaycareRegisterForm,ChildRegistrationForm,StaffRegistrationForm,AttendanceForm,MealPlanForm,PlannedMealForm,HealthIncidentForm,MedicationRecordForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from accounts.models import Parent,Daycare,Child,Staff
from django.urls import reverse
from django.shortcuts import get_object_or_404
import random
import string
from django.contrib.auth.hashers import make_password
from .models import Child, Group,Schedule,MealPlan,Meal,Allergy,ChildAllergy,PlannedMeal,Attendance,HealthIncident,MedicationRecord
from django.http import HttpResponse
from .forms import AssignGroupForm
import random
import string
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from .models import Evaluation,Schedule
from django.utils import timezone
import datetime
from django import forms
import datetime
from datetime import datetime
from django.contrib.auth.views import PasswordChangeView

from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
def register(request):
    if request.method == 'POST':
        form = ParentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('index')  
    else:
        form = ParentRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.role == 'admin':
            return reverse_lazy('admin_dashboard')  
        elif user.role == 'staff':
            return reverse_lazy('staff_dashboard')  
        else:
            return reverse_lazy('index')  

    
@login_required
def home(request):
    daycare_list = Daycare.objects.all()
    children = request.user.children.all()

    # Check if children exist and ensure that child.id is present
    for child in children:
        if not child.id:
            messages.warning(request, f"Child {child.name} does not have a valid ID.")
        child.incidents = HealthIncident.objects.filter(child=child)
        child.medications = MedicationRecord.objects.filter(child = child)
    now = timezone.now()  # Get the current date and time
    context = {
        'daycare_list': daycare_list,
        'children': children,
        'now': now,  # Pass the now object to the template
    }

    return render(request, 'accounts/parent_dashboard.html', context)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/change_password.html'  # Your custom template
    success_url = reverse_lazy('profile')


def is_admin(user):
    return user.role == 'admin'

def is_staff(user):
    return user.role == 'staff'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Fetch all daycares associated with the current admin user
    daycares = Daycare.objects.filter(admin=request.user)

    # Initialize counts
    total_children_count = 0
    total_staff_count = 0
    total_incidents_count = 0
    total_parents_count = Parent.objects.filter(role='parent').count()  # Parent count remains the same

    # Loop through each daycare and calculate the related counts
    for daycare in daycares:
        # Counting children associated with this daycare
        total_children_count += daycare.children.count()

        # Counting staff associated with this daycare
        total_staff_count += Staff.objects.filter(daycare=daycare).count()

        # Counting incidents related to this daycare (through the child model)
        total_incidents_count += HealthIncident.objects.filter(child__daycare=daycare).count()

    # If you want to display a list of daycares


    
    daycare_list = daycares  # No need to query again, we already have the `daycares` QuerySet

    # Prepare context data to pass to the template
    context = {
        'parent_count': total_parents_count,
        'staff_count': total_staff_count,
        'children_count': total_children_count,
        'incidents_count': total_incidents_count,
        'daycare_list': daycare_list,
    }

    # Render the response with context data
    return render(request, 'accounts/admin_dashboard.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from .models import Attendance, Child, Staff

@login_required
@user_passes_test(is_staff)
def staff_dashboard(request):
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, "You are not authorized as a Staff.")
        return redirect('login')

    sort_by = request.GET.get('sort', 'name')  # Default sort by name
    month = int(request.GET.get('month', datetime.now().month))  # Get the selected month or default to current month

    children = Child.objects.filter(daycare=staff.daycare)
    if sort_by == 'name':
        children = children.order_by('name')
    elif sort_by == 'age':
        children = children.order_by('age')
    elif sort_by == 'group':
        children = children.order_by('group')

    current_year = datetime.now().year

    # Create a dictionary to hold daily attendance percentages
    daily_attendance = {}

    # Calculate attendance for each day in the selected month
    for day in range(1, 32):  # Loop for 31 days in the month
        total_children = Child.objects.filter(daycare=staff.daycare).count()
        presents = Attendance.objects.filter(
            date__year=current_year,
            date__month=month,
            date__day=day,
            status='present',
            child__daycare=staff.daycare
        ).count()

        # Calculate attendance percentage for the day
        if total_children == 0:
            attendance_percentage = 0
        else:
            attendance_percentage = (presents / total_children) * 100

        daily_attendance[day] = attendance_percentage

    context = {
        'staff': staff,
        'daily_attendance': daily_attendance,
        'children': children,
        'sort_by': sort_by,
        'month': month,
    }

    return render(request, 'accounts/staff_dashboard.html', context)


@login_required
def profile(request):
    parent = request.user
    return render(request, 'accounts/profile.html', {'parent': parent})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ParentUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            print(form.errors)  
    else:
        form = ParentUpdateForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def register_daycare(request):
    if request.method == 'POST':
        form = DaycareRegisterForm(request.POST)
        if form.is_valid():
            daycare = form.save(commit=False)
            daycare.admin = request.user  # 👉 Auto-assign logged-in admin
            daycare.save()
            messages.success(request, 'Daycare registered successfully.')
            return redirect('admin_dashboard')
    else:
        form = DaycareRegisterForm()
    return render(request, 'accounts/register_daycare.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def daycare_detail(request, daycare_id):
    daycare = get_object_or_404(Daycare, id=daycare_id)

    # Filter children belonging to this daycare
    children = Child.objects.filter(daycare=daycare)

    # Parents are accessed from children (if needed)
    parent_count = children.values('parent').distinct().count()

    # Count incidents related to children
    # incidents_count = Incident.objects.filter(child__in=children).count()
    
    children_count = Child.objects.filter(daycare=daycare).count()
    
    # For incidents, assuming an Incident model exists and is related to children
    incidents_count = HealthIncident.objects.filter(child__daycare=daycare).count()
    # Staff members assigned to this daycare
    staff_members = Staff.objects.filter(daycare=daycare)
    staff_count = Staff.objects.filter(daycare=daycare).count()
    # children_count = children.count()
    # incidents_count = 6 

    context = {
        'daycare': daycare,
        'staff_members': staff_members,
        'parent_count': parent_count,
        'children_count': children_count,
        'incidents_count': incidents_count,
        'staff_count': staff_count,
    }
    return render(request, 'accounts/daycare_detail.html', context)

@login_required
def register_child(request, daycare_id):
    try:
        daycare = Daycare.objects.get(id=daycare_id)
    except Daycare.DoesNotExist:
        return redirect('index')

    if request.method == 'POST':
        form = ChildRegistrationForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user
            child.daycare = daycare
            child.save()
            messages.success(request, "Child registered successfully!")
            return redirect('index')
    else:
        form = ChildRegistrationForm()

    return render(request, 'accounts/register_child.html', {'form': form, 'daycare': daycare})




def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))



@login_required
@user_passes_test(is_admin)
def register_staff(request, daycare_id):
    daycare = get_object_or_404(Daycare, id=daycare_id)

    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.daycare = daycare

            
            username = f"{staff.full_name.split()[0].lower()}{random.randint(1000, 9999)}"
            password = generate_random_password()

            
            staff.user = Parent.objects.create(
                username=username,
                email=f"{username}@staffdaycare.com",
                password=make_password(password),
                role='staff',
                is_active=True,
            )
            staff.username = username
            staff.plain_password = password
            staff.save()

            
            messages.success(request, f"Staff registered successfully!\nUsername: {username}\nPassword: {password}")

            return redirect('admin_dashboard')
    else:
        form = StaffRegistrationForm()

    return render(request, 'accounts/register_staff.html', {'form': form, 'daycare': daycare})



@login_required
@csrf_exempt  
def assign_group_ajax(request, child_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  
            group_name = data.get('group')   

            if not group_name:
                return JsonResponse({'success': False, 'error': 'Group not provided'})

            child = Child.objects.get(id=child_id)
            child.group = group_name   
            child.save()

            return JsonResponse({'success': True})
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
from .forms import ScheduleForm

@login_required
@user_passes_test(is_staff)
def schedule_list(request):
    activity_id = request.GET.get('edit')
    activity = None

    sort_by = request.GET.get('sort_by')

    if sort_by in ['group', 'activity_name', 'activity_time', 'activity_date']:
        schedules = schedules.order_by(sort_by)

    if activity_id:
        try:
            activity = Schedule.objects.get(id=activity_id)
        except Schedule.DoesNotExist:
            activity = None

    if request.method == 'POST':
        if request.POST.get('activity_id'):
            # Editing existing
            activity = Schedule.objects.get(id=request.POST.get('activity_id'))
            form = ScheduleForm(request.POST, instance=activity)
        else:
            # Adding new
            form = ScheduleForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('schedule_list')
    else:
        form = ScheduleForm(instance=activity)

    schedules = Schedule.objects.all()
    return render(request, 'accounts/schedule_list.html', {
        'form': form,
        'schedules': schedules,
        'activity': activity,
    })



@login_required
def enroll_child_dashboard(request):
    daycare_list = Daycare.objects.all()
    return render(request, 'accounts/enroll_child_dashboard.html', {'daycare_list': daycare_list})


@login_required
def parent_schedule_view(request):
    parent = request.user
    children = parent.children.all()
    sort_by = request.GET.get('sort', 'child_name')  # default: name

    schedule_data = []

    for child in children:
        child_schedules = Schedule.objects.filter(group=child.group).order_by('activity_date', 'activity_time')
        
        for schedule in child_schedules:
            evaluation = Evaluation.objects.filter(child=child, activity=schedule).first()
            schedule_data.append({
                'child_name': child.name,
                'group': child.group,
                'activity': schedule.activity_name,
                'time': schedule.activity_time,
                'date': schedule.activity_date,
                'evaluation': evaluation.evaluation if evaluation else None
            })
        

    if sort_by in ['child_name', 'group', 'activity']:
        schedule_data = sorted(schedule_data, key=lambda x: x[sort_by].lower())
    elif sort_by == 'date':
        schedule_data = sorted(schedule_data, key=lambda x: x['date'])
    elif sort_by == 'time':
        schedule_data = sorted(schedule_data, key=lambda x: x['time'])

    context = {
        'schedule_data': schedule_data,
        'sort_by': sort_by,
    }
    return render(request, 'accounts/parent_schedule.html', context)


@login_required
@user_passes_test(is_staff)
def edit_activity(request, activity_id):
    activity = Schedule.objects.get(id=activity_id)

    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('schedule_list')
    else:
        form = ScheduleForm(instance=activity)

    return render(request, 'accounts/edit_activity.html', {'form': form, 'activity': activity})

# Delete activity
@login_required
@user_passes_test(is_staff)
def delete_activity(request, activity_id):
    activity = Schedule.objects.get(id=activity_id)
    activity.delete()
    return redirect('schedule_list')

@require_POST
@user_passes_test(is_staff)
def update_status(request):
    activity_id = request.POST.get('activity_id')
    new_status = request.POST.get('status')
    Schedule.objects.filter(id=activity_id).update(status=new_status)
    return redirect('schedule_list')

@login_required
@user_passes_test(is_staff)
def get_participants(request):
    group = request.GET.get('group')
    children = Child.objects.filter(group=group).values('id', 'name', 'age')  # <-- add 'id' here
    return JsonResponse(list(children), safe=False)


@csrf_exempt
@login_required
@user_passes_test(is_staff)
def save_evaluation(request):
    if request.method == 'POST':
        child_id = request.POST.get('child_id')
        evaluation_value = request.POST.get('evaluation')
        activity_id = request.POST.get('activity_id')   # <-- Get activity id

        try:
            child = Child.objects.get(id=child_id)
            activity = Schedule.objects.get(id=activity_id)  # <-- Now load exact activity

            if child and activity:
                Evaluation.objects.update_or_create(
                    child=child,
                    activity=activity,
                    defaults={'evaluation': evaluation_value}
                )
                return JsonResponse({'success': True})

        except (Child.DoesNotExist, Schedule.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Child or Activity not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
@user_passes_test(is_staff)
def mark_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.staff = request.user
            attendance.save()
            return redirect('mark_attendance')
    else:
        form = AttendanceForm(initial={'date': timezone.now().date()})
    return render(request, 'accounts/mark_attendance.html', {
        'form': form
    })
from datetime import datetime, timedelta
@login_required
@user_passes_test(is_staff)
def attendance_report(request, period='daily'):
    today = timezone.now().date()  # Get today's date using timezone
    if period == 'daily':
        records = Attendance.objects.filter(date=today)
    elif period == 'weekly':
        week_start = today - timedelta(days=today.weekday())  # Get Monday of the current week
        week_end = week_start + timedelta(days=6)  # Get Sunday of the current week
        records = Attendance.objects.filter(date__range=[week_start, week_end]) 
    else:  # For monthly period
        month_start = today.replace(day=1)  # Get the first day of the current month
        records = Attendance.objects.filter(date__gte=month_start)

    return render(request, 'accounts/report.html', {
        'attendance': records,
        'period': period
    })


def attendance_report_for_child(request, child_id, month, year):
    child = get_object_or_404(Child, id=child_id)
    
    # Get the first and last day of the selected month
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Filter attendance records based on the child and the month/year
    attendance_records = Attendance.objects.filter(child=child, date__gte=first_day_of_month, date__lte=last_day_of_month)
    
    # Pass the data to the template
    return render(request, 'accounts/attendance_report.html', {
        'child': child,
        'attendance_records': attendance_records,
        'month': month,
        'year': year
    })

# — Meal Plan Management ——————————————————————————

@login_required
@user_passes_test(is_staff)
def create_mealplan(request):
    MealFormSet = forms.modelformset_factory(PlannedMeal, form=PlannedMealForm, extra=21)

    if request.method == 'POST':
        mealplan_form = MealPlanForm(request.POST, user=request.user)
        formset = MealFormSet(request.POST, queryset=PlannedMeal.objects.none())

        if mealplan_form.is_valid() and formset.is_valid():
            mealplan = mealplan_form.save()

            for form in formset:
                if form.cleaned_data:
                    planned_meal = form.save(commit=False)
                    planned_meal.meal_plan = mealplan
                    planned_meal.save()

            return redirect('view_mealplan', mealplan_id=mealplan.id)
    else:
        mealplan_form = MealPlanForm(user=request.user)
        formset = MealFormSet(queryset=PlannedMeal.objects.none())

    return render(request, 'accounts/mealplan_form.html', {
        'mealplan_form': mealplan_form,
        'formset': formset,
    })


@login_required
@user_passes_test(is_staff)
def view_mealplan(request, mealplan_id):
    mealplan = get_object_or_404(MealPlan, id=mealplan_id)
    planned_meals = PlannedMeal.objects.filter(meal_plan=mealplan)

    # 🛠 Allergy checking will now depend on all children in the group
    group_children = Child.objects.filter(group=mealplan.group)
    child_allergies = ChildAllergy.objects.filter(child__in=group_children).values_list('allergy__name', flat=True)

    meal_alerts = {}
    for meal in planned_meals:
        allergens = meal.meal.allergens.values_list('name', flat=True)
        meal_alerts[meal.id] = set(allergens).intersection(set(child_allergies))

    return render(request, 'accounts/mealplan_detail.html', {
        'mealplan': mealplan,
        'planned_meals': planned_meals,
        'meal_alerts': meal_alerts,
    })



@login_required
@user_passes_test(is_staff)
def record_health_incident(request):
    if request.method == 'POST':
        form = HealthIncidentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Health incident recorded successfully!")
            return redirect('staff_dashboard')
    else:
        form = HealthIncidentForm()
    return render(request, 'accounts/record_health_incident.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def record_medication(request):
    if request.method == 'POST':
        form = MedicationRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Medication record saved successfully!")
            return redirect('staff_dashboard')
    else:
        form = MedicationRecordForm()
    return render(request, 'accounts/record_medication.html', {'form': form})



#----------------------Feedback View----------------------
from .forms import FeedbackForm
from .models import Feedback
@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.parent = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('submit_feedback')
    else:
        form = FeedbackForm()
    
    return render(request, 'accounts/feedback.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def view_feedback(request):
    try:
        staff_profile = Staff.objects.get(user=request.user)
        # Get all feedback from parents who have children in this daycare
        feedback_list = Feedback.objects.filter(
            parent__children__daycare=staff_profile.daycare
        ).distinct().order_by('-created_at')
    except Staff.DoesNotExist:
        messages.error(request, "Staff profile not found")
        return redirect('staff_dashboard')
    
    return render(request, 'accounts/view_feedback.html', {
        'feedback_list': feedback_list
    })


#--------------------Emergency Contact--------------------
@login_required
@user_passes_test(is_staff)
def emergency_contacts(request):
    try:
        # Get single staff profile instance
        staff_profile = Staff.objects.get(user=request.user)
        children = Child.objects.filter(daycare=staff_profile.daycare)
    except (Staff.DoesNotExist, AttributeError):
        messages.error(request, "Staff profile not properly configured")
        return redirect('staff_dashboard')
    
    return render(request, 'accounts/emergency_contacts.html', {
        'children': children
    })

#----------------Milestone Management----------------
from .models import Milestone
from .forms import MilestoneForm, ActivitySummaryForm
# Parent View
@login_required
def child_development(request):
    children = request.user.children.all().prefetch_related('milestones', 'activities')
    return render(request, 'accounts/child_development.html', {
        'children': children
    })

# Staff Views
@login_required
@user_passes_test(is_staff)
def add_milestone(request):
    if request.method == 'POST':
        form = MilestoneForm(request.POST, user=request.user)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.observed_by = request.user
            milestone.save()
            return redirect('child_development')
    else:
        form = MilestoneForm(user=request.user)
    
    return render(request, 'accounts/add_milestone.html', {
        'form': form
    })


@login_required
@user_passes_test(is_staff)
def add_activity_summary(request):
    if request.method == 'POST':
        form = ActivitySummaryForm(request.POST, user=request.user)  # ← Pass user
        if form.is_valid():
            activity = form.save(commit=False)
            activity.staff = request.user
            activity.save()
            return redirect('child_development')
    else:
        form = ActivitySummaryForm(user=request.user)  # ← Pass user
    
    return render(request, 'accounts/add_activity.html', {'form': form})