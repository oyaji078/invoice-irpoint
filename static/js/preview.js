const params = new URLSearchParams(window.location.search);
const invoiceId = params.get("invoiceId");
const frame = document.getElementById("previewFrame");
const subtitle = document.getElementById("previewSubtitle");

if (invoiceId) {
  subtitle.textContent = `Preview untuk ${invoiceId}`;
  frame.src = `/api/invoices/${invoiceId}/html`;
}

document.getElementById("printBtn").addEventListener("click", () => {
  frame.contentWindow?.print();
});

document.getElementById("pdfBtn").addEventListener("click", () => {
  if (!invoiceId) return;
  window.open(`/api/invoices/${invoiceId}/pdf`, "_blank");
});
