let editingInvoiceId = null;
let previewTimer = null;
let paymentMethods = [];

const tableBody = document.querySelector("#invoiceTable tbody");
const form = document.getElementById("invoiceForm");
const toastEl = document.getElementById("invoiceToast");
const formTitle = document.getElementById("invoiceFormTitle");
const itemRows = document.getElementById("itemRows");
const previewFrame = document.getElementById("inlinePreview");
const paymentSelect = document.getElementById("paymentMethodSelect");
const paymentDetailsEl = document.getElementById("paymentMethodDetails");
const refreshPaymentBtn = document.getElementById("refreshPayment");
const searchBtn = document.getElementById("invoiceSearchBtn");
const searchInput = document.getElementById("invoiceSearch");

function formatIdrInput(value) {
  const num = Number(value || 0);
  return `Rp ${num.toLocaleString("id-ID")}`;
}

function createRow(data = {}) {
  const row = document.createElement("div");
  row.className = "row-grid";
  row.innerHTML = `
    <div>
      <input type="text" class="item-name" placeholder="Nama item" value="${data.name || ""}" />
    </div>
    <div>
      <input type="number" class="item-qty" min="1" placeholder="Qty" value="${data.qty || 1}" />
    </div>
    <div>
      <input type="number" class="item-price" min="0" placeholder="Harga" value="${data.unitPrice || ""}" />
      <div class="price-preview">${formatIdrInput(data.unitPrice)}</div>
    </div>
    <div>
      <input type="number" class="item-discount" min="0" placeholder="Diskon" value="${data.discount ?? 0}" />
    </div>
    <button type="button" class="secondary remove-row">X</button>
  `;

  const priceInput = row.querySelector(".item-price");
  const preview = row.querySelector(".price-preview");
  priceInput.addEventListener("input", () => {
    preview.textContent = formatIdrInput(priceInput.value);
    schedulePreview();
  });

  row.querySelector(".remove-row").addEventListener("click", () => {
    row.remove();
    schedulePreview();
  });

  row.querySelector(".item-name").addEventListener("input", schedulePreview);
  row.querySelector(".item-qty").addEventListener("input", schedulePreview);
  row.querySelector(".item-discount").addEventListener("input", schedulePreview);

  itemRows.appendChild(row);
}

function collectItems() {
  const rows = Array.from(itemRows.querySelectorAll(".row-grid"));
  return rows
    .map((row) => {
      const name = row.querySelector(".item-name").value.trim();
      if (!name) return null;
      return {
        name,
        qty: parseInt(row.querySelector(".item-qty").value || "0", 10),
        unitPrice: Number(row.querySelector(".item-price").value || 0),
        discount: Number(row.querySelector(".item-discount").value || 0),
      };
    })
    .filter(Boolean);
}

function typeLabel(type) {
  switch (type) {
    case "bank":
      return "Bank";
    case "ewallet":
      return "E-Wallet";
    case "other":
      return "Lainnya";
    default:
      return "Tunai";
  }
}

function getSelectedPayment() {
  if (!paymentMethods.length) return null;
  const idx = parseInt(paymentSelect.value || "", 10);
  if (Number.isNaN(idx) || !paymentMethods[idx]) return null;
  return paymentMethods[idx];
}

function updatePaymentDetails() {
  const method = getSelectedPayment();
  if (!method) {
    paymentDetailsEl.textContent = "";
    return;
  }
  const parts = [];
  if (method.methodType && method.methodType !== "cash") {
    if (method.accountNumber) parts.push(`No: ${method.accountNumber}`);
    if (method.accountName) parts.push(`A/N: ${method.accountName}`);
  }
  if (method.details) parts.push(method.details);
  paymentDetailsEl.textContent = parts.join(" · ");
}

function renderPaymentOptions(selectedLabel = "") {
  paymentSelect.innerHTML = "";
  if (!paymentMethods.length) {
    paymentSelect.innerHTML = '<option value="">Belum ada metode</option>';
    paymentDetailsEl.textContent = "";
    paymentSelect.disabled = true;
    return;
  }
  paymentSelect.disabled = false;
  paymentMethods.forEach((method, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `${method.label} (${typeLabel(method.methodType)})`;
    if (selectedLabel && method.label === selectedLabel) {
      option.selected = true;
    }
    paymentSelect.appendChild(option);
  });
  if (!selectedLabel) {
    paymentSelect.value = "0";
  }
  updatePaymentDetails();
}

function buildPayload(forPreview = false) {
  const today = new Date().toISOString().split("T")[0];
  const customerName = form.customerName.value.trim();
  const selectedPayment = getSelectedPayment() || (paymentMethods.length ? paymentMethods[0] : null);
  return {
    date: form.date.value || today,
    invoiceType: form.invoiceType.value || "penjualan",
    status: "Sent",
    customer: {
      customerName: forPreview ? (customerName || "Customer") : customerName,
      customerPhone: form.customerPhone.value.trim(),
      customerAddress: form.customerAddress.value.trim(),
    },
    items: collectItems(),
    paymentMethod: selectedPayment,
    notes: form.notes.value.trim(),
  };
}

async function loadPaymentMethods() {
  try {
    const res = await apiRequest("/api/payment-methods");
    paymentMethods = res.data || [];
    if (!paymentMethods.length) {
      paymentMethods = [{ label: "Tunai", methodType: "cash" }];
    }
    renderPaymentOptions();
  } catch (err) {
    toast(toastEl, err.message);
  }
}

async function loadInvoices(query = "") {
  if (!tableBody) return;
  try {
    const res = await apiRequest(`/api/invoices${query ? `?search=${encodeURIComponent(query)}` : ""}`);
    const data = res.data || [];
    data.sort((a, b) => {
      const dateA = a.date || "";
      const dateB = b.date || "";
      if (dateA !== dateB) return dateB.localeCompare(dateA);
      return (b.invoiceId || "").localeCompare(a.invoiceId || "");
    });
    renderTable(data);
  } catch (err) {
    toast(toastEl, err.message);
  }
}

function renderTable(invoices) {
  if (!tableBody) return;
  tableBody.innerHTML = "";
  invoices.forEach((inv) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${inv.invoiceId}</td>
      <td>${inv.date}</td>
      <td>${inv.customer?.customerName || ""}</td>
      <td>${formatIdr(inv.summary?.grandTotal || 0)}</td>
      <td class="actions">
        <button class="ghost" data-action="preview">Preview</button>
        <button class="ghost" data-action="edit">Edit</button>
        <button class="secondary" data-action="delete">Hapus</button>
      </td>
    `;
    row.querySelector('[data-action="preview"]').addEventListener("click", () => {
      window.open(`invoice_preview.html?invoiceId=${inv.invoiceId}`, "_blank");
    });
    row.querySelector('[data-action="edit"]').addEventListener("click", () => startEdit(inv));
    row.querySelector('[data-action="delete"]').addEventListener("click", () => removeInvoice(inv.invoiceId));
    tableBody.appendChild(row);
  });
}

function startEdit(inv) {
  editingInvoiceId = inv.invoiceId;
  formTitle.textContent = `Edit Invoice ${inv.invoiceId}`;
  form.date.value = inv.date;
  form.invoiceType.value = inv.invoiceType || "penjualan";
  form.customerName.value = inv.customer?.customerName || "";
  form.customerPhone.value = inv.customer?.customerPhone || "";
  form.customerAddress.value = inv.customer?.customerAddress || "";
  form.notes.value = inv.notes || "";

  const selectedLabel = inv.paymentMethod?.label || "";
  renderPaymentOptions(selectedLabel);

  itemRows.innerHTML = "";
  (inv.items || []).forEach((line) => createRow(line));
  schedulePreview();
}

function resetForm() {
  editingInvoiceId = null;
  formTitle.textContent = "Buat Invoice";
  form.reset();
  itemRows.innerHTML = "";
  createRow();
  renderPaymentOptions();
  schedulePreview();
}

async function removeInvoice(id) {
  if (!confirm(`Hapus invoice ${id}?`)) return;
  try {
    await apiRequest(`/api/invoices/${id}`, { method: "DELETE" });
    toast(toastEl, "Invoice dihapus.");
    loadInvoices();
  } catch (err) {
    toast(toastEl, err.message);
  }
}

async function updatePreview() {
  if (!previewFrame) return;
  const payload = buildPayload(true);
  try {
    const res = await fetch("/api/invoices/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) return;
    const html = await res.text();
    previewFrame.srcdoc = html;
  } catch {
    // ignore preview errors
  }
}

function schedulePreview() {
  if (!previewFrame) return;
  if (previewTimer) clearTimeout(previewTimer);
  previewTimer = setTimeout(updatePreview, 300);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = buildPayload(false);

  try {
    if (editingInvoiceId) {
      await apiRequest(`/api/invoices/${editingInvoiceId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      toast(toastEl, "Invoice diperbarui.");
    } else {
      await apiRequest("/api/invoices", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      toast(toastEl, "Invoice dibuat.");
    }
    resetForm();
    loadInvoices();
  } catch (err) {
    toast(toastEl, err.message);
  }
});

form.addEventListener("input", schedulePreview);
form.addEventListener("change", schedulePreview);
paymentSelect.addEventListener("change", () => {
  updatePaymentDetails();
  schedulePreview();
});

refreshPaymentBtn.addEventListener("click", async () => {
  await loadPaymentMethods();
  schedulePreview();
});

document.getElementById("addRow").addEventListener("click", () => {
  createRow();
  schedulePreview();
});

document.getElementById("cancelInvoiceEdit").addEventListener("click", resetForm);

if (searchBtn && searchInput) {
  searchBtn.addEventListener("click", () => {
    const query = searchInput.value.trim();
    loadInvoices(query);
  });
}

window.addEventListener("DOMContentLoaded", async () => {
  await loadPaymentMethods();
  if (tableBody) {
    loadInvoices();
  }
  const today = new Date().toISOString().split("T")[0];
  form.date.value = today;
  form.invoiceType.value = "penjualan";
  createRow();
  schedulePreview();

  const params = new URLSearchParams(window.location.search);
  const invoiceIdParam = params.get("invoiceId");
  if (invoiceIdParam) {
    try {
      const res = await apiRequest(`/api/invoices/${encodeURIComponent(invoiceIdParam)}`);
      startEdit(res.data);
    } catch (err) {
      toast(toastEl, err.message);
    }
  }
});
