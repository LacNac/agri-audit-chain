/* ============================ ICONS ============================ */
const ICONS = {
  /* Logo mark: scan-corner frame + QR pattern + leaf, gradient xanh -> tím giống bản gốc */
  logoMark: `<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="scanBlue" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#2F6BFF"/><stop offset="1" stop-color="#4B3BE0"/>
      </linearGradient>
      <linearGradient id="scanPurple" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#6C3BEA"/><stop offset="1" stop-color="#8B3BE0"/>
      </linearGradient>
      <linearGradient id="leafGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#3B7BFF"/><stop offset="1" stop-color="#2F5BE0"/>
      </linearGradient>
    </defs>
    <path d="M3 13V8a2 2 0 0 1 2-2h5" stroke="url(#scanBlue)" stroke-width="2.6" stroke-linecap="round"/>
    <path d="M37 13V8a2 2 0 0 0-2-2h-5" stroke="url(#scanPurple)" stroke-width="2.6" stroke-linecap="round"/>
    <path d="M3 27v5a2 2 0 0 0 2 2h5" stroke="url(#scanBlue)" stroke-width="2.6" stroke-linecap="round"/>
    <path d="M37 27v5a2 2 0 0 1-2 2h-5" stroke="url(#scanPurple)" stroke-width="2.6" stroke-linecap="round"/>
    <g fill="#2F49B8">
      <rect x="10" y="10" width="6" height="6" rx="1"/>
      <rect x="12" y="12" width="2" height="2" rx="0.4" fill="#fff"/>
      <rect x="22" y="10" width="6" height="6" rx="1"/>
      <rect x="24" y="12" width="2" height="2" rx="0.4" fill="#fff"/>
      <rect x="10" y="22" width="6" height="6" rx="1"/>
      <rect x="12" y="24" width="2" height="2" rx="0.4" fill="#fff"/>
      <rect x="22" y="10.5" width="2.2" height="2.2"/>
      <rect x="26.5" y="18" width="2.2" height="2.2"/>
      <rect x="22" y="22" width="2.2" height="2.2"/>
    </g>
    <path d="M15 20c5 0 9 3.5 9 8.2 0 .5-.4.8-.9.7-4.7-1-8.1-4.6-8.1-8.9Z" fill="url(#leafGrad)"/>
  </svg>`,
  overview: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="3" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.8"/><rect x="13" y="3" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.8"/><rect x="3" y="13" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.8"/><rect x="13" y="13" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.8"/></svg>`,
  batches: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 7l8-4 8 4-8 4-8-4Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M4 7v10l8 4 8-4V7" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M12 11v10" stroke="currentColor" stroke-width="1.8"/></svg>`,
  search: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.8"/><path d="M21 21l-4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>`,
  logout: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 4H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M21 12H10M21 12l-4-4M21 12l-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  qrSmall: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="3" width="7" height="7" rx="1" stroke="white" stroke-width="1.6"/><rect x="14" y="3" width="7" height="7" rx="1" stroke="white" stroke-width="1.6"/><rect x="3" y="14" width="7" height="7" rx="1" stroke="white" stroke-width="1.6"/><rect x="15" y="15" width="2" height="2" fill="white"/><rect x="19" y="15" width="2" height="2" fill="white"/><rect x="15" y="19" width="2" height="2" fill="white"/></svg>`,
  file: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M14 2v6h6" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>`,
  menu: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></svg>`,
};

function renderLogo() {
  return `<div class="logo" onclick="navigate('overview')">
    <img src="../assets/logo-icon.svg" class="logo-icon" alt="AgriTrace">
    <img src="../assets/logo-text.svg" class="logo-text" alt="AgriTrace">
  </div>`;
}

/* ============================ STATE ============================ */
const REQUIRED_PROFILE_FIELDS = [
  "fullName",
  "dob",
  "phone",
  "email",
  "address",
  "farmName",
  "landArea",
  "businessType",
  "mainProduct",
  "region",
];

const state = {
  page: "overview", // overview | batches | profile
  filter: "all", // all | pending | approved | rejected
  search: "",
  modal: null, // {type:'detail', id} | {type:'create'} | {type:'editProfile'}
  loggedOut: false,
  mobileMenuOpen: false,
  toastTimer: null,
  createForm: {
    productName: "",
    category: "",
    harvestDate: "",
    origin: "",
    quantity: "",
    unit: "kg",
    note: "",
  },
  createErrors: {},
  editForm: null,
  editErrors: {},
  batches: [
    {
      id: "BATCH-2026-0417",
      product: "Cà phê Robusta",
      harvestDate: "29/08/2026",
      quantity: "1.200 kg",
      status: "approved",
      origin: "Đắk Lắk",
      note: "N/A",
      sample: {
        id: "SPL-A102",
        desc: "Lấy mẫu ngày 31/08/2026 · Mẫu hạt xanh, lô 1",
      },
      trace: { id: "TR-88F2-A0T" },
      report: "BATCH_2026_0417.pdf",
    },
    {
      id: "BATCH-2026-0418",
      product: "Gạo Tám thơm",
      harvestDate: "24/08/2026",
      quantity: "100.000 kg",
      status: "pending",
      origin: "An Giang",
      note: "N/A",
      sample: {
        id: "SPL-B1011",
        desc: "Lấy mẫu ngày 27/08/2026 · Lấy mẫu tại kho chứa",
      },
    },
    {
      id: "BATCH-2026-0409",
      product: "Chè Thái Nguyên",
      harvestDate: "13/07/2026",
      quantity: "200 kg",
      status: "approved",
      origin: "Thái Nguyên",
      note: "N/A",
      sample: { id: "SPL-C204", desc: "Lấy mẫu ngày 10/07/2026 · Mẫu lá tươi" },
      trace: { id: "TR-51C9-K3D" },
      report: "BATCH_2026_0409.pdf",
    },
    {
      id: "BATCH-2026-01199",
      product: "Sầu riêng Ri6",
      harvestDate: "22/01/2026",
      quantity: "100 kg",
      status: "rejected",
      origin: "Sóc Trăng",
      note: "N/A",
      sample: {
        id: "SPL-A102",
        desc: "Lấy mẫu ngày 20/01/2026 · Mẫu lấy từ 5 trái",
      },
      rejectReason:
        "AUDITOR TỪ CHỐI LÔ HÀNG: Báo cáo kiểm nghiệm phòng lab (Laboratory Report) ghi nhận chỉ số thuốc bảo vệ thực vật, kim loại nặng vượt mức cho phép theo quy định chất lượng.",
      report: "BATCH_2026_01199.pdf",
    },
  ],
  profile: {
    fullName: "Nguyễn Văn A",
    dob: "12/01/1978",
    phone: "0998776544",
    email: "abc@gmail.com",
    address: "phường Hạc Thành, Thanh Hóa",
    farmName: "Trang trại HH",
    landArea: "",
    businessType: "Nông trại",
    mainProduct: "Cà phê Robusta",
    taxCode: "",
    region: "Thanh Hóa",
    username: "abc@gmail.com",
    role: "FARMER",
    status: "Đang hoạt động",
    joinDate: "05/12/2019",
  },
};

const API_BASE = "http://127.0.0.1:8000";

function getCurrentSession() {
  const serialized =
    sessionStorage.getItem("currentUser") ||
    localStorage.getItem("currentUser");
  if (!serialized) return null;
  try {
    return JSON.parse(serialized);
  } catch {
    return null;
  }
}

function clearCurrentSession() {
  sessionStorage.removeItem("currentUser");
  localStorage.removeItem("currentUser");
}

async function loadQrImage(batch) {
  const session = getCurrentSession();
  if (!session?.access_token || !batch?.batchId) return;
  const response = await fetch(`${API_BASE}/qr/${batch.batchId}/image`, {
    headers: { Authorization: `Bearer ${session.access_token}` },
  });
  if (!response.ok) throw new Error("Không thể tải mã QR");
  const blob = await response.blob();
  if (batch.qrImageUrl) URL.revokeObjectURL(batch.qrImageUrl);
  batch.qrImageUrl = URL.createObjectURL(blob);
}

async function loadReportPdf(batch) {
  const session = getCurrentSession();
  if (!session?.access_token || !batch?.batchId || !batch.report) return;
  const response = await fetch(
    `${API_BASE}/batches/${batch.batchId}/report-file`,
    {
      headers: { Authorization: `Bearer ${session.access_token}` },
    },
  );
  if (!response.ok) return;
  const blob = await response.blob();
  if (batch.reportPdfUrl) URL.revokeObjectURL(batch.reportPdfUrl);
  batch.reportPdfUrl = URL.createObjectURL(blob);
}

async function generateQr(id) {
  const batch = state.batches.find((item) => item.id === id);
  const session = getCurrentSession();
  if (!batch || !session?.access_token) return;

  try {
    const response = await fetch(`${API_BASE}/batches/${batch.batchId}/qr`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Không thể sinh mã QR");
    batch.trace = { id: data.trace_id, url: data.public_url };
    await loadQrImage(batch);
    render();
  } catch (error) {
    showToast(error.message);
  }
}

async function downloadQr(id) {
  const batch = state.batches.find((item) => item.id === id);
  if (!batch) return;
  try {
    if (!batch.qrImageUrl) await loadQrImage(batch);
    const link = document.createElement("a");
    link.href = batch.qrImageUrl;
    link.download = `qr-${batch.id}.png`;
    link.click();
  } catch (error) {
    showToast(error.message);
  }
}

function mapBatch(batch) {
  const statusMap = {
    UNVERIFIED: "pending",
    PENDING: "pending",
    AUDITED: "approved",
    APPROVED: "approved",
    REJECTED: "rejected",
  };
  const productionDate = batch.production_date || "";
  const dateParts = productionDate.split("-");
  return {
    batchId: batch.id,
    id: batch.batch_code,
    product: batch.product_name,
    productType: batch.product_type || "",
    harvestDate:
      dateParts.length === 3
        ? `${dateParts[2]}/${dateParts[1]}/${dateParts[0]}`
        : productionDate,
    productionDate,
    quantity: `${batch.quantity} ${batch.unit}`,
    quantityValue: batch.quantity,
    unit: batch.unit || "kg",
    status: statusMap[String(batch.status || "").toUpperCase()] || "pending",
    origin: batch.origin,
    note: batch.note || "N/A",
    sample: { id: "—", desc: "Chưa gửi mẫu kiểm định" },
    trace: batch.trace || null,
    report: batch.report || "",
    qrImageUrl: null,
    reportPdfUrl: null,
    rejectReason:
      batch.reason ||
      batch.reject_reason ||
      batch.rejectReason ||
      "Chưa có lý do từ chối được ghi nhận.",
  };
}

async function initFarmer() {
  const session = getCurrentSession();
  if (
    !session?.access_token ||
    String(session.role || "").toUpperCase() !== "FARMER"
  ) {
    window.location.href = "../login.html";
    return;
  }

  state.batches = [];
  state.profile = {
    ...state.profile,
    fullName: session.full_name || "",
    dob: "",
    phone: "",
    email: "",
    address: "",
    farmName: "",
    landArea: "",
    businessType: "",
    mainProduct: "",
    taxCode: "",
    region: "",
    username: session.username || "",
    role: session.role || "FARMER",
    status: "",
  };
  const headers = { Authorization: `Bearer ${session.access_token}` };
  try {
    const [profileResponse, batchesResponse] = await Promise.all([
      fetch(`${API_BASE}/users/me`, { headers }),
      fetch(`${API_BASE}/batches`, { headers }),
    ]);

    if (profileResponse.status === 401 || batchesResponse.status === 401) {
      clearCurrentSession();
      window.location.href = "../login.html";
      return;
    }

    if (profileResponse.ok) {
      const user = await profileResponse.json();
      const business = user.business || {};
      state.profile = {
        ...state.profile,
        fullName: user.full_name || session.full_name || "",
        phone: user.phone || "",
        email: user.email || "",
        farmName: business.business_name || "",
        businessType: business.business_type || "",
        mainProduct: business.product_type || "",
        taxCode: business.tax_code || "",
        username: session.username || user.email || "",
        role: user.role || session.role || "FARMER",
        status: user.status === "active" ? "Đang hoạt động" : user.status || "",
      };
    }
    if (batchesResponse.ok)
      state.batches = (await batchesResponse.json()).map(mapBatch);
    render();
  } catch (error) {
    console.error("Không thể tải dữ liệu farmer:", error);
    render();
    showToast("Không thể kết nối tới máy chủ");
  }
}

/* ============================ HELPERS ============================ */
function esc(s) {
  return s === undefined || s === null
    ? ""
    : String(s).replace(
      /[&<>"']/g,
      (m) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[m],
    );
}
function initials(name) {
  return name
    .trim()
    .split(/\s+/)
    .slice(-2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}
function statusMeta(status) {
  if (status === "approved")
    return { label: "Đã kiểm định", cls: "badge-approved" };
  if (status === "rejected")
    return { label: "Bị từ chối", cls: "badge-rejected" };
  return { label: "Chờ kiểm định", cls: "badge-pending" };
}
function counts() {
  const b = state.batches;
  return {
    total: b.length,
    pending: b.filter((x) => x.status === "pending").length,
    approved: b.filter((x) => x.status === "approved").length,
    rejected: b.filter((x) => x.status === "rejected").length,
  };
}
function missingProfileFields() {
  return REQUIRED_PROFILE_FIELDS.filter(
    (f) => !state.profile[f] || String(state.profile[f]).trim() === "",
  );
}
function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => t.classList.remove("show"), 2600);
}
function filteredBatches() {
  let list = state.batches;
  if (state.filter !== "all")
    list = list.filter((b) => b.status === state.filter);
  if (state.search.trim()) {
    const q = state.search.trim().toLowerCase();
    list = list.filter(
      (b) =>
        b.id.toLowerCase().includes(q) || b.product.toLowerCase().includes(q),
    );
  }
  return list;
}

/* ============================ RENDER: SHELL ============================ */
function render() {
  const app = document.getElementById("app");
  if (state.loggedOut) {
    app.innerHTML = renderLoggedOut();
    return;
  }

  let pageHtml = "";
  if (state.page === "overview") pageHtml = renderOverviewPage();
  else if (state.page === "batches") pageHtml = renderBatchesPage();
  else if (state.page === "profile") pageHtml = renderProfilePage();

  app.innerHTML = `
    ${renderTopbar()}
    ${renderSidebar()}
    <div class="sidebar-backdrop ${state.mobileMenuOpen ? "show" : ""}" onclick="closeMobileMenu()"></div>
    <div class="main">${pageHtml}</div>
    ${state.modal ? renderModal() : ""}
  `;

  if (state.page === "batches") {
    const input = document.getElementById("batchSearchInput");
    if (input) {
      input.focus();
      input.selectionStart = input.selectionEnd = input.value.length;
    }
  }
}

function renderTopbar() {
  return `
  <div class="topbar">
    ${renderLogo()}
    <button class="hamburger-btn" onclick="toggleMobileMenu()" aria-label="Mở menu">${ICONS.menu}</button>
  </div>`;
}

function toggleMobileMenu() {
  state.mobileMenuOpen = !state.mobileMenuOpen;
  render();
}
function closeMobileMenu() {
  state.mobileMenuOpen = false;
  render();
}

function renderSidebar() {
  const p = state.profile;
  return `
  <div class="sidebar ${state.mobileMenuOpen ? "open" : ""}">
    ${renderLogo()}
    <div class="nav">
      <button class="nav-item ${state.page === "overview" ? "active" : ""}" onclick="navigate('overview')">${ICONS.overview} Tổng quan</button>
      <button class="nav-item ${state.page === "batches" ? "active" : ""}" onclick="navigate('batches')">${ICONS.batches} Lô hàng của tôi</button>
    </div>
    <div class="sidebar-spacer"></div>
    <div class="sidebar-footer">
      <div class="role-row"><span class="badge-role">Vai trò: ${esc(p.role)}</span></div>
      <div class="profile-card" onclick="navigate('profile')">
        <div class="avatar">${esc(initials(p.fullName))}</div>
        <div>
          <div class="profile-name">${esc(p.fullName)}</div>
          <div class="profile-farm">${esc(p.farmName)} - ${esc(p.region)}</div>
        </div>
      </div>
      <div class="logout-row">
        <button class="logout-btn" onclick="doLogout()">Đăng xuất ${ICONS.logout}</button>
      </div>
    </div>
  </div>`;
}

/* ============================ RENDER: OVERVIEW ============================ */
function renderOverviewPage() {
  const c = counts();
  return `
    <h1 class="page-title">Tổng quan</h1>
    <div class="stat-grid">
      <div class="stat-card stat-total"><span class="stat-label">Tổng lô hàng</span><div class="stat-value">${c.total}</div></div>
      <div class="stat-card stat-pending"><span class="stat-label">Chưa kiểm định</span><div class="stat-value">${c.pending}</div></div>
      <div class="stat-card stat-approved"><span class="stat-label">Đã kiểm định</span><div class="stat-value">${c.approved}</div></div>
      <div class="stat-card stat-rejected"><span class="stat-label">Bị từ chối</span><div class="stat-value">${c.rejected}</div></div>
    </div>

    <div class="page-header-row">
      <div></div>
      <button class="btn btn-primary" onclick="openCreateModal()">+ Tạo lô hàng mới</button>
    </div>

    <div class="panel">
      <div class="panel-toolbar">
        <div class="panel-title">Danh sách lô hàng</div>
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
          <div class="search-wrap">${ICONS.search}<input class="search-input" placeholder="Mã lô hàng/ Tên sản phẩm" value="${esc(state.search)}" oninput="onOverviewSearch(this.value)"></div>
          <span class="filter-pill">Tất cả</span>
        </div>
      </div>
      ${renderBatchTable(filteredBatches())}
      <div class="pagination"><button disabled>&lt;</button> Trang 1/1 <button disabled>&gt;</button></div>
    </div>
  `;
}
function onOverviewSearch(v) {
  state.search = v;
  const container = document.getElementById("overviewTableWrap");
  if (container) container.innerHTML = renderBatchRowsTable(filteredBatches());
}

/* ============================ RENDER: BATCHES ============================ */
function renderBatchesPage() {
  const c = counts();
  return `
    <h1 class="page-title">Quản lý Lô hàng nông sản</h1>
    <div class="page-header-row">
      <div class="search-wrap" style="max-width:320px;">${ICONS.search}<input id="batchSearchInput" class="search-input" placeholder="Tìm kiếm Lô hàng" value="${esc(state.search)}" oninput="onBatchSearch(this.value)"></div>
      <button class="btn btn-primary" onclick="openCreateModal()">+ Tạo lô hàng mới</button>
    </div>

    <div class="panel">
      <div class="tabs">
        <button class="tab-btn ${state.filter === "all" ? "active" : ""}" onclick="setFilter('all')">Tất cả (${c.total})</button>
        <button class="tab-btn ${state.filter === "pending" ? "active" : ""}" onclick="setFilter('pending')">Chờ kiểm định (${c.pending})</button>
        <button class="tab-btn ${state.filter === "approved" ? "active" : ""}" onclick="setFilter('approved')">Đã kiểm định (${c.approved})</button>
        <button class="tab-btn ${state.filter === "rejected" ? "active" : ""}" onclick="setFilter('rejected')">Bị từ chối (${c.rejected})</button>
      </div>
      ${renderBatchTable(filteredBatches())}
      <div class="pagination"><button disabled>&lt;</button> Trang 1/1 <button disabled>&gt;</button></div>
    </div>
  `;
}
function onBatchSearch(v) {
  state.search = v;
  const container = document.getElementById("batchTableWrap");
  if (container) container.innerHTML = renderBatchRowsTable(filteredBatches());
}
function setFilter(f) {
  state.filter = f;
  render();
}

function renderBatchRowsTable(list) {
  const rows = list.length
    ? list
      .map((b) => {
        const s = statusMeta(b.status);
        return `
    <tr onclick="openDetailModal('${b.id}')">
      <td class="mono-id">${esc(b.id)}</td>
      <td>${esc(b.product)}</td>
      <td class="cell-soft">${esc(b.harvestDate)}</td>
      <td class="cell-soft">${esc(b.quantity)}</td>
      <td><span class="badge ${s.cls}">${s.label}</span></td>
    </tr>`;
      })
      .join("")
    : `<tr class="empty-row"><td colspan="5">Không tìm thấy lô hàng phù hợp.</td></tr>`;

  return `
    <table>
      <thead><tr><th>Mã lô hàng</th><th>Sản phẩm</th><th>Ngày thu hoạch</th><th>Sản lượng</th><th>Trạng thái</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}
function renderBatchTable(list) {
  const wrapId =
    state.page === "overview" ? "overviewTableWrap" : "batchTableWrap";
  return `<div class="table-scroll" id="${wrapId}">${renderBatchRowsTable(list)}</div>`;
}

/* ============================ RENDER: PROFILE ============================ */
function fieldOrMissing(val) {
  const has = val && String(val).trim() !== "";
  return has
    ? `<span class="info-value">${esc(val)}</span>`
    : `<span class="info-value missing">Chưa cập nhật</span>`;
}
function renderProfilePage() {
  const p = state.profile;
  const missing = missingProfileFields();
  return `
    <div class="page-header-row">
      <h1 class="page-title" style="margin:0;">Hồ sơ của bạn</h1>
      <button class="btn btn-primary" onclick="openEditProfile()">Chỉnh sửa Hồ sơ</button>
    </div>

    ${missing.length
      ? `
    <div class="complete-banner">
      <span>Hồ sơ của bạn còn thiếu ${missing.length} thông tin bắt buộc. Vui lòng bổ sung để sử dụng đầy đủ tính năng.</span>
      <button class="btn btn-secondary" style="background:#fff;" onclick="openEditProfile()">Bổ sung ngay</button>
    </div>`
      : ``
    }

    <div class="profile-hero">
      <div class="profile-hero-left">
        <div class="avatar-lg">${esc(initials(p.fullName))}</div>
        <div>
          <div class="profile-hero-name">${esc(p.fullName)}</div>
          <div class="profile-hero-farm">${esc(p.farmName)} - ${esc(p.region)}</div>
        </div>
      </div>
      <span class="badge-role">Vai trò: ${esc(p.role)}</span>
    </div>

    <div class="section-label" style="margin:2px 0 10px 2px;">Thông tin nông trại</div>
    <div class="info-grid">
      <div class="info-card">
        <h3>Thông tin cá nhân</h3>
        <div class="info-line"><span class="info-label">Họ và tên</span>${fieldOrMissing(p.fullName)}</div>
        <div class="info-line"><span class="info-label">Ngày sinh</span>${fieldOrMissing(p.dob)}</div>
        <div class="info-line"><span class="info-label">Số điện thoại</span>${fieldOrMissing(p.phone)}</div>
        <div class="info-line"><span class="info-label">Email</span>${fieldOrMissing(p.email)}</div>
        <div class="info-line"><span class="info-label">Địa chỉ</span>${fieldOrMissing(p.address)}</div>
      </div>
      <div class="info-card">
        <h3>Thông tin doanh nghiệp / Hộ kinh doanh</h3>
        <div class="info-line"><span class="info-label">Tên Doanh nghiệp/Hộ kinh doanh</span>${fieldOrMissing(p.farmName)}</div>
        <div class="info-line"><span class="info-label">Diện tích canh tác</span>${fieldOrMissing(p.landArea)}</div>
        <div class="info-line"><span class="info-label">Loại hình hoạt động</span>${fieldOrMissing(p.businessType)}</div>
        <div class="info-line"><span class="info-label">Sản phẩm chính</span>${fieldOrMissing(p.mainProduct)}</div>
        <div class="info-line"><span class="info-label">Mã số thuế</span>${fieldOrMissing(p.taxCode)}</div>
        <div class="info-line"><span class="info-label">Khu vực</span>${fieldOrMissing(p.region)}</div>
      </div>
    </div>

    <div class="info-card">
      <h3>Tài khoản</h3>
      <div class="info-line"><span class="info-label">Tên đăng nhập</span><span class="info-value">${esc(p.username)}</span></div>
      <div class="info-line"><span class="info-label">Vai trò</span><span class="badge-role">${esc(p.role)}</span></div>
      <div class="info-line"><span class="info-label">Trạng thái</span><span class="badge badge-approved">${esc(p.status)}</span></div>
      <div class="info-line"><span class="info-label">Ngày tham gia</span><span class="info-value">${esc(p.joinDate)}</span></div>
    </div>
  `;
}

/* ============================ MODALS ============================ */
function renderModal() {
  if (!state.modal) return "";
  if (state.modal.type === "detail") return renderDetailModal(state.modal.id);
  if (state.modal.type === "create") return renderCreateModal();
  if (state.modal.type === "editBatch") return renderEditBatchModal();
  if (state.modal.type === "editProfile") return renderEditProfileModal();
  return "";
}
function closeModal() {
  state.modal = null;
  state.createErrors = {};
  state.editErrors = {};
  render();
}
function stop(e) {
  e.stopPropagation();
}

/* ---- detail modal ---- */
async function openDetailModal(id) {
  state.modal = { type: "detail", id };
  render();

  const batch = state.batches.find((item) => item.id === id);
  if (!batch || batch.status !== "approved") return;

  try {
    if (!batch.trace) {
      const response = await fetch(
        `${API_BASE}/public/trace/${encodeURIComponent(id)}`,
      );
      if (!response.ok) return;
      const trace = await response.json();
      batch.trace = trace.trace_id
        ? { id: trace.trace_id, url: trace.public_url }
        : null;
      batch.report = trace.laboratory_result_summary?.latest_report_code || "";
    }
    if (batch.trace) {
      try {
        await loadQrImage(batch);
      } catch (error) {
        console.warn("Không thể tải ảnh QR:", error.message);
      }
    }
    try {
      await loadReportPdf(batch);
    } catch (error) {
      console.warn("Không thể tải file report:", error.message);
    }
    if (state.modal?.type === "detail" && state.modal.id === id) render();
  } catch (error) {
    console.error("Không thể tải thông tin truy xuất:", error);
  }
}
function renderDetailModal(id) {
  const b = state.batches.find((x) => x.id === id);
  if (!b) return "";
  const s = statusMeta(b.status);
  return `
  <div class="overlay" onclick="closeModal()">
    <div class="modal" onclick="stop(event)">
      <div class="modal-header">
        <div class="modal-title">${esc(b.id)}</div>
        <button class="modal-close" onclick="closeModal()">✕</button>
      </div>
      <div class="detail-status-row"><span class="badge ${s.cls}">${s.label}</span></div>

      <div class="detail-grid">
        <div><div class="detail-block-label">Sản phẩm</div><div class="detail-block-value">${esc(b.product)}</div></div>
        <div><div class="detail-block-label">Nguồn gốc</div><div class="detail-block-value">${esc(b.origin)}</div></div>
        <div><div class="detail-block-label">Ngày thu hoạch</div><div class="detail-block-value">${esc(b.harvestDate)}</div></div>
        <div><div class="detail-block-label">Sản lượng</div><div class="detail-block-value">${esc(b.quantity)}</div></div>
      </div>
      <div class="detail-block-label">Ghi chú</div>
      <div class="detail-block-value" style="margin-bottom:4px;">${esc(b.note || "N/A")}</div>

      <div class="divider"></div>
      <div class="section-label">Sample đã gửi</div>
      <div class="sample-box">
        <div class="sample-icon">${esc((b.sample.id || "").slice(-3))}</div>
        <div>
          <div class="sample-id">${esc(b.sample.id)}</div>
          <div class="sample-desc">${esc(b.sample.desc)}</div>
        </div>
      </div>

      ${b.status === "approved"
      ? `
      <div class="divider"></div>
      <div class="section-label">QR &amp; Truy xuất nguồn gốc</div>
      <div class="trace-box" style="margin-bottom:16px;">
        <div class="trace-qr" style="${b.qrImageUrl ? "width:96px;height:96px;flex:0 0 96px;background:#fff;overflow:hidden;" : ""}">${b.qrImageUrl ? `<img src="${esc(b.qrImageUrl)}" alt="QR ${esc(b.id)}" style="display:block;width:96px;height:96px;object-fit:contain;aspect-ratio:1 / 1;">` : ICONS.qrSmall}</div>
        <div>
          <div class="trace-label">Mã QR truy xuất</div>
          <div class="trace-id">${esc(b.trace?.id || "Chưa có Trace ID")}</div>
        </div>
      </div>
      <div class="modal-actions">
        ${b.trace?.id ? "" : `<button class="btn btn-primary" onclick="generateQr('${esc(b.id)}');stop(event)">Sinh QR</button>`}
        ${b.trace?.id ? `<button class="btn btn-secondary" onclick="downloadQr('${esc(b.id)}');stop(event)">Tải QR</button>` : ""}
      </div>
      <div class="section-label">Biên bản kiểm định</div>
      ${b.reportPdfUrl ? `<div style="width:100%;max-height:62vh;overflow-y:auto;overflow-x:hidden;border:1px solid var(--border);border-radius:10px;background:#f5f5f5;"><object data="${esc(b.reportPdfUrl)}" type="application/pdf" style="display:block;width:100%;min-height:760px;border:0;"><a href="${esc(b.reportPdfUrl)}" target="_blank" rel="noopener">Mở file PDF</a></object></div>` : `<div class="file-chip">${ICONS.file} ${esc(b.report || "Chưa có biên bản")}</div>`}
      ${b.trace?.id ? `<a class="file-chip" href="../public/trace.html?trace=${encodeURIComponent(b.trace.id)}" target="_blank" rel="noopener">${ICONS.search} Mở hồ sơ truy xuất</a>` : ""}
      `
      : ``
    }

      ${b.status === "rejected"
      ? `
      <div class="divider"></div>
      <div class="section-label">Lý do từ chối</div>
      <div class="reject-box" style="margin-bottom:16px;">
        <div class="reject-title">AUDITOR TỪ CHỐI LÔ HÀNG</div>
        <div class="reject-text">${esc((b.rejectReason || "Chưa có lý do từ chối được ghi nhận.").replace(/^AUDITOR TỪ CHỐI LÔ HÀNG:\s*/, ""))}</div>
      </div>
      <div class="section-label">Biên bản kiểm định</div>
      ${b.reportPdfUrl ? `<div style="width:100%;max-height:62vh;overflow-y:auto;overflow-x:hidden;border:1px solid var(--border);border-radius:10px;background:#f5f5f5;"><object data="${esc(b.reportPdfUrl)}" type="application/pdf" style="display:block;width:100%;min-height:760px;border:0;"><a href="${esc(b.reportPdfUrl)}" target="_blank" rel="noopener">Mở file PDF</a></object></div>` : `<div class="file-chip">${ICONS.file} ${esc(b.report || "Chưa có biên bản")}</div>`}
      <div class="modal-actions">
        <button class="btn btn-primary" onclick="openEditBatch('${esc(b.id)}');stop(event)">Sửa thông tin và gửi kiểm định lại</button>
      </div>
      `
      : ``
    }
    </div>
  </div>`;
}

function openEditBatch(id) {
  const batch = state.batches.find((item) => item.id === id);
  if (!batch) return;
  state.editBatchForm = {
    productName: batch.product || "",
    productType: batch.productType || "",
    origin: batch.origin || "",
    quantity: String(batch.quantityValue ?? ""),
    unit: batch.unit || "kg",
    productionDate: batch.productionDate || "",
    note: batch.note === "N/A" ? "" : batch.note || "",
  };
  state.editBatchErrors = {};
  state.modal = { type: "editBatch", id };
  render();
}

function onEditBatchField(key, value) {
  state.editBatchForm[key] = value;
}

async function submitEditBatch() {
  const batch = state.batches.find((item) => item.id === state.modal?.id);
  const form = state.editBatchForm;
  const errors = {};
  if (!form.productName.trim())
    errors.productName = "Vui lòng nhập tên sản phẩm";
  if (!form.productType.trim()) errors.productType = "Vui lòng nhập phân loại";
  if (!form.origin.trim()) errors.origin = "Vui lòng nhập nguồn gốc";
  if (!form.quantity || Number(form.quantity) <= 0)
    errors.quantity = "Số lượng không hợp lệ";
  state.editBatchErrors = errors;
  if (!batch || Object.keys(errors).length) {
    render();
    return;
  }

  const session = getCurrentSession();
  try {
    const response = await fetch(`${API_BASE}/batches/${batch.batchId}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_name: form.productName.trim(),
        product_type: form.productType.trim(),
        origin: form.origin.trim(),
        quantity: Number(form.quantity),
        unit: form.unit,
        production_date: form.productionDate || null,
        note: form.note.trim() || null,
      }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok)
      throw new Error(data.detail || "Không thể cập nhật lô hàng");
    state.batches = state.batches.map((item) =>
      item.batchId === batch.batchId ? mapBatch(data) : item,
    );
    state.modal = null;
    render();
    showToast("Đã cập nhật và gửi lại lô hàng để kiểm định");
  } catch (error) {
    showToast(error.message);
  }
}

function renderEditBatchModal() {
  const form = state.editBatchForm;
  const errors = state.editBatchErrors;
  const error = (key) =>
    errors[key]
      ? `<span class="field-error-msg">${esc(errors[key])}</span>`
      : "";
  return `
  <div class="overlay" onclick="closeModal()">
    <div class="modal" onclick="stop(event)">
      <div class="modal-header">
        <div class="modal-title">Sửa thông tin lô hàng</div>
        <button class="modal-close" onclick="closeModal()">✕</button>
      </div>
      <div class="field-grid" style="margin-top:14px;">
        <div class="field ${errors.productName ? "error" : ""}">
          <label>Tên sản phẩm <span class="req">*</span></label>
          <input value="${esc(form.productName)}" oninput="onEditBatchField('productName', this.value)">
          ${error("productName")}
        </div>
        <div class="field ${errors.productType ? "error" : ""}">
          <label>Phân loại <span class="req">*</span></label>
          <input value="${esc(form.productType)}" oninput="onEditBatchField('productType', this.value)">
          ${error("productType")}
        </div>
        <div class="field ${errors.origin ? "error" : ""}">
          <label>Nguồn gốc <span class="req">*</span></label>
          <input value="${esc(form.origin)}" oninput="onEditBatchField('origin', this.value)">
          ${error("origin")}
        </div>
        <div class="field ${errors.quantity ? "error" : ""}">
          <label>Số lượng <span class="req">*</span></label>
          <input type="number" min="0" value="${esc(form.quantity)}" oninput="onEditBatchField('quantity', this.value)">
          ${error("quantity")}
        </div>
        <div class="field">
          <label>Đơn vị</label>
          <select onchange="onEditBatchField('unit', this.value)">
            <option value="kg" ${form.unit === "kg" ? "selected" : ""}>kg</option>
            <option value="tấn" ${form.unit === "tấn" ? "selected" : ""}>tấn</option>
            <option value="tạ" ${form.unit === "tạ" ? "selected" : ""}>tạ</option>
          </select>
        </div>
        <div class="field">
          <label>Ngày thu hoạch</label>
          <input type="date" value="${esc(form.productionDate)}" oninput="onEditBatchField('productionDate', this.value)">
        </div>
        <div class="field full">
          <label>Ghi chú</label>
          <textarea oninput="onEditBatchField('note', this.value)">${esc(form.note)}</textarea>
        </div>
      </div>
      <div class="modal-actions">
        <button class="btn btn-secondary" onclick="closeModal()">Hủy</button>
        <button class="btn btn-primary" onclick="submitEditBatch()">Lưu và gửi lại</button>
      </div>
    </div>
  </div>`;
}

/* ---- create batch modal ---- */
function openCreateModal() {
  state.createForm = {
    productName: "",
    category: "",
    harvestDate: "",
    origin: "",
    quantity: "",
    unit: "kg",
    note: "",
  };
  state.createErrors = {};
  state.modal = { type: "create" };
  render();
}
function onCreateField(key, val) {
  state.createForm[key] = val;
}
function renderCreateModal() {
  const f = state.createForm;
  const err = state.createErrors;
  const errCls = (k) => (err[k] ? "field error" : "field");
  return `
  <div class="overlay" onclick="closeModal()">
    <div class="modal" onclick="stop(event)">
      <div class="modal-header">
        <div class="modal-title">Tạo Lô hàng mới</div>
        <button class="modal-close" onclick="closeModal()">✕</button>
      </div>
      <div class="field-grid" style="margin-top:14px;">
        <div class="${errCls("productName")}">
          <label>Tên sản phẩm <span class="req">*</span></label>
          <input value="${esc(f.productName)}" placeholder="Nhập tên sản phẩm" oninput="onCreateField('productName', this.value)">
          ${err.productName ? `<span class="field-error-msg">${err.productName}</span>` : ``}
        </div>
        <div class="${errCls("category")}">
          <label>Phân loại <span class="req">*</span></label>
          <select onchange="onCreateField('category', this.value)">
            <option value="" ${f.category === "" ? "selected" : ""}>Chọn phân loại</option>
            <option ${f.category === "Nông sản tươi" ? "selected" : ""}>Nông sản tươi</option>
            <option ${f.category === "Nông sản khô" ? "selected" : ""}>Nông sản khô</option>
            <option ${f.category === "Chế biến" ? "selected" : ""}>Chế biến</option>
          </select>
          ${err.category ? `<span class="field-error-msg">${err.category}</span>` : ``}
        </div>
        <div class="${errCls("harvestDate")}">
          <label>Ngày thu hoạch <span class="req">*</span></label>
          <input type="date" value="${esc(f.harvestDate)}" oninput="onCreateField('harvestDate', this.value)">
          ${err.harvestDate ? `<span class="field-error-msg">${err.harvestDate}</span>` : ``}
        </div>
        <div class="${errCls("origin")}">
          <label>Nguồn gốc <span class="req">*</span></label>
          <select onchange="onCreateField('origin', this.value)">
            <option value="" ${f.origin === "" ? "selected" : ""}>Chọn khu vực</option>
            <option ${f.origin === "Đắk Lắk" ? "selected" : ""}>Đắk Lắk</option>
            <option ${f.origin === "An Giang" ? "selected" : ""}>An Giang</option>
            <option ${f.origin === "Thái Nguyên" ? "selected" : ""}>Thái Nguyên</option>
            <option ${f.origin === "Sóc Trăng" ? "selected" : ""}>Sóc Trăng</option>
            <option ${f.origin === "Thanh Hóa" ? "selected" : ""}>Thanh Hóa</option>
          </select>
          ${err.origin ? `<span class="field-error-msg">${err.origin}</span>` : ``}
        </div>
        <div class="${errCls("quantity")}">
          <label>Số lượng <span class="req">*</span></label>
          <input type="number" min="0" value="${esc(f.quantity)}" placeholder="0" oninput="onCreateField('quantity', this.value)">
          ${err.quantity ? `<span class="field-error-msg">${err.quantity}</span>` : ``}
        </div>
        <div class="field">
          <label>Đơn vị <span class="req">*</span></label>
          <select onchange="onCreateField('unit', this.value)">
            <option value="kg" ${f.unit === "kg" ? "selected" : ""}>kg</option>
            <option value="tấn" ${f.unit === "tấn" ? "selected" : ""}>tấn</option>
            <option value="tạ" ${f.unit === "tạ" ? "selected" : ""}>tạ</option>
          </select>
        </div>
        <div class="field full">
          <label>Ghi chú</label>
          <textarea placeholder="Ghi chú thêm về lô hàng (nếu có)" oninput="onCreateField('note', this.value)">${esc(f.note)}</textarea>
        </div>
      </div>
      <div class="form-note">*Batch Code sẽ do hệ thống tự sinh và trạng thái mặc định là <b>CHỜ KIỂM ĐỊNH</b>. Sau khi tạo, thông tin lô hàng sẽ bị khóa, bạn sẽ không thể chỉnh sửa lại.</div>
      <div class="modal-actions">
        <button class="btn btn-secondary" onclick="closeModal()">Hủy</button>
        <button class="btn btn-primary" onclick="submitCreateBatch()">Tạo Lô hàng</button>
      </div>
    </div>
  </div>`;
}
async function submitCreateBatch() {
  const f = state.createForm;
  const errors = {};
  if (!f.productName.trim()) errors.productName = "Vui lòng nhập tên sản phẩm";
  if (!f.category) errors.category = "Vui lòng chọn phân loại";
  if (!f.harvestDate) errors.harvestDate = "Vui lòng chọn ngày thu hoạch";
  if (!f.origin) errors.origin = "Vui lòng chọn nguồn gốc";
  if (!f.quantity || Number(f.quantity) <= 0)
    errors.quantity = "Vui lòng nhập số lượng hợp lệ";
  state.createErrors = errors;
  if (Object.keys(errors).length) {
    render();
    return;
  }

  const session = getCurrentSession();
  try {
    const response = await fetch(`${API_BASE}/batches`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_name: f.productName.trim(),
        product_type: f.category,
        origin: f.origin,
        quantity: Number(f.quantity),
        unit: f.unit,
        production_date: f.harvestDate,
        note: f.note.trim() || null,
      }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((item) => item.msg).join(", ")
        : data.detail;
      throw new Error(detail || "Không thể tạo lô hàng");
    }

    state.batches.unshift(mapBatch(data));
    state.modal = null;
    state.page = "batches";
    state.filter = "all";
    render();
    showToast(`Đã tạo lô hàng ${data.batch_code} thành công`);
  } catch (error) {
    showToast(error.message);
  }
}

/* ---- edit profile modal ---- */
function openEditProfile() {
  state.editForm = { ...state.profile };
  state.editErrors = {};
  state.modal = { type: "editProfile" };
  render();
}
function onEditField(key, val) {
  state.editForm[key] = val;
}
function renderEditProfileModal() {
  const f = state.editForm;
  const err = state.editErrors;
  const errCls = (k) => (err[k] ? "field error" : "field");
  const req = (k) =>
    REQUIRED_PROFILE_FIELDS.includes(k) ? `<span class="req">*</span>` : "";
  return `
  <div class="overlay" onclick="closeModal()">
    <div class="modal" style="max-width:620px;" onclick="stop(event)">
      <div class="modal-header">
        <div class="modal-title">Chỉnh sửa Hồ sơ</div>
        <button class="modal-close" onclick="closeModal()">✕</button>
      </div>
      <div class="modal-sub" style="font-size:12.8px;color:var(--text-soft);margin-top:4px;">Các trường có dấu <span class="req">*</span> là bắt buộc và cần được khai báo đầy đủ.</div>

      <div class="section-label">Thông tin cá nhân</div>
      <div class="field-grid">
        <div class="${errCls("fullName")}">
          <label>Họ và tên ${req("fullName")}</label>
          <input value="${esc(f.fullName)}" oninput="onEditField('fullName', this.value)">
          ${err.fullName ? `<span class="field-error-msg">${err.fullName}</span>` : ``}
        </div>
        <div class="${errCls("dob")}">
          <label>Ngày sinh ${req("dob")}</label>
          <input placeholder="dd/mm/yyyy" value="${esc(f.dob)}" oninput="onEditField('dob', this.value)">
          ${err.dob ? `<span class="field-error-msg">${err.dob}</span>` : ``}
        </div>
        <div class="${errCls("phone")}">
          <label>Số điện thoại ${req("phone")}</label>
          <input value="${esc(f.phone)}" oninput="onEditField('phone', this.value)">
          ${err.phone ? `<span class="field-error-msg">${err.phone}</span>` : ``}
        </div>
        <div class="${errCls("email")}">
          <label>Email ${req("email")}</label>
          <input value="${esc(f.email)}" oninput="onEditField('email', this.value)">
          ${err.email ? `<span class="field-error-msg">${err.email}</span>` : ``}
        </div>
        <div class="field full ${err.address ? "error" : ""}">
          <label>Địa chỉ ${req("address")}</label>
          <input value="${esc(f.address)}" oninput="onEditField('address', this.value)">
          ${err.address ? `<span class="field-error-msg">${err.address}</span>` : ``}
        </div>
      </div>

      <div class="section-label">Thông tin nông trại / Doanh nghiệp</div>
      <div class="field-grid">
        <div class="${errCls("farmName")}">
          <label>Tên trang trại/Doanh nghiệp ${req("farmName")}</label>
          <input value="${esc(f.farmName)}" oninput="onEditField('farmName', this.value)">
          ${err.farmName ? `<span class="field-error-msg">${err.farmName}</span>` : ``}
        </div>
        <div class="${errCls("landArea")}">
          <label>Diện tích canh tác ${req("landArea")}</label>
          <input placeholder="Ví dụ: 10 ha" value="${esc(f.landArea)}" oninput="onEditField('landArea', this.value)">
          ${err.landArea ? `<span class="field-error-msg">${err.landArea}</span>` : ``}
        </div>
        <div class="${errCls("businessType")}">
          <label>Loại hình hoạt động ${req("businessType")}</label>
          <select onchange="onEditField('businessType', this.value)">
            <option value="" ${!f.businessType ? "selected" : ""}>Chọn loại hình</option>
            <option ${f.businessType === "Nông trại" ? "selected" : ""}>Nông trại</option>
            <option ${f.businessType === "Hộ kinh doanh" ? "selected" : ""}>Hộ kinh doanh</option>
            <option ${f.businessType === "Hợp tác xã" ? "selected" : ""}>Hợp tác xã</option>
          </select>
          ${err.businessType ? `<span class="field-error-msg">${err.businessType}</span>` : ``}
        </div>
        <div class="${errCls("mainProduct")}">
          <label>Sản phẩm chính ${req("mainProduct")}</label>
          <input value="${esc(f.mainProduct)}" oninput="onEditField('mainProduct', this.value)">
          ${err.mainProduct ? `<span class="field-error-msg">${err.mainProduct}</span>` : ``}
        </div>
        <div class="field">
          <label>Mã số thuế</label>
          <input value="${esc(f.taxCode)}" oninput="onEditField('taxCode', this.value)">
        </div>
        <div class="${errCls("region")}">
          <label>Khu vực ${req("region")}</label>
          <input value="${esc(f.region)}" oninput="onEditField('region', this.value)">
          ${err.region ? `<span class="field-error-msg">${err.region}</span>` : ``}
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn btn-secondary" onclick="closeModal()">Hủy</button>
        <button class="btn btn-primary" onclick="submitEditProfile()">Lưu thay đổi</button>
      </div>
    </div>
  </div>`;
}
function submitEditProfile() {
  const f = state.editForm;
  const errors = {};
  REQUIRED_PROFILE_FIELDS.forEach((k) => {
    if (!f[k] || String(f[k]).trim() === "")
      errors[k] = "Bắt buộc nhập thông tin này";
  });
  state.editErrors = errors;
  if (Object.keys(errors).length) {
    render();
    return;
  }
  state.profile = { ...f };
  state.modal = null;
  state.page = "profile";
  render();
  showToast("Cập nhật hồ sơ thành công");
}

/* ---- logout ---- */
function doLogout() {
  if (confirm("Bạn có chắc chắn muốn đăng xuất khỏi AgriTrace?")) {
    clearCurrentSession();
    window.location.href = "../login.html";
  }
}
function reLogin() {
  state.loggedOut = false;
  state.page = "overview";
  render();
}
function renderLoggedOut() {
  return `
  <div class="logged-out-wrap">
    <div class="logged-out-card">
      ${renderLogo().replace('class="logo"', 'class="logo" style="justify-content:center;padding-bottom:16px;"')}
      <div style="font-size:15px;font-weight:700;margin-bottom:6px;">Bạn đã đăng xuất</div>
      <div style="font-size:13.3px;color:var(--text-soft);margin-bottom:20px;">Hẹn gặp lại bạn trên AgriTrace.</div>
      <button class="btn btn-primary" style="width:100%;justify-content:center;" onclick="reLogin()">Đăng nhập lại</button>
    </div>
  </div>`;
}

function navigate(page) {
  state.page = page;
  state.search = "";
  state.filter = "all";
  state.modal = null;
  state.mobileMenuOpen = false;
  render();
}

/* ============================ INIT ============================ */
initFarmer();
