import json
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Department


# ─────────────────────────────────────────────
# Curriculum Version (snapshot per regulation)
# ─────────────────────────────────────────────

class CurriculumVersion(models.Model):
    STATUS_DRAFT = 'DRAFT'
    STATUS_PUBLISHED = 'PUBLISHED'
    STATUS_ARCHIVED = 'ARCHIVED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='curriculum_versions')
    regulation = models.CharField(max_length=20, help_text="e.g. R20, R24, R28")
    academic_year = models.CharField(max_length=20, help_text="e.g. 2024-25")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    # Institute-level info (stored per version so old PDFs stay accurate)
    institute_name = models.CharField(max_length=300, default="Curriculum Management System")
    institute_vision = models.TextField(blank=True)
    institute_mission = models.JSONField(default=list, help_text="List of mission statement strings")

    # Department-level
    dept_vision = models.TextField(blank=True)
    dept_mission = models.JSONField(default=list, help_text="List of mission statement strings")

    # Graduate Attributes intro paragraph
    ga_intro = models.TextField(
        blank=True,
        default="The Graduate Attributes are the knowledge skills and attitudes which the students have at "
                "the time of graduation. These attributes are generic and are common to all engineering programs. "
                "These Graduate Attributes are identified by National Board of Accreditation."
    )

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_versions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [('department', 'regulation')]
        verbose_name = 'Curriculum Version'

    def __str__(self):
        return f"{self.department.code} - {self.regulation} ({self.academic_year})"

    @property
    def is_editable(self):
        return self.status == self.STATUS_DRAFT


# ─────────────────────────────────────────────
# Graduate Attributes
# ─────────────────────────────────────────────

class GraduateAttribute(models.Model):
    curriculum_version = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name='graduate_attributes')
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()

    class Meta:
        ordering = ['number']
        unique_together = [('curriculum_version', 'number')]

    def __str__(self):
        return f"GA{self.number}: {self.title}"


# ─────────────────────────────────────────────
# Program Educational Objectives
# ─────────────────────────────────────────────

class PEO(models.Model):
    curriculum_version = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name='peos')
    number = models.PositiveSmallIntegerField()
    description = models.TextField()

    class Meta:
        ordering = ['number']
        unique_together = [('curriculum_version', 'number')]

    def __str__(self):
        return f"PEO{self.number}"


class MissionPEOMapping(models.Model):
    """Maps each dept mission statement to PEOs with strength 1/2/3."""
    STRENGTH_CHOICES = [(1, '1'), (2, '2'), (3, '3')]

    curriculum_version = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name='mission_peo_mappings')
    mission_statement = models.TextField(help_text="One mission statement line")
    mission_order = models.PositiveSmallIntegerField(default=1)
    mappings = models.JSONField(
        default=dict,
        help_text='Dict of PEO number → strength, e.g. {"1": 2, "3": 3}'
    )

    class Meta:
        ordering = ['mission_order']

    @property
    def number(self):
        return self.mission_order

    @property
    def description(self):
        return self.mission_statement

    def __str__(self):
        return f"Mission {self.mission_order} → PEO mappings"


class PEOGAMapping(models.Model):
    """Maps each PEO to GAs with strength 1/2/3."""
    curriculum_version = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name='peo_ga_mappings')
    peo = models.ForeignKey(PEO, on_delete=models.CASCADE, related_name='ga_mappings')
    mappings = models.JSONField(
        default=dict,
        help_text='Dict of GA number → strength, e.g. {"1": 2, "3": 3}'
    )

    class Meta:
        unique_together = [('curriculum_version', 'peo')]

    def __str__(self):
        return f"{self.peo} → GA mappings"


# ─────────────────────────────────────────────
# Program Outcomes
# ─────────────────────────────────────────────

class ProgramOutcome(models.Model):
    curriculum_version = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name='program_outcomes')
    number = models.PositiveSmallIntegerField()
    description = models.TextField()

    class Meta:
        ordering = ['number']
        unique_together = [('curriculum_version', 'number')]

    def __str__(self):
        return f"PO{self.number}"


class POPEOMapping(models.Model):
    """Maps each PO to PEOs with strength 1/2/3."""
    curriculum_version = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name='po_peo_mappings')
    program_outcome = models.ForeignKey(ProgramOutcome, on_delete=models.CASCADE, related_name='peo_mappings')
    mappings = models.JSONField(
        default=dict,
        help_text='Dict of PEO number → strength'
    )

    class Meta:
        unique_together = [('curriculum_version', 'program_outcome')]

    def __str__(self):
        return f"{self.program_outcome} → PEO mappings"


# ─────────────────────────────────────────────
# Course Categories & Credit Summary
# ─────────────────────────────────────────────

class CourseCategory(models.Model):
    curriculum_version = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name='course_categories')
    code = models.CharField(max_length=10, help_text="e.g. BSC, ESC, PCC, DEC, OPC, PRC, MDC, HSC")
    name = models.CharField(max_length=200, help_text="e.g. Basic Science Core")
    credits_offered = models.PositiveSmallIntegerField(default=0)
    min_credits = models.PositiveSmallIntegerField(default=0)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'code']
        unique_together = [('curriculum_version', 'code')]

    def __str__(self):
        return f"{self.code} - {self.name}"


# ─────────────────────────────────────────────
# Semesters and Courses
# ─────────────────────────────────────────────

class Semester(models.Model):
    YEAR_CHOICES = [
        (1, 'Year I'), (2, 'Year II'), (3, 'Year III'), (4, 'Year IV'),
    ]
    SEM_CHOICES = [
        (1, 'Semester I'), (2, 'Semester II'),
    ]

    curriculum_version = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name='semesters')
    year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES)
    semester = models.PositiveSmallIntegerField(choices=SEM_CHOICES)

    class Meta:
        ordering = ['year', 'semester']
        unique_together = [('curriculum_version', 'year', 'semester')]

    def __str__(self):
        return f"Year {self.year} Semester {self.semester}"

    @property
    def label(self):
        return f"B.Tech {self.get_year_display()} - {self.get_semester_display()}"

    @property
    def semester_number(self):
        return (self.year - 1) * 2 + self.semester


class Course(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, related_name='courses')
    code = models.CharField(max_length=20)
    title = models.CharField(max_length=300)
    lectures = models.PositiveSmallIntegerField(default=0, verbose_name='L')
    tutorials = models.PositiveSmallIntegerField(default=0, verbose_name='T')
    practicals = models.PositiveSmallIntegerField(default=0, verbose_name='P')
    credits = models.PositiveSmallIntegerField(default=0)
    is_elective = models.BooleanField(default=False)
    elective_group = models.CharField(
        max_length=50,
        blank=True,
        help_text="Group label for OR electives, e.g. 'Group A'"
    )
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='prerequisite_for'
    )
    syllabus_text = models.TextField(blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'code']

    def __str__(self):
        return f"{self.code} - {self.title}"

    @property
    def ltp_display(self):
        return f"{self.lectures} – {self.tutorials} – {self.practicals}"

    @property
    def curriculum_version(self):
        return self.semester.curriculum_version


class CourseOutcome(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_outcomes')
    number = models.PositiveSmallIntegerField()
    description = models.TextField()

    class Meta:
        ordering = ['number']
        unique_together = [('course', 'number')]

    def __str__(self):
        return f"CO{self.number} of {self.course.code}"


class COPOMapping(models.Model):
    """Maps a CourseOutcome to ProgramOutcomes with strength 1/2/3."""
    course_outcome = models.ForeignKey(CourseOutcome, on_delete=models.CASCADE, related_name='po_mappings')
    mappings = models.JSONField(
        default=dict,
        help_text='Dict of PO number → strength, e.g. {"1": 3, "4": 2}'
    )

    class Meta:
        unique_together = [('course_outcome',)]

    def __str__(self):
        return f"CO{self.course_outcome.number} of {self.course_outcome.course.code} → PO mappings"


class ReferenceBook(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='references')
    number = models.PositiveSmallIntegerField()
    citation = models.TextField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Ref {self.number} for {self.course.code}"


# ─────────────────────────────────────────────
# Change Request (GitHub-like workflow)
# ─────────────────────────────────────────────

class ChangeRequest(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    curriculum_version = models.ForeignKey(CurriculumVersion, on_delete=models.CASCADE, related_name='change_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='change_requests')
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests'
    )

    model_name = models.CharField(max_length=100, help_text="e.g. Course, CourseOutcome, PEO")
    record_id = models.PositiveIntegerField(help_text="Primary key of the changed record")
    field_changed = models.CharField(max_length=200, blank=True, help_text="Comma-separated field names")
    old_data = models.JSONField(default=dict, help_text="State before change")
    new_data = models.JSONField(default=dict, help_text="Proposed state")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    hod_comment = models.TextField(blank=True, help_text="HOD note when approving/rejecting")

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ChangeRequest #{self.pk} by {self.requested_by.username} [{self.status}]"

    def get_diff(self):
        """Return list of (field, old_val, new_val) tuples for display."""
        diffs = []
        all_keys = set(list(self.old_data.keys()) + list(self.new_data.keys()))
        for key in sorted(all_keys):
            old_val = self.old_data.get(key, '—')
            new_val = self.new_data.get(key, '—')
            if old_val != new_val:
                diffs.append((key, old_val, new_val))
        return diffs


# ─────────────────────────────────────────────
# Audit Log
# ─────────────────────────────────────────────

class AuditLog(models.Model):
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_APPROVE = 'APPROVE'
    ACTION_REJECT = 'REJECT'
    ACTION_ROLLBACK = 'ROLLBACK'
    ACTION_GENERATE_PDF = 'GENERATE_PDF'
    ACTION_PUBLISH = 'PUBLISH'

    ACTION_CHOICES = [
        (ACTION_CREATE, 'Create'),
        (ACTION_UPDATE, 'Update'),
        (ACTION_DELETE, 'Delete'),
        (ACTION_APPROVE, 'Approve'),
        (ACTION_REJECT, 'Reject'),
        (ACTION_ROLLBACK, 'Rollback'),
        (ACTION_GENERATE_PDF, 'Generate PDF'),
        (ACTION_PUBLISH, 'Publish'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='audit_logs')
    curriculum_version = models.ForeignKey(
        CurriculumVersion, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    record_id = models.PositiveIntegerField(null=True, blank=True)
    record_label = models.CharField(max_length=300, blank=True)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user} {self.action} {self.model_name}"


# ─────────────────────────────────────────────
# Helper: create audit log entry
# ─────────────────────────────────────────────

def log_action(user, department, action, model_name, record_id=None,
               record_label='', old_data=None, new_data=None,
               description='', curriculum_version=None):
    AuditLog.objects.create(
        user=user,
        department=department,
        curriculum_version=curriculum_version,
        action=action,
        model_name=model_name,
        record_id=record_id,
        record_label=record_label,
        old_data=old_data,
        new_data=new_data,
        description=description,
    )