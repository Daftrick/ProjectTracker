document.querySelectorAll(".quote-terms-editor").forEach(editor => {
  const rows = editor.querySelector(".quote-terms-rows");
  const select = editor.querySelector("select");

  function publish() {
    const terms = Array.from(rows.children).map(row => ({
      title: row.querySelector(".term-title").value,
      body: row.querySelector(".term-body").value,
      enabled: row.querySelector(".term-enabled").checked,
    }));
    editor.dispatchEvent(new CustomEvent("quote-terms-changed", { bubbles: true, detail: terms }));
  }

  function addTerm(term = {}) {
    const row = document.createElement("div");
    row.className = "quote-term-row mb-3 pb-3 border-bottom";
    row.innerHTML = `
      <input type="hidden" name="term_id[]">
      <input type="hidden" name="term_enabled[]">
      <div class="d-flex align-items-center justify-content-between mb-2">
        <label class="form-check small mb-0">
          <input class="form-check-input term-enabled" type="checkbox">
          <span class="form-check-label">Incluir en PDF</span>
        </label>
        <button type="button" class="btn btn-sm btn-outline-danger remove-term" aria-label="Eliminar término">Eliminar</button>
      </div>
      <label class="form-label small d-block">Título
        <input name="term_title[]" class="form-control form-control-sm term-title">
      </label>
      <label class="form-label small d-block">Contenido
        <textarea name="term_body[]" class="form-control form-control-sm term-body" rows="3"></textarea>
      </label>`;
    row.querySelector('[name="term_id[]"]').value = term.id || "term-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2);
    row.querySelector(".term-title").value = term.title || "";
    row.querySelector(".term-body").value = term.body || "";
    row.querySelector(".term-enabled").checked = term.enabled !== false;
    row.querySelector('[name="term_enabled[]"]').value = term.enabled !== false ? "1" : "0";
    rows.append(row);
    return row;
  }

  editor.querySelector(".add-term").addEventListener("click", () => {
    addTerm().querySelector(".term-title").focus();
    publish();
  });
  editor.querySelector(".apply-terms-template").addEventListener("click", () => {
    const option = select.selectedOptions[0];
    if (!option || !option.dataset.terms) return;
    const terms = JSON.parse(option.dataset.terms);
    rows.replaceChildren();
    terms.forEach(addTerm);
    publish();
  });
  rows.addEventListener("click", event => {
    const button = event.target.closest(".remove-term");
    if (button) {
      button.closest(".quote-term-row").remove();
      publish();
    }
  });
  rows.addEventListener("input", publish);
  rows.addEventListener("change", event => {
    if (event.target.matches(".term-enabled")) {
      event.target.closest(".quote-term-row").querySelector('[name="term_enabled[]"]').value = event.target.checked ? "1" : "0";
    }
    publish();
  });
});
