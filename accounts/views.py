from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from accounts.forms import RegisterForm, ProfileForm
from accounts.mixins import AdminRequiredMixin, ManagerRequiredMixin, TechnicianRequiredMixin, StaffRequiredMixin
from accounts.models import Profile


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("accounts:dashboard")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse_lazy("accounts:profile")


class DashboardRouterView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_superuser:
            return redirect("accounts:dashboard_admin")

        if user.groups.filter(name="Admin").exists():
            return redirect("accounts:dashboard_admin")

        if user.groups.filter(name="Manager").exists():
            return redirect("accounts:dashboard_manager")

        if user.groups.filter(name="Technician").exists():
            return redirect("accounts:dashboard_technician")

        if user.groups.filter(name="Staff").exists():
            return redirect("accounts:dashboard_staff")

        # No role assigned → this is a configuration error
        raise PermissionDenied("User has no assigned role.")


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/dashboard_admin.html"


class ManagerDashboardView(ManagerRequiredMixin, TemplateView):
    template_name = "accounts/dashboard_manager.html"


class TechnicianDashboardView(TechnicianRequiredMixin, TemplateView):
    template_name = "accounts/dashboard_technician.html"


class StaffDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "accounts/dashboard_staff.html"