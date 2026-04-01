from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from accounts.mixins import ManagerRequiredMixin, TechnicianRequiredMixin
from maintenance.choices import InspectionStatus
from maintenance.models import WorkOrder, WorkOrderComment, Inspection
from maintenance.forms import WorkOrderForm, WorkOrderCommentForm, InspectionForm


# ─────────────────────────────────────────────
# WorkOrder Views
# ─────────────────────────────────────────────

class WorkOrderListView(LoginRequiredMixin, ListView):
    model = WorkOrder
    template_name = "maintenance/workorder_list.html"
    context_object_name = "work_orders"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "building", "room", "asset", "created_by", "assigned_to"
        )
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        assigned_to = self.request.GET.get("assigned_to")

        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if assigned_to:
            qs = qs.filter(assigned_to__pk=assigned_to)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .choices import WorkOrderStatus, WorkOrderPriority
        from accounts.models import User
        context["status_choices"] = WorkOrderStatus.choices
        context["priority_choices"] = WorkOrderPriority.choices
        context["staff_members"] = User.objects.filter(
            is_active=True,
            groups__name__in=["Technician", "Manager", "Admin"]
        ).order_by("email")
        context["current_filters"] = {
            "status": self.request.GET.get("status", ""),
            "priority": self.request.GET.get("priority", ""),
            "assigned_to": self.request.GET.get("assigned_to", ""),
        }
        return context


class WorkOrderDetailView(LoginRequiredMixin, DetailView):
    model = WorkOrder
    template_name = "maintenance/workorder_detail.html"
    context_object_name = "work_order"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "building", "room", "asset", "created_by", "assigned_to"
        ).prefetch_related("comments__user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = WorkOrderCommentForm()
        context["comments"] = self.object.comments.select_related("user").all()
        return context


class WorkOrderCreateView(LoginRequiredMixin, CreateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = "maintenance/workorder_form.html"

    def get_success_url(self):
        return reverse_lazy("maintenance:workorder_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        self.object.log(
            user=self.request.user,
            action="Created",
            notes=f'Work order "{self.object.title}" created.',
        )
        messages.success(self.request, f'Work order "{self.object.title}" created successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class WorkOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = "maintenance/workorder_form.html"

    def get_success_url(self):
        return reverse_lazy("maintenance:workorder_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        changed = form.changed_data
        response = super().form_valid(form)
        self.object.log(
            user=self.request.user,
            action="Updated",
            notes=f'Fields changed: {", ".join(changed)}.' if changed else "No fields changed.",
        )
        messages.success(self.request, f'Work order "{self.object.title}" updated successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class WorkOrderDeleteView(ManagerRequiredMixin, DeleteView):
    model = WorkOrder
    template_name = "maintenance/workorder_confirm_delete.html"
    context_object_name = "work_order"
    success_url = reverse_lazy("maintenance:workorder_list")

    def form_valid(self, form):
        messages.success(self.request, f'Work order "{self.object.title}" deleted.')
        return super().form_valid(form)


class WorkOrderCommentCreateView(LoginRequiredMixin, CreateView):
    model = WorkOrderComment
    form_class = WorkOrderCommentForm

    def get_work_order(self):
        return get_object_or_404(WorkOrder, pk=self.kwargs["work_order_pk"])

    def form_valid(self, form):
        form.instance.work_order = self.get_work_order()
        form.instance.user = self.request.user
        messages.success(self.request, "Comment added.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("maintenance:workorder_detail", kwargs={"pk": self.kwargs["work_order_pk"]})

    def form_invalid(self, form):
        messages.error(self.request, "Comment could not be saved. Please try again.")
        return redirect(reverse_lazy("maintenance:workorder_detail", kwargs={"pk": self.kwargs["work_order_pk"]}))


# ─────────────────────────────────────────────
# Inspection Views
# ─────────────────────────────────────────────

class InspectionListView(TechnicianRequiredMixin, ListView):
    model = Inspection
    template_name = "maintenance/inspection_list.html"
    context_object_name = "inspections"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "performed_by", "building", "room", "asset"
        )
        status = self.request.GET.get("status")
        performed_by = self.request.GET.get("performed_by")
        if status:
            qs = qs.filter(status=status)
        if performed_by:
            qs = qs.filter(performed_by__pk=performed_by)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        context["status_choices"] = InspectionStatus.choices
        context["staff_members"] = User.objects.filter(
            is_active=True,
            groups__name__in=["Technician", "Manager", "Admin"]
        ).order_by("email")
        context["current_filters"] = {
            "status": self.request.GET.get("status", ""),
            "performed_by": self.request.GET.get("performed_by", ""),
        }
        return context


class InspectionDetailView(TechnicianRequiredMixin, DetailView):
    model = Inspection
    template_name = "maintenance/inspection_detail.html"
    context_object_name = "inspection"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "performed_by", "building", "room", "asset"
        )


class InspectionCreateView(TechnicianRequiredMixin, CreateView):
    model = Inspection
    form_class = InspectionForm
    template_name = "maintenance/inspection_form.html"

    def get_success_url(self):
        return reverse_lazy("maintenance:inspection_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Inspection "{self.object.title}" scheduled successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Schedule"
        return context


class InspectionUpdateView(TechnicianRequiredMixin, UpdateView):
    model = Inspection
    form_class = InspectionForm
    template_name = "maintenance/inspection_form.html"

    def get_success_url(self):
        return reverse_lazy("maintenance:inspection_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Inspection "{self.object.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class InspectionDeleteView(ManagerRequiredMixin, DeleteView):
    model = Inspection
    template_name = "maintenance/inspection_confirm_delete.html"
    context_object_name = "inspection"
    success_url = reverse_lazy("maintenance:inspection_list")

    def form_valid(self, form):
        messages.success(self.request, f'Inspection "{self.object.title}" deleted.')
        return super().form_valid(form)