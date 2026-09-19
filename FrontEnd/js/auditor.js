const API_BASE = "http://127.0.0.1:8000";
const session = readSession();
let queue = [];
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

function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast show${isError ? " error" : ""}`;
  window.setTimeout(() => {
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
  if (!response.ok) throw new Error(data.detail || "Không thể tải dữ liệu");
  return data;
}

function statusLabel(status) {
  return (
    {
      UNVERIFIED: "Chưa kiểm định",
      REJECTED: "Cần kiểm tra lại",
      AUDITED: "Đã kiểm định",
    }[status] || status
  );
}

function statusClass(status) {
  return `status-${String(status || "").toLowerCase()}`;
}

function renderQueue() {
  const list = document.getElementById("queue-list");
  document.getElementById("pending-count").textContent = queue.filter(
    (item) => item.status === "UNVERIFIED",
  ).length;
  document.getElementById("rejected-count").textContent = queue.filter(
    (item) => item.status === "REJECTED",
  ).length;
  document.getElementById("reported-count").textContent = queue.filter(
    (item) => item.report_count > 0,
  ).length;
  document.getElementById("queue-status").textContent = `${queue.length} hồ sơ`;

  if (!queue.length) {
    list.innerHTML =
      '<p class="empty-state">Không có lô hàng cần kiểm định.</p>';
    return;
  }

  list.innerHTML = queue
    .map(
      (batch) => `
    <button class="queue-item ${batch.id === selectedBatchId ? "selected" : ""}" data-batch-id="${batch.id}" type="button">
      <div class="queue-top"><strong>${escapeHtml(batch.batch_code)}</strong><span class="status ${statusClass(batch.status)}">${statusLabel(batch.status)}</span></div>
      <p>${escapeHtml(batch.product_name)} · ${escapeHtml(batch.producer_name)}</p>
      <div class="queue-meta"><span>${batch.sample_count} sample · ${batch.report_count} report</span><span>${escapeHtml(batch.origin || "Chưa có nguồn gốc")}</span></div>
    </button>
  `,
    )
    .join("");
}

function renderDetail(batch) {
  const panel = document.getElementById("detail-panel");
  if (!batch) {
    panel.innerHTML =
      '<div class="empty-state detail-empty">Chọn một lô hàng để xem hồ sơ kiểm định.</div>';
    return;
  }

  const samples = batch.samples || [];
  const reports = batch.reports || [];
  panel.innerHTML = `
    <div class="detail-header">
      <div><p class="eyebrow">CASE FILE</p><h2>${escapeHtml(batch.batch_code)}</h2><p class="detail-subtitle">${escapeHtml(batch.product_name)} · ${escapeHtml(batch.producer_name)}</p></div>
      <span class="status ${statusClass(batch.status)}">${statusLabel(batch.status)}</span>
    </div>
    <div class="detail-section">
      <h3>Thông tin lô hàng</h3>
      <div class="info-grid">
        <div><span class="info-label">Loại sản phẩm</span><span class="info-value">${escapeHtml(batch.product_type || "-")}</span></div>
        <div><span class="info-label">Số lượng</span><span class="info-value">${escapeHtml(batch.quantity)} ${escapeHtml(batch.unit)}</span></div>
        <div><span class="info-label">Nguồn gốc</span><span class="info-value">${escapeHtml(batch.origin || "-")}</span></div>
        <div><span class="info-label">Ngày sản xuất</span><span class="info-value">${escapeHtml(batch.production_date || "-")}</span></div>
      </div>
    </div>
    <div class="detail-section"><h3>Sample liên kết (${samples.length})</h3>${renderSamples(samples)}</div>
    <div class="detail-section"><h3>Laboratory Test Report (${reports.length})</h3>${renderReports(reports)}</div>
    <div class="detail-section"><h3>Upload report mới</h3>${renderReportForm(batch, samples)}</div>
    <div class="detail-section"><h3>Quyết định kiểm định</h3><label class="info-label" for="decision-reason">Ghi chú / lý do</label><textarea id="decision-reason" rows="3" style="width:100%;margin-top:6px;border:1px solid #dce5e8;border-radius:6px;padding:9px;resize:vertical" placeholder="Nhập nhận xét kiểm định"></textarea><div class="action-row"><button class="button button-primary" data-action="approve" type="button">Approve batch</button><button class="button button-danger" data-action="reject" type="button">Reject batch</button></div></div>
  `;
}

function renderSamples(samples) {
  if (!samples.length)
    return '<p class="empty-state">Chưa có sample liên kết.</p>';
  return `<table class="data-table"><thead><tr><th>Sample</th><th>Ngày lấy</th><th>Khối lượng</th><th>Địa điểm</th></tr></thead><tbody>${samples.map((sample) => `<tr><td>${escapeHtml(sample.sample_code)}</td><td>${escapeHtml(sample.sampling_date || "-")}</td><td>${escapeHtml(sample.sample_quantity || "-")} ${escapeHtml(sample.sample_unit || "")}</td><td>${escapeHtml(sample.sampling_location || "-")}</td></tr>`).join("")}</tbody></table>`;
}

function renderReports(reports) {
  if (!reports.length)
    return '<p class="empty-state">Chưa có báo cáo. Auditor cần upload PDF trước khi approve.</p>';
  return `<table class="data-table"><thead><tr><th>Report</th><th>Kết quả</th><th>File</th><th>SHA-256</th></tr></thead><tbody>${reports.map((report) => `<tr><td>${escapeHtml(report.report_code)}<br><small>${escapeHtml(report.lab_name || "-")}</small></td><td>${escapeHtml(report.result)}</td><td>${escapeHtml(report.file_name || "-")}</td><td class="hash">${escapeHtml(report.file_hash || "-")}</td></tr>`).join("")}</tbody></table>`;
}

function renderReportForm(batch, samples) {
  if (!samples.length)
    return '<p class="empty-state">Cần tạo sample trước khi upload report.</p>';
  return `<form id="report-form" class="report-form" data-batch-id="${batch.id}"><label>Sample<select name="sample_id" required>${samples.map((sample) => `<option value="${sample.id}">${escapeHtml(sample.sample_code)}</option>`).join("")}</select></label><label>Kết quả<input name="result" value="PASS" required /></label><label>Tên phòng lab<input name="lab_name" required /></label><label>Mã phòng lab<input name="lab_code" required /></label><label>Ngày báo cáo<input type="date" name="report_date" /></label><label>File PDF<input type="file" name="file" accept="application/pdf,.pdf" required /></label><div class="full"><button class="button button-secondary" type="submit">Upload và tạo SHA-256</button></div></form>`;
}

async function loadQueue() {
  document.getElementById("queue-status").textContent = "Đang tải...";
  try {
    queue = await request("/auditor/queue");
    renderQueue();
    renderDetail(queue.find((item) => item.id === selectedBatchId) || null);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function submitReport(form) {
  const data = new FormData(form);
  data.append("batch_id", form.dataset.batchId);
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    await request("/auditor/reports", { method: "POST", body: data });
    showToast("Đã upload report và tạo SHA-256.");
    await loadQueue();
    selectBatch(Number(form.dataset.batchId));
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
  }
}

async function decideBatch(action) {
  const reason = document.getElementById("decision-reason").value.trim();
  if (!reason) {
    showToast("Vui lòng nhập nhận xét kiểm định.", true);
    return;
  }
  const button = document.querySelector(`[data-action="${action}"]`);
  button.disabled = true;
  try {
    await request(`/auditor/batches/${selectedBatchId}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason }),
    });
    showToast(
      action === "approve" ? "Batch đã được approve." : "Batch đã được reject.",
    );
    selectedBatchId = null;
    await loadQueue();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
  }
}

function selectBatch(batchId) {
  selectedBatchId = batchId;
  renderQueue();
  renderDetail(queue.find((item) => item.id === batchId));
}

document.addEventListener("click", (event) => {
  const batchButton = event.target.closest("[data-batch-id]");
  if (batchButton) selectBatch(Number(batchButton.dataset.batchId));
  const viewButton = event.target.closest("[data-view]");
  if (viewButton) {
    document
      .querySelectorAll(".view")
      .forEach((view) =>
        view.classList.toggle("hidden", view.id !== viewButton.dataset.view),
      );
    document
      .querySelectorAll(".nav-item")
      .forEach((item) =>
        item.classList.toggle(
          "active",
          item.dataset.view === viewButton.dataset.view,
        ),
      );
  }
  const actionButton = event.target.closest("[data-action]");
  if (actionButton) decideBatch(actionButton.dataset.action);
});

document.addEventListener("submit", (event) => {
  if (event.target.id !== "report-form") return;
  event.preventDefault();
  submitReport(event.target);
});

document.getElementById("refresh-button").addEventListener("click", loadQueue);
document.getElementById("logout-button").addEventListener("click", () => {
  sessionStorage.removeItem("currentUser");
  localStorage.removeItem("currentUser");
  window.location.href = "./login.html";
});
document.getElementById("auditor-name").textContent =
  session.full_name || session.username || "Auditor";

if (
  !session.access_token ||
  !["AUDITOR", "ADMIN"].includes(String(session.role || "").toUpperCase())
) {
  window.location.href = "./login.html";
} else {
  loadQueue();
}
