from django import forms
from accounts.models import User
from assets.models import Asset
from facilities.models import Building, Room
from maintenance.models import WorkOrder, WorkOrderComment, Inspection


# ─────────────────────────────────────────────
# WorkOrder Forms
# ─────────────────────────────────────────────

class WorkOrderForm(forms.ModelForm):
    building = forms.ModelChoiceField(
        queryset=Building.objects.all().order_by("name"),
        required=False,
        empty_label="— None —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.select_related("building").order_by("building__name", "name"),
        required=False,
        empty_label="— None —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.filter(is_active=True).order_by("name"),
        required=False,
        empty_label="— None —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(
            is_active=True,
            groups__name__in=["Technician", "Manager", "Admin"]
        ).order_by("email"),
        required=False,
        empty_label="— Unassigned —",
        widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = WorkOrder
        fields = [
            "title", "description", "building", "room", "asset",
            "status", "priority", "assigned_to", "due_date", "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Work order title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

        if user:
            # Technicians — lock assignment to themselves
            if user.groups.filter(name="Technician").exists():
                self.fields["assigned_to"].widget.attrs["disabled"] = True
                self.fields["assigned_to"].required = False

            # Staff — hide assignment entirely, they can't assign work orders
            elif not user.groups.filter(name__in=["Manager", "Admin"]).exists():
                self.fields["assigned_to"].widget = forms.HiddenInput()
                self.fields["assigned_to"].required = False

    def clean_assigned_to(self):
        # Restore locked value for technicians
        if self._user and self._user.groups.filter(name="Technician").exists():
            return self.instance.assigned_to if self.instance.pk else self._user
        return self.cleaned_data.get("assigned_to")

    def clean(self):
        cleaned_data = super().clean()
        if not any([cleaned_data.get("building"), cleaned_data.get("room"), cleaned_data.get("asset")]):
            raise forms.ValidationError("A work order must reference at least a building, room, or asset.")
        return cleaned_data


class WorkOrderCommentForm(forms.ModelForm):
    class Meta:
        model = WorkOrderComment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Add a comment..."}),
        }


# ─────────────────────────────────────────────
# Inspection Form
# ─────────────────────────────────────────────

class InspectionForm(forms.ModelForm):
    performed_by = forms.ModelChoiceField(
        queryset=User.objects.filter(
            is_active=True,
            groups__name__in=["Technician", "Manager", "Admin"]
        ).order_by("email"),
        required=False,
        empty_label="— Unassigned —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    building = forms.ModelChoiceField(
        queryset=Building.objects.all().order_by("name"),
        required=False,
        empty_label="— None —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.select_related("building").order_by("building__name", "name"),
        required=False,
        empty_label="— None —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.filter(is_active=True).order_by("name"),
        required=False,
        empty_label="— None —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Inspection
        fields = [
            "title", "performed_by", "building", "room", "asset",
            "scheduled_for", "performed_at", "status", "findings",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Inspection title"}),
            "scheduled_for": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "performed_at": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "findings": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Describe findings..."}),
        }