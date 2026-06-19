from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Challan, ChallanItem, ChallanLine


class ChallanFlowTests(TestCase):
    def test_create_challan_with_multiple_lines_under_one_description(self):
        url = reverse("entries:create_challan")
        payload = {
            "items-TOTAL_FORMS": "1",
            "items-0-description": "Roll A",
            "items-0-lines-TOTAL_FORMS": "3",
            "items-0-lines-0-meters": "5",
            "items-0-lines-1-meters": "3",
            "items-0-lines-2-meters": "2",
        }
        response = self.client.post(url, payload, follow=False)
        self.assertRedirects(
            response,
            reverse("entries:dashboard"),
            fetch_redirect_response=False,
        )
        self.assertEqual(Challan.objects.count(), 1)
        self.assertEqual(ChallanItem.objects.count(), 1)
        self.assertEqual(ChallanLine.objects.count(), 3)
        item = ChallanItem.objects.get()
        self.assertEqual(item.description, "Roll A")
        challan = item.challan
        self.assertEqual(challan.total_meters(), Decimal("10"))

    def test_create_challan_with_multiple_items(self):
        url = reverse("entries:create_challan")
        payload = {
            "items-TOTAL_FORMS": "2",
            "items-0-description": "Roll A",
            "items-0-lines-TOTAL_FORMS": "2",
            "items-0-lines-0-meters": "5",
            "items-0-lines-1-meters": "3",
            "items-1-description": "",
            "items-1-lines-TOTAL_FORMS": "1",
            "items-1-lines-0-meters": "4",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        challan = Challan.objects.get()
        self.assertEqual(challan.items.count(), 2)
        self.assertEqual(challan.line_count(), 3)
        self.assertEqual(challan.total_meters(), Decimal("12"))

    def test_create_challan_accepts_decimal_meters(self):
        url = reverse("entries:create_challan")
        payload = {
            "items-TOTAL_FORMS": "1",
            "items-0-description": "",
            "items-0-lines-TOTAL_FORMS": "2",
            "items-0-lines-0-meters": "5.5",
            "items-0-lines-1-meters": "3.25",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        challan = Challan.objects.get()
        self.assertEqual(challan.total_meters(), Decimal("8.75"))

    def test_create_challan_rejects_description_without_meters(self):
        url = reverse("entries:create_challan")
        payload = {
            "items-TOTAL_FORMS": "1",
            "items-0-description": "Roll A",
            "items-0-lines-TOTAL_FORMS": "1",
            "items-0-lines-0-meters": "",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Challan.objects.count(), 0)

    def test_dashboard_lists_challan_with_link_to_detail(self):
        c = Challan.objects.create()
        item = ChallanItem.objects.create(challan=c, description="x", sort_order=0)
        ChallanLine.objects.create(item=item, meters=10, sort_order=0)
        ChallanLine.objects.create(item=item, meters=2, sort_order=1)
        r = self.client.get(reverse("entries:dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Challan #")
        self.assertContains(r, "12 meters total")
        self.assertContains(r, reverse("entries:challan_detail", args=[c.pk]))

    def test_challan_detail_report_and_export(self):
        c = Challan.objects.create()
        item = ChallanItem.objects.create(challan=c, description="Roll A", sort_order=0)
        ChallanLine.objects.create(item=item, meters=10, sort_order=0)
        ChallanLine.objects.create(item=item, meters=2, sort_order=1)
        url = reverse("entries:challan_detail", args=[c.pk])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Export PDF")
        self.assertContains(r, "Total Items")
        self.assertContains(r, "Total Count")
        self.assertContains(r, "Total Meters")
        self.assertContains(r, "12")
        self.assertContains(r, "Roll A")
        self.assertContains(r, reverse("entries:edit_challan", args=[c.pk]))

    def test_challan_detail_shows_item_and_line_counts(self):
        c = Challan.objects.create()
        item_a = ChallanItem.objects.create(challan=c, description="Roll A", sort_order=0)
        ChallanLine.objects.create(item=item_a, meters=5, sort_order=0)
        ChallanLine.objects.create(item=item_a, meters=3, sort_order=1)
        item_b = ChallanItem.objects.create(challan=c, description="Roll B", sort_order=1)
        ChallanLine.objects.create(item=item_b, meters=4, sort_order=0)
        r = self.client.get(reverse("entries:challan_detail", args=[c.pk]))
        self.assertEqual(r.context["item_count"], 2)
        self.assertEqual(r.context["line_count"], 3)
        report_rows = r.context["report_rows"]
        self.assertEqual(len(report_rows), 2)
        self.assertEqual(report_rows[0]["item_line_count"], 2)
        self.assertEqual(len(report_rows[0]["meters_values"]), 2)
        self.assertEqual(report_rows[0]["item_total_meters"], Decimal("8"))
        self.assertEqual(report_rows[1]["item_line_count"], 1)
        self.assertEqual(report_rows[1]["item_total_meters"], Decimal("4"))

    def test_edit_challan_updates_grouped_lines(self):
        c = Challan.objects.create()
        item = ChallanItem.objects.create(challan=c, description="Roll A", sort_order=0)
        ChallanLine.objects.create(item=item, meters=5, sort_order=0)
        url = reverse("entries:edit_challan", args=[c.pk])
        payload = {
            "items-TOTAL_FORMS": "1",
            "items-0-description": "Roll A",
            "items-0-lines-TOTAL_FORMS": "2",
            "items-0-lines-0-meters": "5",
            "items-0-lines-1-meters": "7",
        }
        response = self.client.post(url, payload)
        self.assertRedirects(response, reverse("entries:challan_detail", args=[c.pk]))
        c.refresh_from_db()
        self.assertEqual(c.line_count(), 2)
        self.assertEqual(c.total_meters(), Decimal("12"))

    def test_delete_challan_post_only(self):
        c = Challan.objects.create()
        item = ChallanItem.objects.create(challan=c, description="", sort_order=0)
        ChallanLine.objects.create(item=item, meters=1, sort_order=0)
        del_url = reverse("entries:delete_challan", args=[c.pk])
        self.client.get(del_url)
        self.assertTrue(Challan.objects.filter(pk=c.pk).exists())
        self.client.post(del_url)
        self.assertFalse(Challan.objects.filter(pk=c.pk).exists())
