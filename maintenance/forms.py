from django import forms
from django.forms import inlineformset_factory
from accounts.models import User
from assets.models import Asset
from facilities.models import Building, Room
from maintenance.models import (
    WorkOrder, WorkOrderComment, WorkOrderAttachment,
    InspectionTemplate, InspectionItem, Inspection, InspectionResult,
)


# ─────────────────────────────────────────────
# Work Order Forms
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
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(
            is_active=True,
            groups__name__in=["Technician", "Manager", "Admin"]
        ).order_by("email"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
    )

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


class WorkOrderAttachmentForm(forms.ModelForm):
    class Meta:
        model = WorkOrderAttachment
        fields = ["file"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


# ─────────────────────────────────────────────
# Inspection Template & Item Forms
# ─────────────────────────────────────────────

class InspectionTemplateForm(forms.ModelForm):
    class Meta:
        model = InspectionTemplate
        fields = ["name", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Template name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class InspectionItemForm(forms.ModelForm):
    class Meta:
        model = InspectionItem
        fields = ["template", "text", "order"]
        widgets = {
            "template": forms.Select(attrs={"class": "form-select"}),
            "text": forms.TextInput(attrs={"class": "form-control", "placeholder": "Inspection item description"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, template=None, **kwargs):
        """
        Optional: pass template=<instance> to pre-select and lock the template field.
        Used when adding items from within a template's detail page.
        """
        super().__init__(*args, **kwargs)
        if template is not None:
            self.fields["template"].initial = template
            self.fields["template"].widget.attrs["disabled"] = True
            self.fields["template"].required = False
            self._locked_template = template
        else:
            self._locked_template = None

    def clean_template(self):
        if self._locked_template is not None:
            return self._locked_template
        return self.cleaned_data.get("template")


# ─────────────────────────────────────────────
# Inspection Forms
# ─────────────────────────────────────────────

class InspectionForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=InspectionTemplate.objects.filter(is_active=True).order_by("name"),
        empty_label="— Select template —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
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
            "template", "performed_by", "building", "room", "asset",
            "scheduled_for", "status", "notes",
        ]
        widgets = {
            "scheduled_for": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class InspectionCompleteForm(forms.ModelForm):
    """Used when marking an inspection as completed — captures performed_at and final notes."""
    class Meta:
        model = Inspection
        fields = ["performed_at", "status", "notes"]
        widgets = {
            "performed_at": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class InspectionResultForm(forms.ModelForm):
    class Meta:
        model = InspectionResult
        fields = ["status", "notes", "photo"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


# Inline formset: one InspectionResult per InspectionItem when completing an inspection
InspectionResultFormSet = inlineformset_factory(
    Inspection,
    InspectionResult,
    form=InspectionResultForm,
    extra=0,       # No blank extras — results are pre-created from template items in the view
    can_delete=False,
)