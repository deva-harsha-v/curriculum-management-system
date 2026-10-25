import io
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Department, Profile
from curriculum.models import (
    CurriculumVersion, Semester, Course, CourseCategory, AuditLog
)
from pdf_generator.generator import generate_curriculum_pdf
from pdf_generator.prereq_chart import generate_prereq_chart


class PDFGeneratorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name='Computer Science and Engineering', code='CSE')

        self.hod = User.objects.create_user(username='hod_pdf', password='password123')
        Profile.objects.create(user=self.hod, role=Profile.ROLE_HOD, department=self.dept)

        self.faculty = User.objects.create_user(username='fac_pdf', password='password123')
        Profile.objects.create(user=self.faculty, role=Profile.ROLE_FACULTY, department=self.dept)

        self.draft_version = CurriculumVersion.objects.create(
            department=self.dept,
            regulation='R24',
            academic_year='2024-25',
            status=CurriculumVersion.STATUS_DRAFT,
            created_by=self.hod
        )
        self.published_version = CurriculumVersion.objects.create(
            department=self.dept,
            regulation='R20',
            academic_year='2020-21',
            status=CurriculumVersion.STATUS_PUBLISHED,
            created_by=self.hod
        )

        self.sem = Semester.objects.create(curriculum_version=self.draft_version, year=1, semester=1)
        self.cat = CourseCategory.objects.create(curriculum_version=self.draft_version, code='BSC', name='Basic Science', credits_offered=4)

        self.course1 = Course.objects.create(semester=self.sem, category=self.cat, code='CS101', title='Programming Basics', credits=4)
        self.course2 = Course.objects.create(semester=self.sem, category=self.cat, code='CS102', title='Data Structures', credits=4)

    def test_pdf_generate_confirm_template_renders(self):
        """GET request to pdf_generate renders generate_confirm.html."""
        self.client.login(username='hod_pdf', password='password123')
        resp = self.client.get(reverse('pdf_generator:pdf_generate', args=[self.draft_version.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'pdf_generator/generate_confirm.html')
        self.assertContains(resp, 'Official Curriculum Document Compilation')

    def test_pdf_preview_hod_can_preview_draft(self):
        """HOD can preview a draft curriculum version."""
        self.client.login(username='hod_pdf', password='password123')
        resp = self.client.get(reverse('pdf_generator:pdf_preview', args=[self.draft_version.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'pdf_generator/preview.html')

    def test_pdf_preview_faculty_draft_forbidden(self):
        """Faculty cannot preview a draft curriculum version (403 Forbidden)."""
        self.client.login(username='fac_pdf', password='password123')
        resp = self.client.get(reverse('pdf_generator:pdf_preview', args=[self.draft_version.id]))
        self.assertEqual(resp.status_code, 403)

    def test_pdf_preview_faculty_published_allowed(self):
        """Faculty can preview a published curriculum version."""
        self.client.login(username='fac_pdf', password='password123')
        resp = self.client.get(reverse('pdf_generator:pdf_preview', args=[self.published_version.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'pdf_generator/preview.html')

    def test_pdf_generation_without_prerequisites(self):
        """PDF compiles cleanly when no course prerequisites exist."""
        buf = generate_curriculum_pdf(self.draft_version)
        self.assertIsInstance(buf, io.BytesIO)
        pdf_bytes = buf.getvalue()
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
        self.assertGreater(len(pdf_bytes), 1000)

    def test_pdf_generation_with_prerequisites(self):
        """PDF compiles cleanly when courses contain prerequisite dependencies."""
        self.course2.prerequisites.add(self.course1)
        buf = generate_curriculum_pdf(self.draft_version)
        pdf_bytes = buf.getvalue()
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
        self.assertGreater(len(pdf_bytes), 1000)

    def test_pdf_stream_inline_response(self):
        """pdf_stream view returns PDF content type and inline disposition."""
        self.client.login(username='hod_pdf', password='password123')
        resp = self.client.get(reverse('pdf_generator:pdf_stream', args=[self.draft_version.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertIn('inline', resp['Content-Disposition'])

    def test_prereq_chart_fallback_when_graphviz_fails(self):
        """When Graphviz execution fails, chart generator safely returns None and fallback renders."""
        self.course2.prerequisites.add(self.course1)
        with patch('graphviz.Digraph.render', side_effect=Exception('Graphviz executable not found')):
            chart_path = generate_prereq_chart(self.draft_version)
            self.assertIsNone(chart_path)

            # PDF generator must still succeed using the fallback table
            buf = generate_curriculum_pdf(self.draft_version)
            pdf_bytes = buf.getvalue()
            self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
