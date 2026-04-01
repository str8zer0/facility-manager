from django import forms
from inventory.models import Supplier, SparePart, StockMovement
from inventory.choices import Reason
from maintenance.models import WorkOrder


# ─────────────────────────────────────────────
# Supplier Form
# ─────────────────────────────────────────────

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_email", "phone"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Supplier name"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "contact@example.com"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
        }


# ─────────────────────────────────────────────
# SparePart Form
# ─────────────────────────────────────────────

class SparePartForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all().order_by("name"),
        required=False,
        empty_label="— No supplier —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = SparePart
        fields = ["name", "part_number", "supplier", "quantity", "minimum_quantity"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Part name"}),
            "part_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Part number"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "minimum_quantity": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }


# ─────────────────────────────────────────────
# StockMovement Form
# ─────────────────────────────────────────────

class StockMovementForm(forms.ModelForm):
    work_order = forms.ModelChoiceField(
        queryset=WorkOrder.objects.filter(is_active=True).order_by("-created_at"),
        required=False,
        empty_label="— Not linked to a work order —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = StockMovement
        fields = ["change", "reason", "work_order"]
        widgets = {
            "change": forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 5 or -3"}),
            "reason": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, part=None, **kwargs):
        """
        Optional: pass part=<instance> to bind the movement to a specific spare part.
        Used when logging a movement from the SparePart detail page.
        """
        super().__init__(*args, **kwargs)
        self._part = part

    def clean(self):
        cleaned_data = super().clean()
        reason = cleaned_data.get("reason")
        work_order = cleaned_data.get("work_order")
        change = cleaned_data.get("change")

        if reason == Reason.USED_IN_WORK_ORDER and not work_order:
            raise forms.ValidationError("A work order must be selected when reason is 'Used in Work Order'.")

        if change == 0:
            raise forms.ValidationError("Stock change cannot be zero.")

        return cleaned_data