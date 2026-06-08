from django.contrib import admin
from .models import (
    CurriculumVersion, GraduateAttribute, PEO, MissionPEOMapping, PEOGAMapping,
    ProgramOutcome, POPEOMapping, CourseCategory, Semester, Course,
    CourseOutcome, COPOMapping, ReferenceBook, ChangeRequest, AuditLog
)


class GraduateAttributeInline(admin.TabularInline):
    model = GraduateAttribute
    extra = 0


class PEOInline(admin.TabularInline):
    model = PEO
    extra = 0


class ProgramOutcomeInline(admin.TabularInline):
    model = ProgramOutcome
    extra = 0


class CourseCategoryInline(admin.TabularInline):
    model = CourseCategory
    extra = 0


@admin.register(CurriculumVersion)
class CurriculumVersionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'department', 'regulation', 'academic_year', 'status', 'created_at')
    list_filter = ('status', 'department')
    search_fields = ('regulation', 'academic_year', 'department__name')
    inlines = [GraduateAttributeInline, PEOInline, ProgramOutcomeInline, CourseCategoryInline]


class CourseOutcomeInline(admin.TabularInline):
    model = CourseOutcome
    extra = 0


class ReferenceBookInline(admin.TabularInline):
    model = ReferenceBook
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'semester', 'category', 'credits', 'is_elective')
    list_filter = ('semester__curriculum_version__department', 'semester', 'is_elective')
    search_fields = ('code', 'title')
    inlines = [CourseOutcomeInline, ReferenceBookInline]
    filter_horizontal = ('prerequisites',)


@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('pk', 'requested_by', 'curriculum_version', 'model_name', 'status', 'created_at')
    list_filter = ('status', 'model_name')
    readonly_fields = ('old_data', 'new_data', 'created_at', 'reviewed_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'record_label', 'department')
    list_filter = ('action', 'department', 'model_name')
    readonly_fields = ('timestamp', 'old_data', 'new_data')
    search_fields = ('user__username', 'record_label', 'description')


admin.site.register(Semester)
admin.site.register(CourseCategory)
admin.site.register(GraduateAttribute)
admin.site.register(PEO)
admin.site.register(ProgramOutcome)
admin.site.register(MissionPEOMapping)
admin.site.register(PEOGAMapping)
admin.site.register(POPEOMapping)
admin.site.register(COPOMapping)