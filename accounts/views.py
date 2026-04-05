from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView
from accounts.forms import RegisterForm, ProfileForm, UserRoleAddForm, UserRoleForm, AdminProfileForm
from accounts.mixins import AdminRequiredMixin, ManagerRequiredMixin, TechnicianRequiredMixin, StaffRequiredMixin
from accounts.models import Profile, User


# ─────────────────────────────────────────────
# User Views
# ─────────────────────────────────────────────

class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        from django.contrib import messages
        user = form.get_user()
        if not user.email_verified:
            messages.error(
                self.request,
                "Please verify your email before logging in. "
                '<a href="{}">Resend verification email</a>.'.format(
                    reverse_lazy("accounts:resend_verification")
                )
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        from django.contrib import messages
        response = super().form_valid(form)

        # Send verification email asynchronously
        from accounts.tasks import send_verification_email
        send_verification_email.delay(self.object.pk)
        messages.info(
            self.request,
            "Registration successful. Please check your email to verify your account before logging in."
        )

        return response


class VerifyEmailView(TemplateView):
    template_name = "accounts/verify_email.html"

    def get(self, request, *args, **kwargs):
        from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
        from django.contrib import messages

        token = kwargs.get("token")
        signer = TimestampSigner()

        try:
            # max_age=86400 → 24 hours
            user_pk = signer.unsign(token, max_age=86400)
            from accounts.models import User
            user = User.objects.get(pk=user_pk)

            if not user.email_verified:
                user.email_verified = True
                user.save(update_fields=["email_verified"])
                messages.success(request, "Email verified successfully. You can now log in.")
            else:
                messages.info(request, "Your email is already verified.")

        except SignatureExpired:
            messages.error(request, "Verification link has expired. Please request a new one.")
        except (BadSignature, Exception):
            messages.error(request, "Invalid verification link.")

        return redirect(reverse_lazy("accounts:login"))


class ResendVerificationView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/resend_verification.html"

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        from accounts.tasks import send_verification_email

        if request.user.email_verified:
            messages.info(request, "Your email is already verified.")
        else:
            send_verification_email.delay(request.user.pk)
            messages.success(request, "Verification email sent. Please check your inbox.")

        return redirect(reverse_lazy("accounts:profile"))


# ─────────────────────────────────────────────
# Profile Views
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# Dashboard Router
# ─────────────────────────────────────────────

class DashboardRouterView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_superuser or user.groups.filter(name="Admin").exists():
            return redirect("accounts:dashboard_admin")

        if user.groups.filter(name="Manager").exists():
            return redirect("accounts:dashboard_manager")

        if user.groups.filter(name="Technician").exists():
            return redirect("accounts:dashboard_technician")

        if user.groups.filter(name="Staff").exists():
            return redirect("accounts:dashboard_staff")

        # No role assigned → this is a configuration error
        raise PermissionDenied("User has no assigned role.")


# ─────────────────────────────────────────────
# Admin Dashboard
# ─────────────────────────────────────────────

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/dashboard_admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from common.models import History
        from django.contrib.auth.models import Group

        context["recent_logs"] = (
            History.objects
            .select_related("user", "content_type")
            .all()[:50]
        )
        context["users"] = (
            User.objects
            .prefetch_related("groups", "profile")
            .filter(is_active=True)
            .order_by("email")
        )
        context["inactive_users"] = (
            User.objects
            .filter(is_active=False)
            .order_by("email")
        )
        context["groups"] = Group.objects.all()
        context["total_users"] = User.objects.filter(is_active=True).count()
        context["users_no_role"] = (
            User.objects
            .filter(is_active=True, groups__isnull=True, is_superuser=False)
            .count()
        )

        # Log counts per action type
        from django.db.models import Count
        context["log_summary"] = (
            History.objects
            .values("action")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        return context


# ─────────────────────────────────────────────
# Manager Dashboard
# ─────────────────────────────────────────────

class ManagerDashboardView(ManagerRequiredMixin, TemplateView):
    template_name = "accounts/dashboard_manager.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from maintenance.models import WorkOrder, Inspection
        from maintenance.choices import WorkOrderStatus, WorkOrderPriority, InspectionStatus
        from assets.models import Asset
        from inventory.models import SparePart
        from django.db.models import Count, F

        # Work order stats
        context["workorder_status_summary"] = (
            WorkOrder.objects
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        context["open_work_orders"] = (
            WorkOrder.objects
            .filter(status=WorkOrderStatus.OPEN)
            .select_related("building", "room", "asset", "assigned_to")
            .order_by("priority")[:10]
        )
        context["critical_work_orders"] = (
            WorkOrder.objects
            .filter(priority=WorkOrderPriority.CRITICAL, is_active=True)
            .exclude(status=WorkOrderStatus.COMPLETED)
            .select_related("building", "room", "asset", "assigned_to")
        )

        # Inspection stats
        context["upcoming_inspections"] = (
            Inspection.objects
            .filter(status=InspectionStatus.SCHEDULED)
            .select_related("performed_by", "building", "room", "asset")
            .order_by("scheduled_for")[:10]
        )

        # Staff overview
        context["staff"] = (
            User.objects
            .filter(is_active=True, groups__name__in=["Technician", "Staff"])
            .prefetch_related("groups", "profile__department", "profile__job")
            .order_by("email")
        )
        context["technicians"] = (
            User.objects
            .filter(is_active=True, groups__name="Technician")
            .prefetch_related("profile")
            .annotate(assigned_count=Count("assigned_work_orders"))
        )

        # Low stock alerts
        context["low_stock_parts"] = (
            SparePart.objects
            .filter(quantity__lte=F("minimum_quantity"))
            .select_related("supplier")
        )

        # Asset stats
        context["total_assets"] = Asset.objects.filter(is_active=True).count()
        context["assets_under_maintenance"] = (
            Asset.objects
            .filter(status__in=["501", "502"])
            .count()
        )

        return context


# ─────────────────────────────────────────────
# Technician Dashboard
# ─────────────────────────────────────────────

class TechnicianDashboardView(TechnicianRequiredMixin, TemplateView):
    template_name = "accounts/dashboard_technician.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from maintenance.models import WorkOrder, Inspection
        from maintenance.choices import WorkOrderStatus, InspectionStatus
        from inventory.models import SparePart
        from django.db.models import F
        from django.utils import timezone

        user = self.request.user

        # Work orders assigned to this technician
        context["my_work_orders"] = (
            WorkOrder.objects
            .filter(assigned_to=user, is_active=True)
            .exclude(status=WorkOrderStatus.COMPLETED)
            .select_related("building", "room", "asset")
            .order_by("priority")
        )
        context["my_completed_work_orders"] = (
            WorkOrder.objects
            .filter(assigned_to=user, status=WorkOrderStatus.COMPLETED)
            .select_related("building", "room", "asset")
            .order_by("-updated_at")[:5]
        )

        # Work orders created by this technician
        context["created_work_orders"] = (
            WorkOrder.objects
            .filter(created_by=user, is_active=True)
            .exclude(status=WorkOrderStatus.COMPLETED)
            .select_related("building", "room", "asset")
            .order_by("-created_at")[:5]
        )

        # Inspections assigned to this technician
        context["my_inspections"] = (
            Inspection.objects
            .filter(performed_by=user)
            .exclude(status=InspectionStatus.COMPLETED)
            .select_related("building", "room", "asset")
            .order_by("scheduled_for")
        )
        context["overdue_inspections"] = (
            Inspection.objects
            .filter(
                performed_by=user,
                status=InspectionStatus.SCHEDULED,
                scheduled_for__lt=timezone.now().date()
            )
            .select_related("building", "room", "asset")
        )

        # Low stock alerts
        context["low_stock_parts"] = (
            SparePart.objects
            .filter(quantity__lte=F("minimum_quantity"))
            .select_related("supplier")
        )

        # Counts
        context["open_count"] = context["my_work_orders"].filter(status=WorkOrderStatus.OPEN).count()
        context["in_progress_count"] = context["my_work_orders"].filter(status=WorkOrderStatus.IN_PROGRESS).count()

        return context


# ─────────────────────────────────────────────
# Staff Dashboard
# ─────────────────────────────────────────────

class StaffDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "accounts/dashboard_staff.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from maintenance.models import WorkOrder
        from maintenance.choices import WorkOrderStatus
        from facilities.models import Building
        from assets.models import Asset

        user = self.request.user

        # Work orders this staff member created
        context["my_work_orders"] = (
            WorkOrder.objects
            .filter(created_by=user)
            .select_related("building", "room", "asset")
            .order_by("-created_at")[:10]
        )
        context["my_open_work_orders"] = (
            WorkOrder.objects
            .filter(created_by=user)
            .exclude(status__in=[WorkOrderStatus.COMPLETED, WorkOrderStatus.CANCELLED])
            .select_related("building", "room", "asset")
        )

        # General facility overview
        context["total_buildings"] = Building.objects.count()
        context["total_assets"] = Asset.objects.filter(is_active=True).count()

        return context


# ─────────────────────────────────────────────
# Department Views
# ─────────────────────────────────────────────

class DepartmentListView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/department_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import Department
        context["departments"] = Department.objects.prefetch_related("jobs").order_by("name")
        return context


class DepartmentCreateView(AdminRequiredMixin, CreateView):
    model = None
    template_name = "accounts/department_form.html"
    success_url = reverse_lazy("accounts:department_list")

    def setup(self, request, *args, **kwargs):
        from accounts.models import Department
        self.model = Department
        super().setup(request, *args, **kwargs)

    def get_form_class(self):
        from accounts.forms import DepartmentForm
        return DepartmentForm

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, f'Department "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class DepartmentUpdateView(AdminRequiredMixin, UpdateView):
    model = None
    template_name = "accounts/department_form.html"
    success_url = reverse_lazy("accounts:department_list")

    def setup(self, request, *args, **kwargs):
        from accounts.models import Department
        self.model = Department
        super().setup(request, *args, **kwargs)

    def get_form_class(self):
        from accounts.forms import DepartmentForm
        return DepartmentForm

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, f'Department "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class DepartmentDeleteView(AdminRequiredMixin, DeleteView):
    model = None
    template_name = "accounts/department_confirm_delete.html"
    context_object_name = "department"
    success_url = reverse_lazy("accounts:department_list")

    def setup(self, request, *args, **kwargs):
        from accounts.models import Department
        self.model = Department
        super().setup(request, *args, **kwargs)

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, f'Department "{self.object.name}" deleted.')
        return super().form_valid(form)


# ─────────────────────────────────────────────
# Job Views
# ─────────────────────────────────────────────

class JobListView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/job_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import Job
        context["jobs"] = Job.objects.select_related("department").order_by("department__name", "title")
        return context


class JobCreateView(AdminRequiredMixin, CreateView):
    model = None
    template_name = "accounts/job_form.html"
    success_url = reverse_lazy("accounts:job_list")

    def setup(self, request, *args, **kwargs):
        from accounts.models import Job
        self.model = Job
        super().setup(request, *args, **kwargs)

    def get_form_class(self):
        from accounts.forms import JobForm
        return JobForm

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, f'Job "{form.instance.title}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class JobUpdateView(AdminRequiredMixin, UpdateView):
    model = None
    template_name = "accounts/job_form.html"
    success_url = reverse_lazy("accounts:job_list")

    def setup(self, request, *args, **kwargs):
        from accounts.models import Job
        self.model = Job
        super().setup(request, *args, **kwargs)

    def get_form_class(self):
        from accounts.forms import JobForm
        return JobForm

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, f'Job "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class JobDeleteView(AdminRequiredMixin, DeleteView):
    model = None
    template_name = "accounts/job_confirm_delete.html"
    context_object_name = "job"
    success_url = reverse_lazy("accounts:job_list")

    def setup(self, request, *args, **kwargs):
        from accounts.models import Job
        self.model = Job
        super().setup(request, *args, **kwargs)

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, f'Job "{self.object.title}" deleted.')
        return super().form_valid(form)


# ─────────────────────────────────────────────
# Admin User Management Views
# ─────────────────────────────────────────────

class UserListView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/user_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth.models import Group
        context["active_users"] = (
            User.objects
            .filter(is_active=True)
            .prefetch_related("groups", "profile")
            .order_by("email")
        )
        context["inactive_users"] = (
            User.objects
            .filter(is_active=False)
            .prefetch_related("groups", "profile")
            .order_by("email")
        )
        context["groups"] = Group.objects.all()
        return context


class UserDetailView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/user_detail.html"

    def get_object(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            User.objects.prefetch_related("groups", "profile__department", "profile__job"),
            pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = self.get_object()
        context["target_user"] = target_user
        context["profile"] = target_user.profile
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserRoleAddForm
    template_name = "accounts/user_form.html"

    def get_success_url(self):
        return reverse_lazy("accounts:user_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        from django.contrib import messages
        response = super().form_valid(form)
        messages.success(self.request, f'User "{self.object.email}" created successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class UserRoleUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserRoleForm
    template_name = "accounts/user_form.html"

    def get_success_url(self):
        return reverse_lazy("accounts:user_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, f'User "{self.object.email}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        context["target_user"] = self.object
        return context


class UserProfileUpdateView(AdminRequiredMixin, UpdateView):
    model = Profile
    form_class = AdminProfileForm
    template_name = "accounts/user_profile_form.html"

    def get_object(self, queryset=None):
        from django.shortcuts import get_object_or_404
        target_user = get_object_or_404(User, pk=self.kwargs["pk"])
        return target_user.profile

    def get_success_url(self):
        return reverse_lazy("accounts:user_detail", kwargs={"pk": self.kwargs["pk"]})

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.shortcuts import get_object_or_404
        context["target_user"] = get_object_or_404(User, pk=self.kwargs["pk"])
        return context


class UserDeactivateView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/user_confirm_deactivate.html"

    def get_object(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(User, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["target_user"] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        target_user = self.get_object()

        # Prevent admin from deactivating themselves
        if target_user == request.user:
            messages.error(request, "You cannot deactivate your own account.")
            return redirect(reverse_lazy("accounts:user_detail", kwargs={"pk": target_user.pk}))

        target_user.is_active = not target_user.is_active
        target_user.save()
        status = "activated" if target_user.is_active else "deactivated"
        messages.success(request, f'User "{target_user.email}" {status} successfully.')
        return redirect(reverse_lazy("accounts:user_list"))