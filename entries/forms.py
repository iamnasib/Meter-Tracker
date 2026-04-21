from django import forms

from .models import Entry


class EntryForm(forms.ModelForm):
    # ModelForm ensures clean validation instead of trusting raw POST data.
    class Meta:
        model = Entry
        fields = ["meters", "description"]
        widgets = {
            "meters": forms.NumberInput(
                attrs={
                    "min": "1",
                    "placeholder": "Enter meter value",
                    "class": "w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Optional description",
                    "class": "w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200",
                }
            ),
        }

    def clean_meters(self):
        # Extra explicit validation with user-friendly error text.
        meters = self.cleaned_data.get("meters")
        if meters is None:
            raise forms.ValidationError("Meters is required.")
        if meters <= 0:
            raise forms.ValidationError("Meters must be a positive integer.")
        return meters
