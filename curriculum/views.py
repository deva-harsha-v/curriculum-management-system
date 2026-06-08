import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.db import transaction

from accounts.models import Profile
from .models import (
    CurriculumVersion, GraduateAttribute, PEO, MissionPEOMapping, PEOGAMapping,
    ProgramOutcome, POPEOMapping, CourseCategory, Semester, Course,
    CourseOutcome, COPOMapping, ReferenceBook, ChangeRequest, AuditLog, log_action
)
from .forms import (
    CurriculumVersionForm, GraduateAttributeFormSet, PEOFormSet,
    MissionPEOMappingFormSet, ProgramOutcomeFormSet, CourseCategoryFormSet,
    SemesterForm, CourseForm, CourseOutcomeFormSet, COPOMappingForm,
    ReferenceBookFormSet, ChangeRequestReviewForm
)


# ─────────────────────────────────────────────
# Role helpers
# ─────────────────────────────────────────────

def get_profile(request):
    try:
        return request.user.profile
    except Profile.DoesNotExist:
        return None


def dept_required(view_func):
    """Ensures user has a department."""
    @login_required
    def wrapper(request, *args, **kwargs):
        profile = get_profile(request)
        if not profile or not profile.department:
            return HttpResponseForbidden("No department assigned.")
        return view_func(request, *args, **kwargs)
    return wrapper


def get_version_or_403(request, version_pk):
    """Get curriculum version, ensuring it belongs to user's department."""
    profile = get_profile(request)
    version = get_object_or_404(CurriculumVersion, pk=version_pk)
    if profile.is_admin:
        return version
    if version.department != profile.department:
        return None
    return version


# ─────────────────────────────────────────────
# Curriculum Version
# ─────────────────────────────────────────────

@dept_required
def version_list(request):
    profile = get_profile(request)
    if profile.is_admin:
        versions = CurriculumVersion.objects.select_related('department').order_by('department', '-created_at')
    else:
        versions = CurriculumVersion.objects.filter(
            department=profile.department
        ).order_by('-created_at')
    return render(request, 'curriculum/version_list.html', {'versions': versions, 'profile': profile})


@login_required
def version_create(request):
    profile = get_profile(request)
    if not profile or profile.role not in (Profile.ROLE_HOD, Profile.ROLE_ADMIN):
        return HttpResponseForbidden("Only HOD or Admin can create curriculum versions.")

    if request.method == 'POST':
        form = CurriculumVersionForm(request.POST)
        if form.is_valid():
            version = form.save(commit=False)
            version.department = profile.department
            version.created_by = request.user
            version.save()
            log_action(
                user=request.user,
                department=profile.department,
                action=AuditLog.ACTION_CREATE,
                model_name='CurriculumVersion',
                record_id=version.pk,
                record_label=str(version),
                new_data={'regulation': version.regulation, 'academic_year': version.academic_year},
                curriculum_version=version
            )
            messages.success(request, f"Curriculum version '{version}' created.")
            return redirect('curriculum:version_detail', pk=version.pk)
    else:
        form = CurriculumVersionForm()
    return render(request, 'curriculum/version_form.html', {'form': form, 'action': 'Create'})


@dept_required
def version_detail(request, pk):
    profile = get_profile(request)
    version = get_version_or_403(request, pk)
    if version is None:
        return HttpResponseForbidden("You cannot access this curriculum version.")

    semesters = version.semesters.prefetch_related('courses__category', 'courses__course_outcomes').all()
    context = {
        'version': version,
        'profile': profile,
        'semesters': semesters,
        'peos': version.peos.all(),
        'pos': version.program_outcomes.all(),
        'gas': version.graduate_attributes.all(),
        'categories': version.course_categories.all(),
    }
    return render(request, 'curriculum/version_detail.html', context)


@login_required
def version_edit(request, pk):
    profile = get_profile(request)
    if not profile or profile.role not in (Profile.ROLE_HOD, Profile.ROLE_ADMIN):
        return HttpResponseForbidden("Only HOD can edit curriculum versions.")

    version = get_version_or_403(request, pk)
    if version is None:
        return HttpResponseForbidden("You cannot access this curriculum version.")
    if not version.is_editable:
        messages.error(request, "This version is published/archived and cannot be edited.")
        return redirect('curriculum:version_detail', pk=pk)

    form = CurriculumVersionForm(request.POST or None, instance=version)
    if request.method == 'POST' and form.is_valid():
        old = {'regulation': version.regulation, 'academic_year': version.academic_year}
        form.save()
        log_action(
            user=request.user, department=profile.department,
            action=AuditLog.ACTION_UPDATE, model_name='CurriculumVersion',
            record_id=version.pk, record_label=str(version),
            old_data=old, new_data={'regulation': version.regulation},
            curriculum_version=version
        )
        messages.success(request, "Curriculum version updated.")
        return redirect('curriculum:version_detail', pk=pk)
    return render(request, 'curriculum/version_form.html', {'form': form, 'action': 'Edit', 'version': version})


@login_required
def version_publish(request, pk):
    profile = get_profile(request)
    if not profile or not profile.is_hod:
        return HttpResponseForbidden("Only HOD can publish.")
    version = get_version_or_403(request, pk)
    if version is None:
        return HttpResponseForbidden()
    if request.method == 'POST':
        version.status = CurriculumVersion.STATUS_PUBLISHED
        version.save()
        log_action(
            user=request.user, department=profile.department,
            action=AuditLog.ACTION_PUBLISH, model_name='CurriculumVersion',
            record_id=version.pk, record_label=str(version),
            curriculum_version=version
        )
        messages.success(request, f"Curriculum '{version}' has been published.")
    return redirect('curriculum:version_detail', pk=pk)


# ─────────────────────────────────────────────
# Graduate Attributes (inline formset)
# ─────────────────────────────────────────────

@dept_required
def edit_graduate_attributes(request, version_pk):
    profile = get_profile(request)
    if not profile or profile.role not in (Profile.ROLE_HOD, Profile.ROLE_ADMIN):
        return HttpResponseForbidden("Only HOD can edit curriculum versions.")
    
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    formset = GraduateAttributeFormSet(request.POST or None, instance=version)
    if request.method == 'POST' and formset.is_valid():
        formset.save()
        log_action(
            user=request.user, department=profile.department,
            action=AuditLog.ACTION_UPDATE, model_name='GraduateAttribute',
            record_label=str(version), curriculum_version=version
        )
        messages.success(request, "Graduate Attributes saved.")
        return redirect('curriculum:version_detail', pk=version_pk)
    return render(request, 'curriculum/formset_page.html', {
        'formset': formset, 'version': version,
        'title': 'Graduate Attributes', 'back_url': f'/curriculum/version/{version_pk}/'
    })


# ─────────────────────────────────────────────
# PEOs
# ─────────────────────────────────────────────

@dept_required
def edit_peos(request, version_pk):
    profile = get_profile(request)
    if not profile or profile.role not in (Profile.ROLE_HOD, Profile.ROLE_ADMIN):
        return HttpResponseForbidden("Only HOD can edit curriculum versions.")
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    formset = PEOFormSet(request.POST or None, instance=version)
    if request.method == 'POST' and formset.is_valid():
        formset.save()
        log_action(
            user=request.user, department=profile.department,
            action=AuditLog.ACTION_UPDATE, model_name='PEO',
            record_label=str(version), curriculum_version=version
        )
        messages.success(request, "PEOs saved.")
        return redirect('curriculum:version_detail', pk=version_pk)
    return render(request, 'curriculum/formset_page.html', {
        'formset': formset, 'version': version,
        'title': 'Program Educational Objectives (PEOs)',
        'back_url': f'/curriculum/version/{version_pk}/'
    })


@dept_required
def edit_mission_peo_mappings(request, version_pk):
    profile = get_profile(request)
    if not profile or profile.role not in (Profile.ROLE_HOD, Profile.ROLE_ADMIN):
        return HttpResponseForbidden("Only HOD can edit curriculum versions.")
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    formset = MissionPEOMappingFormSet(request.POST or None, instance=version)
    if request.method == 'POST' and formset.is_valid():
        formset.save()
        messages.success(request, "Mission–PEO mappings saved.")
        return redirect('curriculum:version_detail', pk=version_pk)
    return render(request, 'curriculum/formset_page.html', {
        'formset': formset, 'version': version,
        'title': 'Mission → PEO Mappings',
        'help_text': 'Enter mappings as JSON: {"1": 2, "2": 3} where key=PEO number, value=strength (1/2/3)',
        'back_url': f'/curriculum/version/{version_pk}/'
    })


# ─────────────────────────────────────────────
# Program Outcomes
# ─────────────────────────────────────────────

@dept_required
def edit_program_outcomes(request, version_pk):
    profile = get_profile(request)
    if not profile or profile.role not in (Profile.ROLE_HOD, Profile.ROLE_ADMIN):
        return HttpResponseForbidden("Only HOD can edit curriculum versions.")
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    formset = ProgramOutcomeFormSet(request.POST or None, instance=version)
    if request.method == 'POST' and formset.is_valid():
        formset.save()
        log_action(
            user=request.user, department=profile.department,
            action=AuditLog.ACTION_UPDATE, model_name='ProgramOutcome',
            record_label=str(version), curriculum_version=version
        )
        messages.success(request, "Program Outcomes saved.")
        return redirect('curriculum:version_detail', pk=version_pk)
    return render(request, 'curriculum/formset_page.html', {
        'formset': formset, 'version': version,
        'title': 'Program Outcomes (POs)',
        'back_url': f'/curriculum/version/{version_pk}/'
    })


# ─────────────────────────────────────────────
# Course Categories
# ─────────────────────────────────────────────

@dept_required
def edit_categories(request, version_pk):
    profile = get_profile(request)
    if not profile or profile.role not in (Profile.ROLE_HOD, Profile.ROLE_ADMIN):
        return HttpResponseForbidden("Only HOD can edit curriculum versions.")
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    formset = CourseCategoryFormSet(request.POST or None, instance=version)
    if request.method == 'POST' and formset.is_valid():
        formset.save()
        messages.success(request, "Course categories saved.")
        return redirect('curriculum:version_detail', pk=version_pk)
    return render(request, 'curriculum/formset_page.html', {
        'formset': formset, 'version': version,
        'title': 'Course Categories & Credit Summary',
        'back_url': f'/curriculum/version/{version_pk}/'
    })


# ─────────────────────────────────────────────
# Semester Management
# ─────────────────────────────────────────────

@dept_required
def semester_create(request, version_pk):
    profile = get_profile(request)
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    form = SemesterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        semester = form.save(commit=False)
        semester.curriculum_version = version
        try:
            semester.save()
            messages.success(request, f"Semester {semester} added.")
        except Exception:
            messages.error(request, "This semester already exists in this version.")
        return redirect('curriculum:version_detail', pk=version_pk)
    return render(request, 'curriculum/semester_form.html', {'form': form, 'version': version})


# ─────────────────────────────────────────────
# Courses
# ─────────────────────────────────────────────

@dept_required
def course_list(request, version_pk):
    profile = get_profile(request)
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    semesters = version.semesters.prefetch_related(
        'courses__category', 'courses__course_outcomes'
    ).all()
    return render(request, 'curriculum/course_list.html', {
        'version': version, 'semesters': semesters, 'profile': profile
    })


@dept_required
def course_create(request, version_pk, semester_pk):
    profile = get_profile(request)
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    semester = get_object_or_404(Semester, pk=semester_pk, curriculum_version=version)
    form = CourseForm(request.POST or None, curriculum_version=version)

    if request.method == 'POST' and form.is_valid():
        print(
    "DEBUG:",
    request.user.username,
    profile.role,
    profile.is_faculty
    )
        if profile.is_faculty:
            # Faculty: create ChangeRequest instead of direct save
            new_data = {k: str(v) for k, v in form.cleaned_data.items()
                        if not hasattr(v, 'pk') and k != 'prerequisites'}
            new_data['prerequisites'] = [str(c.pk) for c in form.cleaned_data.get('prerequisites', [])]
            new_data['semester_pk'] = str(semester.pk)
            ChangeRequest.objects.create(
                curriculum_version=version,
                requested_by=request.user,
                model_name='Course',
                record_id=0,
                field_changed='new_course',
                old_data={},
                new_data=new_data,
            )
            log_action(
                user=request.user, department=profile.department,
                action=AuditLog.ACTION_CREATE, model_name='ChangeRequest',
                record_label=f"New course: {form.cleaned_data.get('code')}",
                curriculum_version=version
            )
            messages.success(request, "Change request submitted for HOD review.")
            return redirect('curriculum:course_list', version_pk=version_pk)
        else:
            # HOD: direct save
            course = form.save(commit=False)
            course.semester = semester
            course.save()
            form.save_m2m()
            log_action(
                user=request.user, department=profile.department,
                action=AuditLog.ACTION_CREATE, model_name='Course',
                record_id=course.pk, record_label=str(course),
                new_data={'code': course.code, 'title': course.title},
                curriculum_version=version
            )
            messages.success(request, f"Course '{course.code}' created.")
            return redirect('curriculum:course_detail', version_pk=version_pk, course_pk=course.pk)

    return render(request, 'curriculum/course_form.html', {
        'form': form, 'version': version, 'semester': semester, 'action': 'Create'
    })


@dept_required
def course_detail(request, version_pk, course_pk):
    profile = get_profile(request)
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    course = get_object_or_404(Course, pk=course_pk, semester__curriculum_version=version)
    cos = course.course_outcomes.prefetch_related('po_mappings').all()
    refs = course.references.all()

    return render(request, 'curriculum/course_detail.html', {
        'version': version, 'course': course,
        'cos': cos, 'refs': refs, 'profile': profile
    })


@dept_required
def course_edit(request, version_pk, course_pk):
    profile = get_profile(request)
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    course = get_object_or_404(Course, pk=course_pk, semester__curriculum_version=version)

    form = CourseForm(request.POST or None, instance=course, curriculum_version=version)

    if request.method == 'POST' and form.is_valid():
        if profile.is_faculty:
            old_data = {
                'code': course.code,
                'title': course.title,
                'credits': str(course.credits),
                'syllabus_text': course.syllabus_text,
                'lectures': str(course.lectures),
                'tutorials': str(course.tutorials),
                'practicals': str(course.practicals),
            }
            new_data = {
                'code': form.cleaned_data['code'],
                'title': form.cleaned_data['title'],
                'credits': str(form.cleaned_data['credits']),
                'syllabus_text': form.cleaned_data['syllabus_text'],
                'lectures': str(form.cleaned_data['lectures']),
                'tutorials': str(form.cleaned_data['tutorials']),
                'practicals': str(form.cleaned_data['practicals']),
            }
            ChangeRequest.objects.create(
                curriculum_version=version,
                requested_by=request.user,
                model_name='Course',
                record_id=course.pk,
                field_changed=', '.join([k for k in new_data if old_data.get(k) != new_data.get(k)]),
                old_data=old_data,
                new_data=new_data,
            )
            log_action(
                user=request.user, department=profile.department,
                action=AuditLog.ACTION_UPDATE, model_name='ChangeRequest',
                record_id=course.pk, record_label=str(course),
                old_data=old_data, new_data=new_data, curriculum_version=version
            )
            messages.info(request, "Change request submitted. Awaiting HOD approval.")
            return redirect('curriculum:course_detail', version_pk=version_pk, course_pk=course_pk)
        else:
            # HOD: direct save
            old_data = {'code': course.code, 'title': course.title}
            form.save()
            log_action(
                user=request.user, department=profile.department,
                action=AuditLog.ACTION_UPDATE, model_name='Course',
                record_id=course.pk, record_label=str(course),
                old_data=old_data, new_data={'code': course.code, 'title': course.title},
                curriculum_version=version
            )
            messages.success(request, "Course updated.")
            return redirect('curriculum:course_detail', version_pk=version_pk, course_pk=course_pk)

    return render(request, 'curriculum/course_form.html', {
        'form': form, 'version': version, 'course': course, 'action': 'Edit'
    })


@login_required
def course_delete(request, version_pk, course_pk):
    profile = get_profile(request)
    if not profile or not profile.is_hod:
        return HttpResponseForbidden("Only HOD can delete courses.")

    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    course = get_object_or_404(Course, pk=course_pk, semester__curriculum_version=version)
    if request.method == 'POST':
        log_action(
            user=request.user, department=profile.department,
            action=AuditLog.ACTION_DELETE, model_name='Course',
            record_id=course.pk, record_label=str(course),
            old_data={'code': course.code, 'title': course.title},
            curriculum_version=version
        )
        course.delete()
        messages.success(request, "Course deleted.")
    return redirect('curriculum:course_list', version_pk=version_pk)


# ─────────────────────────────────────────────
# Course Outcomes & CO-PO Mapping
# ─────────────────────────────────────────────

@dept_required
def edit_course_outcomes(request, version_pk, course_pk):
    profile = get_profile(request)
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()
    course = get_object_or_404(Course, pk=course_pk, semester__curriculum_version=version)

    co_formset = CourseOutcomeFormSet(request.POST or None, instance=course)

    if request.method == 'POST' and co_formset.is_valid():
        if profile.is_faculty:
            # Collect all COs as change request
            old_cos = list(course.course_outcomes.values('number', 'description'))
            new_cos_data = [
                {'number': str(f.cleaned_data.get('number', '')),
                 'description': f.cleaned_data.get('description', '')}
                for f in co_formset
                if f.cleaned_data and not f.cleaned_data.get('DELETE', False)
            ]
            ChangeRequest.objects.create(
                curriculum_version=version,
                requested_by=request.user,
                model_name='CourseOutcome',
                record_id=course.pk,
                field_changed='course_outcomes',
                old_data={'outcomes': old_cos},
                new_data={'outcomes': new_cos_data},
            )
            messages.info(request, "Course outcomes change submitted for HOD review.")
        else:
            co_formset.save()
            log_action(
                user=request.user, department=profile.department,
                action=AuditLog.ACTION_UPDATE, model_name='CourseOutcome',
                record_id=course.pk, record_label=str(course),
                curriculum_version=version
            )
            messages.success(request, "Course outcomes saved.")
        return redirect('curriculum:course_detail', version_pk=version_pk, course_pk=course_pk)

    return render(request, 'curriculum/course_outcomes_form.html', {
        'co_formset': co_formset, 'course': course, 'version': version
    })


@dept_required
def edit_copo_mapping(request, version_pk, course_pk, co_pk):
    profile = get_profile(request)
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()
    course = get_object_or_404(Course, pk=course_pk, semester__curriculum_version=version)
    co = get_object_or_404(CourseOutcome, pk=co_pk, course=course)
    mapping, _ = COPOMapping.objects.get_or_create(course_outcome=co)

    pos = version.program_outcomes.all()
    po_count = pos.count()

    if request.method == 'POST':
        # Build mappings from individual PO strength inputs
        mappings = {}
        for po in pos:
            val = request.POST.get(f'po_{po.number}', '').strip()
            if val in ('1', '2', '3'):
                mappings[str(po.number)] = int(val)
        if profile.is_faculty:
            ChangeRequest.objects.create(
                curriculum_version=version,
                requested_by=request.user,
                model_name='COPOMapping',
                record_id=mapping.pk,
                field_changed='mappings',
                old_data=mapping.mappings,
                new_data=mappings,
            )
            messages.info(request, "CO-PO mapping change submitted for review.")
        else:
            mapping.mappings = mappings
            mapping.save()
            messages.success(request, "CO-PO mapping saved.")
        return redirect('curriculum:course_detail', version_pk=version_pk, course_pk=course_pk)

    return render(request, 'curriculum/copo_mapping_form.html', {
        'co': co, 'course': course, 'version': version,
        'pos': pos, 'mapping': mapping
    })


@dept_required
def edit_references(request, version_pk, course_pk):
    profile = get_profile(request)
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()
    course = get_object_or_404(Course, pk=course_pk, semester__curriculum_version=version)

    ref_formset = ReferenceBookFormSet(request.POST or None, instance=course)
    if request.method == 'POST' and ref_formset.is_valid():
        if profile.is_faculty:
            old_refs = list(course.references.values('number', 'citation'))
            new_refs = [
                {'number': str(f.cleaned_data.get('number', '')),
                 'citation': f.cleaned_data.get('citation', '')}
                for f in ref_formset
                if f.cleaned_data and not f.cleaned_data.get('DELETE', False)
            ]
            ChangeRequest.objects.create(
                curriculum_version=version,
                requested_by=request.user,
                model_name='ReferenceBook',
                record_id=course.pk,
                field_changed='references',
                old_data={'refs': old_refs},
                new_data={'refs': new_refs},
            )
            messages.info(request, "Reference change submitted for review.")
        else:
            ref_formset.save()
            messages.success(request, "References saved.")
        return redirect('curriculum:course_detail', version_pk=version_pk, course_pk=course_pk)

    return render(request, 'curriculum/references_form.html', {
        'ref_formset': ref_formset, 'course': course, 'version': version
    })


# ─────────────────────────────────────────────
# PEO-GA and PO-PEO Mappings (HOD only)
# ─────────────────────────────────────────────

@login_required
def edit_peo_ga_mapping(request, version_pk):
    profile = get_profile(request)
    if not profile or not (profile.is_hod or profile.is_admin):
        return HttpResponseForbidden("Only HOD can edit mappings.")
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    peos = version.peos.all()
    gas = version.graduate_attributes.all()

    if request.method == 'POST':
        for peo in peos:
            mappings = {}
            for ga in gas:
                val = request.POST.get(f'peo_{peo.number}_ga_{ga.number}', '').strip()
                if val in ('1', '2', '3'):
                    mappings[str(ga.number)] = int(val)
            obj, _ = PEOGAMapping.objects.get_or_create(curriculum_version=version, peo=peo)
            obj.mappings = mappings
            obj.save()
        messages.success(request, "PEO–GA mappings saved.")
        return redirect('curriculum:version_detail', pk=version_pk)

    matrix = {}

    for peo in peos:
        matrix[peo.number] = {}

    mapping_objs = PEOGAMapping.objects.filter(curriculum_version=version)

    for obj in mapping_objs:
        for ga_num, strength in obj.mappings.items():
           matrix[obj.peo.number][int(ga_num)] = strength

    return render(request, 'curriculum/matrix_mapping.html', {
        'version': version,
        'row_items': peos,
        'col_items': gas,
        'row_label': 'PEO',
        'col_label': 'GA',
        'matrix': matrix,
        'title': 'PEO → GA Mapping',
        'form_action': request.path,
    })


@login_required
def edit_po_peo_mapping(request, version_pk):
    profile = get_profile(request)
    if not profile or not (profile.is_hod or profile.is_admin):
        return HttpResponseForbidden("Only HOD can edit mappings.")
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    pos = version.program_outcomes.all()
    peos = version.peos.all()

    if request.method == 'POST':
        for po in pos:
            mappings = {}
            for peo in peos:
                val = request.POST.get(f'po_{po.number}_peo_{peo.number}', '').strip()
                if val in ('1', '2', '3'):
                    mappings[str(peo.number)] = int(val)
            obj, _ = POPEOMapping.objects.get_or_create(curriculum_version=version, program_outcome=po)
            obj.mappings = mappings
            obj.save()
        messages.success(request, "PO–PEO mappings saved.")
        return redirect('curriculum:version_detail', pk=version_pk)
    matrix = {}

    for po in pos:
        matrix[po.number] = {}

    mapping_objs = POPEOMapping.objects.filter(curriculum_version=version)

    for obj in mapping_objs:
        for peo_num, strength in obj.mappings.items():
            matrix[obj.program_outcome.number][int(peo_num)] = strength

    return render(request, 'curriculum/matrix_mapping.html', {
        'version': version,
        'row_items': pos,
        'col_items': peos,
        'row_label': 'PO',
        'col_label': 'PEO',
        'matrix': matrix,
        'title': 'PO → PEO Mapping',
        'form_action': request.path,
    })


# ─────────────────────────────────────────────
# Change Requests (HOD Review)
# ─────────────────────────────────────────────

@login_required
def change_request_list(request, version_pk):
    profile = get_profile(request)
    if not profile or not (profile.is_hod or profile.is_admin):
        return HttpResponseForbidden("Only HOD can review change requests.")
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    status_filter = request.GET.get('status', 'PENDING')
    requests_qs = ChangeRequest.objects.filter(
        curriculum_version=version
    ).select_related('requested_by').order_by('-created_at')

    if status_filter != 'ALL':
        requests_qs = requests_qs.filter(status=status_filter)

    return render(request, 'curriculum/change_requests.html', {
        'version': version,
        'change_requests': requests_qs,
        'status_filter': status_filter,
        'profile': profile,
    })


@login_required
def change_request_review(request, version_pk, cr_pk):
    profile = get_profile(request)
    if not profile or not (profile.is_hod or profile.is_admin):
        return HttpResponseForbidden()
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    cr = get_object_or_404(ChangeRequest, pk=cr_pk, curriculum_version=version)
    form = ChangeRequestReviewForm(request.POST or None, instance=cr)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action not in ('approve', 'reject'):
            messages.error(request, "Invalid action.")
            return redirect('curriculum:change_requests', version_pk=version_pk)

        if form.is_valid():
            cr = form.save(commit=False)
            cr.reviewed_by = request.user
            cr.reviewed_at = timezone.now()

            if action == 'approve':
                cr.status = ChangeRequest.STATUS_APPROVED
                _apply_change_request(cr)
                log_action(
                    user=request.user, department=profile.department,
                    action=AuditLog.ACTION_APPROVE, model_name=cr.model_name,
                    record_id=cr.record_id,
                    record_label=f"CR#{cr.pk} by {cr.requested_by.username}",
                    old_data=cr.old_data, new_data=cr.new_data,
                    curriculum_version=version
                )
                messages.success(request, "Change approved and applied.")
            else:
                cr.status = ChangeRequest.STATUS_REJECTED
                log_action(
                    user=request.user, department=profile.department,
                    action=AuditLog.ACTION_REJECT, model_name=cr.model_name,
                    record_id=cr.record_id,
                    record_label=f"CR#{cr.pk} by {cr.requested_by.username}",
                    old_data=cr.old_data, new_data=cr.new_data,
                    curriculum_version=version
                )
                messages.warning(request, "Change rejected.")

            cr.save()
            return redirect('curriculum:change_requests', version_pk=version_pk)

    return render(request, 'curriculum/change_request_review.html', {
        'cr': cr, 'form': form, 'version': version
    })


def _apply_change_request(cr):
    """Apply approved change to actual database records."""
    model_map = {
        'Course': Course,
        'CourseOutcome': CourseOutcome,
        'COPOMapping': COPOMapping,
        'ReferenceBook': ReferenceBook,
    }
    model_class = model_map.get(cr.model_name)
    if not model_class:
        return

    if cr.model_name == 'Course' and cr.record_id == 0:
        # New course creation
        new_data = cr.new_data
        try:
            semester = Semester.objects.get(pk=int(new_data.get('semester_pk', 0)))
            category_pk = new_data.get('category')
            category = CourseCategory.objects.filter(pk=category_pk).first() if category_pk else None
            course = Course.objects.create(
                semester=semester,
                category=category,
                code=new_data.get('code', ''),
                title=new_data.get('title', ''),
                lectures=int(new_data.get('lectures', 0)),
                tutorials=int(new_data.get('tutorials', 0)),
                practicals=int(new_data.get('practicals', 0)),
                credits=int(new_data.get('credits', 0)),
                syllabus_text=new_data.get('syllabus_text', ''),
            )
            prereq_pks = [int(p) for p in new_data.get('prerequisites', []) if p]
            for pk in prereq_pks:
                prereq = Course.objects.filter(pk=pk).first()
                if prereq:
                    course.prerequisites.add(prereq)
        except Exception:
            pass
        return

    if cr.model_name == 'COPOMapping':
        mapping = COPOMapping.objects.filter(pk=cr.record_id).first()
        if mapping:
            mapping.mappings = cr.new_data
            mapping.save()
        return

    if cr.model_name == 'CourseOutcome':
        # Replace all outcomes for a course
        course = Course.objects.filter(pk=cr.record_id).first()
        if course:
            course.course_outcomes.all().delete()
            for co_data in cr.new_data.get('outcomes', []):
                CourseOutcome.objects.create(
                    course=course,
                    number=int(co_data.get('number', 0)),
                    description=co_data.get('description', ''),
                )
        return

    if cr.model_name == 'ReferenceBook':
        course = Course.objects.filter(pk=cr.record_id).first()
        if course:
            course.references.all().delete()
            for ref_data in cr.new_data.get('refs', []):
                ReferenceBook.objects.create(
                    course=course,
                    number=int(ref_data.get('number', 0)),
                    citation=ref_data.get('citation', ''),
                )
        return

    # Generic field update for Course
    try:
        obj = model_class.objects.get(pk=cr.record_id)
        for field, value in cr.new_data.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        obj.save()
    except model_class.DoesNotExist:
        pass


# ─────────────────────────────────────────────
# Audit Log
# ─────────────────────────────────────────────

@login_required
def audit_log(request, version_pk):
    profile = get_profile(request)
    if not profile or not (profile.is_hod or profile.is_admin):
        return HttpResponseForbidden("Only HOD can view audit logs.")
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    logs = AuditLog.objects.filter(
        curriculum_version=version
    ).select_related('user').order_by('-timestamp')

    return render(request, 'curriculum/audit_log.html', {
        'version': version, 'logs': logs, 'profile': profile
    })


# ─────────────────────────────────────────────
# Rollback
# ─────────────────────────────────────────────

@login_required
def rollback_audit(request, version_pk, log_pk):
    profile = get_profile(request)
    if not profile or not profile.is_hod:
        return HttpResponseForbidden("Only HOD can perform rollback.")
    version = get_version_or_403(request, version_pk)
    if version is None:
        return HttpResponseForbidden()

    if request.method == 'POST':
        log_entry = get_object_or_404(AuditLog, pk=log_pk, curriculum_version=version)

        if not log_entry.old_data:
            messages.error(request, "No previous state to roll back to.")
            return redirect('curriculum:audit_log', version_pk=version_pk)

        model_map = {'Course': Course, 'CourseOutcome': CourseOutcome, 'COPOMapping': COPOMapping}
        model_class = model_map.get(log_entry.model_name)
        if model_class and log_entry.record_id:
            try:
                obj = model_class.objects.get(pk=log_entry.record_id)
                for field, value in log_entry.old_data.items():
                    if hasattr(obj, field):
                        setattr(obj, field, value)
                obj.save()
                log_action(
                    user=request.user, department=profile.department,
                    action=AuditLog.ACTION_ROLLBACK, model_name=log_entry.model_name,
                    record_id=log_entry.record_id, record_label=log_entry.record_label,
                    old_data=log_entry.new_data, new_data=log_entry.old_data,
                    description=f"Rolled back from audit log #{log_entry.pk}",
                    curriculum_version=version
                )
                messages.success(request, f"Rollback successful for {log_entry.model_name} #{log_entry.record_id}.")
            except model_class.DoesNotExist:
                messages.error(request, "Record not found for rollback.")
        else:
            messages.error(request, "Rollback not supported for this record type.")

    return redirect('curriculum:audit_log', version_pk=version_pk)