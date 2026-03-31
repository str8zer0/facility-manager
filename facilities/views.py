from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.mixins import ManagerRequiredMixin, StaffRequiredMixin
from .models import Building, Room
from .forms import BuildingForm, RoomForm


# ─────────────────────────────────────────────
# Building Views
# ─────────────────────────────────────────────

class BuildingListView(StaffRequiredMixin, ListView):
    model = Building
    template_name = "facilities/building_list.html"
    context_object_name = "buildings"
    paginate_by = 20


class BuildingDetailView(StaffRequiredMixin, DetailView):
    model = Building
    template_name = "facilities/building_detail.html"
    context_object_name = "building"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rooms"] = self.object.rooms.all()
        context["room_form"] = RoomForm(building=self.object)
        return context


class BuildingCreateView(ManagerRequiredMixin, CreateView):
    model = Building
    form_class = BuildingForm
    template_name = "facilities/building_form.html"

    def get_success_url(self):
        return reverse_lazy("facilities:building_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Building "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class BuildingUpdateView(ManagerRequiredMixin, UpdateView):
    model = Building
    form_class = BuildingForm
    template_name = "facilities/building_form.html"

    def get_success_url(self):
        return reverse_lazy("facilities:building_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Building "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class BuildingDeleteView(ManagerRequiredMixin, DeleteView):
    model = Building
    template_name = "facilities/building_confirm_delete.html"
    context_object_name = "building"
    success_url = reverse_lazy("facilities:building_list")

    def form_valid(self, form):
        messages.success(self.request, f'Building "{self.object.name}" deleted.')
        return super().form_valid(form)


# ─────────────────────────────────────────────
# Room Views
# ─────────────────────────────────────────────

class RoomListView(StaffRequiredMixin, ListView):
    model = Room
    template_name = "facilities/room_list.html"
    context_object_name = "rooms"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("building")
        building_pk = self.request.GET.get("building")
        if building_pk:
            qs = qs.filter(building__pk=building_pk)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["buildings"] = Building.objects.all()
        context["selected_building"] = self.request.GET.get("building", "")
        return context


class RoomDetailView(StaffRequiredMixin, DetailView):
    model = Room
    template_name = "facilities/room_detail.html"
    context_object_name = "room"

    def get_queryset(self):
        return super().get_queryset().select_related("building")


class RoomCreateView(ManagerRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = "facilities/room_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pre-lock the building if coming from a building detail page
        building_pk = self.request.GET.get("building")
        if building_pk:
            try:
                kwargs["building"] = Building.objects.get(pk=building_pk)
            except Building.DoesNotExist:
                pass
        return kwargs

    def get_success_url(self):
        return reverse_lazy("facilities:room_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Room "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class RoomUpdateView(ManagerRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = "facilities/room_form.html"

    def get_success_url(self):
        return reverse_lazy("facilities:room_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Room "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context


class RoomDeleteView(ManagerRequiredMixin, DeleteView):
    model = Room
    template_name = "facilities/room_confirm_delete.html"
    context_object_name = "room"

    def get_success_url(self):
        return reverse_lazy("facilities:building_detail", kwargs={"pk": self.object.building.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Room "{self.object.name}" deleted.')
        return super().form_valid(form)
