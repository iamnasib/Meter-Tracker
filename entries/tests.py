from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Challan, ChallanLine


class ChallanFlowTests(TestCase):
    def test_create_challan_saves_lines_and_redirects(self):
        url = reverse("entries:create_challan")
        payload = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-0-meters": "5",
            "form-0-description": "Roll A",
            "form-1-meters": "3",
            "form-1-description": "",
        }
        response = self.client.post(url, payload, follow=False)
        self.assertRedirects(
            response,
            reverse("entries:dashboard"),
            fetch_redirect_response=False,
        )
        self.assertEqual(Challan.objects.count(), 1)
        self.assertEqual(ChallanLine.objects.count(), 2)
        challan = Challan.objects.get()
        self.assertEqual(challan.total_meters(), Decimal("8"))

    def test_create_challan_accepts_decimal_meters(self):
        url = reverse("entries:create_challan")
        payload = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-0-meters": "5.5",
            "form-0-description": "",
            "form-1-meters": "3.25",
            "form-1-description": "",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        challan = Challan.objects.get()
        self.assertEqual(challan.total_meters(), Decimal("8.75"))

    def test_dashboard_lists_challan_with_link_to_detail(self):
        c = Challan.objects.create()
        ChallanLine.objects.create(challan=c, meters=10, description="x", sort_order=0)
        ChallanLine.objects.create(challan=c, meters=2, description="", sort_order=1)
        r = self.client.get(reverse("entries:dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Challan #")
        self.assertContains(r, "12 meters total")
        self.assertContains(r, reverse("entries:challan_detail", args=[c.pk]))

    def test_challan_detail_report_and_export(self):
        c = Challan.objects.create()
        ChallanLine.objects.create(challan=c, meters=10, description="Roll A", sort_order=0)
        ChallanLine.objects.create(challan=c, meters=2, description="", sort_order=1)
        url = reverse("entries:challan_detail", args=[c.pk])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Export PDF")
        self.assertContains(r, "Total Count")
        self.assertContains(r, "Total Meters")
        self.assertContains(r, "12")
        self.assertContains(r, "Roll A")
        self.assertContains(r, reverse("entries:edit_challan", args=[c.pk]))

    def test_delete_challan_post_only(self):
        c = Challan.objects.create()
        ChallanLine.objects.create(challan=c, meters=1, description="", sort_order=0)
        del_url = reverse("entries:delete_challan", args=[c.pk])
        self.client.get(del_url)
        self.assertTrue(Challan.objects.filter(pk=c.pk).exists())
        self.client.post(del_url)
        self.assertFalse(Challan.objects.filter(pk=c.pk).exists())
