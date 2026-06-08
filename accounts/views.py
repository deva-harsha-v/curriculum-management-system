from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Count

from .models import Department, Profile
from .forms import (
    LoginForm, DepartmentForm, CreateHODForm,
    CreateFacultyForm, EditProfileForm
)


# ─────────────────────────────────────────────
# Helpers / Decorators
# ─────────────────────────────────────────────

def get_profile_or_403(request):
    """Return profile or raise 403 if no profile found."""
    try:
        return request.user.profile
    except Profile.DoesNotExist:
        return None


def require_role(*roles):
    """Decorator that enforces role-based access."""
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            profile = get_profile_or_403(request)
            if profile is None or profile.role not in roles:
                return HttpResponseForbidden(
                    "<h2>403 Forbidden</h2><p>You do not have permission to access this page.</p>"
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
        return redirect('accounts:dashboard')
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


# ─────────────────────────────────────────────
# Dashboard Routing
# ─────────────────────────────────────────────

@login_required
def dashboard(request):
    profile = get_profile_or_403(request)
    if profile is None:
        return HttpResponseForbidden("No profile found. Please contact administrator.")
    if profile.is_admin:
        return redirect('accounts:admin_dashboard')
    elif profile.is_hod:
        return redirect('accounts:hod_dashboard')
    else:
        return redirect('accounts:faculty_dashboard')


# ─────────────────────────────────────────────
# Admin Dashboard
# ─────────────────────────────────────────────

@require_role(Profile.ROLE_ADMIN)
def admin_dashboard(request):
    departments = Department.objects.annotate(
        faculty_count=Count('profiles')
    ).prefetch_related('profiles__user')
    total_users = User.objects.count()
    total_depts = Department.objects.count()
    context = {
        'departments': departments,
        'total_users': total_users,
        'total_depts': total_depts,
    }
    return render(request, 'accounts/dashboard_admin.html', context)


@require_role(Profile.ROLE_ADMIN)
def create_department(request):
    form = DepartmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        dept = form.save()
        messages.success(request, f"Department '{dept.name}' created successfully.")
        return redirect('accounts:admin_dashboard')
    return render(request, 'accounts/department_form.html', {'form': form, 'action': 'Create'})


@require_role(Profile.ROLE_ADMIN)
def edit_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=dept)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Department '{dept.name}' updated.")
        return redirect('accounts:admin_dashboard')
    return render(request, 'accounts/department_form.html', {'form': form, 'action': 'Edit', 'dept': dept})


@require_role(Profile.ROLE_ADMIN)
def create_hod(request):
    form = CreateHODForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f"HOD account created for {user.get_full_name()}.")
        return redirect('accounts:admin_dashboard')
    return render(request, 'accounts/register_hod.html', {'form': form})


@require_role(Profile.ROLE_ADMIN)
def manage_users(request):
    profiles = Profile.objects.select_related('user', 'department').order_by('role', 'department__name')
    return render(request, 'accounts/manage_users.html', {'profiles': profiles})


@require_role(Profile.ROLE_ADMIN)
def toggle_user_active(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        if target_user == request.user:
            messages.error(request, "You cannot deactivate your own account.")
        else:
            target_user.is_active = not target_user.is_active
            target_user.save()
            status = "activated" if target_user.is_active else "deactivated"
            messages.success(request, f"User {target_user.username} has been {status}.")
    return redirect('accounts:manage_users')


# ─────────────────────────────────────────────
# HOD Dashboard
# ─────────────────────────────────────────────

@require_role(Profile.ROLE_HOD)
def hod_dashboard(request):
    from curriculum.models import CurriculumVersion, ChangeRequest, AuditLog

    profile = request.user.profile
    dept = profile.department

    faculty_list = Profile.objects.filter(
        department=dept, role=Profile.ROLE_FACULTY
    ).select_related('user')

    versions = CurriculumVersion.objects.filter(department=dept).order_by('-created_at')

    pending_requests = ChangeRequest.objects.filter(
        curriculum_version__department=dept,
        status=ChangeRequest.STATUS_PENDING
    ).select_related('requested_by__profile').order_by('-created_at')

    recent_logs = AuditLog.objects.filter(
        department=dept
    ).select_related('user').order_by('-timestamp')[:20]

    context = {
        'profile': profile,
        'dept': dept,
        'faculty_list': faculty_list,
        'versions': versions,
        'pending_requests': pending_requests,
        'recent_logs': recent_logs,
        'pending_count': pending_requests.count(),
    }
    return render(request, 'accounts/dashboard_hod.html', context)


@require_role(Profile.ROLE_HOD)
def create_faculty(request):
    profile = request.user.profile
    form = CreateFacultyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(department=profile.department)
        messages.success(request, f"Faculty account created for {user.get_full_name()}.")
        return redirect('accounts:hod_dashboard')
    return render(request, 'accounts/register_faculty.html', {'form': form})


@require_role(Profile.ROLE_HOD)
def remove_faculty(request, user_id):
    """HOD can deactivate a faculty in their department."""
    if request.method == 'POST':
        hod_profile = request.user.profile
        target = get_object_or_404(User, pk=user_id)
        try:
            target_profile = target.profile
        except Profile.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect('accounts:hod_dashboard')

        if target_profile.department != hod_profile.department:
            messages.error(request, "You can only manage faculty in your department.")
            return redirect('accounts:hod_dashboard')

        if target_profile.role != Profile.ROLE_FACULTY:
            messages.error(request, "You can only remove faculty accounts.")
            return redirect('accounts:hod_dashboard')

        target.is_active = not target.is_active
        target.save()
        status = "activated" if target.is_active else "deactivated"
        messages.success(request, f"{target.get_full_name()} has been {status}.")
    return redirect('accounts:hod_dashboard')


# ─────────────────────────────────────────────
# Faculty Dashboard
# ─────────────────────────────────────────────

@require_role(Profile.ROLE_FACULTY)
def faculty_dashboard(request):
    from curriculum.models import CurriculumVersion, ChangeRequest

    profile = request.user.profile
    dept = profile.department

    versions = CurriculumVersion.objects.filter(department=dept).order_by('-created_at')

    my_requests = ChangeRequest.objects.filter(
        requested_by=request.user
    ).order_by('-created_at')[:10]

    context = {
        'profile': profile,
        'dept': dept,
        'versions': versions,
        'my_requests': my_requests,
    }
    return render(request, 'accounts/dashboard_faculty.html', context)


# ─────────────────────────────────────────────
# Shared Profile Edit
# ─────────────────────────────────────────────

@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    form = EditProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('accounts:dashboard')
    return render(request, 'accounts/edit_profile.html', {'form': form})