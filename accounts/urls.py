from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard routing
    path('dashboard/', views.dashboard, name='dashboard'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('departments/create/', views.create_department, name='create_department'),
    path('departments/<int:pk>/edit/', views.edit_department, name='edit_department'),
    path('hod/create/', views.create_hod, name='create_hod'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/toggle/', views.toggle_user_active, name='toggle_user_active'),

    # HOD
    path('hod-dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('faculty/create/', views.create_faculty, name='create_faculty'),
    path('faculty/<int:user_id>/remove/', views.remove_faculty, name='remove_faculty'),

    # Faculty
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),

    # Shared
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]