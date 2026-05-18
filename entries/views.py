from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LineFormSet, LineFormSetEdit
from .models import Challan, ChallanLine


def _build_summary():
    total_count = Challan.objects.count()
    total_meters = ChallanLine.objects.aggregate(total=Sum("meters")).get("total") or Decimal(
        "0"
    )
    return {
        "total_count": total_count,
        "total_meters": total_meters,
    }


def create_challan_view(request):
    if request.method == "POST":
        formset = LineFormSet(request.POST)
        if formset.is_valid():
            with transaction.atomic():
                challan = Challan.objects.create()
                order = 0
                for form in formset:
                    meters = form.cleaned_data.get("meters")
                    if meters is not None and meters > 0:
                        ChallanLine.objects.create(
                            challan=challan,
                            meters=meters,
                            description=form.cleaned_data.get("description") or "",
                            sort_order=order,
                        )
                        order += 1
            messages.success(request, "Challan saved successfully.")
            return redirect("entries:dashboard")
    else:
        formset = LineFormSet()

    context = {
        "formset": formset,
        **_build_summary(),
    }
    return render(request, "entries/create_challan.html", context)


def dashboard_view(request):
    challan_list = Challan.objects.prefetch_related("lines").order_by("-created_at")
    context = {
        "challans": challan_list,
        **_build_summary(),
    }
    return render(request, "entries/dashboard.html", context)


def challan_detail_view(request, pk):
    challan = get_object_or_404(Challan.objects.prefetch_related("lines"), pk=pk)
    lines = list(challan.lines.all())
    context = {
        "challan": challan,
        "lines": lines,
        "total_count": len(lines),
        "total_meters": challan.total_meters(),
    }
    return render(request, "entries/challan_detail.html", context)


def edit_challan_view(request, pk):
    challan = get_object_or_404(Challan.objects.prefetch_related("lines"), pk=pk)

    if request.method == "POST":
        formset = LineFormSetEdit(request.POST)
        if formset.is_valid():
            with transaction.atomic():
                challan.lines.all().delete()
                order = 0
                for form in formset:
                    meters = form.cleaned_data.get("meters")
                    if meters is not None and meters > 0:
                        ChallanLine.objects.create(
                            challan=challan,
                            meters=meters,
                            description=form.cleaned_data.get("description") or "",
                            sort_order=order,
                        )
                        order += 1
            messages.success(request, "Challan updated successfully.")
            return redirect("entries:challan_detail", pk=challan.pk)
    else:
        initial = [
            {"meters": line.meters, "description": line.description}
            for line in challan.lines.all()
        ]
        if not initial:
            initial = [{}]
        formset = LineFormSetEdit(initial=initial)

    context = {
        "formset": formset,
        "challan": challan,
    }
    return render(request, "entries/edit_challan.html", context)


def delete_challan_view(request, pk):
    challan = get_object_or_404(Challan, pk=pk)
    if request.method == "POST":
        challan.delete()
        messages.success(request, "Challan deleted successfully.")
    return redirect("entries:dashboard")
