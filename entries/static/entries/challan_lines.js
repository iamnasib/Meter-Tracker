(function () {
  function totalFormsInput() {
    return document.getElementById("id_form-TOTAL_FORMS");
  }

  function stripCloneErrors(row) {
    row.querySelectorAll("ul.errorlist, .line-field-errors").forEach(function (n) {
      n.remove();
    });
    row.querySelectorAll("input").forEach(function (inp) {
      inp.classList.remove("border-red-500");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var tbody = document.getElementById("line-rows");
    if (!tbody) return;

    tbody.addEventListener("keydown", function (e) {
      if (e.key !== "Enter") return;
      var target = e.target;
      if (!target.matches("[data-line-input]")) return;
      e.preventDefault();

      var rows = tbody.querySelectorAll("tr[data-line-row]");
      if (!rows.length) return;

      var last = rows[rows.length - 1];
      var totalEl = totalFormsInput();
      if (!totalEl) return;

      var newIndex = parseInt(totalEl.value, 10);
      if (Number.isNaN(newIndex)) return;

      var row = last.cloneNode(true);
      stripCloneErrors(row);

      row.querySelectorAll("input").forEach(function (inp) {
        if (inp.getAttribute("data-line-input")) {
          inp.value = "";
        }
      });

      row.querySelectorAll("[name^='form-']").forEach(function (el) {
        el.name = el.name.replace(/form-\d+-/, "form-" + newIndex + "-");
        if (el.id) {
          el.id = el.id.replace(/id_form-\d+-/, "id_form-" + newIndex + "-");
        }
      });

      tbody.appendChild(row);
      totalEl.value = String(newIndex + 1);

      var meters = row.querySelector('[data-line-input="meters"]');
      if (meters) meters.focus();
    });
  });
})();
