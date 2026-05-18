from django.contrib import admin

from .models import Challan, ChallanLine


class ChallanLineInline(admin.TabularInline):
    model = ChallanLine
    extra = 0


@admin.register(Challan)
class ChallanAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "total_meters_display")
    ordering = ("-created_at",)
    inlines = (ChallanLineInline,)

    @admin.display(description="Total meters")
    def total_meters_display(self, obj):
        return obj.total_meters()
