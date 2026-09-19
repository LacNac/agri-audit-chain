const API_BASE = "http://127.0.0.1:8000";
const params = new URLSearchParams(window.location.search);
const lookup = params.get("trace") || params.get("batch") || "";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
function showError(message) {
  document.getElementById("loading").classList.add("hidden");
  const error = document.getElementById("error");
  error.textContent = message;
  error.classList.remove("hidden");
}
function renderTrace(data) {
  document.getElementById("loading").classList.add("hidden");
  const card = document.getElementById("trace-card");
  const summary = data.laboratory_result_summary || {};
  const verification = data.verification || {};
  card.innerHTML = `<div class="hero"><p class="eyebrow">BATCH TRACEABILITY RECORD</p><h1>${escapeHtml(data.product_name || "Nông sản")}</h1><div class="hero-meta"><span>${escapeHtml(data.batch_code)} · ${escapeHtml(data.trace_id || "Chưa có Trace ID")}</span><span class="verified">${escapeHtml(data.audit_status)}</span></div></div><div class="content"><section class="section"><h2>Nguồn gốc sản phẩm</h2><div class="facts"><div><span class="fact-label">Nhà sản xuất</span><span class="fact-value">${escapeHtml(data.farmer || "Chưa cập nhật")}</span></div><div><span class="fact-label">Nguồn gốc</span><span class="fact-value">${escapeHtml(data.origin || "Chưa cập nhật")}</span></div><div><span class="fact-label">Ngày sản xuất</span><span class="fact-value">${escapeHtml(data.production_date || "Chưa cập nhật")}</span></div></div></section><section class="section"><h2>Kiểm định chất lượng</h2><div class="facts"><div><span class="fact-label">Số báo cáo</span><span class="fact-value">${escapeHtml(summary.report_count || 0)}</span></div><div><span class="fact-label">Mã báo cáo mới nhất</span><span class="fact-value">${escapeHtml(summary.latest_report_code || "Chưa có")}</span></div><div class="result-box"><span class="fact-label">Kết quả mới nhất</span><strong>${escapeHtml(summary.latest_result || "Chưa cập nhật")}</strong></div></div></section><section class="section"><h2>Tính toàn vẹn hồ sơ</h2><div class="facts"><div><span class="fact-label">SHA-256</span><span class="hash">${escapeHtml(verification.sha256 || "Chưa có")}</span></div><div><span class="fact-label">Trạng thái xác minh</span><span class="integrity">${verification.verified ? "Đã xác minh" : "Chưa xác minh"}</span></div></div></section><section class="section"><h2>Định danh truy xuất</h2><div class="facts"><div><span class="fact-label">Batch Code</span><span class="fact-value">${escapeHtml(data.batch_code)}</span></div><div><span class="fact-label">Trace ID</span><span class="fact-value">${escapeHtml(data.trace_id || "-")}</span></div></div></section></div><div class="footer-note">Thông tin này được cung cấp từ hồ sơ số AgriTrace và chỉ hiển thị cho Batch đã được Auditor kiểm định.<a class="about-link" href="../index.html">Tìm hiểu thêm về AgriTrace</a></div>`;
  card.classList.remove("hidden");
}

async function loadTrace() {
  if (!lookup) {
    showError("Mã truy xuất đang trống. Hãy quét QR hoặc nhập Batch Code.");
    return;
  }
  const normalizedLookup = lookup.toUpperCase();
  const endpoint =
    normalizedLookup.startsWith("QR-") || normalizedLookup.startsWith("TRACE-")
      ? `/public/trace-id/${encodeURIComponent(lookup)}`
      : `/public/trace/${encodeURIComponent(lookup)}`;
  try {
    const response = await fetch(`${API_BASE}${endpoint}`);
    const data = await response.json().catch(() => ({}));
    if (!response.ok)
      throw new Error(data.detail || "Không tìm thấy hồ sơ truy xuất");
    renderTrace(data);
  } catch (error) {
    showError(error.message);
  }
}
loadTrace();
