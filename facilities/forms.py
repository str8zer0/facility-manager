from django import forms
from accounts.models import User
from facilities.models import Building, Room


class BuildingForm(forms.ModelForm):
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True, groups__name="Manager").order_by("email"),
        required=False,
        empty_label="— No manager —",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Building
        fields = ["name", "address", "description", "manager"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Building name"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Street address"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["name", "floor", "description", "building"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Room name"}),
            "floor": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Floor number"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "building": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, building=None, **kwargs):
        """
        Optional: pass building=<instance> to pre-select and lock the building field.
        Used when creating a Room from within a Building's detail page.
        """
        super().__init__(*args, **kwargs)
        if building is not None:
            self.fields["building"].initial = building
            self.fields["building"].widget.attrs["disabled"] = True
            self.fields["building"].required = False
            self._locked_building = building
        else:
            self._locked_building = None

    def clean_building(self):
        """Restore locked building value even if the field was disabled."""
        if self._locked_building is not None:
            return self._locked_building
        return self.cleaned_data.get("building")