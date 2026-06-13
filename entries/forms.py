from decimal import Decimal, InvalidOperation

from django import forms

from .models import Challan, ChallanItem, ChallanLine

INPUT_CLASS = (
    "line-input w-full rounded-lg border border-slate-300 px-3 py-2 "
    "focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
)


def default_challan_initial():
    return [{"description": "", "lines": [{"meters": "", "error": None}]}]


def challan_initial_from_instance(challan):
    items = []
    for item in challan.items.prefetch_related("lines").all():
        lines = [{"meters": line.meters, "error": None} for line in item.lines.all()]
        if not lines:
            lines = [{"meters": "", "error": None}]
        items.append({"description": item.description, "lines": lines})
    return items or default_challan_initial()


class ChallanComposeForm:
    """Parses nested item/line POST data for create and edit challan views."""

    def __init__(self, data=None, initial=None):
        self.data = data
        self.initial = initial if initial is not None else default_challan_initial()
        self.items = []
        self.bound = self.initial
        self.errors = []
        self.item_errors = {}
        self._valid = False

    def _parse_post(self):
        bound_items = []
        valid_items = []
        item_errors = {}
        form_errors = []

        try:
            total_items = int(self.data.get("items-TOTAL_FORMS", "0"))
        except ValueError:
            total_items = 0

        if total_items <= 0:
            form_errors.append("Add at least one item with meters before saving the challan.")
            return bound_items, valid_items, item_errors, form_errors

        saved_items = 0
        for item_index in range(total_items):
            prefix = f"items-{item_index}"
            description = (self.data.get(f"{prefix}-description") or "").strip()
            item_error = {"description": [], "lines": {}}

            try:
                total_lines = int(self.data.get(f"{prefix}-lines-TOTAL_FORMS", "0"))
            except ValueError:
                total_lines = 0

            bound_lines = []
            parsed_lines = []
            for line_index in range(total_lines):
                raw_meters = (self.data.get(f"{prefix}-lines-{line_index}-meters") or "").strip()
                bound_line = {"meters": raw_meters, "error": None}
                if not raw_meters:
                    bound_lines.append(bound_line)
                    continue
                try:
                    meters = Decimal(raw_meters)
                except InvalidOperation:
                    bound_line["error"] = "Enter a valid meter value."
                    item_error["lines"][line_index] = bound_line["error"]
                    bound_lines.append(bound_line)
                    continue
                if meters <= 0:
                    bound_line["error"] = "Enter a positive meter value."
                    item_error["lines"][line_index] = bound_line["error"]
                    bound_lines.append(bound_line)
                    continue
                parsed_lines.append({"meters": meters})
                bound_lines.append(bound_line)

            if not bound_lines:
                bound_lines = [{"meters": "", "error": None}]

            has_item_errors = bool(item_error["description"] or item_error["lines"])
            if parsed_lines:
                valid_items.append({"description": description, "lines": parsed_lines})
                saved_items += 1
            elif description and not item_error["lines"]:
                item_error["description"].append(
                    "Enter at least one positive meter value for this description."
                )
                has_item_errors = True

            if has_item_errors:
                item_errors[item_index] = item_error

            bound_items.append(
                {
                    "description": description,
                    "lines": bound_lines,
                    "errors": item_error if has_item_errors else None,
                }
            )

        if saved_items == 0 and not item_errors:
            form_errors.append("Add at least one item with meters before saving the challan.")

        return bound_items, valid_items, item_errors, form_errors

    def is_valid(self):
        self.errors = []
        self.item_errors = []
        self.items = []
        self.bound = self.initial

        if self.data is None:
            self._valid = False
            return False

        bound_items, valid_items, item_errors, form_errors = self._parse_post()
        self.bound = bound_items or self.initial
        self.item_errors = item_errors
        self.errors = form_errors

        if item_errors or form_errors:
            self._valid = False
            return False

        self.items = valid_items
        self._valid = True
        return True

    def save(self, challan=None):
        if not self._valid:
            raise ValueError("Cannot save an invalid challan form.")

        if challan is None:
            challan = Challan.objects.create()
        else:
            challan.items.all().delete()

        for item_order, item_data in enumerate(self.items):
            item = ChallanItem.objects.create(
                challan=challan,
                description=item_data["description"],
                sort_order=item_order,
            )
            for line_order, line_data in enumerate(item_data["lines"]):
                ChallanLine.objects.create(
                    item=item,
                    meters=line_data["meters"],
                    sort_order=line_order,
                )

        return challan

    @property
    def bound_items(self):
        return self.bound


class DescriptionWidget(forms.TextInput):
    def __init__(self):
        super().__init__(
            attrs={
                "placeholder": "Optional description",
                "class": INPUT_CLASS,
                "data-item-input": "description",
            }
        )


class MetersWidget(forms.NumberInput):
    def __init__(self):
        super().__init__(
            attrs={
                "min": "0.01",
                "step": "any",
                "placeholder": "Meters",
                "class": INPUT_CLASS,
                "data-line-input": "meters",
            }
        )
