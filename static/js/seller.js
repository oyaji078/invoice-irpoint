const form = document.getElementById("sellerForm");
const toastEl = document.getElementById("sellerToast");
const logoPreview = document.getElementById("logoPreview");
const logoFileInput = form.elements["logoFile"];
const logoUrlInput = form.elements["logoUrl"];
const paymentLabelInput = form.elements["paymentLabel"];
const paymentDetailsInput = form.elements["paymentDetails"];
const paymentTypeInput = form.elements["paymentType"];
const paymentAccountNumberInput = form.elements["paymentAccountNumber"];
const paymentAccountNameInput = form.elements["paymentAccountName"];
const paymentExtra = document.getElementById("paymentExtra");
const paymentListEl = document.getElementById("paymentList");
const addPaymentBtn = document.getElementById("addPayment");

let currentLogo = "";
let logoDataUrl = "";
let paymentMethods = [];

function setLogoPreview(src) {
  if (src) {
    logoPreview.innerHTML = `<img src="${src}" alt="Logo" />`;
  } else {
    logoPreview.textContent = "No logo";
  }
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

function updatePaymentExtra() {
  const type = paymentTypeInput.value;
  if (type === "cash") {
    paymentExtra.classList.add("hidden");
  } else {
    paymentExtra.classList.remove("hidden");
  }
}

function renderPaymentList() {
  paymentListEl.innerHTML = "";
  if (!paymentMethods.length) {
    paymentListEl.innerHTML = '<div class="subtle">Belum ada metode pembayaran.</div>';
    return;
  }
  paymentMethods.forEach((method, index) => {
    const item = document.createElement("div");
    item.className = "payment-item";
    const parts = [];
    if (method.methodType && method.methodType !== "cash") {
      if (method.accountNumber) parts.push(`No: ${method.accountNumber}`);
      if (method.accountName) parts.push(`A/N: ${method.accountName}`);
    }
    if (method.details) parts.push(method.details);
    const detailHtml = parts.length ? `<div class="subtle">${parts.join(" · ")}</div>` : "";
    item.innerHTML = `
      <div>
        <strong>${method.label}</strong>
        <span>(${typeLabel(method.methodType)})</span>
        ${detailHtml}
      </div>
      <button type="button" class="ghost" data-index="${index}">Hapus</button>
    `;
    item.querySelector("button").addEventListener("click", () => {
      paymentMethods.splice(index, 1);
      renderPaymentList();
    });
    paymentListEl.appendChild(item);
  });
}

async function loadSeller() {
  try {
    const res = await apiRequest("/api/seller");
    const data = res.data || {};
    form.storeName.value = data.storeName || "";
    form.sellerName.value = data.sellerName || "";
    form.email.value = data.email || "";
    form.phone.value = data.phone || "";
    form.address.value = data.address || "";
    form.logoUrl.value = data.logoUrl || "";

    currentLogo = data.logoUrl || "";
    setLogoPreview(currentLogo);
  } catch (err) {
    toast(toastEl, err.message);
  }
}

async function loadPaymentMethods() {
  try {
    const res = await apiRequest("/api/payment-methods");
    paymentMethods = res.data || [];
    if (!paymentMethods.length) {
      paymentMethods = [{ label: "Tunai", methodType: "cash" }];
    }
    renderPaymentList();
  } catch (err) {
    toast(toastEl, err.message);
  }
}

async function savePaymentMethods() {
  return apiRequest("/api/payment-methods", {
    method: "PUT",
    body: JSON.stringify(paymentMethods),
  });
}

logoFileInput.addEventListener("change", () => {
  const file = logoFileInput.files[0];
  if (!file) {
    logoDataUrl = "";
    setLogoPreview(logoUrlInput.value.trim() || currentLogo);
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    logoDataUrl = reader.result;
    setLogoPreview(logoDataUrl);
  };
  reader.readAsDataURL(file);
});

logoUrlInput.addEventListener("input", () => {
  const url = logoUrlInput.value.trim();
  if (url) {
    setLogoPreview(url);
  } else if (!logoDataUrl) {
    setLogoPreview(currentLogo);
  }
});

paymentTypeInput.addEventListener("change", updatePaymentExtra);

addPaymentBtn.addEventListener("click", () => {
  const label = paymentLabelInput.value.trim();
  const details = paymentDetailsInput.value.trim();
  const methodType = paymentTypeInput.value;
  const accountNumber = paymentAccountNumberInput.value.trim();
  const accountName = paymentAccountNameInput.value.trim();
  if (!label) {
    toast(toastEl, "Nama metode wajib diisi.");
    return;
  }
  paymentMethods.push({
    label,
    methodType,
    accountNumber: methodType === "cash" ? undefined : accountNumber,
    accountName: methodType === "cash" ? undefined : accountName,
    details: details || undefined,
  });
  paymentLabelInput.value = "";
  paymentDetailsInput.value = "";
  paymentAccountNumberInput.value = "";
  paymentAccountNameInput.value = "";
  paymentTypeInput.value = "cash";
  updatePaymentExtra();
  renderPaymentList();
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const pendingLabel = paymentLabelInput.value.trim();
  if (pendingLabel) {
    const pendingDetails = paymentDetailsInput.value.trim();
    const pendingType = paymentTypeInput.value;
    const pendingAccountNumber = paymentAccountNumberInput.value.trim();
    const pendingAccountName = paymentAccountNameInput.value.trim();
    paymentMethods.push({
      label: pendingLabel,
      methodType: pendingType,
      accountNumber: pendingType === "cash" ? undefined : pendingAccountNumber,
      accountName: pendingType === "cash" ? undefined : pendingAccountName,
      details: pendingDetails || undefined,
    });
    paymentLabelInput.value = "";
    paymentDetailsInput.value = "";
    paymentAccountNumberInput.value = "";
    paymentAccountNameInput.value = "";
    paymentTypeInput.value = "cash";
    updatePaymentExtra();
  }
  if (!paymentMethods.length) {
    paymentMethods = [{ label: "Tunai", methodType: "cash" }];
  }
  const logoFinal = logoDataUrl || logoUrlInput.value.trim() || currentLogo || "";
  const payload = {
    storeName: form.storeName.value.trim(),
    sellerName: form.sellerName.value.trim(),
    email: form.email.value.trim(),
    phone: form.phone.value.trim(),
    address: form.address.value.trim(),
    logoUrl: logoFinal,
  };
  try {
    await apiRequest("/api/seller", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    await savePaymentMethods();
    currentLogo = logoFinal;
    logoDataUrl = "";
    toast(toastEl, "Profil tersimpan.");
  } catch (err) {
    toast(toastEl, err.message);
  }
});

window.addEventListener("DOMContentLoaded", () => {
  updatePaymentExtra();
  loadSeller();
  loadPaymentMethods();
});
