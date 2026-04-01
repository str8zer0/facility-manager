from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
from accounts.models import Profile

User = get_user_model()


# ─────────────────────────────────────────────
# User Forms
# ─────────────────────────────────────────────

class UserRoleForm(UserChangeForm):
    role = forms.ChoiceField(required=False)

    class Meta:
        model = User
        fields = ("email", "role", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load only role groups
        role_groups = Group.objects.filter(name__in=settings.ROLE_GROUPS)
        self.fields["role"].choices = [("", "---------")] + [(g.name, g.name) for g in role_groups]

        # Pre-select current role
        if self.instance and self.instance.pk:
            user_groups = self.instance.groups.filter(name__in=settings.ROLE_GROUPS).values_list("name", flat=True)
            if user_groups:
                self.fields["role"].initial = user_groups[0]

    def save(self, commit=True):
        user = super().save(commit=False)
        selected_role = self.cleaned_data.get("role")

        def save_m2m():
            # Call original _save_m2m
            self._save_m2m()

            # Remove user from all role groups defined in settings
            user.groups.remove(*Group.objects.filter(name__in=settings.ROLE_GROUPS))

            # Assign selected role
            if selected_role:
                try:
                    group = Group.objects.get(name=selected_role)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    pass

        self.save_m2m = save_m2m

        if commit:
            user.save()
            self.save_m2m()
        return user


class UserRoleAddForm(UserCreationForm):
    role = forms.ChoiceField(required=False)

    class Meta:
        model = User
        fields = ("email", "role", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        role_groups = Group.objects.filter(name__in=settings.ROLE_GROUPS)
        self.fields["role"].choices = [("", "---------")] + [(g.name, g.name) for g in role_groups]

    def save(self, commit=True):
        user = super().save(commit=False)
        selected_role = self.cleaned_data.get("role")

        def save_m2m():
            # Call original _save_m2m
            self._save_m2m()

            if selected_role:
                try:
                    group = Group.objects.get(name=selected_role)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    pass

        self.save_m2m = save_m2m

        if commit:
            user.save()
            self.save_m2m()
        return user


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            # Assign default role: Staff
            try:
                staff_group = Group.objects.get(name="Staff")
                user.groups.add(staff_group)
            except Group.DoesNotExist:
                pass

        return user


# ─────────────────────────────────────────────
# Profile Forms
# ─────────────────────────────────────────────

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "department", "job", "phone", "profile_picture"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "job": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class AdminProfileForm(forms.ModelForm):
    """
    Used by Admin to edit another user's profile.
    Identical fields to ProfileForm but scoped separately
    so future admin-only fields can be added without
    affecting the user-facing form.
    """
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "department", "job", "phone", "profile_picture"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "job": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


# ─────────────────────────────────────────────
# Department Forms
# ─────────────────────────────────────────────

class DepartmentForm(forms.ModelForm):
    class Meta:
        from accounts.models import Department
        model = Department
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Department name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


# ─────────────────────────────────────────────
# Job Forms
# ─────────────────────────────────────────────

class JobForm(forms.ModelForm):
    class Meta:
        from accounts.models import Job
        model = Job
        fields = ["title", "description", "department"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Job title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "department": forms.Select(attrs={"class": "form-select"}),
        }