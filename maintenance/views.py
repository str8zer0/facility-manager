from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from accounts.mixins import ManagerRequiredMixin, TechnicianRequiredMixin
from .models import (
    WorkOrder, WorkOrderComment, WorkOrderAttachment,
    InspectionTemplate, InspectionItem, Inspection, InspectionResult,
)
from .forms import (
    WorkOrderForm, WorkOrderCommentForm, WorkOrderAttachmentForm,
    InspectionTemplateForm, InspectionItemForm,
    InspectionForm, InspectionCompleteForm, InspectionResultFormSet,
)


# ─────────────────────────────────────────────
# Work Order Views
# ─────────────────────────────────────────────

class WorkOrderListView(LoginRequiredMixin, ListView):
    model = WorkOrder
    template_name = "maintenance/workorder_list.html"
    context_object_name = "work_orders"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "building", "room", "asset", "created_by"
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
        from .choices import WorkOrderStatus, WorkOrderPriority
        from accounts.models import User
        context = super().get_context_data(**kwargs)
        context["status_choices"] = WorkOrderStatus.choices
        context["priority_choices"] = WorkOrderPriority.choices
        context["technicians"] = User.objects.filter(
            is_active=True, groups__name__in=["Technician", "Manager", "Admin"]
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
            "building", "room", "asset", "created_by"
        ).prefetch_related("assigned_to", "comments__user", "attachments__uploaded_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = WorkOrderCommentForm()
        context["attachment_form"] = WorkOrderAttachmentForm()
        context["comments"] = self.object.comments.select_related("user").order_by("timestamp")
        context["attachments"] = self.object.attachments.select_related("uploaded_by").order_by("uploaded_at")
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


# ─────────────────────────────────────────────
# Work Order Comment & Attachment Views
# ─────────────────────────────────────────────

class WorkOrderCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        work_order = get_object_or_404(WorkOrder, pk=pk)
        form = WorkOrderCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.work_order = work_order
            comment.user = request.user
            comment.save()
            work_order.log(
                user=request.user,
                action="Comment Added",
                notes=comment.comment[:100],
            )
            messages.success(request, "Comment posted.")
        else:
            messages.error(request, "Failed to post comment.")
        return redirect(reverse("maintenance:workorder_detail", kwargs={"pk": pk}))


class WorkOrderAttachmentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        work_order = get_object_or_404(WorkOrder, pk=pk)
        form = WorkOrderAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.work_order = work_order
            attachment.uploaded_by = request.user
            attachment.save()
            work_order.log(
                user=request.user,
                action="Attachment Added",
                notes=f"File: {attachment.file.name}",
            )
            messages.success(request, "Attachment uploaded.")
        else:
            messages.error(request, "Failed to upload attachment.")
        return redirect(reverse("maintenance:workorder_detail", kwargs={"pk": pk}))


# ─────────────────────────────────────────────
# InspectionTemplate Views
# ─────────────────────────────────────────────

class InspectionTemplateListView(TechnicianRequiredMixin, ListView):
    model = InspectionTemplate
    template_name = "maintenance/inspectiontemplate_list.html"
    context_object_name = "templates"
    paginate_by = 20


class InspectionTemplateDetailView(TechnicianRequiredMixin, DetailView):
    model = InspectionTemplate
    template_name = "maintenance/inspectiontemplate_detail.html"
    context_object_name = "template"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = self.object.items.all()
        context["item_form"] = InspectionItemForm(template=self.object)
        return context


class InspectionTemplateCreateView(ManagerRequiredMixin, CreateView):
    model = InspectionTemplate
    form_class = InspectionTemplateForm
    template_name = "maintenance/inspectiontemplate_form.html"

    def get_success_url(self):
        return reverse_lazy("maintenance:inspectiontemplate_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Template "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class InspectionTemplateUpdateView(ManagerRequiredMixin, UpdateView):
    model = InspectionTemplate
    form_class = InspectionTemplateForm
    template_name = "maintenance/inspectiontemplate_form.html"

    def get_success_url(self):
        return reverse_lazy("maintenance:inspectiontemplate_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Template "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class InspectionTemplateDeleteView(ManagerRequiredMixin, DeleteView):
    model = InspectionTemplate
    template_name = "maintenance/inspectiontemplate_confirm_delete.html"
    context_object_name = "template"
    success_url = reverse_lazy("maintenance:inspectiontemplate_list")

    def form_valid(self, form):
        messages.success(self.request, f'Template "{self.object.name}" deleted.')
        return super().form_valid(form)


# ─────────────────────────────────────────────
# InspectionItem Views
# ─────────────────────────────────────────────

class InspectionItemCreateView(ManagerRequiredMixin, CreateView):
    model = InspectionItem
    form_class = InspectionItemForm
    template_name = "maintenance/inspectionitem_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        template_pk = self.kwargs.get("template_pk")
        if template_pk:
            kwargs["template"] = get_object_or_404(InspectionTemplate, pk=template_pk)
        return kwargs

    def get_success_url(self):
        return reverse_lazy("maintenance:inspectiontemplate_detail", kwargs={"pk": self.object.template.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Item "{form.instance.text}" added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template_pk = self.kwargs.get("template_pk")
        if template_pk:
            context["template"] = get_object_or_404(InspectionTemplate, pk=template_pk)
        context["action"] = "Create"
        return context


class InspectionItemUpdateView(ManagerRequiredMixin, UpdateView):
    model = InspectionItem
    form_class = InspectionItemForm
    template_name = "maintenance/inspectionitem_form.html"

    def get_success_url(self):
        return reverse_lazy("maintenance:inspectiontemplate_detail", kwargs={"pk": self.object.template.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Item "{form.instance.text}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["template"] = self.object.template
        context["action"] = "Edit"
        return context


class InspectionItemDeleteView(ManagerRequiredMixin, DeleteView):
    model = InspectionItem
    template_name = "maintenance/inspectionitem_confirm_delete.html"
    context_object_name = "item"

    def get_success_url(self):
        return reverse_lazy("maintenance:inspectiontemplate_detail", kwargs={"pk": self.object.template.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Item "{self.object.text}" deleted.')
        return super().form_valid(form)


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
            "template", "performed_by", "building", "room", "asset"
        )
        status = self.request.GET.get("status")
        template = self.request.GET.get("template")

        if status:
            qs = qs.filter(status=status)
        if template:
            qs = qs.filter(template__pk=template)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .choices import InspectionStatus
        context["status_choices"] = InspectionStatus.choices
        context["templates"] = InspectionTemplate.objects.filter(is_active=True)
        context["current_filters"] = {
            "status": self.request.GET.get("status", ""),
            "template": self.request.GET.get("template", ""),
        }
        return context


class InspectionDetailView(TechnicianRequiredMixin, DetailView):
    model = Inspection
    template_name = "maintenance/inspection_detail.html"
    context_object_name = "inspection"

    def get_queryset(self):
        return super().get_queryset().select_related(
            "template", "performed_by", "building", "room", "asset"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["results"] = self.object.results_for_inspection.select_related("item").all()
        return context


class InspectionCreateView(TechnicianRequiredMixin, CreateView):
    model = Inspection
    form_class = InspectionForm
    template_name = "maintenance/inspection_form.html"

    def get_success_url(self):
        return reverse_lazy("maintenance:inspection_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Inspection scheduled successfully.')
        return response

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
        messages.success(self.request, "Inspection updated successfully.")
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
        messages.success(self.request, "Inspection deleted.")
        return super().form_valid(form)


class InspectionCompleteView(TechnicianRequiredMixin, View):
    template_name = "maintenance/inspection_complete.html"

    def get_inspection(self, pk):
        return get_object_or_404(
            Inspection.objects.select_related("template"),
            pk=pk
        )

    def _ensure_results_exist(self, inspection):
        """
        Pre-create one InspectionResult per template item if not already present.
        This ensures the formset always has a row for every checklist item.
        """
        existing_item_ids = inspection.results_for_inspection.values_list("item_id", flat=True)
        items_to_create = inspection.template.items.exclude(pk__in=existing_item_ids)
        InspectionResult.objects.bulk_create([
            InspectionResult(inspection=inspection, item=item)
            for item in items_to_create
        ])

    def get(self, request, pk):
        from django.shortcuts import render
        inspection = self.get_inspection(pk)
        self._ensure_results_exist(inspection)
        complete_form = InspectionCompleteForm(instance=inspection)
        formset = InspectionResultFormSet(instance=inspection)
        # Attach the item text to each form for display in the template
        items = list(inspection.template.items.order_by("order"))
        for form, item in zip(formset.forms, items):
            form.item = item
        return render(request, self.template_name, {
            "inspection": inspection,
            "complete_form": complete_form,
            "formset": formset,
        })

    def post(self, request, pk):
        from django.shortcuts import render
        inspection = self.get_inspection(pk)
        self._ensure_results_exist(inspection)
        complete_form = InspectionCompleteForm(request.POST, instance=inspection)
        formset = InspectionResultFormSet(request.POST, request.FILES, instance=inspection)

        if complete_form.is_valid() and formset.is_valid():
            complete_form.save()
            formset.save()
            messages.success(request, "Inspection completed and results saved.")
            return redirect(reverse_lazy("maintenance:inspection_detail", kwargs={"pk": pk}))

        items = list(inspection.template.items.order_by("order"))
        for form, item in zip(formset.forms, items):
            form.item = item
        return render(request, self.template_name, {
            "inspection": inspection,
            "complete_form": complete_form,
            "formset": formset,
        })