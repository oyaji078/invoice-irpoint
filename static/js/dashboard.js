const dashboardTableBody = document.querySelector("#dashboardInvoiceTable tbody");
const dashboardSearchInput = document.getElementById("dashboardInvoiceSearch");
const dashboardSearchBtn = document.getElementById("dashboardInvoiceSearchBtn");
const dashboardToast = document.getElementById("dashboardInvoiceToast");

function sortInvoicesDesc(invoices) {
  return [...invoices].sort((a, b) => {
    const dateA = a.date || "";
    const dateB = b.date || "";
    if (dateA !== dateB) return dateB.localeCompare(dateA);
    return (b.invoiceId || "").localeCompare(a.invoiceId || "");
  });
}

function renderDashboardTable(invoices) {
  if (!dashboardTableBody) return;
  dashboardTableBody.innerHTML = "";
  invoices.forEach((inv) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${inv.invoiceId}</td>
      <td>${inv.date || ""}</td>
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
    row.querySelector('[data-action="edit"]').addEventListener("click", () => {
      window.location.href = `invoices.html?invoiceId=${inv.invoiceId}`;
    });
    row.querySelector('[data-action="delete"]').addEventListener("click", async () => {
      if (!confirm(`Hapus invoice ${inv.invoiceId}?`)) return;
      try {
        await apiRequest(`/api/invoices/${encodeURIComponent(inv.invoiceId)}`, { method: "DELETE" });
        toast(dashboardToast, "Invoice dihapus.");
        loadDashboardInvoices(dashboardSearchInput?.value.trim() || "");
      } catch (err) {
        toast(dashboardToast, err.message);
      }
    });
    dashboardTableBody.appendChild(row);
  });
}

async function loadDashboardInvoices(query = "") {
  if (!dashboardTableBody) return;
  try {
    const res = await apiRequest(`/api/invoices${query ? `?search=${encodeURIComponent(query)}` : ""}`);
    const sorted = sortInvoicesDesc(res.data || []);
    renderDashboardTable(sorted);
  } catch (err) {
    toast(dashboardToast, err.message);
  }
}

if (dashboardSearchBtn) {
  dashboardSearchBtn.addEventListener("click", () => {
    loadDashboardInvoices(dashboardSearchInput?.value.trim() || "");
  });
}

if (dashboardSearchInput) {
  dashboardSearchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      loadDashboardInvoices(dashboardSearchInput.value.trim());
    }
  });
}

window.addEventListener("DOMContentLoaded", () => {
  loadDashboardInvoices();
});
