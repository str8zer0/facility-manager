from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.mixins import ManagerRequiredMixin, StaffRequiredMixin
from assets.models import Asset, AssetCategory
from assets.forms import AssetForm, AssetCategoryForm


# ─────────────────────────────────────────────
# AssetCategory Views
# ─────────────────────────────────────────────

class AssetCategoryListView(StaffRequiredMixin, ListView):
    model = AssetCategory
    template_name = "assets/category_list.html"
    context_object_name = "categories"
    paginate_by = 20


class AssetCategoryCreateView(ManagerRequiredMixin, CreateView):
    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = "assets/category_form.html"
    success_url = reverse_lazy("assets:category_list")

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class AssetCategoryUpdateView(ManagerRequiredMixin, UpdateView):
    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = "assets/category_form.html"
    success_url = reverse_lazy("assets:category_list")

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class AssetCategoryDeleteView(ManagerRequiredMixin, DeleteView):
    model = AssetCategory
    template_name = "assets/category_confirm_delete.html"
    context_object_name = "category"
    success_url = reverse_lazy("assets:category_list")

    def form_valid(self, form):
        messages.success(self.request, f'Category "{self.object.name}" deleted.')
        return super().form_valid(form)


# ─────────────────────────────────────────────
# Asset Views
# ─────────────────────────────────────────────

class AssetListView(StaffRequiredMixin, ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related("categories").select_related("room__building", "assigned_to")

        category = self.request.GET.get("category")
        status = self.request.GET.get("status")
        is_active = self.request.GET.get("is_active")

        if category:
            qs = qs.filter(categories__pk=category)
        if status:
            qs = qs.filter(status=status)
        if is_active in ("true", "false"):
            qs = qs.filter(is_active=(is_active == "true"))

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .choices import StatusCode
        context["categories"] = AssetCategory.objects.all()
        context["status_choices"] = StatusCode.choices
        context["current_filters"] = {
            "category": self.request.GET.get("category", ""),
            "status": self.request.GET.get("status", ""),
            "is_active": self.request.GET.get("is_active", ""),
        }
        return context


class AssetDetailView(StaffRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("categories").select_related(
            "room__building", "assigned_to"
        )


class AssetCreateView(ManagerRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.log(
            user=self.request.user,
            action="Created",
            notes=f'Asset "{self.object.name}" created.',
        )
        messages.success(self.request, f'Asset "{self.object.name}" created successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class AssetUpdateView(ManagerRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        changed = form.changed_data
        response = super().form_valid(form)
        self.object.log(
            user=self.request.user,
            action="Updated",
            notes=f'Fields changed: {", ".join(changed)}.' if changed else "No fields changed.",
        )
        messages.success(self.request, f'Asset "{self.object.name}" updated successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class AssetDeleteView(ManagerRequiredMixin, DeleteView):
    model = Asset
    template_name = "assets/asset_confirm_delete.html"
    context_object_name = "asset"
    success_url = reverse_lazy("assets:asset_list")

    def form_valid(self, form):
        self.object.log(
            user=self.request.user,
            action="Deleted",
            notes=f'Asset "{self.object.name}" deleted.',
        )
        messages.success(self.request, f'Asset "{self.object.name}" deleted.')
        return super().form_valid(form)