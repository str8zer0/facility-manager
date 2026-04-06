from django.db.models import F
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from accounts.mixins import TechnicianRequiredMixin, ManagerRequiredMixin
from inventory.choices import Reason
from inventory.models import Supplier, SparePart, StockMovement
from inventory.forms import SupplierForm, SparePartForm, StockMovementForm


# ─────────────────────────────────────────────
# Supplier Views
# ─────────────────────────────────────────────

class SupplierListView(TechnicianRequiredMixin, ListView):
    model = Supplier
    template_name = "inventory/supplier_list.html"
    context_object_name = "suppliers"
    paginate_by = 20


class SupplierDetailView(TechnicianRequiredMixin, DetailView):
    model = Supplier
    template_name = "inventory/supplier_detail.html"
    context_object_name = "supplier"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parts"] = self.object.spare_parts.all()
        return context


class SupplierCreateView(TechnicianRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/supplier_form.html"

    def get_success_url(self):
        return reverse_lazy("inventory:supplier_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Supplier "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class SupplierUpdateView(TechnicianRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/supplier_form.html"

    def get_success_url(self):
        return reverse_lazy("inventory:supplier_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Supplier "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class SupplierDeleteView(ManagerRequiredMixin, DeleteView):
    model = Supplier
    template_name = "inventory/supplier_confirm_delete.html"
    context_object_name = "supplier"
    success_url = reverse_lazy("inventory:supplier_list")

    def form_valid(self, form):
        messages.success(self.request, f'Supplier "{self.object.name}" deleted.')
        return super().form_valid(form)


# ─────────────────────────────────────────────
# SparePart Views
# ─────────────────────────────────────────────

class SparePartListView(TechnicianRequiredMixin, ListView):
    model = SparePart
    template_name = "inventory/sparepart_list.html"
    context_object_name = "parts"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("supplier")
        supplier = self.request.GET.get("supplier")
        low_stock = self.request.GET.get("low_stock")

        if supplier:
            qs = qs.filter(supplier__pk=supplier)
        if low_stock == "true":
            qs = qs.filter(quantity__lte=F("minimum_quantity"))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["suppliers"] = Supplier.objects.all()
        context["current_filters"] = {
            "supplier": self.request.GET.get("supplier", ""),
            "low_stock": self.request.GET.get("low_stock", ""),
        }
        return context


class SparePartDetailView(TechnicianRequiredMixin, DetailView):
    model = SparePart
    template_name = "inventory/sparepart_detail.html"
    context_object_name = "sparepart"

    def get_queryset(self):
        return super().get_queryset().select_related("supplier")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movements"] = self.object.movements.select_related("work_order").all()[:20]
        context["movement_form"] = StockMovementForm(part=self.object)
        context["is_low_stock"] = self.object.quantity <= self.object.minimum_quantity
        return context


class SparePartCreateView(TechnicianRequiredMixin, CreateView):
    model = SparePart
    form_class = SparePartForm
    template_name = "inventory/sparepart_form.html"

    def get_success_url(self):
        return reverse_lazy("inventory:sparepart_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Spare part "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class SparePartUpdateView(TechnicianRequiredMixin, UpdateView):
    model = SparePart
    form_class = SparePartForm
    template_name = "inventory/sparepart_form.html"

    def get_success_url(self):
        return reverse_lazy("inventory:sparepart_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Spare part "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class SparePartDeleteView(ManagerRequiredMixin, DeleteView):
    model = SparePart
    template_name = "inventory/sparepart_confirm_delete.html"
    context_object_name = "part"
    success_url = reverse_lazy("inventory:sparepart_list")

    def form_valid(self, form):
        messages.success(self.request, f'Spare part "{self.object.name}" deleted.')
        return super().form_valid(form)


# ─────────────────────────────────────────────
# StockMovement Views
# ─────────────────────────────────────────────

class StockMovementCreateView(TechnicianRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = "inventory/movement_form.html"

    def get_part(self):
        part_pk = self.kwargs.get("part_pk") or self.request.GET.get("part")
        if part_pk:
            return get_object_or_404(SparePart, pk=part_pk)
        return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["part"] = self.get_part()
        return kwargs

    def form_valid(self, form):
        part = self.get_part()
        if part:
            form.instance.part = part
            # Update the stock quantity
            part.quantity += form.instance.change
            part.save()
        messages.success(self.request, "Stock movement logged successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("inventory:sparepart_detail", kwargs={"pk": self.object.part.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["part"] = self.get_part()
        return context


class StockMovementListView(TechnicianRequiredMixin, ListView):
    model = StockMovement
    template_name = "inventory/movement_list.html"
    context_object_name = "movements"
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset().select_related("part", "work_order")
        part = self.request.GET.get("part")
        reason = self.request.GET.get("reason")

        if part:
            qs = qs.filter(part__pk=part)
        if reason:
            qs = qs.filter(reason=reason)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parts"] = SparePart.objects.all()
        context["reason_choices"] = Reason.choices
        context["current_filters"] = {
            "part": self.request.GET.get("part", ""),
            "reason": self.request.GET.get("reason", ""),
        }
        return context