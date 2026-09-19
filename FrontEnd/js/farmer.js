const API_BASE = "http://127.0.0.1:8000";
const session = readSession();
let batches = [];
let selectedBatchId = null;

function readSession() {
  try {
    return JSON.parse(
      sessionStorage.getItem("currentUser") ||
        localStorage.getItem("currentUser") ||
        "{}",
    );
  } catch {
    return {};
  }
}
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
function showToast(message, error = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast show${error ? " error" : ""}`;
  setTimeout(() => {
    toast.className = "toast";
  }, 3200);
}
async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      ...(options.headers || {}),
    },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok)
    throw new Error(
      Array.isArray(data.detail)
        ? data.detail.map((item) => item.msg).join("; ")
        : data.detail || "Không thể tải dữ liệu",
    );
  return data;
}
function statusLabel(status) {
  return (
    {
      UNVERIFIED: "Chưa kiểm định",
      REJECTED: "Cần cập nhật",
      AUDITED: "Đã kiểm định",
    }[status] || status
  );
}
function statusClass(status) {
  return `status-${String(status || "").toLowerCase()}`;
}

function renderMetrics() {
  document.getElementById("total-count").textContent = batches.length;
  document.getElementById("pending-count").textContent = batches.filter(
    (item) => item.status === "UNVERIFIED",
  ).length;
  document.getElementById("audited-count").textContent = batches.filter(
    (item) => item.status === "AUDITED",
  ).length;
  document.getElementById("rejected-count").textContent = batches.filter(
    (item) => item.status === "REJECTED",
  ).length;
}
function renderBatches() {
  const list = document.getElementById("batch-list");
  renderMetrics();
  if (!batches.length) {
    list.innerHTML = '<p class="empty-state">Bạn chưa có lô hàng nào.</p>';
    return;
  }
  list.innerHTML = batches
    .map(
      (batch) =>
        `<button class="batch-item ${batch.id === selectedBatchId ? "selected" : ""}" data-batch-id="${batch.id}" type="button"><div class="batch-top"><strong>${escapeHtml(batch.batch_code)}</strong><span class="status ${statusClass(batch.status)}">${statusLabel(batch.status)}</span></div><p>${escapeHtml(batch.product_name)} · ${escapeHtml(batch.origin)}</p><div class="batch-meta"><span>${escapeHtml(batch.quantity)} ${escapeHtml(batch.unit)}</span><span>${escapeHtml(batch.production_date || "Chưa có ngày")}</span></div></button>`,
    )
    .join("");
}
function renderDetail(batch) {
  const panel = document.getElementById("batch-detail");
  if (!batch) {
    panel.innerHTML =
      '<div class="empty-state detail-empty">Chọn một lô hàng để xem chi tiết.</div>';
    return;
  }
  const canEdit = ["UNVERIFIED", "REJECTED"].includes(batch.status);
  panel.innerHTML = `<div class="detail-header"><div><p class="eyebrow">BATCH RECORD</p><h2>${escapeHtml(batch.batch_code)}</h2><p class="detail-subtitle">${escapeHtml(batch.product_name)} · ${escapeHtml(batch.producer_name)}</p></div><span class="status ${statusClass(batch.status)}">${statusLabel(batch.status)}</span></div><div class="detail-section"><h3>Thông tin lô hàng</h3><div class="info-grid"><div><span class="info-label">Loại sản phẩm</span><span class="info-value">${escapeHtml(batch.product_type || "-")}</span></div><div><span class="info-label">Số lượng</span><span class="info-value">${escapeHtml(batch.quantity)} ${escapeHtml(batch.unit)}</span></div><div><span class="info-label">Nguồn gốc</span><span class="info-value">${escapeHtml(batch.origin)}</span></div><div><span class="info-label">Ngày sản xuất</span><span class="info-value">${escapeHtml(batch.production_date || "-")}</span></div><div><span class="info-label">Hạn sử dụng</span><span class="info-value">${escapeHtml(batch.expiry_date || "-")}</span></div><div><span class="info-label">Ghi chú</span><span class="info-value">${escapeHtml(batch.note || "-")}</span></div></div></div><div class="detail-section"><div class="detail-header"><h3>Mẫu kiểm nghiệm</h3><button class="button button-secondary" data-action="new-sample" type="button">+ Tạo mẫu</button></div><div id="detail-samples"><p class="empty-state">Đang tải mẫu...</p></div></div>${batch.status === "AUDITED" ? '<div id="qr-section" class="detail-section"><h3>Truy xuất công khai</h3><p class="empty-state">Chưa sinh QR cho Batch này.</p><button class="button button-primary" data-action="create-qr" type="button">Sinh QR truy xuất</button></div>' : ""}<div class="action-row">${canEdit ? `<button class="button button-secondary" data-action="edit-batch" type="button">Chỉnh sửa</button>` : ""}${batch.status === "UNVERIFIED" ? '<button class="button button-danger" data-action="delete-batch" type="button">Xóa lô</button>' : ""}</div>`;
  loadSamples(batch.id);
}
async function loadSamples(batchId) {
  const target = document.getElementById("detail-samples");
  if (!target) return;
  try {
    const samples = await request(`/batches/${batchId}/samples`);
    target.innerHTML = samples.length
      ? `<table class="sample-table"><thead><tr><th>Mã mẫu</th><th>Ngày lấy</th><th>Số lượng</th><th>Địa điểm</th><th>Trạng thái</th></tr></thead><tbody>${samples.map((sample) => `<tr><td>${escapeHtml(sample.sample_code)}</td><td>${escapeHtml(sample.sampling_date || "-")}</td><td>${escapeHtml(sample.sample_quantity)} ${escapeHtml(sample.sample_unit)}</td><td>${escapeHtml(sample.sampling_location)}</td><td>${escapeHtml(sample.status)}</td></tr>`).join("")}</tbody></table>`
      : '<p class="empty-state">Chưa có mẫu kiểm nghiệm.</p>';
  } catch (error) {
    target.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
  }
}
async function loadBatches() {
  try {
    batches = await request("/batches");
    renderBatches();
    renderDetail(batches.find((item) => item.id === selectedBatchId) || null);
  } catch (error) {
    showToast(error.message, true);
  }
}
function openBatchDialog(batch = null) {
  const dialog = document.getElementById("batch-dialog");
  const form = document.getElementById("batch-form");
  form.reset();
  form.elements.batch_id.value = batch?.id || "";
  document.getElementById("batch-form-title").textContent = batch
    ? "Chỉnh sửa lô hàng"
    : "Tạo lô hàng mới";
  [
    "product_name",
    "product_type",
    "origin",
    "quantity",
    "unit",
    "production_date",
    "expiry_date",
    "note",
  ].forEach((key) => {
    if (batch) form.elements[key].value = batch[key] ?? "";
  });
  dialog.showModal();
}
function openSampleDialog(batchId) {
  const form = document.getElementById("sample-form");
  form.reset();
  form.elements.batch_id.value = batchId;
  document.getElementById("sample-dialog").showModal();
}
async function saveBatch(form) {
  const id = form.elements.batch_id.value;
  const payload = Object.fromEntries(new FormData(form));
  delete payload.batch_id;
  payload.quantity = Number(payload.quantity);
  Object.keys(payload).forEach((key) => {
    if (payload[key] === "") delete payload[key];
  });
  try {
    await request(id ? `/batches/${id}` : "/batches", {
      method: id ? "PATCH" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    form.closest("dialog").close();
    showToast(id ? "Đã cập nhật lô hàng." : "Đã tạo lô hàng.");
    selectedBatchId = null;
    await loadBatches();
  } catch (error) {
    showToast(error.message, true);
  }
}
async function saveSample(form) {
  const payload = Object.fromEntries(new FormData(form));
  payload.batch_id = Number(payload.batch_id);
  payload.sample_quantity = Number(payload.sample_quantity);
  Object.keys(payload).forEach((key) => {
    if (payload[key] === "") delete payload[key];
  });
  try {
    await request("/samples", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    form.closest("dialog").close();
    showToast("Đã tạo mẫu kiểm nghiệm.");
    await loadSamples(payload.batch_id);
  } catch (error) {
    showToast(error.message, true);
  }
}
async function deleteBatch() {
  if (!confirm("Bạn có chắc muốn xóa lô hàng này?")) return;
  try {
    await request(`/batches/${selectedBatchId}`, { method: "DELETE" });
    showToast("Đã xóa lô hàng.");
    selectedBatchId = null;
    await loadBatches();
  } catch (error) {
    showToast(error.message, true);
  }
}

async function createQr() {
  const button = document.querySelector('[data-action="create-qr"]');
  if (button) button.disabled = true;
  try {
    const result = await request(`/batches/${selectedBatchId}/qr`, {
      method: "POST",
    });
    const qrSection = document.getElementById("qr-section");
    const publicUrl = new URL(result.public_url, window.location.origin).href;
    const imageResponse = await fetch(
      `${API_BASE}/qr/${selectedBatchId}/image`,
      {
        headers: { Authorization: `Bearer ${session.access_token}` },
      },
    );
    if (!imageResponse.ok) throw new Error("Không thể tạo ảnh QR");
    const imageUrl = URL.createObjectURL(await imageResponse.blob());
    qrSection.innerHTML = `<h3>Truy xuất công khai</h3><div class="qr-result"><img id="qr-image" src="${imageUrl}" alt="Mã QR truy xuất" width="190" height="190"><div><span class="info-label">Trace ID</span><strong class="trace-id">${escapeHtml(result.trace_id)}</strong><span class="info-label">Đường dẫn truy xuất</span><a class="trace-link" href="${escapeHtml(publicUrl)}" target="_blank" rel="noopener">Mở trang công khai</a><button class="button button-secondary" data-action="download-qr" type="button">Tải QR</button></div></div>`;
    showToast(
      result.created
        ? "Đã sinh QR truy xuất."
        : "Batch đã có QR, giữ nguyên mã hiện tại.",
    );
  } catch (error) {
    showToast(error.message, true);
  } finally {
    if (button) button.disabled = false;
  }
}

function downloadQr() {
  const image = document.getElementById("qr-image");
  if (!image) return;
  const link = document.createElement("a");
  link.download = `qr-${selectedBatchId}.png`;
  link.href = image.src;
  link.click();
}

document.addEventListener("click", (event) => {
  const item = event.target.closest("[data-batch-id]");
  if (item) {
    selectedBatchId = Number(item.dataset.batchId);
    renderBatches();
    renderDetail(batches.find((batch) => batch.id === selectedBatchId));
  }
  const view = event.target.closest("[data-view]");
  if (view) {
    document
      .querySelectorAll(".view")
      .forEach((element) =>
        element.classList.toggle("hidden", element.id !== view.dataset.view),
      );
    document
      .querySelectorAll(".nav-item")
      .forEach((element) =>
        element.classList.toggle(
          "active",
          element.dataset.view === view.dataset.view,
        ),
      );
  }

  const action = event.target.closest("[data-action]");
  if (!action) return;
  if (action.dataset.action === "edit-batch")
    openBatchDialog(batches.find((batch) => batch.id === selectedBatchId));
  if (action.dataset.action === "new-sample") openSampleDialog(selectedBatchId);
  if (action.dataset.action === "delete-batch") deleteBatch();
  if (action.dataset.action === "create-qr") createQr();
  if (action.dataset.action === "download-qr") downloadQr();
});
document
  .getElementById("new-batch-button")
  .addEventListener("click", () => openBatchDialog());
document
  .getElementById("refresh-button")
  .addEventListener("click", loadBatches);
document.getElementById("batch-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (event.submitter?.value === "cancel")
    return event.currentTarget.closest("dialog").close();
  saveBatch(event.currentTarget);
});
document.getElementById("sample-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (event.submitter?.value === "cancel")
    return event.currentTarget.closest("dialog").close();
  saveSample(event.currentTarget);
});
document.getElementById("logout-button").addEventListener("click", () => {
  sessionStorage.removeItem("currentUser");
  localStorage.removeItem("currentUser");
  window.location.href = "./login.html";
});
document.getElementById("farmer-name").textContent =
  session.full_name || session.username || "Farmer";
if (
  !session.access_token ||
  String(session.role || "").toUpperCase() !== "FARMER"
)
  window.location.href = "./login.html";
else loadBatches();
