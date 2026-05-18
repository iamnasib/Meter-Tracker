from decimal import Decimal

from django import forms
from django.forms import BaseFormSet, formset_factory


class LineForm(forms.Form):
    meters = forms.DecimalField(
        required=False,
        min_value=Decimal("0.01"),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "min": "0.01",
                "step": "any",
                "placeholder": "Meters",
                "class": "line-input w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200",
                "data-line-input": "meters",
            }
        ),
    )
    description = forms.CharField(
        required=False,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Optional description",
                "class": "line-input w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200",
                "data-line-input": "description",
            }
        ),
    )

    def clean(self):
        cleaned = super().clean()
        meters = cleaned.get("meters")
        description = (cleaned.get("description") or "").strip()
        cleaned["description"] = description
        if meters is not None and meters > 0:
            return cleaned
        if description:
            raise forms.ValidationError(
                "Enter a positive meter value for each line that has a description."
            )
        return cleaned


class BaseLineFormSet(BaseFormSet):
    def clean(self):
        super().clean()
        lines_with_meters = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            data = form.cleaned_data
            if not data:
                continue
            meters = data.get("meters")
            if meters is not None and meters > 0:
                lines_with_meters += 1
        if lines_with_meters == 0:
            raise forms.ValidationError(
                "Add at least one line with meters before saving the challan."
            )


LineFormSet = formset_factory(
    LineForm,
    formset=BaseLineFormSet,
    extra=1,
    max_num=500,
    absolute_max=500,
)

LineFormSetEdit = formset_factory(
    LineForm,
    formset=BaseLineFormSet,
    extra=0,
    max_num=500,
    absolute_max=500,
)
