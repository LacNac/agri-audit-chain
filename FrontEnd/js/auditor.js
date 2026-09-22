/* ========================================================
   1. DỮ LIỆU MOCK THEO TÀI LIỆU SRS & BA
   ======================================================== */
let BATCHES = [
  {
    code: "AGT-2026-0042",
    product: "Xoài Cát Hòa Lộc",
    createdDate: "19/09/2026",
    harvestDate: "16/09/2026",
    farmer: "Nông trại Ba Thức",
    weight: "180 kg",
    origin: "An Giang",
    status: "PENDING",
    samples: [
      {
        id: "SMP-HN-2026-005",
        date: "16/09/2026",
        weight: "1 kg",
        lab: "TT Kiểm định An Giang",
        status: "WAITING_RESULT",
      },
    ],
    report: null,
    auditor: "Đặng Nhật Hải",
    auditDate: null,
    traceId: null,
    rejectReason: null,
  },
  {
    code: "AGT-2026-0043",
    product: "Chè Thái Nguyên",
    createdDate: "19/09/2026",
    harvestDate: "17/09/2026",
    farmer: "Vườn trái cây Chợ Lách",
    weight: "95 kg",
    origin: "Thái Nguyên",
    status: "PENDING",
    samples: [],
    report: null,
    auditor: "Đặng Nhật Hải",
    auditDate: null,
    traceId: null,
    rejectReason: null,
  },
  {
    code: "AGT-2026-0040",
    product: "Cà phê Robusta",
    createdDate: "19/09/2026",
    harvestDate: "14/09/2026",
    farmer: "Hợp tác xã Tân Cương",
    weight: "320 kg",
    origin: "Đắk Lắk",
    status: "AUDITED",
    samples: [
      {
        id: "SPL-0091",
        date: "16/09/2026",
        weight: "2 kg",
        lab: "Lab Đắk Lắk",
        status: "HAS_REPORT",
      },
    ],
    report: {
      fileName: "phieu-kiem-nghiem-0040.pdf",
      sha256: "3f9c1a7e5b21d0...889fa2e02b8d",
      result: "PASS",
    },
    auditor: "Đặng Nhật Hải",
    auditDate: "19/09/2026",
    traceId: "TRC-9F21-AGT",
    rejectReason: null,
  },
  {
    code: "AGT-2026-0044",
    product: "Bơ Sáp Đắk Lắk",
    createdDate: "19/09/2026",
    harvestDate: "15/09/2026",
    farmer: "Nông trại Ba Thức",
    weight: "180 kg",
    origin: "An Giang",
    status: "REJECTED",
    samples: [
      {
        id: "SPL-0091",
        date: "16/09/2026",
        weight: "1.5 kg",
        lab: "Lab Đắk Lắk",
        status: "HAS_REPORT",
      },
    ],
    report: {
      fileName: "phieu-kiem-nghiem-0044.pdf",
      sha256: "a1b2c3d4...99887766",
      result: "FAIL",
    },
    auditor: "Đặng Nhật Hải",
    auditDate: "18/09/2026 14:32",
    traceId: null,
    rejectReason:
      "Kết quả kiểm nghiệm cho thấy dư lượng thuốc bảo vệ thực vật vượt ngưỡng cho phép. Đề nghị nông dân kiểm tra lại quy trình canh tác và gửi mẫu kiểm nghiệm lại.",
  },
  {
    code: "AGT-2026-0041",
    product: "Sầu riêng Ri6",
    createdDate: "19/09/2026",
    harvestDate: "13/09/2026",
    farmer: "Hợp tác xã Cư M'gar",
    weight: "210 kg",
    origin: "Đắk Lắk",
    status: "AUDITED",
    samples: [
      {
        id: "SPL-0085",
        date: "14/09/2026",
        weight: "3 kg",
        lab: "Lab Tây Nguyên",
        status: "HAS_REPORT",
      },
    ],
    report: {
      fileName: "phieu-kiem-nghiem-0041.pdf",
      sha256: "77fa918b...12ca45bd",
      result: "PASS",
    },
    auditor: "Lê Thu Hằng",
    auditDate: "18/09/2026",
    traceId: "TRC-77FA-SR",
    rejectReason: null,
  },
];

let SAMPLES = [
  {
    id: "SPL-0095",
    batchCode: "AGT-2026-0042",
    product: "Xoài Cát Hòa Lộc",
    farmer: "Nông trại Ba Thức",
    weight: "1 kg",
    date: "16/09/2026",
    origin: "An Giang",
    lab: "Trung tâm Kiểm định Nông sản An Giang",
    sendDate: "17/09/2026",
    status: "WAITING_LAB",
    reportFile: null,
    sha256: null,
  },
  {
    id: "SPL-0094",
    batchCode: "AGT-2026-0043",
    product: "Chè Thái Nguyên",
    farmer: "Vườn trái cây Chợ Lách",
    weight: "500 g",
    date: "16/09/2026",
    origin: "Thái Nguyên",
    lab: "Viện Khoa học Nông nghiệp",
    sendDate: "17/09/2026",
    status: "HAS_REPORT",
    reportFile: "phieu-kiem-nghiem-0042.pdf",
    sha256: "3f9c1a7e5b21d0...889fa2e02b8d",
  },
  {
    id: "SPL-0093",
    batchCode: "AGT-2026-0040",
    product: "Cà phê Robusta",
    farmer: "Hợp tác xã Tân Cương",
    weight: "2 kg",
    date: "16/09/2026",
    origin: "Đắk Lắk",
    lab: "Trung tâm Kiểm định Nông sản An Giang",
    sendDate: "17/09/2026",
    status: "WAITING_RESULT",
    reportFile: null,
    sha256: null,
  },
  {
    id: "SPL-0092",
    batchCode: "AGT-2026-0044",
    product: "Gạo Tám thơm",
    farmer: "Nông trại Hải Hậu",
    weight: "1 kg",
    date: "16/09/2026",
    origin: "Nam Định",
    lab: "Lab An Giang",
    sendDate: "17/09/2026",
    status: "WAITING_RESULT",
    reportFile: null,
    sha256: null,
  },
  {
    id: "SPL-0091",
    batchCode: "AGT-2026-0041",
    product: "Sầu riêng Ri6",
    farmer: "Hợp tác xã Cư M'gar",
    weight: "3 kg",
    date: "16/09/2026",
    origin: "Đắk Lắk",
    lab: "Lab Tây Nguyên",
    sendDate: "17/09/2026",
    status: "WAITING_LAB",
    reportFile: null,
    sha256: null,
  },
];

let AUDIT_HISTORY = [
  {
    action: "APPROVE",
    title: "Đã phê duyệt",
    batchCode: "AGT-2026-0042",
    product: "Xoài Cát Hòa Lộc",
    transition: "UNVERIFIED → AUDITED",
    reason: null,
    auditor: "Đặng Nhật Hải",
    time: "19/09, 15:04",
  },
  {
    action: "REJECT",
    title: "Đã từ chối",
    batchCode: "AGT-2026-0037",
    product: "Bơ Sáp Đắk Lắk",
    transition: "UNVERIFIED → REJECTED",
    reason: "Dư lượng thuốc BVTV vượt ngưỡng cho phép",
    auditor: "Đặng Nhật Hải",
    time: "18/09, 14:32",
  },
  {
    action: "APPROVE",
    title: "Đã phê duyệt",
    batchCode: "AGT-2026-0038",
    product: "Cà phê Robusta",
    transition: "UNVERIFIED → AUDITED",
    reason: null,
    auditor: "Lê Thu Hằng",
    time: "18/09, 09:47",
  },
  {
    action: "RESUBMIT",
    title: "Đã gửi lại kiểm định",
    batchCode: "AGT-2026-0037",
    product: null,
    transition: "Nông dân đã bổ sung hồ sơ — chờ Auditor xem xét lại",
    reason: null,
    auditor: "Nông dân Ba Thức (Tiếp nhận: Đặng Nhật Hải)",
    time: "17/09, 11:20",
  },
];

let activeTab = "pending";
let currentBatch = null;

/* ========================================================
   2. QUẢN LÝ CHUYỂN TAB VÀ ĐIỀU HƯỚNG
   ======================================================== */
document.querySelectorAll(".sidebar-nav .nav-item").forEach((btn) => {
  btn.addEventListener("click", () => {
    document
      .querySelectorAll(".sidebar-nav .nav-item")
      .forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    activeTab = btn.getAttribute("data-tab");
    switchTab(activeTab);
  });
});

function switchTab(tab) {
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

    // Đổi form lọc sang 3 ô chuẩn ảnh
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
            h.batchCode.toLowerCase().includes(code) &&
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

    let titleText = "Danh sách chờ duyệt";
    let filterStatus = "PENDING";
    let countLabel = "Tổng lô hàng chưa duyệt";
    let countNum = BATCHES.filter((b) => b.status === "PENDING").length;

    if (tab === "approved") {
      titleText = "Danh sách đã duyệt";
      filterStatus = "AUDITED";
      countLabel = "Tổng lô hàng đã duyệt";
      countNum = 192;
    } else if (tab === "rejected") {
      titleText = "Danh sách từ chối";
      filterStatus = "REJECTED";
      countLabel = "Tổng lô hàng từ chối";
      countNum = BATCHES.filter((b) => b.status === "REJECTED").length;
    }

    heading.textContent = titleText;
    statContainer.innerHTML = `
      <div class="counter-box">
        <span>${countLabel}</span>
        <div class="box-badge">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5c33cf" stroke-width="2"><path d="M21 8 12 3 3 8l9 5 9-5Z"/><path d="M3 8v9l9 5 9-5V8"/><path d="M12 13v9"/></svg>
          <strong>${countNum}</strong>
        </div>
      </div>
    `;

    renderBatchTable(filterStatus);
  }
}

/* ========================================================
   3. RENDER BẢNG BATCH (CÁC TAB DANH SÁCH)
   ======================================================== */
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
    </tr>
  `;

  let list = BATCHES.filter((b) => b.status === statusFilter);

  list.forEach((b) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="code-col">${b.code}</td>
      <td>${b.product}</td>
      <td>${b.auditDate || b.createdDate}</td>
      <td>${b.farmer}</td>
    `;
    tr.addEventListener("click", () => openBatchDetail(b.code));
    tbody.appendChild(tr);
  });
}

/* ========================================================
   4. RENDER TIMELINE DÒNG THỜI GIAN (TAB LỊCH SỬ)
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
            ${item.title} <a href="javascript:void(0)" class="batch-link" onclick="openBatchDetail('${item.batchCode}')">${item.batchCode}</a>
          </div>
          <div class="timeline-time">${item.time}</div>
        </div>
        <div class="timeline-desc">
          ${item.product ? `${item.product} — trạng thái: ` : ""}${item.transition}
        </div>
        ${item.reason ? `<div class="timeline-reason">Lý do: ${item.reason}</div>` : ""}
        <div class="timeline-auditor">Auditor thực hiện: <strong>${item.auditor}</strong></div>
      </div>
    `;
    timeline.appendChild(div);
  });
}

/* ========================================================
   5. RENDER BẢNG QUẢN LÝ MẪU (SAMPLES)
   ======================================================== */
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

  list.forEach((s) => {
    let tag = '<span class="status-tag waiting-lab">Chờ gửi lab</span>';
    if (s.status === "HAS_REPORT")
      tag = '<span class="status-tag has-report">Đã có báo cáo</span>';
    if (s.status === "WAITING_RESULT")
      tag = '<span class="status-tag waiting-result">Đang chờ kết quả</span>';

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="code-col">${s.id}</td>
      <td>${s.batchCode}</td>
      <td>${s.product}</td>
      <td>${tag}</td>
    `;
    tr.addEventListener("click", () => openSampleDetail(s.id));
    tbody.appendChild(tr);
  });
}

/* ========================================================
   6. OVERLAY XEM CHI TIẾT BATCH
   ======================================================== */
function openBatchDetail(code) {
  currentBatch = BATCHES.find((b) => b.code === code);
  if (!currentBatch) return;

  const card = document.getElementById("detail-card-content");
  const overlay = document.getElementById("detail-overlay");

  let statusBadge = '<span class="status-badge amber">Chờ kiểm định</span>';
  if (currentBatch.status === "AUDITED")
    statusBadge = '<span class="status-badge green">Đã kiểm định</span>';
  if (currentBatch.status === "REJECTED")
    statusBadge = '<span class="status-badge red">Bị từ chối</span>';

  let sampleSection = "";
  if (currentBatch.samples.length === 0) {
    sampleSection = `
      <div class="link-row">
        <span>📎 Sample</span>
        <button type="button" class="btn-chip" id="btn-open-create-sample">+ Tạo sample mới</button>
      </div>
    `;
  } else {
    const s = currentBatch.samples[0];
    sampleSection = `
      <div class="link-row" style="background:#ede9fe;">
        <span><strong>${s.id}</strong></span>
        <span style="color:#64748b; font-size:12px;">Lấy mẫu ${s.date}</span>
      </div>
    `;
  }

  let dynamicBody = "";
  if (currentBatch.status === "PENDING") {
    dynamicBody = `
      <div class="link-row">
        <span>📄 Báo cáo kiểm nghiệm: <strong id="report-name">${currentBatch.report ? currentBatch.report.fileName : "chưa có"}</strong></span>
        <button type="button" class="btn-action-blue" id="btn-mock-upload">+ Upload báo cáo</button>
      </div>

      <div class="report-form">
        <h4 style="margin:0 0 12px; font-size:13px;">Upload report mới</h4>
        <div class="form-grid">
          <div class="form-field">
            <label>Sample</label>
            <select id="r-sample-select">
              ${currentBatch.samples.map((s) => `<option value="${s.id}">${s.id}</option>`).join("") || "<option>— Chưa có Sample —</option>"}
            </select>
          </div>
          <div class="form-field">
            <label>Kết quả</label>
            <select id="r-result-select"><option value="PASS">PASS</option><option value="FAIL">FAIL</option></select>
          </div>
          <div class="form-field"><label>Tên phòng lab</label><input type="text" id="r-lab-name" placeholder="VD: TT Kiểm định An Giang" /></div>
          <div class="form-field"><label>Mã phòng lab</label><input type="text" placeholder="VD: LAB-AG-01" /></div>
          <div class="form-field"><label>Ngày báo cáo</label><input type="date" /></div>
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
          <p class="fact-label">MÃ BĂM SHA-256</p>
          <p class="hash-value" id="hash-val-text"></p>
        </div>
      </div>

      <h4 class="section-label">Lí do từ chối</h4>
      <textarea id="txt-reject-reason" class="reason-box" placeholder="Nhập lí do trước khi từ chối..."></textarea>

      <div class="decision-row">
        <button type="button" class="btn-approve" id="btn-action-approve" ${currentBatch.report ? "" : "disabled"}>APPROVE</button>
        <button type="button" class="btn-reject" id="btn-action-reject">REJECT</button>
      </div>
    `;
  } else if (currentBatch.status === "AUDITED") {
    dynamicBody = `
      <div class="link-row" style="background:#f1f5f9;">
        <span>📄 Báo cáo kiểm nghiệm &nbsp;<a href="#" style="text-decoration:underline; font-weight:600;">${currentBatch.report?.fileName || "phieu-kiem-nghiem.pdf"}</a></span>
        <button type="button" class="btn-gray-pill">Xem file</button>
      </div>

      <div class="criteria-box">
        <div class="criteria-title">Điều kiện phê duyệt</div>
        <div class="criteria-grid">
          <div class="criteria-item valid">✓ Laboratory Test Report tồn tại</div>
          <div class="criteria-item valid">✓ SHA-256 hợp lệ</div>
          <div class="criteria-item valid">✓ Report thuộc đúng Sample</div>
          <div class="criteria-item valid">✓ Proof of Integrity hợp lệ</div>
          <div class="criteria-item valid">✓ Sample thuộc đúng Batch</div>
        </div>
      </div>

      <div class="link-row" style="background:#f1f5f9;">
        <span>📄 Biên bản kiểm định</span>
        <button type="button" class="btn-gray-pill">Xem file</button>
      </div>

      <div style="background:#f8fafc; border-radius:8px; padding:12px; font-size:11.5px; color:#64748b; margin-top:12px;">
        <div>Mã băm SHA-256 báo cáo: <code>${currentBatch.report?.sha256 || "3f9c1a7e5b21d0...889fa2e02b8d"}</code></div>
        <div>Trace ID: <strong>${currentBatch.traceId || "TRC-9F21-AGT"}</strong></div>
      </div>

      <div class="qr-section">
        <div class="qr-left">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#1f2937" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="3" height="3"/><rect x="18" y="14" width="3" height="3"/><rect x="14" y="18" width="3" height="3"/><rect x="18" y="18" width="3" height="3"/></svg>
          <span>Mã QR đã kích hoạt, sẵn sàng in lên bao bì</span>
        </div>
        <button type="button" class="btn btn-purple" style="background:#60a5fa;" onclick="alert('Đang tải xuống tệp QR Code...')">Tải QR</button>
      </div>
    `;
  } else if (currentBatch.status === "REJECTED") {
    dynamicBody = `
      <div class="link-row" style="background:#f1f5f9;">
        <span>📄 Báo cáo kiểm nghiệm &nbsp;<a href="#" style="text-decoration:underline;">${currentBatch.report?.fileName || "phieu-kiem-nghiem.pdf"}</a></span>
        <button type="button" class="btn-gray-pill">Xem file</button>
      </div>

      <div class="criteria-box">
        <div class="criteria-title">Điều kiện phê duyệt</div>
        <div class="criteria-grid">
          <div class="criteria-item invalid">✕ Laboratory Test Report không đạt chuẩn</div>
          <div class="criteria-item valid">✓ SHA-256 hợp lệ</div>
          <div class="criteria-item valid">✓ Report thuộc đúng Sample</div>
          <div class="criteria-item valid">✓ Proof of Integrity hợp lệ</div>
          <div class="criteria-item valid">✓ Sample thuộc đúng Batch</div>
        </div>
      </div>

      <div class="reject-alert">
        <div class="reject-alert-title">⚠ Lý do từ chối</div>
        <p class="reject-alert-body">${currentBatch.rejectReason}</p>
        <p class="reject-alert-meta">Từ chối bởi: ${currentBatch.auditor} — ${currentBatch.auditDate}</p>
      </div>
    `;
  }

  card.innerHTML = `
    <button class="back-link" id="btn-close-detail" type="button">
      ← Quay lại danh sách
    </button>
    <div class="detail-header">
      <div>
        <p class="detail-code">${currentBatch.code}</p>
        <h2 class="detail-title">${currentBatch.product}</h2>
      </div>
      ${statusBadge}
    </div>

    <div class="fact-grid">
      <div class="fact"><p class="fact-label">Nông dân</p><p class="fact-value">${currentBatch.farmer}</p></div>
      <div class="fact"><p class="fact-label">Ngày thu hoạch</p><p class="fact-value">${currentBatch.harvestDate}</p></div>
      <div class="fact"><p class="fact-label">Khối lượng</p><p class="fact-value">${currentBatch.weight}</p></div>
      <div class="fact"><p class="fact-label">Ngày tạo hồ sơ</p><p class="fact-value">${currentBatch.createdDate}</p></div>
      <div class="fact"><p class="fact-label">Nguồn gốc</p><p class="fact-value">${currentBatch.origin}</p></div>
    </div>

    <h4 class="section-label">Sample liên kết</h4>
    ${sampleSection}
    ${dynamicBody}
  `;

  overlay.hidden = false;
  bindDetailEvents();
}

/* ========================================================
   7. OVERLAY XEM CHI TIẾT SAMPLE (QUẢN LÝ MẪU)
   ======================================================== */
function openSampleDetail(sampleId) {
  const sample = SAMPLES.find((s) => s.id === sampleId);
  if (!sample) return;

  const card = document.getElementById("detail-card-content");
  const overlay = document.getElementById("detail-overlay");

  let badge = '<span class="status-badge amber">Chờ gửi lab</span>';
  let banner = `
    <div class="report-form" style="margin-top:20px;">
      <h4 style="margin:0 0 8px; font-size:13px;">Trung tâm kiểm nghiệm</h4>
      <p style="color:#64748b; font-size:12.5px; border:1px dashed #cbd5e1; padding:12px; border-radius:8px;">Chưa gửi đến phòng thí nghiệm</p>
      <button class="btn btn-purple" style="background:#93c5fd; color:#1e3a8a; width:100%; margin-top:8px;" id="btn-mark-sent">🌿 Đánh dấu đã gửi lab</button>
    </div>
  `;

  if (sample.status === "WAITING_RESULT") {
    badge = '<span class="status-badge blue">Đang chờ kết quả</span>';
    banner = `
      <div class="link-row" style="background:#ede9fe; margin-top:20px;">
        <span><strong>${sample.lab}</strong></span>
        <span style="font-size:12px; color:#64748b;">Gửi mẫu ${sample.sendDate}</span>
      </div>
      <div class="link-row">
        <span>📎 Báo cáo kiểm nghiệm</span>
        <button class="btn-action-blue" id="btn-sample-upload">+ Upload báo cáo</button>
      </div>
      <div class="status-banner banner-yellow">
        ⌛ Đã gửi lab 1 ngày trước — chưa có kết quả
      </div>
    `;
  } else if (sample.status === "HAS_REPORT") {
    badge = '<span class="status-badge green">Đã có báo cáo</span>';
    banner = `
      <div class="link-row" style="background:#ede9fe; margin-top:20px;">
        <span><strong>${sample.lab}</strong></span>
        <span style="font-size:12px; color:#64748b;">Gửi mẫu ${sample.sendDate}</span>
      </div>
      <div class="link-row">
        <span>📎 Báo cáo kiểm nghiệm &nbsp;<a href="#" style="text-decoration:underline;">${sample.reportFile}</a></span>
        <button class="btn-gray-pill">Xem file</button>
      </div>
      <div style="background:#f8fafc; border-radius:8px; padding:10px; font-size:11.5px; color:#64748b; margin:12px 0;">
        Mã băm SHA-256 báo cáo:<br><code>${sample.sha256}</code>
      </div>
      <div class="status-banner banner-blue">
        ➔ Mẫu đã đủ điều kiện — Batch ${sample.batchCode} có thể được Submit để kiểm định
      </div>
    `;
  }

  card.innerHTML = `
    <button class="back-link" id="btn-close-detail" type="button">
      ← Quay lại danh sách mẫu
    </button>
    <div class="detail-header">
      <div>
        <p class="detail-code">${sample.id}</p>
        <h2 class="detail-title">Mẫu - ${sample.product}</h2>
      </div>
      ${badge}
    </div>

    <div class="fact-grid">
      <div class="fact"><p class="fact-label">Nông dân</p><p class="fact-value">${sample.farmer}</p></div>
      <div class="fact"><p class="fact-label">Batch liên kết</p><p class="fact-value">${sample.batchCode}</p></div>
      <div class="fact"><p class="fact-label">Khối lượng mẫu</p><p class="fact-value">${sample.weight}</p></div>
      <div class="fact"><p class="fact-label">Ngày lấy mẫu</p><p class="fact-value">${sample.date}</p></div>
      <div class="fact"><p class="fact-label">Nguồn gốc</p><p class="fact-value">${sample.origin}</p></div>
    </div>

    ${banner}
  `;

  overlay.hidden = false;
  document
    .getElementById("btn-close-detail")
    .addEventListener("click", closeDetail);

  const btnMark = document.getElementById("btn-mark-sent");
  if (btnMark) {
    btnMark.addEventListener("click", () => {
      sample.status = "WAITING_RESULT";
      sample.sendDate = new Date().toLocaleDateString("vi-VN");
      alert(
        `Đã chuyển trạng thái mẫu ${sample.id} sang "Đang chờ kết quả" từ lab.`,
      );
      openSampleDetail(sample.id);
      renderSampleTable(SAMPLES);
    });
  }

  const btnUp = document.getElementById("btn-sample-upload");
  if (btnUp) {
    btnUp.addEventListener("click", () => {
      sample.status = "HAS_REPORT";
      sample.reportFile = `phieu-kiem-nghiem-${sample.id.toLowerCase()}.pdf`;
      sample.sha256 = "3f9c1a7e5b21d0...889fa2e02b8d";
      alert(
        `Đã tải lên báo cáo kiểm nghiệm và tạo mã băm SHA-256 cho mẫu ${sample.id}.`,
      );
      openSampleDetail(sample.id);
      renderSampleTable(SAMPLES);
    });
  }
}

/* ========================================================
   8. SỰ KIỆN DUYỆT / TỪ CHỐI / ĐÓNG OVERLAY
   ======================================================== */
function bindDetailEvents() {
  document
    .getElementById("btn-close-detail")
    ?.addEventListener("click", closeDetail);

  document
    .getElementById("btn-open-create-sample")
    ?.addEventListener("click", () => {
      openCreateSampleModal(currentBatch);
    });

  document.getElementById("btn-hash-upload")?.addEventListener("click", () => {
    const file = document.getElementById("mock-file-input").files[0];
    const labName = document.getElementById("r-lab-name").value.trim();
    if (!labName) return alert("Vui lòng nhập tên phòng lab kiểm nghiệm.");

    const mockHash =
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
    currentBatch.report = {
      fileName: file ? file.name : "bao-cao-kiem-nghiem.pdf",
      sha256: mockHash,
      result: document.getElementById("r-result-select").value,
    };

    document.getElementById("hash-box").style.display = "block";
    document.getElementById("hash-val-text").textContent = mockHash;
    document.getElementById("report-name").textContent =
      currentBatch.report.fileName;
    document.getElementById("btn-action-approve").disabled = false;
    alert("Đã upload báo cáo và niêm phong số bằng mã băm SHA-256.");
  });

  document
    .getElementById("btn-action-approve")
    ?.addEventListener("click", () => {
      currentBatch.status = "AUDITED";
      currentBatch.auditDate = new Date().toLocaleDateString("vi-VN");
      currentBatch.traceId = `TRC-${Math.random().toString(36).substring(2, 6).toUpperCase()}-AGT`;

      // Thêm vào đầu lịch sử
      AUDIT_HISTORY.unshift({
        action: "APPROVE",
        title: "Đã phê duyệt",
        batchCode: currentBatch.code,
        product: currentBatch.product,
        transition: "UNVERIFIED → AUDITED",
        reason: null,
        auditor: "Đặng Nhật Hải",
        time: "Vừa xong",
      });

      alert(
        `Lô hàng ${currentBatch.code} đã được APPROVE thành công! Mã QR đã được kích hoạt.`,
      );
      closeDetail();
      switchTab(activeTab);
    });

  document
    .getElementById("btn-action-reject")
    ?.addEventListener("click", () => {
      const reason = document.getElementById("txt-reject-reason").value.trim();
      if (!reason) {
        alert("Vui lòng nhập lý do từ chối trước khi Reject.");
        document.getElementById("txt-reject-reason").focus();
        return;
      }
      currentBatch.status = "REJECTED";
      currentBatch.auditDate =
        new Date().toLocaleDateString("vi-VN") +
        " " +
        new Date().toLocaleTimeString("vi-VN", {
          hour: "2-digit",
          minute: "2-digit",
        });
      currentBatch.rejectReason = reason;

      // Thêm vào đầu lịch sử
      AUDIT_HISTORY.unshift({
        action: "REJECT",
        title: "Đã từ chối",
        batchCode: currentBatch.code,
        product: currentBatch.product,
        transition: "UNVERIFIED → REJECTED",
        reason: reason,
        auditor: "Đặng Nhật Hải",
        time: "Vừa xong",
      });

      alert(`Lô hàng ${currentBatch.code} đã chuyển sang trạng thái REJECTED.`);
      closeDetail();
      switchTab(activeTab);
    });
}

function closeDetail() {
  const overlay = document.getElementById("detail-overlay");
  overlay.hidden = true;
}

document.getElementById("detail-overlay").addEventListener("click", (e) => {
  if (e.target.id === "detail-overlay") closeDetail();
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeDetail();
    closeModal();
  }
});

/* ========================================================
   9. MODAL TẠO SAMPLE CHO AUDITOR
   ======================================================== */
function openCreateSampleModal(batch) {
  document.getElementById("m-batch-code").value = batch.code;
  document.getElementById("m-product-name").value = batch.product;
  document.getElementById("m-farmer").value = batch.farmer;
  document.getElementById("m-origin").value = batch.origin;
  document.getElementById("m-sample-id").value =
    `SPL-0${100 + SAMPLES.length + 1}`;
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
  .addEventListener("click", closeModal);
document
  .getElementById("btn-cancel-modal")
  .addEventListener("click", closeModal);

document
  .getElementById("create-sample-form")
  .addEventListener("submit", (e) => {
    e.preventDefault();
    const newSampleId = document.getElementById("m-sample-id").value.trim();
    const weight = document.getElementById("m-weight").value.trim();
    const dateStr = document.getElementById("m-date").value;
    const targetLab =
      document.getElementById("m-lab-target").value.trim() ||
      "Chưa gửi phòng lab";

    const newSampleObj = {
      id: newSampleId,
      batchCode: currentBatch.code,
      product: currentBatch.product,
      farmer: currentBatch.farmer,
      weight: weight,
      date: dateStr,
      origin: currentBatch.origin,
      lab: targetLab,
      sendDate: null,
      status: "WAITING_LAB",
      reportFile: null,
      sha256: null,
    };

    SAMPLES.unshift(newSampleObj);
    currentBatch.samples.unshift({
      id: newSampleId,
      date: dateStr,
      weight,
      lab: targetLab,
      status: "WAITING_LAB",
    });

    alert(
      `Đã khởi tạo Sample [${newSampleId}] thành công cho lô hàng ${currentBatch.code}.`,
    );
    closeModal();
    openBatchDetail(currentBatch.code);
  });

/* ========================================================
   10. TÌM KIẾM VÀ LÀM MỚI
   ======================================================== */
document.getElementById("btn-search")?.addEventListener("click", () => {
  if (activeTab === "samples") {
    const idVal = document.getElementById("sf-id").value.trim().toLowerCase();
    const batchVal = document
      .getElementById("sf-batch")
      .value.trim()
      .toLowerCase();
    const statusVal = document.getElementById("sf-status").value;

    const filtered = SAMPLES.filter(
      (s) =>
        s.id.toLowerCase().includes(idVal) &&
        s.batchCode.toLowerCase().includes(batchVal) &&
        (!statusVal || s.status === statusVal),
    );
    renderSampleTable(filtered);
  } else {
    const code = document.getElementById("f-code").value.trim().toLowerCase();
    const product = document
      .getElementById("f-product")
      .value.trim()
      .toLowerCase();
    const farmer = document
      .getElementById("f-farmer")
      .value.trim()
      .toLowerCase();

    let targetBatches = BATCHES;
    if (activeTab === "pending")
      targetBatches = BATCHES.filter((b) => b.status === "PENDING");
    if (activeTab === "approved")
      targetBatches = BATCHES.filter((b) => b.status === "AUDITED");
    if (activeTab === "rejected")
      targetBatches = BATCHES.filter((b) => b.status === "REJECTED");

    const filtered = targetBatches.filter(
      (b) =>
        b.code.toLowerCase().includes(code) &&
        b.product.toLowerCase().includes(product) &&
        b.farmer.toLowerCase().includes(farmer),
    );
    renderBatchTable(
      activeTab === "pending"
        ? "PENDING"
        : activeTab === "approved"
          ? "AUDITED"
          : "REJECTED",
    );
  }
});

document.getElementById("btn-refresh")?.addEventListener("click", () => {
  document.getElementById("batch-filter-form")?.reset();
  document.getElementById("sample-filter-form")?.reset();
  switchTab(activeTab);
});

/* ========================================================
   KHỞI ĐỘNG MẶC ĐỊNH
   ======================================================== */
switchTab("pending");
