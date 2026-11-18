/* ========================================================
   1. CẤU HÌNH API & XÁC THỰC (JWT AUTHENTICATION)
   ======================================================== */
const API_BASE = "https://agri-audit-chain-backend.onrender.com";
const COLD_CHAIN_LOGISTICS_LABELS = {
  PICKUP_REQUESTED: "Chưa lấy hàng",
  PICKUP_ASSIGNED: "Đang lấy hàng",
  PICKED_UP: "Đã lấy hàng · chờ bàn giao kiểm định",
  AT_INSPECTION: "Đã bàn giao kiểm định",
  DELIVERY_READY: "Chờ giao hàng",
  RETURN_READY: "Chờ hoàn hàng",
  OUT_FOR_DELIVERY: "Đang giao hàng",
  OUT_FOR_RETURN: "Đang hoàn trả",
  DELIVERED: "Đã giao hàng",
  RETURNED: "Đã hoàn hàng",
  CANCELLED: "Đã hủy",
};
const COLD_CHAIN_IN_TRANSIT_STATUSES = new Set([
  "PICKUP_ASSIGNED",
  "PICKED_UP",
  "OUT_FOR_DELIVERY",
  "OUT_FOR_RETURN",
  "IN_TRANSIT",
  "IN_PROGRESS",
]);

function getAuthHeaders() {
  const sessionUser =
    sessionStorage.getItem("currentUser") ||
    localStorage.getItem("currentUser");
  const token = sessionUser ? JSON.parse(sessionUser).access_token : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

let BATCHES = [];
let SAMPLES = [];
let AUDIT_HISTORY = [];
let activeTab = "pending";
let currentBatch = null;
let currentAuditorName = "Auditor";
let editingReportId = null;
let batchLoadError = null;
let COLD_CHAIN_AGRI_BATCHES = [];
let coldChainBatchesError = null;

async function loadAuditorIdentity() {
  try {
    const response = await fetch(`${API_BASE}/auditor/profile`, {
      headers: getAuthHeaders(),
    });
    const data = await response.json();
    if (!response.ok)
      throw new Error(data.detail || "Không thể tải hồ sơ Auditor.");

    currentAuditorName = data.full_name;
    const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(data.full_name)}&background=5c33cf&color=fff`;
    const nameElement = document.getElementById("sidebar-user-name");
    const avatarElement = document.getElementById("sidebar-user-avatar");
    if (nameElement) nameElement.textContent = data.full_name;
    if (avatarElement) avatarElement.src = avatarUrl;
  } catch (error) {
    console.warn("Không thể tải thông tin Auditor:", error.message);
  }
}

/* ========================================================
   2. GỌI API LẤY DỮ LIỆU TỪ DATABASE
   ======================================================== */

// Lấy danh sách Batches từ DB
async function fetchBatchesFromDB(filters = null) {
  try {
    const endpoint =
      activeTab === "pending" || activeTab === "rejected"
        ? "/auditor/queue"
        : "/batches";
    const query = endpoint === "/auditor/queue" ? filters?.toString() : "";
    const res = await fetch(`${API_BASE}${endpoint}${query ? `?${query}` : ""}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });
    const data = await res.json();
    if (!res.ok)
      throw new Error(
        data.detail || `Không thể tải danh sách lô hàng (HTTP ${res.status}).`,
      );
    BATCHES = Array.isArray(data) ? data : data.items || [];
    batchLoadError = null;
  } catch (err) {
    BATCHES = [];
    batchLoadError = err.message;
    console.warn("Lỗi kết nối API batches:", err.message);
  }
}

async function fetchSamplesFromDB() {
  try {
    const res = await fetch(`${API_BASE}/samples`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Không thể tải danh sách mẫu.");
    const data = await res.json();
    SAMPLES = Array.isArray(data) ? data : data.items || [];
  } catch (err) {
    console.warn("Lỗi kết nối API samples:", err.message);
  }
}

async function fetchAuditHistoryFromDB() {
  try {
    const res = await fetch(`${API_BASE}/auditor/history`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Không thể tải lịch sử kiểm định.");
    const data = await res.json();
    AUDIT_HISTORY = Array.isArray(data) ? data : data.items || [];
  } catch (err) {
    console.warn("Lỗi kết nối API history:", err.message);
  }
}

document.querySelectorAll(".sidebar-nav .nav-item").forEach((btn) => {
  btn.addEventListener("click", async () => {
    document
      .querySelectorAll(".sidebar-nav .nav-item")
      .forEach((item) => item.classList.remove("active"));
    btn.classList.add("active");
    activeTab = btn.getAttribute("data-tab");
    await switchTab(activeTab);
  });
});

async function switchTab(tab) {
  const heading = document.getElementById("page-heading");
  const batchForm = document.getElementById("batch-filter-form");
  const sampleForm = document.getElementById("sample-filter-form");
  const statContainer = document.getElementById("stat-container");
  const table = document.querySelector(".data-table");
  const pagination = document.querySelector(".pagination");
  const timeline = document.getElementById("audit-timeline-box");
  const toolbarActions = document.querySelector(".toolbar-actions");

  if (tab === "samples") {
    heading.textContent = "Danh sách mẫu";
    if (table) table.style.display = "table";
    if (pagination) pagination.style.display = "flex";
    if (timeline) timeline.style.display = "none";
    if (toolbarActions) toolbarActions.style.display = "flex";

    batchForm.style.display = "none";
    sampleForm.style.display = "grid";

    await fetchSamplesFromDB();

    const countWaitingLab = SAMPLES.filter(
      (s) => s.status === "WAITING_LAB",
    ).length;
    const countHasReport = SAMPLES.filter(
      (s) => s.status === "HAS_REPORT",
    ).length;
    const countWaitingResult = SAMPLES.filter(
      (s) => s.status === "WAITING_RESULT",
    ).length;

    statContainer.innerHTML = `
      <div class="stat-pills">
        <span class="stat-pill pill-yellow">Chờ gửi lab &nbsp;<strong>${countWaitingLab}</strong></span>
        <span class="stat-pill pill-green">Đã có báo cáo &nbsp;<strong>${countHasReport}</strong></span>
        <span class="stat-pill pill-blue">Đang chờ kết quả &nbsp;<strong>${countWaitingResult}</strong></span>
      </div>
    `;
    renderSampleTable(SAMPLES);
  } else if (tab === "history") {
    heading.textContent = "Lịch sử kiểm định";
    if (table) table.style.display = "none";
    if (pagination) pagination.style.display = "none";
    if (sampleForm) sampleForm.style.display = "none";
    if (statContainer) statContainer.innerHTML = "";
    if (toolbarActions) toolbarActions.style.display = "none";

    batchForm.style.display = "flex";
    batchForm.className = "history-filter-bar";
    batchForm.innerHTML = `
      <div class="history-filter-group">
        <label>Batch code</label>
        <input id="hf-code" type="text" placeholder="Nhập mã lô hàng" />
      </div>
      <div class="history-filter-group">
        <label>Hành động</label>
        <select id="hf-action">
          <option value="">Tất cả</option>
          <option value="APPROVE">Phê duyệt</option>
          <option value="REJECT">Từ chối</option>
          <option value="RESUBMIT">Gửi lại kiểm định</option>
        </select>
      </div>
      <div class="history-filter-group">
        <label>Khoảng thời gian</label>
        <input id="hf-date" type="text" placeholder="Chọn ngày" onfocus="(this.type='date')" onblur="if(!this.value)this.type='text'" />
      </div>
      <button type="button" class="btn-filter-action" id="btn-history-filter">Lọc</button>
    `;

    await fetchAuditHistoryFromDB();
    renderAuditTimeline(AUDIT_HISTORY);

    document
      .getElementById("btn-history-filter")
      ?.addEventListener("click", () => {
        const code = document
          .getElementById("hf-code")
          .value.trim()
          .toLowerCase();
        const action = document.getElementById("hf-action").value;
        const filtered = AUDIT_HISTORY.filter(
          (h) =>
            (h.batch_code || h.batchCode || "").toLowerCase().includes(code) &&
            (!action || h.action === action),
        );
        renderAuditTimeline(filtered);
      });
  } else {
    // pending, approved, rejected
    if (table) table.style.display = "table";
    if (pagination) pagination.style.display = "flex";
    if (timeline) timeline.style.display = "none";
    if (toolbarActions) toolbarActions.style.display = "flex";

    batchForm.className = "filter-grid";
    batchForm.style.display = "grid";
    batchForm.innerHTML = `
      <div class="filter-group">
        <label for="f-code">Batch code</label>
        <input id="f-code" type="text" placeholder="Nhập mã lô hàng" />
      </div>
      <div class="filter-group">
        <label for="f-product">Tên sản phẩm</label>
        <input id="f-product" type="text" placeholder="Nhập tên sản phẩm" />
      </div>
      <div class="filter-group">
        <label for="f-date" id="lbl-date">${tab === "approved" ? "Ngày duyệt" : "Ngày gửi kiểm định"}</label>
        <input id="f-date" type="text" placeholder="Chọn ngày" onfocus="(this.type='date')" onblur="if(!this.value)this.type='text'" />
      </div>
      <div class="filter-group full-width">
        <label for="f-farmer">Nông dân</label>
        <input id="f-farmer" type="text" placeholder="Nhập tên nông dân" />
      </div>
    `;

    sampleForm.style.display = "none";

    await fetchBatchesFromDB();
    await fetchColdChainAgriBatches();

    let titleText = "Danh sách chờ duyệt";
    let filterStatus = "UNVERIFIED";
    if (tab === "approved") {
      titleText = "Danh sách đã duyệt";
      filterStatus = "AUDITED";
    } else if (tab === "rejected") {
      titleText = "Danh sách từ chối";
      filterStatus = "REJECTED";
    }

    heading.textContent = titleText;
    renderBatchCount(filterStatus);
    renderBatchTable(filterStatus);
  }
}

function renderBatchCount(statusFilter) {
  const count = BATCHES.filter(
    (batch) => (batch.status || "").toUpperCase() === statusFilter,
  ).length;
  const label =
    statusFilter === "AUDITED"
      ? "đã duyệt"
      : statusFilter === "REJECTED"
        ? "từ chối"
        : "chưa duyệt";
  document.getElementById("stat-container").innerHTML = `
    <div class="counter-box">
      <span>Tổng lô hàng ${label}</span>
      <div class="box-badge">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5c33cf" stroke-width="2"><path d="M21 8 12 3 3 8l9 5 9-5Z"/><path d="M3 8v9l9 5 9-5V8"/><path d="M12 13v9"/></svg>
        <strong>${count}</strong>
      </div>
    </div>
  `;
}

async function searchPendingBatches() {
  if (activeTab !== "pending") return;

  const filters = new URLSearchParams();
  const fields = [
    ["batch_code", "f-code"],
    ["product_name", "f-product"],
    ["inspection_sent_date", "f-date"],
    ["farmer_name", "f-farmer"],
  ];
  fields.forEach(([parameter, elementId]) => {
    const value = document.getElementById(elementId)?.value.trim();
    if (value) filters.set(parameter, value);
  });

  await fetchBatchesFromDB(filters);
  await fetchColdChainAgriBatches();
  renderBatchCount("UNVERIFIED");
  renderBatchTable("UNVERIFIED");
}

/* ========================================================
   4. RENDER BẢNG BATCH TỪ DỮ LIỆU DATABASE
   ======================================================== */
function formatAuditDate(value) {
  const match = String(value || "").match(
    /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?/
  );
  if (!match) return "—";
  const [, year, month, day, hours, minutes] = match;
  return `${day}/${month}/${year}${hours ? ` ${hours}:${minutes}` : ""}`;
}

function renderBatchTable(statusFilter) {
  const thead = document.getElementById("table-head");
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";

  thead.innerHTML = `
    <tr>
      <th>Batch code</th>
      <th>Sản phẩm</th>
      <th>Ngày ${activeTab === "approved" ? "duyệt" : "tạo hồ sơ"}</th>
      <th>Nông dân</th>
      <th>Trạng thái vận chuyển</th>
    </tr>
  `;

  const list = BATCHES.filter(
    (b) => (b.status || "").toUpperCase() === statusFilter,
  );

  if (list.length === 0) {
    const emptyMessage = batchLoadError
      ? `Không tải được lô hàng: ${escapeHtml(batchLoadError)}`
      : "Không tìm thấy lô hàng phù hợp";
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#9ca3af; padding:32px;">${emptyMessage}</td></tr>`;
    return;
  }

  list.forEach((b) => {
    const code = b.batch_code || b.code;
    const name = b.product_name || b.product;
    const date =
      activeTab === "approved"
        ? formatAuditDate(b.audit_date)
        : b.created_at || b.createdDate || "—";
    const farmer = b.producer_name || b.farmer_name || b.farmer || "—";
    const transportBatch = findTransportBatch(b);
    const transportStatus = renderTransportStatus(transportBatch);

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="code-col">${code}</td>
      <td>${name}</td>
      <td>${date}</td>
      <td>${farmer}</td>
      <td>${transportStatus}</td>
    `;
    tr.addEventListener("click", () => openBatchDetail(b.id || code));
    tbody.appendChild(tr);
  });
}

/* ========================================================
   5. XEM CHI TIẾT BATCH QUA API (GET /api/v1/auditor/batches/{id})
   ======================================================== */
async function openBatchDetail(batchIdOrCode) {
  try {
    const res = await fetch(`${API_BASE}/auditor/batches/${batchIdOrCode}`, {
      headers: getAuthHeaders(),
    });
    if (res.ok) {
      currentBatch = await res.json();
    } else {
      currentBatch = BATCHES.find(
        (b) =>
          b.id === batchIdOrCode ||
          b.code === batchIdOrCode ||
          b.batch_code === batchIdOrCode,
      );
    }
  } catch (e) {
    currentBatch = BATCHES.find(
      (b) =>
        b.id === batchIdOrCode ||
        b.code === batchIdOrCode ||
        b.batch_code === batchIdOrCode,
    );
  }

  if (!currentBatch) return;
  await fetchColdChainAgriBatches();

  const card = document.getElementById("detail-card-content");
  const overlay = document.getElementById("detail-overlay");

  const code = currentBatch.batch_code || currentBatch.code;
  const product = currentBatch.product_name || currentBatch.product;
  const farmer =
    currentBatch.producer_name ||
    currentBatch.farmer_name ||
    currentBatch.farmer ||
    "Chưa cập nhật";
  const harvest =
    currentBatch.production_date ||
    currentBatch.harvest_date ||
    currentBatch.harvestDate ||
    "—";
  const weight = currentBatch.quantity
    ? `${currentBatch.quantity} ${currentBatch.unit || ""}`
    : currentBatch.weight || "—";
  const created = currentBatch.created_at || currentBatch.createdDate || "—";
  const origin = currentBatch.origin || "Việt Nam";
  const status = (currentBatch.status || "").toUpperCase();
  const transportBatch = findTransportBatch(currentBatch);
  const isInTransit = isBatchInTransit(transportBatch);
  const latestReport = currentBatch.reports?.[0] || currentBatch.report || null;
  const reportResult = (latestReport?.result || "").toUpperCase();
  editingReportId = null;

  let statusBadge = '<span class="status-badge amber">Chờ kiểm định</span>';
  if (status === "AUDITED")
    statusBadge = '<span class="status-badge green">Đã kiểm định</span>';
  if (status === "REJECTED")
    statusBadge = '<span class="status-badge red">Bị từ chối</span>';
  if (hasAssignedTransport(transportBatch))
    statusBadge = `<span class="status-badge blue">${escapeHtml(
      getTransportStatusLabel(transportBatch),
    )}</span>`;
  else if (coldChainBatchesError)
    statusBadge = '<span class="status-badge blue">Chưa xác định vận chuyển</span>';

  const samplesList = currentBatch.samples || [];
  let sampleSection = "";
  if (
    (isInTransit || coldChainBatchesError) &&
    (status === "UNVERIFIED" || status === "PENDING")
  ) {
    sampleSection = `
      <div class="status-banner banner-blue">
        ${coldChainBatchesError
        ? "Không thể xác minh trạng thái vận chuyển"
        : getTransportStatusLabel(transportBatch)}; tạm khóa thao tác tạo mẫu và kiểm định.
      </div>
    `;
  } else if (samplesList.length === 0) {
    sampleSection = `
      <div class="link-row">
        <span>📎 Sample</span>
        <button type="button" class="btn-chip" id="btn-open-create-sample">+ Tạo sample mới</button>
      </div>
    `;
  } else {
    const s = samplesList[0];
    sampleSection = `
      <div class="link-row" style="background:#ede9fe;">
        <span><strong>${s.sample_code || s.id}</strong></span>
        <span style="color:#64748b; font-size:12px;">Lấy mẫu ${s.created_at || s.date || ""}</span>
      </div>
    `;
  }

  const transportStatusText = coldChainBatchesError
    ? "Không thể xác minh trạng thái vận chuyển."
    : getTransportStatusLabel(transportBatch);
  const coldChainSection = `
    <section class="cold-chain-panel" style="margin:16px 0; padding:14px; border:1px solid #dbeafe; border-radius:10px; background:#f8fbff;">
      <h4 style="margin:0 0 10px;">Trạng thái vận chuyển</h4>
      <p id="cold-chain-status" role="status" style="margin:0; color:#1d4ed8; font-size:13px;">${escapeHtml(transportStatusText)}</p>
      <div id="cold-chain-details" style="margin-top:8px; font-size:12px;">${renderTransportDetails(transportBatch)}</div>
    </section>
  `;

  let dynamicBody = "";
  if (isInTransit && (status === "UNVERIFIED" || status === "PENDING")) {
    dynamicBody = `
      <div class="status-banner banner-blue">
        Lô hàng đang được vận chuyển. Không thể tải báo cáo, phê duyệt hoặc từ chối kiểm định cho đến khi chuyến đi kết thúc.
      </div>
    `;
  } else if (coldChainBatchesError && (status === "UNVERIFIED" || status === "PENDING")) {
    dynamicBody = `
      <div class="status-banner banner-yellow">
        Không thể xác minh trạng thái vận chuyển. Tạm thời không thể thực hiện kiểm định.
      </div>
    `;
  } else if (status === "UNVERIFIED" || status === "PENDING") {
    dynamicBody = `
      <div class="link-row">
        <span>📄 Báo cáo kiểm nghiệm: <strong id="report-name">${latestReport ? latestReport.file_name || latestReport.fileName : "chưa có"}</strong></span>
        ${latestReport ? '<span style="display:flex; gap:8px;"><button type="button" class="btn-gray-pill" id="btn-view-report">Xem file</button><button type="button" class="btn-gray-pill" id="btn-edit-report">Sửa</button></span>' : ""}
      </div>

      ${latestReport
        ? `
        <div class="link-row" style="background:#f8fafc;">
          <span>Phòng lab: <strong>${latestReport.lab_name || "—"}</strong></span>
          <span>Mã phòng lab: <strong>${latestReport.lab_code || "—"}</strong></span>
        </div>
        <div class="link-row" style="background:${reportResult === "PASS" ? "#f0fdf4" : reportResult === "FAIL" ? "#fef2f2" : "#fffbeb"};">
          <span>Kết quả lab: <strong>${reportResult || "Chưa có PASS/FAIL"}</strong></span>
          <span>${reportResult === "PASS" ? "Có thể approve hoặc reject" : reportResult === "FAIL" ? "Chỉ được reject" : "Cần cập nhật kết quả"}</span>
        </div>
      `
        : ""
      }

      <div class="report-form" style="${latestReport ? "display:none;" : ""}">
        <h4 style="margin:0 0 12px; font-size:13px;">Upload báo cáo mới</h4>
        <div class="form-grid">
          <div class="form-field">
            <label>Sample</label>
            <select id="r-sample-select">
              ${samplesList
        .map(function (s) {
          return (
            '<option value="' +
            (s.id || s.sample_code) +
            '">' +
            (s.sample_code || s.id) +
            "</option>"
          );
        })
        .join("") || "<option>— Chưa có Sample —</option>"
      }
            </select>
          </div>
          <div class="form-field">
            <label>Kết quả</label>
            <select id="r-result-select"><option value="PASS">PASS</option><option value="FAIL">FAIL</option></select>
          </div>
          <div class="form-field"><label>Tên phòng lab</label><input type="text" id="r-lab-name" placeholder="VD: TT Kiểm định An Giang" /></div>
          <div class="form-field"><label>Mã phòng lab</label><input type="text" id="r-lab-code" placeholder="VD: LAB-AG-01" /></div>
          <div class="form-field"><label>Ngày báo cáo</label><input type="date" id="r-report-date" /></div>
          <div class="form-field">
            <label>File PDF</label>
            <div class="file-picker">
              <button type="button" class="btn-chip" onclick="document.getElementById('mock-file-input').click()">Chọn tệp</button>
              <span id="file-chosen-text">Chưa chọn tệp</span>
              <input type="file" id="mock-file-input" hidden accept=".pdf" onchange="document.getElementById('file-chosen-text').textContent=this.files[0]?.name||'Chưa chọn tệp'" />
            </div>
          </div>
        </div>
        <button type="button" class="btn-upload" id="btn-hash-upload">Upload và tạo SHA-256</button>
        <div class="hash-result" id="hash-box" style="display:none;">
          <p class="fact-label">MÃ BĂM SHA-256 (TỪ FILE DATABASE)</p>
          <p class="hash-value" id="hash-val-text"></p>
        </div>
      </div>

      <h4 class="section-label">Lí do từ chối</h4>
      <textarea id="txt-reject-reason" class="reason-box" placeholder="Nhập lí do trước khi từ chối..."></textarea>

      <div style="margin: 10px 0; padding: 10px 14px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px;">
        <label style="display: flex; align-items: center; gap: 8px; font-weight: 600; color: #9f1239; cursor: pointer;">
          <input type="checkbox" id="chk-return-goods" style="width: 18px; height: 18px; accent-color: #e11d48;" />
          <span>Yêu cầu trả hàng (Tích chọn nếu hàng hỏng / lỗi chất lượng cần trả về nông dân)</span>
        </label>
        <p style="margin: 4px 0 0 26px; font-size: 11.5px; color: #64748b;">
          * Nếu không tích: Lô hàng chỉ sai thông tin, Nông dân có 24h để sửa lại thông tin trước khi hệ thống tự động yêu cầu trả hàng.
        </p>
      </div>

      <div class="decision-row">
        <button type="button" class="btn-approve" id="btn-action-approve" ${reportResult === "PASS" ? "" : "disabled"}>APPROVE</button>
        <button type="button" class="btn-reject" id="btn-action-reject">REJECT</button>
      </div>
    `;
  } else if (status === "AUDITED") {
    dynamicBody = `
      <div class="link-row" style="background:#f1f5f9;">
        <span>📄 Báo cáo kiểm nghiệm: <strong>${latestReport?.file_name || "Chưa có báo cáo"}</strong></span>
        ${latestReport ? '<button type="button" class="btn-gray-pill" id="btn-view-report">Xem file</button>' : ""}
      </div>
      <div class="link-row" style="background:#f8fafc;">
        <span>Phòng lab: <strong>${latestReport?.lab_name || "—"}</strong></span>
        <span>Mã phòng lab: <strong>${latestReport?.lab_code || "—"}</strong></span>
      </div>

      <div class="criteria-box">
        <div class="criteria-title">Điều kiện phê duyệt trong Database</div>
        <div class="criteria-grid">
          <div class="criteria-item valid">✓ Laboratory Test Report tồn tại</div>
          <div class="criteria-item valid">✓ SHA-256 hợp lệ</div>
          <div class="criteria-item valid">✓ Report thuộc đúng Sample</div>
          <div class="criteria-item valid">✓ Proof of Integrity hợp lệ</div>
          <div class="criteria-item valid">✓ Sample thuộc đúng Batch</div>
        </div>
      </div>

      <div style="background:#f8fafc; border-radius:8px; padding:12px; font-size:11.5px; color:#64748b; margin-top:12px;">
        <div>Mã băm SHA-256: <code>${latestReport?.file_hash || "Chưa có"}</code></div>
        <div>Trace ID: <strong>${currentBatch.trace_id || currentBatch.traceId || "TRC-9F21-AGT"}</strong></div>
      </div>
    `;
  } else if (status === "REJECTED") {
    dynamicBody = `
      <div class="reject-alert">
        <div class="reject-alert-title">⚠ Lý do từ chối ghi nhận trong Database</div>
        <p class="reject-alert-body">${currentBatch.reason || currentBatch.reject_reason || currentBatch.rejectReason || "Không đạt chuẩn kiểm định chất lượng."}</p>
        <p class="reject-alert-meta">Auditor phụ trách: ${currentBatch.auditor_name || currentAuditorName}</p>
      </div>
    `;
  }

  card.innerHTML = `
    <button class="back-link" id="btn-close-detail" type="button">← Quay lại danh sách</button>
    <div class="detail-header">
      <div>
        <p class="detail-code">${code}</p>
        <h2 class="detail-title">${product}</h2>
      </div>
      ${statusBadge}
    </div>

    <div class="fact-grid">
      <div class="fact"><p class="fact-label">Nông dân</p><p class="fact-value">${farmer}</p></div>
      <div class="fact"><p class="fact-label">Ngày thu hoạch</p><p class="fact-value">${harvest}</p></div>
      <div class="fact"><p class="fact-label">Khối lượng</p><p class="fact-value">${weight}</p></div>
      <div class="fact"><p class="fact-label">Ngày tạo</p><p class="fact-value">${created}</p></div>
      <div class="fact"><p class="fact-label">Nguồn gốc</p><p class="fact-value">${origin}</p></div>
      <div class="fact"><p class="fact-label">Điểm đến</p><p class="fact-value">${currentBatch.destination || "Chưa cập nhật"}</p></div>
    </div>

    ${coldChainSection}
    <h4 class="section-label">Sample liên kết</h4>
    ${sampleSection}
    ${dynamicBody}
  `;

  overlay.hidden = false;
  bindDetailEvents();
}

async function coldChainRequest(path) {
  const response = await fetch(`${API_BASE}/cold-chain/${path}`, {
    headers: getAuthHeaders(),
  });
  const payload = await response.json();
  if (!response.ok)
    throw new Error(payload.detail || "Không thể tải dữ liệu Cold Chain.");
  return payload;
}

async function fetchColdChainAgriBatches() {
  try {
    const payload = await coldChainRequest("agri-batches");
    if (!Array.isArray(payload.data))
      throw new Error("Cold Chain API không trả về danh sách lô hàng.");
    COLD_CHAIN_AGRI_BATCHES = payload.data;
    coldChainBatchesError = null;
    return true;
  } catch (error) {
    coldChainBatchesError = error.message;
    console.warn("Không thể tải lô hàng Cold Chain:", error.message);
    return false;
  }
}

function findTransportBatch(batch) {
  const batchCode = String(batch?.batch_code || batch?.code || "")
    .trim()
    .toUpperCase();
  if (!batchCode) return null;
  return COLD_CHAIN_AGRI_BATCHES.find(
    (transportBatch) =>
      String(
        transportBatch.external_batch_code ||
        transportBatch.batch_code ||
        transportBatch.code ||
        "",
      )
        .trim()
        .toUpperCase() === batchCode,
  ) || null;
}

function getLogisticsStatus(transportBatch) {
  return String(transportBatch?.logistics_status || "")
    .trim()
    .toUpperCase()
    .replace(/[\s-]+/g, "_");
}

function hasAssignedTransport(transportBatch) {
  return transportBatch?.vehicle_id !== null &&
    transportBatch?.vehicle_id !== undefined &&
    String(transportBatch.vehicle_id).trim() !== "";
}

function getTransportStatusLabel(transportBatch) {
  if (!hasAssignedTransport(transportBatch)) return "Chưa lấy hàng";
  const status = getLogisticsStatus(transportBatch);
  return (
    COLD_CHAIN_LOGISTICS_LABELS[status] ||
    status ||
    "Đã điều phối xe vận chuyển"
  );
}

function isBatchInTransit(transportBatch) {
  return COLD_CHAIN_IN_TRANSIT_STATUSES.has(
    getLogisticsStatus(transportBatch),
  );
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function renderTransportStatus(transportBatch) {
  if (coldChainBatchesError) {
    return '<span class="status-tag waiting-result">Không tải được</span>';
  }
  const status = getTransportStatusLabel(transportBatch);
  const className = isBatchInTransit(transportBatch)
    ? "in-transit"
    : "transport-status";
  return `<span class="status-tag ${className}">${escapeHtml(status)}</span>`;
}

function renderTransportDetails(transportBatch) {
  if (!transportBatch) return "";
  const details = [
    ["Điểm lấy hàng", transportBatch.pickup_address],
    ["Điểm giao hàng", transportBatch.consumption_address],
  ].filter(([, value]) => value);
  return details
    .map(
      ([label, value]) =>
        `<p style="margin:4px 0;"><strong>${label}:</strong> ${escapeHtml(value)}</p>`,
    )
    .join("");
}

/* ========================================================
   6. GỌI API: UPLOAD REPORT, APPROVE, REJECT
   ======================================================== */
async function openLabReportFile() {
  const reportWindow = window.open("about:blank", "_blank");
  try {
    const batchId = currentBatch.id || currentBatch.batch_id;
    const res = await fetch(`${API_BASE}/batches/${batchId}/report-file`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Không thể tải file report.");
    const fileUrl = URL.createObjectURL(await res.blob());
    if (reportWindow) reportWindow.location.href = fileUrl;
    else window.location.href = fileUrl;
  } catch (err) {
    if (reportWindow) reportWindow.close();
    alert(`Lỗi: ${err.message}`);
  }
}

function bindDetailEvents() {
  document
    .getElementById("btn-close-detail")
    ?.addEventListener("click", closeDetail);

  document
    .getElementById("btn-view-report")
    ?.addEventListener("click", openLabReportFile);

  document.getElementById("btn-edit-report")?.addEventListener("click", () => {
    const reportForm = document.querySelector(".report-form");
    if (!reportForm || !currentBatch.reports?.[0]) return;
    const report = currentBatch.reports[0];
    editingReportId = report.id;
    reportForm.style.display = "block";
    document.getElementById("r-sample-select").value = report.sample_id;
    document.getElementById("r-result-select").value = report.result;
    document.getElementById("r-lab-name").value = report.lab_name || "";
    document.getElementById("r-lab-code").value = report.lab_code || "";
    document.getElementById("r-report-date").value = report.report_date || "";
    document.getElementById("file-chosen-text").textContent =
      "Giữ file hiện tại nếu không chọn file mới";
    document.getElementById("btn-hash-upload").textContent =
      "Lưu thay đổi và tạo SHA-256";
    reportForm.scrollIntoView({ behavior: "smooth", block: "center" });
  });

  document
    .getElementById("btn-open-create-sample")
    ?.addEventListener("click", () => {
      openCreateSampleModal(currentBatch);
    });

  // Upload Báo cáo kiểm nghiệm lên API
  document
    .getElementById("btn-hash-upload")
    ?.addEventListener("click", async () => {
      const fileInput = document.getElementById("mock-file-input");
      const file = fileInput.files[0];
      const labName = document.getElementById("r-lab-name").value.trim();
      const sampleSelect = document.getElementById("r-sample-select");
      const sampleId = sampleSelect?.value;

      if (!editingReportId && !file)
        return alert("Vui lòng chọn file PDF kết quả kiểm định.");
      if (!labName) return alert("Vui lòng điền tên phòng lab.");
      if (
        !sampleId ||
        !samplesListForBatch(currentBatch).some(
          (sample) => String(sample.id) === String(sampleId),
        )
      ) {
        return alert(
          "Batch phải có Sample hợp lệ trước khi upload Laboratory Test Report.",
        );
      }

      const formData = new FormData();
      formData.append("file", file);
      const batchId =
        currentBatch.id || currentBatch.code || currentBatch.batch_code;
      formData.append("batch_id", batchId);
      formData.append("lab_name", labName);
      formData.append(
        "lab_code",
        document.getElementById("r-lab-code").value.trim(),
      );
      formData.append(
        "result",
        document.getElementById("r-result-select").value,
      );
      formData.append("sample_id", sampleId);
      formData.append(
        "report_date",
        document.getElementById("r-report-date").value,
      );

      try {
        const endpoint = editingReportId
          ? `${API_BASE}/auditor/reports/${editingReportId}`
          : `${API_BASE}/auditor/reports`;
        const res = await fetch(endpoint, {
          method: editingReportId ? "PUT" : "POST",
          headers: {
            ...(getAuthHeaders().Authorization
              ? { Authorization: getAuthHeaders().Authorization }
              : {}),
          },
          body: formData,
        });

        const data = await res.json();
        if (!res.ok)
          throw new Error(
            data.detail || "Không thể upload báo cáo lên Database.",
          );

        alert(
          editingReportId
            ? "Đã lưu thay đổi report vào Database và cập nhật SHA-256."
            : "Upload báo cáo thành công! Mã SHA-256 đã được Backend tính và lưu vào cơ sở dữ liệu.",
        );
        document.getElementById("hash-box").style.display = "block";
        document.getElementById("hash-val-text").textContent = data.file_hash;
        document.getElementById("btn-action-approve").disabled =
          data.result !== "PASS";
        editingReportId = null;
        currentBatch.report = data;
        currentBatch.reports = [
          data,
          ...(currentBatch.reports || []).filter(
            (report) => report.id !== data.id,
          ),
        ];
        await openBatchDetail(currentBatch.id);
      } catch (err) {
        alert(`Lỗi: ${err.message}`);
      }
    });

  // Phê duyệt Lô hàng qua API (POST /batches/{id}/approve)
  document
    .getElementById("btn-action-approve")
    ?.addEventListener("click", async () => {
      const batchId =
        currentBatch.id || currentBatch.code || currentBatch.batch_code;
      try {
        const res = await fetch(
          `${API_BASE}/auditor/batches/${batchId}/approve`,
          {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({ reason: "Auditor approved" }),
          },
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Phê duyệt thất bại.");

        alert(
          `Lô hàng ${currentBatch.batch_code || currentBatch.code} đã được cập nhật trạng thái AUDITED trong Database!`,
        );
        closeDetail();
        await switchTab(activeTab);
      } catch (err) {
        alert(`Lỗi: ${err.message}`);
      }
    });

  // Từ chối Lô hàng qua API (POST /batches/{id}/reject)
  document
    .getElementById("btn-action-reject")
    ?.addEventListener("click", async () => {
      const reason = document.getElementById("txt-reject-reason").value.trim();
      if (!reason) return alert("Vui lòng nhập lý do từ chối.");
      const return_goods = document.getElementById("chk-return-goods")?.checked || false;

      const batchId =
        currentBatch.id || currentBatch.code || currentBatch.batch_code;
      try {
        const res = await fetch(
          `${API_BASE}/auditor/batches/${batchId}/reject`,
          {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({ reason, return_goods }),
          },
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Từ chối thất bại.");

        const noticeMsg = return_goods
          ? "Đã cập nhật trạng thái REJECTED (Có yêu cầu trả hàng) và gửi thông báo đến Nông dân & Kho lạnh!"
          : "Đã cập nhật trạng thái REJECTED (Chờ nông dân sửa trong 24h) và gửi thông báo!";
        alert(noticeMsg);
        closeDetail();
        await switchTab(activeTab);
      } catch (err) {
        alert(`Lỗi: ${err.message}`);
      }
    });
}

function samplesListForBatch(batch) {
  return (batch?.samples || []).filter(
    (sample) => String(sample.batch_id) === String(batch.id),
  );
}

function closeDetail() {
  const overlay = document.getElementById("detail-overlay");
  overlay.hidden = true;
}

document.getElementById("detail-overlay")?.addEventListener("click", (e) => {
  if (e.target.id === "detail-overlay") closeDetail();
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeDetail();
    closeModal();
  }
});

/* ========================================================
   7. GỌI API: TẠO SAMPLE VÀO DATABASE
   ======================================================== */
function openCreateSampleModal(batch) {
  document.getElementById("m-batch-code").value =
    batch.batch_code || batch.code;
  document.getElementById("m-product-name").value =
    batch.product_name || batch.product;
  document.getElementById("m-farmer").value =
    batch.farmer_name || batch.farmer || "";
  document.getElementById("m-origin").value = batch.origin || "";
  document.getElementById("m-sample-id").value =
    `SMP-HN-${Date.now().toString().slice(-4)}`;
  document.getElementById("m-weight").value = "1 kg";
  document.getElementById("m-date").value = new Date()
    .toISOString()
    .split("T")[0];

  document.getElementById("create-sample-modal").hidden = false;
}

function closeModal() {
  document.getElementById("create-sample-modal").hidden = true;
}

document
  .getElementById("btn-close-modal")
  ?.addEventListener("click", closeModal);
document
  .getElementById("btn-cancel-modal")
  ?.addEventListener("click", closeModal);

document
  .getElementById("create-sample-form")
  ?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const samplePayload = {
      batch_id: currentBatch.id,
      sample_id: document.getElementById("m-sample-id").value.trim(),
      sampling_date: document.getElementById("m-date").value,
      sample_quantity: Number.parseFloat(
        document.getElementById("m-weight").value,
      ),
      sample_unit: "kg",
      sampling_location: currentBatch.origin || "Chưa cập nhật",
      sampling_method: "Lấy mẫu kiểm định",
    };

    try {
      const res = await fetch(`${API_BASE}/samples`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(samplePayload),
      });
      const data = await res.json();
      if (!res.ok)
        throw new Error(data.detail || "Không thể tạo mẫu vào Database.");

      alert(
        `Tạo mẫu ${data.sample_code || data.sample_id} vào cơ sở dữ liệu thành công!`,
      );
      closeModal();
      openBatchDetail(currentBatch.id || currentBatch.code);
    } catch (err) {
      alert(`Lỗi: ${err.message}`);
    }
  });

document.getElementById("btn-search")?.addEventListener("click", searchPendingBatches);
document.getElementById("btn-refresh")?.addEventListener("click", async () => {
  document.getElementById("batch-filter-form")?.reset();
  await switchTab(activeTab);
});

/* ========================================================
   8. RENDER TIMELINE & MẪU
   ======================================================== */
function renderAuditTimeline(list) {
  const contentCard = document.querySelector(".content-card");
  let timeline = document.getElementById("audit-timeline-box");

  if (!timeline) {
    timeline = document.createElement("div");
    timeline.id = "audit-timeline-box";
    timeline.className = "timeline-container";
    contentCard.appendChild(timeline);
  }

  timeline.style.display = "block";
  timeline.innerHTML = "";

  if (list.length === 0) {
    timeline.innerHTML =
      '<p style="text-align:center; color:#9ca3af; padding:24px;">Chưa có bản ghi lịch sử nào trong cơ sở dữ liệu.</p>';
    return;
  }

  list.forEach((item) => {
    let dotClass = "dot-approve";
    if (item.action === "REJECT") dotClass = "dot-reject";
    if (item.action === "RESUBMIT") dotClass = "dot-resubmit";

    const div = document.createElement("div");
    div.className = "timeline-item";
    div.innerHTML = `
      <div class="timeline-dot ${dotClass}"></div>
      <div class="timeline-card">
        <div class="timeline-header">
          <div class="timeline-title">
            ${item.title || "Thao tác"} <a href="javascript:void(0)" class="batch-link" onclick="openBatchDetail('${item.batch_code || item.batchCode}')">${item.batch_code || item.batchCode}</a>
          </div>
          <div class="timeline-time">${item.time || item.created_at || ""}</div>
        </div>
        <div class="timeline-desc">
          ${item.product ? `${item.product} — trạng thái: ` : ""}${item.transition || item.details || ""}
        </div>
        ${item.reason ? `<div class="timeline-reason">Lý do: ${item.reason}</div>` : ""}
        <div class="timeline-auditor">Auditor: <strong>${item.auditor_name || item.auditor || "Hệ thống"}</strong></div>
      </div>
    `;
    timeline.appendChild(div);
  });
}

function renderSampleTable(list) {
  const thead = document.getElementById("table-head");
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = "";

  thead.innerHTML = `
    <tr>
      <th>Sample ID</th>
      <th>Batch code</th>
      <th>Sản phẩm</th>
      <th>Trạng thái</th>
    </tr>
  `;

  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#9ca3af; padding:32px;">Không có mẫu nào trong Database.</td></tr>`;
    return;
  }

  list.forEach((s) => {
    let tag = '<span class="status-tag waiting-lab">Chờ gửi lab</span>';
    if (s.status === "HAS_REPORT")
      tag = '<span class="status-tag has-report">Đã có báo cáo</span>';
    if (s.status === "WAITING_RESULT")
      tag = '<span class="status-tag waiting-result">Đang chờ kết quả</span>';

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="code-col">${s.sample_code || s.id}</td>
      <td>${s.batch_code || s.batchCode}</td>
      <td>${s.product_name || s.product || "Nông sản"}</td>
      <td>${tag}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Khởi động trang với dữ liệu từ DB
loadAuditorIdentity();
switchTab("pending");
