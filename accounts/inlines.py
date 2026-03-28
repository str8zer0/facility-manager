from django.contrib import admin
from accounts.models import Profile, Job


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fk_name = "user"


class JobInline(admin.TabularInline):
    model = Job
    extra = 1
    show_change_link = True
