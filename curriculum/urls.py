from django.urls import path
from . import views

app_name = 'curriculum'

urlpatterns = [
    # Curriculum Versions
    path('', views.version_list, name='version_list'),
    path('version/create/', views.version_create, name='version_create'),
    path('version/<int:pk>/', views.version_detail, name='version_detail'),
    path('version/<int:pk>/edit/', views.version_edit, name='version_edit'),
    path('version/<int:pk>/publish/', views.version_publish, name='version_publish'),
    path('version/<int:pk>/archive/', views.version_archive, name='version_archive'),

    # Graduate Attributes
    path('version/<int:version_pk>/ga/', views.edit_graduate_attributes, name='edit_ga'),

    # PEOs
    path('version/<int:version_pk>/peo/', views.edit_peos, name='edit_peos'),
    path('version/<int:version_pk>/mission-peo/', views.edit_mission_peo_mappings, name='edit_mission_peo'),

    # Program Outcomes
    path('version/<int:version_pk>/po/', views.edit_program_outcomes, name='edit_pos'),

    # Mappings (HOD only)
    path('version/<int:version_pk>/peo-ga-mapping/', views.edit_peo_ga_mapping, name='edit_peo_ga'),
    path('version/<int:version_pk>/po-peo-mapping/', views.edit_po_peo_mapping, name='edit_po_peo'),

    # Course Categories
    path('version/<int:version_pk>/categories/', views.edit_categories, name='edit_categories'),

    # Semesters
    path('version/<int:version_pk>/semester/create/', views.semester_create, name='semester_create'),

    # Courses
    path('version/<int:version_pk>/courses/', views.course_list, name='course_list'),
    path('version/<int:version_pk>/semester/<int:semester_pk>/course/create/', views.course_create, name='course_create'),
    path('version/<int:version_pk>/course/<int:course_pk>/', views.course_detail, name='course_detail'),
    path('version/<int:version_pk>/course/<int:course_pk>/edit/', views.course_edit, name='course_edit'),
    path('version/<int:version_pk>/course/<int:course_pk>/delete/', views.course_delete, name='course_delete'),

    # Course Outcomes & Mappings
    path('version/<int:version_pk>/course/<int:course_pk>/outcomes/', views.edit_course_outcomes, name='edit_course_outcomes'),
    path('version/<int:version_pk>/course/<int:course_pk>/co/<int:co_pk>/copo/', views.edit_copo_mapping, name='edit_copo'),
    path('version/<int:version_pk>/course/<int:course_pk>/references/', views.edit_references, name='edit_references'),

    # Change Requests
    path('version/<int:version_pk>/changes/', views.change_request_list, name='change_requests'),
    path('version/<int:version_pk>/changes/<int:cr_pk>/review/', views.change_request_review, name='change_request_review'),

    # Audit Log
    path('version/<int:version_pk>/audit/', views.audit_log, name='audit_log'),
    path('version/<int:version_pk>/audit/<int:log_pk>/rollback/', views.rollback_audit, name='rollback_audit'),
]