from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    degree = models.CharField(max_length=100, default='B.Tech')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_hod(self):
        profile = self.profiles.filter(role=Profile.ROLE_HOD).first()
        return profile.user if profile else None


class Profile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_HOD = 'HOD'
    ROLE_FACULTY = 'FACULTY'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_HOD, 'HOD'),
        (ROLE_FACULTY, 'Faculty'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profiles'
    )
    employee_id = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_hod(self):
        return self.role == self.ROLE_HOD

    @property
    def is_faculty(self):
        return self.role == self.ROLE_FACULTY

    @property
    def display_name(self):
        full = self.user.get_full_name()
        return full if full.strip() else self.user.username