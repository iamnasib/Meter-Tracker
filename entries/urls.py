from django.urls import path

from .views import add_entry_view, dashboard_view, delete_entry_view, edit_entry_view

app_name = "entries"

urlpatterns = [
    # Add entry page available at both / and /add/.
    path("", add_entry_view, name="add_entry"),
    path("add/", add_entry_view, name="add_entry_alias"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("entries/<int:pk>/edit/", edit_entry_view, name="edit_entry"),
    path("entries/<int:pk>/delete/", delete_entry_view, name="delete_entry"),
]
