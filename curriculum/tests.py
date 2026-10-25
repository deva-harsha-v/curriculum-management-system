from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Department, Profile
from curriculum.models import (
    CurriculumVersion, Semester, CourseCategory, Course,
    CourseOutcome, COPOMapping, PEO, GraduateAttribute,
    MissionPEOMapping, PEOGAMapping, POPEOMapping, ProgramOutcome,
    ChangeRequest, AuditLog
)


class BaseCurriculumTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Departments
        self.dept_cse = Department.objects.create(name='Computer Science and Engineering', code='CSE')
        self.dept_ece = Department.objects.create(name='Electronics and Communication Engineering', code='ECE')

        # Users & Profiles
        self.admin_user = User.objects.create_user(username='admin_u', password='password123')
        Profile.objects.create(user=self.admin_user, role=Profile.ROLE_ADMIN)

        self.hod_cse = User.objects.create_user(username='hod_cse', password='password123')
        Profile.objects.create(user=self.hod_cse, role=Profile.ROLE_HOD, department=self.dept_cse)

        self.faculty_cse = User.objects.create_user(username='faculty_cse', password='password123')
        Profile.objects.create(user=self.faculty_cse, role=Profile.ROLE_FACULTY, department=self.dept_cse)

        self.hod_ece = User.objects.create_user(username='hod_ece', password='password123')
        Profile.objects.create(user=self.hod_ece, role=Profile.ROLE_HOD, department=self.dept_ece)

        # Versions
        self.version_cse = CurriculumVersion.objects.create(
            department=self.dept_cse,
            regulation='R24',
            academic_year='2024-25',
            status=CurriculumVersion.STATUS_DRAFT,
            created_by=self.hod_cse,
            dept_mission=['Mission 1 statement', 'Mission 2 statement']
        )
        self.version_ece = CurriculumVersion.objects.create(
            department=self.dept_ece,
            regulation='R24',
            academic_year='2024-25',
            status=CurriculumVersion.STATUS_DRAFT,
            created_by=self.hod_ece
        )

        # Semester & Categories
        self.semester_cse = Semester.objects.create(
            curriculum_version=self.version_cse,
            year=1,
            semester=1
        )
        self.category_cse = CourseCategory.objects.create(
            curriculum_version=self.version_cse,
            code='PCC',
            name='Professional Core Course',
            credits_offered=20
        )


class CurriculumVersionLifecycleTests(BaseCurriculumTestCase):
    def test_hod_creates_curriculum_version_auto_sets_department(self):
        """When an HOD creates a version, their department is auto-assigned."""
        self.client.login(username='hod_cse', password='password123')
        response = self.client.post(reverse('curriculum:version_create'), {
            'regulation': 'R28',
            'academic_year': '2028-29',
            'institute_name': 'NIT AP',
        })
        self.assertEqual(response.status_code, 302)
        v = CurriculumVersion.objects.filter(regulation='R28').first()
        self.assertIsNotNone(v)
        self.assertEqual(v.department, self.dept_cse)
        # Check audit log
        log = AuditLog.objects.filter(action=AuditLog.ACTION_CREATE, model_name='CurriculumVersion', record_id=v.pk).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.department, self.dept_cse)

    def test_admin_creates_curriculum_version_with_department_choice(self):
        """Admin can select which department to create a version for."""
        self.client.login(username='admin_u', password='password123')
        response = self.client.post(reverse('curriculum:version_create'), {
            'department': self.dept_ece.id,
            'regulation': 'R26',
            'academic_year': '2026-27',
            'institute_name': 'NIT AP',
        })
        self.assertEqual(response.status_code, 302)
        v = CurriculumVersion.objects.filter(regulation='R26').first()
        self.assertIsNotNone(v)
        self.assertEqual(v.department, self.dept_ece)

    def test_curriculum_publish_and_archive_lifecycle(self):
        """Publish transitions DRAFT -> PUBLISHED; Archive transitions to ARCHIVED."""
        self.client.login(username='hod_cse', password='password123')

        # Publish
        pub_resp = self.client.post(reverse('curriculum:version_publish', args=[self.version_cse.id]))
        self.assertEqual(pub_resp.status_code, 302)
        self.version_cse.refresh_from_db()
        self.assertEqual(self.version_cse.status, CurriculumVersion.STATUS_PUBLISHED)
        self.assertFalse(self.version_cse.is_editable)

        # Archive
        arc_resp = self.client.post(reverse('curriculum:version_archive', args=[self.version_cse.id]))
        self.assertEqual(arc_resp.status_code, 302)
        self.version_cse.refresh_from_db()
        self.assertEqual(self.version_cse.status, CurriculumVersion.STATUS_ARCHIVED)

    def test_published_version_cannot_be_edited(self):
        """Editing a published or archived curriculum version is disallowed."""
        self.version_cse.status = CurriculumVersion.STATUS_PUBLISHED
        self.version_cse.save()

        self.client.login(username='hod_cse', password='password123')
        resp = self.client.post(reverse('curriculum:version_edit', args=[self.version_cse.id]), {
            'regulation': 'R24_MODIFIED',
            'academic_year': '2024-25',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.version_cse.refresh_from_db()
        self.assertEqual(self.version_cse.regulation, 'R24')  # Remains unedited


class DepartmentIsolationTests(BaseCurriculumTestCase):
    def test_cross_department_access_denied(self):
        """User from CSE department cannot view or edit ECE curriculum."""
        self.client.login(username='hod_cse', password='password123')

        # Detail view cross-access
        resp_detail = self.client.get(reverse('curriculum:version_detail', args=[self.version_ece.id]))
        self.assertEqual(resp_detail.status_code, 403)

        # Edit view cross-access
        resp_edit = self.client.get(reverse('curriculum:version_edit', args=[self.version_ece.id]))
        self.assertEqual(resp_edit.status_code, 403)

    def test_cross_department_change_requests_denied(self):
        """HOD cannot view or review change requests belonging to another department."""
        self.client.login(username='hod_cse', password='password123')
        resp = self.client.get(reverse('curriculum:change_requests', args=[self.version_ece.id]))
        self.assertEqual(resp.status_code, 403)

    def test_admin_has_cross_department_access(self):
        """Admin is authorized across all departments."""
        self.client.login(username='admin_u', password='password123')
        resp_cse = self.client.get(reverse('curriculum:version_detail', args=[self.version_cse.id]))
        self.assertEqual(resp_cse.status_code, 200)

        resp_ece = self.client.get(reverse('curriculum:version_detail', args=[self.version_ece.id]))
        self.assertEqual(resp_ece.status_code, 200)


class CourseAndPrerequisiteTests(BaseCurriculumTestCase):
    def test_hod_direct_course_creation(self):
        """HOD creates a course directly in the database."""
        self.client.login(username='hod_cse', password='password123')
        resp = self.client.post(
            reverse('curriculum:course_create', args=[self.version_cse.id, self.semester_cse.id]),
            {
                'code': 'CS101',
                'title': 'Problem Solving & Python',
                'category': self.category_cse.id,
                'lectures': 3,
                'tutorials': 0,
                'practicals': 2,
                'credits': 4,
                'syllabus_text': 'Unit 1: Introduction to Programming'
            }
        )
        self.assertEqual(resp.status_code, 302)
        course = Course.objects.filter(code='CS101').first()
        self.assertIsNotNone(course)
        self.assertEqual(course.semester, self.semester_cse)

    def test_faculty_course_creation_creates_change_request(self):
        """Faculty creating a course submits a ChangeRequest awaiting HOD review."""
        self.client.login(username='faculty_cse', password='password123')
        resp = self.client.post(
            reverse('curriculum:course_create', args=[self.version_cse.id, self.semester_cse.id]),
            {
                'code': 'CS102',
                'title': 'Data Structures',
                'category': self.category_cse.id,
                'lectures': 3,
                'tutorials': 1,
                'practicals': 0,
                'credits': 4,
            }
        )
        self.assertEqual(resp.status_code, 302)
        # Course should NOT be created directly
        self.assertFalse(Course.objects.filter(code='CS102').exists())
        # ChangeRequest should be created
        cr = ChangeRequest.objects.filter(model_name='Course', requested_by=self.faculty_cse).first()
        self.assertIsNotNone(cr)
        self.assertEqual(cr.status, ChangeRequest.STATUS_PENDING)
        self.assertEqual(cr.new_data.get('code'), 'CS102')

    def test_prerequisite_assignment_and_deletion(self):
        """Courses can be configured with prerequisites and deleted by HOD."""
        self.client.login(username='hod_cse', password='password123')
        c1 = Course.objects.create(
            semester=self.semester_cse, code='CS201', title='Basic Programming', credits=3
        )
        c2 = Course.objects.create(
            semester=self.semester_cse, code='CS202', title='Advanced Algorithms', credits=4
        )
        c2.prerequisites.add(c1)
        self.assertIn(c1, c2.prerequisites.all())

        # Delete course
        del_resp = self.client.post(reverse('curriculum:course_delete', args=[self.version_cse.id, c2.id]))
        self.assertEqual(del_resp.status_code, 302)
        self.assertFalse(Course.objects.filter(id=c2.id).exists())


class MappingValidationTests(BaseCurriculumTestCase):
    def test_copo_mapping_save_and_validation(self):
        """CO-PO mapping saves valid strengths (1, 2, 3) and ignores invalid ones."""
        self.client.login(username='hod_cse', password='password123')
        po1 = ProgramOutcome.objects.create(curriculum_version=self.version_cse, number=1, description='Engineering Knowledge')
        po2 = ProgramOutcome.objects.create(curriculum_version=self.version_cse, number=2, description='Problem Analysis')

        course = Course.objects.create(semester=self.semester_cse, code='CS301', title='Database Systems', credits=3)
        co = CourseOutcome.objects.create(course=course, number=1, description='Understand Relational Models')

        # Post valid mapping
        resp = self.client.post(
            reverse('curriculum:edit_copo', args=[self.version_cse.id, course.id, co.id]),
            {'po_1': '3', 'po_2': '2'}
        )
        self.assertEqual(resp.status_code, 302)
        mapping = COPOMapping.objects.get(course_outcome=co)
        self.assertEqual(mapping.mappings.get('1'), 3)
        self.assertEqual(mapping.mappings.get('2'), 2)

    def test_mission_peo_matrix_mapping(self):
        """Mission-PEO matrix mapping saves strength values properly."""
        self.client.login(username='hod_cse', password='password123')
        peo1 = PEO.objects.create(curriculum_version=self.version_cse, number=1, description='Technical Proficiency')
        peo2 = PEO.objects.create(curriculum_version=self.version_cse, number=2, description='Professional Leadership')

        resp = self.client.post(
            reverse('curriculum:edit_mission_peo', args=[self.version_cse.id]),
            {
                'mission_1_peo_1': '3',
                'mission_1_peo_2': '2',
                'mission_2_peo_1': '1',
            }
        )
        self.assertEqual(resp.status_code, 302)
        m1 = MissionPEOMapping.objects.filter(curriculum_version=self.version_cse, mission_order=1).first()
        self.assertIsNotNone(m1)
        self.assertEqual(m1.mappings.get('1'), 3)
        self.assertEqual(m1.mappings.get('2'), 2)


class ChangeRequestWorkflowTests(BaseCurriculumTestCase):
    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            semester=self.semester_cse, code='CS401', title='Computer Networks', credits=3
        )
        self.co = CourseOutcome.objects.create(course=self.course, number=1, description='Network layers')
        self.mapping = COPOMapping.objects.create(course_outcome=self.co, mappings={'1': 2})

    def test_approve_change_request_applies_changes_atomically(self):
        """HOD approving a change request applies changes and updates audit log in a transaction."""
        cr = ChangeRequest.objects.create(
            curriculum_version=self.version_cse,
            requested_by=self.faculty_cse,
            model_name='Course',
            record_id=self.course.id,
            field_changed='title',
            old_data={'title': 'Computer Networks'},
            new_data={'title': 'Advanced Computer Networks'},
            status=ChangeRequest.STATUS_PENDING
        )

        self.client.login(username='hod_cse', password='password123')
        resp = self.client.post(
            reverse('curriculum:change_request_review', args=[self.version_cse.id, cr.id]),
            {
                'action': 'approve',
                'hod_comment': 'Approved by HOD'
            }
        )
        self.assertEqual(resp.status_code, 302)
        cr.refresh_from_db()
        self.assertEqual(cr.status, ChangeRequest.STATUS_APPROVED)
        self.assertEqual(cr.hod_comment, 'Approved by HOD')

        # Check course was updated in database
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Advanced Computer Networks')

        # Check audit log
        log = AuditLog.objects.filter(action=AuditLog.ACTION_APPROVE, model_name='Course').first()
        self.assertIsNotNone(log)

    def test_reject_change_request_does_not_apply_changes(self):
        """HOD rejecting a change request leaves database unmodified."""
        cr = ChangeRequest.objects.create(
            curriculum_version=self.version_cse,
            requested_by=self.faculty_cse,
            model_name='Course',
            record_id=self.course.id,
            field_changed='title',
            old_data={'title': 'Computer Networks'},
            new_data={'title': 'Rejected Network Title'},
            status=ChangeRequest.STATUS_PENDING
        )

        self.client.login(username='hod_cse', password='password123')
        resp = self.client.post(
            reverse('curriculum:change_request_review', args=[self.version_cse.id, cr.id]),
            {
                'action': 'reject',
                'hod_comment': 'Not compliant with regulation guidelines'
            }
        )
        self.assertEqual(resp.status_code, 302)
        cr.refresh_from_db()
        self.assertEqual(cr.status, ChangeRequest.STATUS_REJECTED)

        # Database remains untouched
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Computer Networks')


class AuditLogAndRollbackTests(BaseCurriculumTestCase):
    def test_audit_rollback_restores_previous_state(self):
        """HOD can roll back a course update using an AuditLog entry."""
        self.client.login(username='hod_cse', password='password123')
        course = Course.objects.create(semester=self.semester_cse, code='CS501', title='Original Title', credits=3)

        # Log an update with old_data
        log_entry = AuditLog.objects.create(
            user=self.hod_cse,
            department=self.dept_cse,
            action=AuditLog.ACTION_UPDATE,
            model_name='Course',
            record_id=course.id,
            record_label=str(course),
            old_data={'title': 'Original Title'},
            new_data={'title': 'Updated Title'},
            curriculum_version=self.version_cse
        )
        course.title = 'Updated Title'
        course.save()

        # Execute rollback
        resp = self.client.post(reverse('curriculum:rollback_audit', args=[self.version_cse.id, log_entry.id]))
        self.assertEqual(resp.status_code, 302)

        # Verify title was restored
        course.refresh_from_db()
        self.assertEqual(course.title, 'Original Title')
