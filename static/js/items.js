let editingId = null;
const tableBody = document.querySelector("#itemsTable tbody");
const form = document.getElementById("itemForm");
const toastEl = document.getElementById("itemsToast");
const formTitle = document.getElementById("formTitle");

async function loadItems(query = "") {
  try {
    const res = await apiRequest(`/api/items${query ? `?search=${encodeURIComponent(query)}` : ""}`);
    renderTable(res.data || []);
  } catch (err) {
    toast(toastEl, err.message);
  }
}

function renderTable(items) {
  tableBody.innerHTML = "";
  items.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.id}</td>
      <td>${item.name}</td>
      <td>${item.sku || "-"}</td>
      <td>${item.unit}</td>
      <td>${formatIdr(item.price)}</td>
      <td>${item.taxRate || 0}%</td>
      <td class="actions">
        <button class="ghost" data-action="edit">Edit</button>
        <button class="secondary" data-action="delete">Hapus</button>
      </td>
    `;
    row.querySelector('[data-action="edit"]').addEventListener("click", () => startEdit(item));
    row.querySelector('[data-action="delete"]').addEventListener("click", () => removeItem(item.id));
    tableBody.appendChild(row);
  });
}

function startEdit(item) {
  editingId = item.id;
  formTitle.textContent = `Edit Item ${item.id}`;
  form.elements["id"].value = item.id;
  form.elements["name"].value = item.name;
  form.elements["sku"].value = item.sku || "";
  form.elements["unit"].value = item.unit;
  form.elements["price"].value = item.price;
  form.elements["taxRate"].value = item.taxRate || 0;
}

function resetForm() {
  editingId = null;
  formTitle.textContent = "Tambah Item";
  form.reset();
}

async function removeItem(itemId) {
  if (!confirm(`Hapus item ${itemId}?`)) return;
  try {
    await apiRequest(`/api/items/${itemId}`, { method: "DELETE" });
    toast(toastEl, "Item dihapus.");
    loadItems();
  } catch (err) {
    toast(toastEl, err.message);
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    id: form.elements["id"].value.trim() || undefined,
    name: form.elements["name"].value.trim(),
    sku: form.elements["sku"].value.trim() || undefined,
    unit: form.elements["unit"].value.trim(),
    price: Number(form.elements["price"].value),
    taxRate: Number(form.elements["taxRate"].value || 0),
  };
  try {
    if (editingId) {
      await apiRequest(`/api/items/${editingId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      toast(toastEl, "Item diperbarui.");
    } else {
      await apiRequest("/api/items", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      toast(toastEl, "Item ditambahkan.");
    }
    resetForm();
    loadItems();
  } catch (err) {
    toast(toastEl, err.message);
  }
});

document.getElementById("cancelEdit").addEventListener("click", resetForm);
document.getElementById("searchBtn").addEventListener("click", () => {
  const query = document.getElementById("searchInput").value.trim();
  loadItems(query);
});

window.addEventListener("DOMContentLoaded", () => loadItems());
