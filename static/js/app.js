const apiBase = "";

async function apiRequest(path, options = {}) {
  const res = await fetch(`${apiBase}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error?.message || data.detail?.error?.message || "Request failed");
  }
  return data;
}

function formatIdr(value) {
  const num = Number(value || 0);
  return `Rp ${num.toLocaleString("id-ID")}`;
}

function setActiveNav() {
  const path = window.location.pathname.split("/").pop();
  document.querySelectorAll(".nav a").forEach((link) => {
    if (link.getAttribute("href") === path) {
      link.classList.add("active");
    }
  });
}

function toast(el, message) {
  if (!el) return;
  el.textContent = message;
  setTimeout(() => {
    el.textContent = "";
  }, 3000);
}

window.addEventListener("DOMContentLoaded", setActiveNav);
