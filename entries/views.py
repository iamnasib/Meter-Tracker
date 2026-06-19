from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ChallanComposeForm, challan_initial_from_instance, default_challan_initial
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
        form = ChallanComposeForm(data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, "Challan saved successfully.")
            return redirect("entries:dashboard")
    else:
        form = ChallanComposeForm(initial=default_challan_initial())

    context = {
        "form": form,
        **_build_summary(),
    }
    return render(request, "entries/create_challan.html", context)


def dashboard_view(request):
    challan_list = Challan.objects.prefetch_related("items__lines").order_by("-created_at")
    context = {
        "challans": challan_list,
        **_build_summary(),
    }
    return render(request, "entries/dashboard.html", context)


def _build_report_rows(items):
    rows = []
    for item_num, item in enumerate(items, start=1):
        lines = list(item.lines.all())
        meters_values = [line.meters for line in lines]
        rows.append(
            {
                "item_number": item_num,
                "description": item.description,
                "item_line_count": len(lines),
                "meters_values": meters_values,
                "item_total_meters": sum(meters_values, Decimal("0")),
            }
        )
    return rows


def challan_detail_view(request, pk):
    challan = get_object_or_404(
        Challan.objects.prefetch_related("items__lines"),
        pk=pk,
    )
    items = list(challan.items.all())
    context = {
        "challan": challan,
        "items": items,
        "report_rows": _build_report_rows(items),
        "item_count": challan.item_count(),
        "line_count": challan.line_count(),
        "total_meters": challan.total_meters(),
    }
    return render(request, "entries/challan_detail.html", context)


def edit_challan_view(request, pk):
    challan = get_object_or_404(
        Challan.objects.prefetch_related("items__lines"),
        pk=pk,
    )

    if request.method == "POST":
        form = ChallanComposeForm(data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save(challan=challan)
            messages.success(request, "Challan updated successfully.")
            return redirect("entries:challan_detail", pk=challan.pk)
    else:
        form = ChallanComposeForm(initial=challan_initial_from_instance(challan))

    context = {
        "form": form,
        "challan": challan,
    }
    return render(request, "entries/edit_challan.html", context)


def delete_challan_view(request, pk):
    challan = get_object_or_404(Challan, pk=pk)
    if request.method == "POST":
        challan.delete()
        messages.success(request, "Challan deleted successfully.")
    return redirect("entries:dashboard")
