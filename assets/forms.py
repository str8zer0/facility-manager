from django import forms
from .models import Asset, AssetCategory
from accounts.models import User
from facilities.models import Room


class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Category name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class AssetForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=AssetCategory.objects.all().order_by("name"),
        required=True,
        empty_label="— Select category —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.select_related("building").order_by("building__name", "name"),
        required=False,
        empty_label="— No room assigned —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by("email"),
        required=False,
        empty_label="— Unassigned —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Asset
        fields = [
            "name", "category", "room", "tag", "status",
            "serial_number", "manufacturer", "model_number",
            "purchase_date", "installation_date", "warranty_expiration",
            "assigned_to", "is_active", "notes",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Asset name"}),
            "tag": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "serial_number": forms.TextInput(attrs={"class": "form-control"}),
            "manufacturer": forms.TextInput(attrs={"class": "form-control"}),
            "model_number": forms.TextInput(attrs={"class": "form-control"}),
            "purchase_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "installation_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "warranty_expiration": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }