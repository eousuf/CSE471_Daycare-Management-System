from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Parent, Daycare,Staff,Attendance,MealPlan,PlannedMeal,Allergy

class ParentRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Parent.ROLE_CHOICES, required=True)

    class Meta:
        model = Parent
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user

    
class ParentUpdateForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = [
            'username', 'email','child_name', 'first_name', 'last_name',
            'date_of_birth', 'parents_profession', 'country', 'state',
            'home_phone', 'alt_phone', 'work_phone',
            'emergency_contact', 'emergency_relation','profile_picture'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'previous_employers': forms.Textarea(attrs={'rows': 3}),
        }

class DaycareRegisterForm(forms.ModelForm):
    class Meta:
        model = Daycare
        fields = ['name', 'address', 'phone', 'email', 'website', 'established_date']
        widgets = {
            'established_date': forms.DateInput(attrs={'type': 'date'}),
        }

from .models import Child, Daycare

class ChildRegistrationForm(forms.ModelForm):
    daycare = forms.ModelChoiceField(queryset=Daycare.objects.all(), required=True)

    class Meta:
        model = Child
        fields = ['daycare', 'name', 'age', 'medical_history', 'emergency_contacts']
    def __init__(self, *args, **kwargs):
        super(ChildRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['daycare'].widget = forms.HiddenInput()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['name'].widget.attrs.update({'placeholder': "Enter your child's name"})
        self.fields['age'].widget.attrs.update({'placeholder': "Enter your child's age"})
        self.fields['medical_history'].widget.attrs.update({'placeholder': "Enter any known medical conditions"})
        self.fields['emergency_contacts'].widget.attrs.update({'placeholder': "Enter emergency contact details"})
class StaffRegistrationForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['full_name', 'phone_number', 'position']

from django import forms
from .models import Child, Group

class AssignGroupForm(forms.Form):
    child = forms.ModelChoiceField(queryset=Child.objects.none())
    group = forms.ModelChoiceField(queryset=Group.objects.none())

    def __init__(self, daycare, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['child'].queryset = Child.objects.filter(daycare=daycare)
        self.fields['group'].queryset = Group.objects.filter(daycare=daycare)
from .models import Schedule

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['group', 'activity_name', 'activity_time', 'activity_date','status']
        widgets = {
            'activity_time': forms.TimeInput(attrs={'type': 'time'}),
            'activity_date': forms.DateInput(attrs={'type': 'date'}),  # ← add this
        
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['child', 'date', 'status']

# ------------------ Meal Plan Forms ------------------

class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['group', 'week_start']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)   # ⬅️ get user from view
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'staff'):   # ⬅️ check if user is staff
            staff = user.staff
            self.fields['group'].queryset = Group.objects.filter(daycare=staff.daycare)
        else:
            self.fields['group'].queryset = Group.objects.none()



class PlannedMealForm(forms.ModelForm):
    class Meta:
        model = PlannedMeal
        fields = ['meal', 'meal_type', 'day_of_week']





from .models import HealthIncident, MedicationRecord

class HealthIncidentForm(forms.ModelForm):
    class Meta:
        model = HealthIncident
        fields = ['child', 'description', 'type', 'medication_administered']
    
class MedicationRecordForm(forms.ModelForm):
    class Meta:
        model = MedicationRecord
        fields = ['child', 'medication_name', 'dosage', 'administration_date', 'administered_by']

from .models import Feedback, ActivitySummary
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }


from .models import Milestone, ActivitySummary
class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone  # ← This line was missing
        fields = ['child', 'date_achieved', 'category', 'description']
        widgets = {
            'date_achieved': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'staff_profile'):
            self.fields['child'].queryset = Child.objects.filter(
                daycare=user.staff_profile.daycare
            )
    

class ActivitySummaryForm(forms.ModelForm):
    class Meta:
        model = ActivitySummary  # ← This line was missing
        fields = ['child', 'date', 'activity_type', 'duration', 'skills_developed', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'skills_developed': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)  # ← Call super() properly
        if user and hasattr(user, 'staff_profile'):
            self.fields['child'].queryset = Child.objects.filter(
                daycare=user.staff_profile.daycare
            )