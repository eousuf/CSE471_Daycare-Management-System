from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import Parent,Child,Daycare,Schedule,Evaluation,Meal,Allergy,ChildAllergy, PlannedMeal,MealPlan,Attendance

class ParentAdmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'daycare', 'phone_number', 'position')
    search_fields = ('full_name', 'phone_number', 'position')

admin.site.register(Parent, ParentAdmin)

class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'daycare', 'age', 'group')
    list_filter = ('daycare', 'group')
    search_fields = ('name',)

admin.site.register(Child, ChildAdmin)


@admin.register(Daycare)
class DaycareAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin')
    search_fields = ('name',)


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('child', 'activity', 'evaluation')  
    list_filter = ('evaluation', 'activity')          
    search_fields = ('child__name', 'activity__activity_name')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('group', 'activity_name', 'activity_date', 'activity_time', 'status')

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories', 'protein')  # carbohydrates removed
    search_fields = ('name',)

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('group', 'week_start')         # filter removed

@admin.register(PlannedMeal)
class PlannedMealAdmin(admin.ModelAdmin):
    list_display = ('meal_plan', 'meal', 'meal_type', 'day_of_week')
    list_filter = ('day_of_week', 'meal_type')

@admin.register(ChildAllergy)
class ChildAllergyAdmin(admin.ModelAdmin):
    list_display = ('child', 'allergy')
    list_filter = ('allergy',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('child', 'date', 'status', 'staff')
    list_filter = ('date', 'status')
    search_fields = ('child__name', 'staff__username')



from .models import HealthIncident, MedicationRecord

admin.site.register(HealthIncident)
admin.site.register(MedicationRecord)
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('parent', 'feedback_type', 'created_at', 'is_reviewed')
    list_filter = ('feedback_type', 'is_reviewed')
    search_fields = ('parent__username', 'message')