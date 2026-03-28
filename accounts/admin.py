from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.inlines import ProfileInline, JobInline
from accounts.models import User, Department, Job
from accounts.forms import UserRoleForm, UserRoleAddForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = UserRoleForm
    add_form = UserRoleAddForm
    inlines = [ProfileInline]

    list_display = ('email', 'get_role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('email',)
    readonly_fields = ("date_joined",)
    ordering = ('email',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.get_add_fieldsets(request)

        if request.user.is_superuser:
            return (
            (None, {'fields': ('email', 'password')}),
            ('Role', {'fields': ('role',)}),
            ('Permissions', {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'user_permissions',
                )
            }),
            ('Important dates', {'fields': ('date_joined',)}),
        )

        return (
            (None, {'fields': ('email', 'password')}),
            ('Role', {'fields': ('role',)}),
            ('Permissions', {
                'fields': (
                    'is_active',
                )
            }),
            ('Important dates', {'fields': ('date_joined',)}),
        )


    # Same for add_fieldsets
    def get_add_fieldsets(self, request):
        return (
            (None, {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2', 'role', 'is_active'),
            }),
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def get_role(self, obj):
        groups = obj.groups.filter(name__in=settings.ROLE_GROUPS).values_list("name", flat=True)
        return groups[0] if groups else "-"
    get_role.short_description = "Role"

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    inlines = [JobInline]

    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "description")
    list_filter = ("department",)
    search_fields = ("title",)
    ordering = ("title",)
