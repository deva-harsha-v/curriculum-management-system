import json
from django import forms
from django.forms import inlineformset_factory

from .models import (
    CurriculumVersion, GraduateAttribute, PEO, MissionPEOMapping, PEOGAMapping,
    ProgramOutcome, POPEOMapping, CourseCategory, Semester, Course,
    CourseOutcome, COPOMapping, ReferenceBook, ChangeRequest
)


W_TEXT = {'class': 'form-control'}
W_TEXTAREA = {'class': 'form-control', 'rows': 3}
W_SELECT = {'class': 'form-select'}
W_NUMBER = {'class': 'form-control', 'style': 'width:80px'}


# ─────────────────────────────────────────────
# Curriculum Version
# ─────────────────────────────────────────────

class CurriculumVersionForm(forms.ModelForm):
    institute_mission_text = forms.CharField(
        widget=forms.Textarea(attrs={**W_TEXTAREA, 'rows': 5,
                              'placeholder': 'Enter each mission statement on a new line'}),
        label='Institute Mission Statements (one per line)',
        required=False
    )
    dept_mission_text = forms.CharField(
        widget=forms.Textarea(attrs={**W_TEXTAREA, 'rows': 4,
                              'placeholder': 'Enter each mission statement on a new line'}),
        label='Department Mission Statements (one per line)',
        required=False
    )

    class Meta:
        model = CurriculumVersion
        fields = [
            'regulation', 'academic_year',
            'institute_name', 'institute_vision',
            'dept_vision', 'ga_intro',
        ]
        widgets = {
            'regulation': forms.TextInput(attrs={**W_TEXT, 'placeholder': 'e.g. R24'}),
            'academic_year': forms.TextInput(attrs={**W_TEXT, 'placeholder': 'e.g. 2024-25'}),
            'institute_name': forms.TextInput(attrs=W_TEXT),
            'institute_vision': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 3}),
            'dept_vision': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 3}),
            'ga_intro': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            inst_missions = self.instance.institute_mission
            if isinstance(inst_missions, list):
                self.fields['institute_mission_text'].initial = '\n'.join(inst_missions)
            dept_missions = self.instance.dept_mission
            if isinstance(dept_missions, list):
                self.fields['dept_mission_text'].initial = '\n'.join(dept_missions)

    def save(self, commit=True):
        instance = super().save(commit=False)
        inst_text = self.cleaned_data.get('institute_mission_text', '')
        instance.institute_mission = [
            line.strip() for line in inst_text.splitlines() if line.strip()
        ]
        dept_text = self.cleaned_data.get('dept_mission_text', '')
        instance.dept_mission = [
            line.strip() for line in dept_text.splitlines() if line.strip()
        ]
        if commit:
            instance.save()
        return instance


# ─────────────────────────────────────────────
# Graduate Attributes
# ─────────────────────────────────────────────

class GraduateAttributeForm(forms.ModelForm):
    class Meta:
        model = GraduateAttribute
        fields = ['number', 'title', 'description']
        widgets = {
            'number': forms.NumberInput(attrs=W_NUMBER),
            'title': forms.TextInput(attrs=W_TEXT),
            'description': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 3}),
        }


GraduateAttributeFormSet = inlineformset_factory(
    CurriculumVersion, GraduateAttribute,
    form=GraduateAttributeForm,
    extra=1, can_delete=True
)


# ─────────────────────────────────────────────
# PEO
# ─────────────────────────────────────────────

class PEOForm(forms.ModelForm):
    class Meta:
        model = PEO
        fields = ['number', 'description']
        widgets = {
            'number': forms.NumberInput(attrs=W_NUMBER),
            'description': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 3}),
        }


PEOFormSet = inlineformset_factory(
    CurriculumVersion, PEO,
    form=PEOForm,
    extra=1, can_delete=True
)


# ─────────────────────────────────────────────
# Mission-PEO Mapping
# ─────────────────────────────────────────────

class MissionPEOMappingForm(forms.ModelForm):
    class Meta:
        model = MissionPEOMapping
        fields = ['mission_order', 'mission_statement', 'mappings']
        widgets = {
            'mission_order': forms.NumberInput(attrs=W_NUMBER),
            'mission_statement': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 3}),
            'mappings': forms.Textarea(attrs={
                **W_TEXTAREA, 'rows': 2,
                'placeholder': '{"1": 2, "2": 3, "3": 1}'
            }),
        }


MissionPEOMappingFormSet = inlineformset_factory(
    CurriculumVersion, MissionPEOMapping,
    form=MissionPEOMappingForm,
    extra=1, can_delete=True
)


# ─────────────────────────────────────────────
# Program Outcomes
# ─────────────────────────────────────────────

class ProgramOutcomeForm(forms.ModelForm):
    class Meta:
        model = ProgramOutcome
        fields = ['number', 'description']
        widgets = {
            'number': forms.NumberInput(attrs=W_NUMBER),
            'description': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 3}),
        }


ProgramOutcomeFormSet = inlineformset_factory(
    CurriculumVersion, ProgramOutcome,
    form=ProgramOutcomeForm,
    extra=1, can_delete=True
)


# ─────────────────────────────────────────────
# Course Category
# ─────────────────────────────────────────────

class CourseCategoryForm(forms.ModelForm):
    class Meta:
        model = CourseCategory
        fields = ['code', 'name', 'credits_offered', 'min_credits', 'display_order']
        widgets = {
            'code': forms.TextInput(attrs=W_TEXT),
            'name': forms.TextInput(attrs=W_TEXT),
            'credits_offered': forms.NumberInput(attrs=W_NUMBER),
            'min_credits': forms.NumberInput(attrs=W_NUMBER),
            'display_order': forms.NumberInput(attrs=W_NUMBER),
        }


CourseCategoryFormSet = inlineformset_factory(
    CurriculumVersion, CourseCategory,
    form=CourseCategoryForm,
    extra=1, can_delete=True
)


# ─────────────────────────────────────────────
# Semester
# ─────────────────────────────────────────────

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['year', 'semester']
        widgets = {
            'year': forms.Select(attrs=W_SELECT),
            'semester': forms.Select(attrs=W_SELECT),
        }


# ─────────────────────────────────────────────
# Course
# ─────────────────────────────────────────────

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'code', 'title', 'category', 'lectures', 'tutorials',
            'practicals', 'credits', 'is_elective', 'elective_group',
            'prerequisites', 'syllabus_text', 'display_order'
        ]
        widgets = {
            'code': forms.TextInput(attrs=W_TEXT),
            'title': forms.TextInput(attrs=W_TEXT),
            'category': forms.Select(attrs=W_SELECT),
            'lectures': forms.NumberInput(attrs=W_NUMBER),
            'tutorials': forms.NumberInput(attrs=W_NUMBER),
            'practicals': forms.NumberInput(attrs=W_NUMBER),
            'credits': forms.NumberInput(attrs=W_NUMBER),
            'is_elective': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'elective_group': forms.TextInput(attrs=W_TEXT),
            'prerequisites': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
            'syllabus_text': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 8}),
            'display_order': forms.NumberInput(attrs=W_NUMBER),
        }

    def __init__(self, *args, curriculum_version=None, **kwargs):
        super().__init__(*args, **kwargs)
        if curriculum_version:
            self.fields['category'].queryset = CourseCategory.objects.filter(
                curriculum_version=curriculum_version
            )
            # Only allow prerequisites from same curriculum version
            all_courses = Course.objects.filter(
                semester__curriculum_version=curriculum_version
            )
            if self.instance.pk:
                all_courses = all_courses.exclude(pk=self.instance.pk)
            self.fields['prerequisites'].queryset = all_courses
        else:
            self.fields['category'].queryset = CourseCategory.objects.none()
            self.fields['prerequisites'].queryset = Course.objects.none()


# ─────────────────────────────────────────────
# Course Outcomes
# ─────────────────────────────────────────────

class CourseOutcomeForm(forms.ModelForm):
    class Meta:
        model = CourseOutcome
        fields = ['number', 'description']
        widgets = {
            'number': forms.NumberInput(attrs=W_NUMBER),
            'description': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 2}),
        }


CourseOutcomeFormSet = inlineformset_factory(
    Course, CourseOutcome,
    form=CourseOutcomeForm,
    extra=1, can_delete=True
)


# ─────────────────────────────────────────────
# CO-PO Mapping
# ─────────────────────────────────────────────

class COPOMappingForm(forms.ModelForm):
    class Meta:
        model = COPOMapping
        fields = ['mappings']
        widgets = {
            'mappings': forms.Textarea(attrs={
                **W_TEXTAREA, 'rows': 2,
                'placeholder': '{"1": 3, "2": 2, "6": 1}'
            }),
        }


# ─────────────────────────────────────────────
# Reference Books
# ─────────────────────────────────────────────

class ReferenceBookForm(forms.ModelForm):
    class Meta:
        model = ReferenceBook
        fields = ['number', 'citation']
        widgets = {
            'number': forms.NumberInput(attrs=W_NUMBER),
            'citation': forms.Textarea(attrs={**W_TEXTAREA, 'rows': 2}),
        }


ReferenceBookFormSet = inlineformset_factory(
    Course, ReferenceBook,
    form=ReferenceBookForm,
    extra=1, can_delete=True
)


# ─────────────────────────────────────────────
# HOD Review Form for ChangeRequest
# ─────────────────────────────────────────────

class ChangeRequestReviewForm(forms.ModelForm):
    class Meta:
        model = ChangeRequest
        fields = ['hod_comment']
        widgets = {
            'hod_comment': forms.Textarea(attrs={
                **W_TEXTAREA, 'rows': 3,
                'placeholder': 'Optional comment for the faculty...'
            }),
        }
        labels = {
            'hod_comment': 'Comment (optional)',
        }