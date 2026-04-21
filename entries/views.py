from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EntryForm
from .models import Entry


def _build_summary():
    """Return shared summary values used across pages."""
    total_count = Entry.objects.count()
    total_meters = Entry.objects.aggregate(total=Sum("meters")).get("total") or 0
    return {
        "total_count": total_count,
        "total_meters": total_meters,
    }


def add_entry_view(request):
    # Handle form submit (POST) and empty form display (GET).
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Entry added successfully!")
            # PRG pattern: redirect after successful POST.
            return redirect("entries:add_entry")
    else:
        form = EntryForm()

    context = {
        "form": form,
        **_build_summary(),
    }
    return render(request, "entries/add_entry.html", context)


def dashboard_view(request):
    # Pull newest-first list from model ordering and explicit query for clarity.
    entry_list = Entry.objects.order_by("-created_at")
    context = {
        "entries": entry_list,
        **_build_summary(),
    }
    return render(request, "entries/dashboard.html", context)


def edit_entry_view(request, pk):
    """Edit an existing entry with full form validation."""
    entry = get_object_or_404(Entry, pk=pk)

    if request.method == "POST":
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Entry updated successfully!")
            return redirect("entries:dashboard")
    else:
        form = EntryForm(instance=entry)

    context = {
        "form": form,
        "entry": entry,
    }
    return render(request, "entries/edit_entry.html", context)


def delete_entry_view(request, pk):
    """Delete an entry safely via POST only."""
    entry = get_object_or_404(Entry, pk=pk)

    if request.method == "POST":
        entry.delete()
        messages.success(request, "Entry deleted successfully!")
    return redirect("entries:dashboard")
