from django.urls import path

from .views import (
    challan_detail_view,
    create_challan_view,
    dashboard_view,
    delete_challan_view,
    edit_challan_view,
)

app_name = "entries"

urlpatterns = [
    path("", create_challan_view, name="create_challan"),
    path("add/", create_challan_view, name="add_entry_alias"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("challans/<int:pk>/", challan_detail_view, name="challan_detail"),
    path("challans/<int:pk>/edit/", edit_challan_view, name="edit_challan"),
    path("challans/<int:pk>/delete/", delete_challan_view, name="delete_challan"),
]
