from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Department, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_department', 'is_active')
    list_select_related = ('profile',)

    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else '-'
    get_role.short_description = 'Role'

    def get_department(self, obj):
        if hasattr(obj, 'profile') and obj.profile.department:
            return obj.profile.department.code
        return '-'
    get_department.short_description = 'Department'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'degree', 'get_hod', 'created_at')
    search_fields = ('name', 'code')

    def get_hod(self, obj):
        hod = obj.get_hod()
        return hod.get_full_name() if hod else 'Not assigned'
    get_hod.short_description = 'HOD'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)