from django.contrib import admin

from .models import Challan, ChallanItem, ChallanLine


class ChallanLineInline(admin.TabularInline):
    model = ChallanLine
    extra = 0


class ChallanItemInline(admin.TabularInline):
    model = ChallanItem
    extra = 0
    show_change_link = True


@admin.register(Challan)
class ChallanAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "total_meters_display")
    ordering = ("-created_at",)
    inlines = (ChallanItemInline,)

    @admin.display(description="Total meters")
    def total_meters_display(self, obj):
        return obj.total_meters()


@admin.register(ChallanItem)
class ChallanItemAdmin(admin.ModelAdmin):
    list_display = ("id", "challan", "description", "sort_order")
    list_filter = ("challan",)
    inlines = (ChallanLineInline,)
