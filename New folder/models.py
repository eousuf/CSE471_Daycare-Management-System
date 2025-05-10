from django.db import models
from django.contrib.auth.models import AbstractUser,User
from django.conf import settings
from datetime import datetime  # Correct import

class Parent(AbstractUser):
    ROLE_CHOICES = (
        ('parent', 'Parent'),
        ('admin', 'Admin'),
        ('staff', 'Daycare Staff'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='parent')
    
    email = models.EmailField(unique=True)
    child_name = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    parents_profession = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    home_phone = models.CharField(max_length=20, blank=True)
    alt_phone = models.CharField(max_length=20, blank=True)
    work_phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_relation = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default-profile.png')

    def __str__(self):
        return self.username

class Daycare(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    established_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daycares',
        null=True,    # <-- ADD THIS
        blank=True    # <-- ADD THIS
    )

    def __str__(self):
        return self.name
    
from .models import Daycare  # Import Daycare model
class Group(models.Model):
    name = models.CharField(max_length=100)
    min_age = models.IntegerField(help_text="Minimum age in years")
    max_age = models.IntegerField(help_text="Maximum age in years")
    daycare = models.ForeignKey(Daycare, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.min_age}-{self.max_age} yrs)"

class Child(models.Model):
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='children'
    )
    daycare = models.ForeignKey(
        Daycare,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    group = models.CharField(
        max_length=50,
        choices=[
            ('Infant', 'Infant'),
            ('Toddlers', 'Toddlers'),
            ('Preschool', 'Preschool'),
            ('School Aged', 'School Aged'),
        ],
        blank=True,
        null=True
    )
    medical_history = models.TextField(blank=True, null=True)
    emergency_contacts = models.CharField(max_length=250)
    
    def __str__(self):
        return f"{self.name} (Age: {self.age})"
    
    def save(self, *args, **kwargs):
        if self.age is not None:
            if self.age < 1:
                self.group = 'Infant'
            elif 1 <= self.age < 3:
                self.group = 'Toddler'
            elif 3 <= self.age < 5:
                self.group = 'Preschool'
            else:
                self.group = 'School Aged'
        super().save(*args, **kwargs)




class Staff(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # link to Django user
    daycare = models.ForeignKey('Daycare', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    position = models.CharField(max_length=50)  # example: "Teacher", "Manager", etc.
    daycare = models.ForeignKey(Daycare, on_delete=models.CASCADE)
    plain_password = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.full_name
    
class Schedule(models.Model):
    GROUP_CHOICES = [
        ('Infant', 'Infant'),
        ('Toddler', 'Toddler'),
        ('Preschool', 'Preschool'),
        ('School Aged', 'School Aged'),
    ]
    STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Running', 'Running'),
    ('Done', 'Done'),
]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    group = models.CharField(max_length=50, choices=GROUP_CHOICES)
    activity_name = models.CharField(max_length=100)
    activity_time = models.TimeField()
    activity_date = models.DateField()  # Optional, today's date

    def __str__(self):
        return f"{self.group} - {self.activity_name} at {self.activity_time}"
    
class Evaluation(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    activity = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    evaluation = models.CharField(max_length=20, choices=[
        ('Excellent', 'Excellent'),
        ('Good', 'Good'),
        ('Satisfactory', 'Satisfactory'),
        ('Poor', 'Poor'),
    ])


class Attendance(models.Model):
    child = models.ForeignKey(
        'Child',
        on_delete=models.CASCADE,
        related_name="attendance_child",
        null=True,  # 👈 Add this
        blank=True
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_staff"
    )

    def __str__(self):
        if self.child:
            return f"{self.child.name} - {self.date} - {self.status}"
        else:
            return f"Unknown Child - {self.date} - {self.status}"


# ------------------ ADDED Meal Plan Feature Models ------------------

class Allergy(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class ChildAllergy(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    allergy = models.ForeignKey(Allergy, on_delete=models.CASCADE)

class Meal(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    calories = models.IntegerField()
    protein = models.IntegerField()
    allergens = models.ManyToManyField(Allergy, blank=True)

    def __str__(self):
        return self.name

class MealPlan(models.Model):
    # OLD
    # child = models.ForeignKey(Child, on_delete=models.CASCADE)

    # NEW → group instead of child
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
   # like 'Red', 'Blue', etc.
    week_start = models.DateField()

    def __str__(self):
        return f"Meal Plan for {self.group} (Week of {self.week_start})"

class PlannedMeal(models.Model):
    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack'),
    )
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    day_of_week = models.IntegerField()  # 0=Monday, 6=Sunday



class HealthIncident(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now)  # Using datetime.now correctly

    description = models.TextField()
    type = models.CharField(max_length=50, choices=[('Accident', 'Accident'), ('Illness', 'Illness')])
    medication_administered = models.BooleanField(default=False)

    def __str__(self):
        return f"Incident for {self.child.name} on {self.date}"

class MedicationRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    administration_date = models.DateField(default=datetime.now)
    administered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return f"Medication for {self.child.name} on {self.administration_date}"
    


class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('activity', 'Activity Suggestion'),
        ('meal', 'Meal Suggestion'),
        ('general', 'General Feedback'),
    ]
    
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback from {self.parent.username} - {self.get_feedback_type_display()}"
    

#----------------Milestone------------------
class Milestone(models.Model):
    CATEGORY_CHOICES = [
        ('physical', 'Physical Development'),
        ('cognitive', 'Cognitive Development'),
        ('social', 'Social-Emotional'),
        ('language', 'Language Skills'),
    ]
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='milestones')
    date_achieved = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    observed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-date_achieved']

class ActivitySummary(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='activities')
    date = models.DateField()
    activity_type = models.CharField(max_length=50)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    skills_developed = models.TextField()
    notes = models.TextField(blank=True)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Activity Summaries"