const API_BASE = "http://127.0.0.1:8000";

function getCurrentUser() {
  try {
    const serializedUser = sessionStorage.getItem("currentUser") || localStorage.getItem("currentUser") || "{}";
    const user = JSON.parse(serializedUser);
    if (user.access_token && !sessionStorage.getItem("currentUser")) {
      sessionStorage.setItem("currentUser", serializedUser);
    }
    return user;
  } catch (error) {
    return {};
  }
}

function logout() {
  sessionStorage.removeItem("currentUser");
  localStorage.removeItem("currentUser");
  window.location.href = "./admin_login.html";
}

function renderList(elementId, items, emptyMessage = "Không có dữ liệu") {
  const list = document.getElementById(elementId);
  if (!list) return;

  if (!items || items.length === 0) {
    list.innerHTML = `<li class="empty">${emptyMessage}</li>`;
    return;
  }

  list.innerHTML = items
    .map((item) => {
      const status = (item.status || "UNVERIFIED").toUpperCase();
      const tagClass = status === "AUDITED" ? "audited" : status === "REJECTED" ? "rejected" : "unverified";
      return `
        <li class="batch-item">
          <div>
            <strong>${item.batch_code || "-"}</strong>
            <span>${item.product_name || "Không có tên"}</span>
          </div>
          <span class="tag ${tagClass}">${status}</span>
        </li>
      `;
    })
    .join("");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setTextContent(elementId, value) {
  const element = document.getElementById(elementId);
  if (element) element.textContent = value;
}

function formatDateTime(value) {
  if (!value) return "-";
  const date = new Date(value.replace(" ", "T") + (value.endsWith("Z") ? "" : "Z"));
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("vi-VN");
}

function renderBatches(items) {
  const tableBody = document.getElementById("batches-table-body");
  if (!tableBody) return;
  if (!items || items.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="6" class="empty">Chưa có lô hàng</td></tr>';
    return;
  }

  tableBody.innerHTML = items.map((item) => {
    const status = String(item.status || "UNVERIFIED").toUpperCase();
    const tagClass = status === "AUDITED" ? "audited" : status === "REJECTED" ? "rejected" : "unverified";
    return `<tr>
      <td class="batch-code">${escapeHtml(item.batch_code)}</td>
      <td>${escapeHtml(item.product_name)}</td>
      <td>${escapeHtml(item.producer_name)}</td>
      <td class="table-muted">${escapeHtml(formatDateTime(item.created_at))}</td>
      <td><span class="tag ${tagClass}">${escapeHtml(status)}</span></td>
      <td><button class="table-action" type="button" data-batch-id="${item.id}">Chi tiết</button></td>
    </tr>`;
  }).join("");
}

function renderAuditTrails(items) {
  const tableBody = document.getElementById("audit-table-body");
  if (!tableBody) return;
  if (!items || items.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="5" class="empty">Chưa có lịch sử audit</td></tr>';
    return;
  }

  tableBody.innerHTML = items.map((item) => `<tr>
    <td class="table-muted">${escapeHtml(formatDateTime(item.created_at))}</td>
    <td>${escapeHtml(item.user_name)}</td>
    <td><span class="tag">${escapeHtml(item.role)}</span></td>
    <td class="audit-action">${escapeHtml(item.action)}</td>
    <td class="audit-entity">${escapeHtml(item.entity_type)} #${escapeHtml(item.entity_id)}</td>
  </tr>`).join("");
}

async function loadBatches(token) {
  const response = await fetch(`${API_BASE}/admin/batches`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Không thể tải danh sách lô hàng");
  renderBatches(data);
}

async function loadAuditTrails(token) {
  const response = await fetch(`${API_BASE}/admin/audit-trails`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Không thể tải nhật ký hoạt động");
  renderAuditTrails(data);
}

async function loadUsers(token) {
  const response = await fetch(`${API_BASE}/users`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Không thể tải danh sách người dùng");
  }

  const users = await response.json();
  const tableBody = document.getElementById("users-table-body");
  if (!tableBody) return;
  tableBody.innerHTML = users.map((item) => {
    const status = String(item.status || "active").toLowerCase();
    const isLocked = status === "locked";
    return `
      <tr>
        <td>${escapeHtml(item.name)}</td>
        <td>${escapeHtml(item.email)}</td>
        <td>${escapeHtml(item.role)}</td>
        <td><span class="user-status ${isLocked ? "locked" : "active"}">${isLocked ? "Đã khóa" : "Đang hoạt động"}</span></td>
        <td><button class="status-btn ${isLocked ? "unlock" : "lock"}" data-user-id="${item.id}" data-next-status="${isLocked ? "active" : "locked"}">${isLocked ? "Mở khóa" : "Khóa"}</button></td>
      </tr>`;
  }).join("") || '<tr><td colspan="5" class="empty">Chưa có người dùng</td></tr>';
}

async function updateUserStatus(userId, status, token) {
  const response = await fetch(`${API_BASE}/users/${userId}/status`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Không thể cập nhật trạng thái");
}

async function loadDashboard() {
  const currentUser = getCurrentUser();
  const token = currentUser.access_token;

  if (!token || String(currentUser.role || "").toUpperCase() !== "ADMIN") {
    window.location.href = "./login.html";
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/admin/dashboard`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(errorData.detail || "Không thể tải dashboard");
      error.status = response.status;
      throw error;
    }

    const data = await response.json();
    const summary = data.summary || {};

    setTextContent("users-count", summary.users ?? 0);
    setTextContent("farmers-count", summary.farmers ?? 0);
    setTextContent("auditors-count", summary.auditors ?? 0);
    setTextContent("batches-count", summary.batches ?? 0);
    setTextContent("audited-count", summary.audited_batches ?? 0);
    setTextContent("rejected-count", summary.rejected_batches ?? 0);
    setTextContent("pending-count", summary.pending_batches ?? 0);
    setTextContent("admins-count", summary.admins ?? 0);
    await loadUsers(token);
  } catch (error) {
    alert(error.message);
    if (error.status === 401 || error.status === 403) {
      sessionStorage.removeItem("currentUser");
      localStorage.removeItem("currentUser");
      window.location.href = "./login.html";
    }
  }
}

document.getElementById("users-table-body")?.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-user-id]");
  if (!button) return;

  const currentUser = getCurrentUser();
  button.disabled = true;
  try {
    await updateUserStatus(button.dataset.userId, button.dataset.nextStatus, currentUser.access_token);
    await loadUsers(currentUser.access_token);
    await loadDashboard();
  } catch (error) {
    alert(error.message);
    button.disabled = false;
  }
});

document.getElementById("create-auditor-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type=submit]");
  const message = document.getElementById("auditor-form-message");
  const currentUser = getCurrentUser();
  button.disabled = true;
  if (message) message.textContent = "Đang tạo tài khoản...";

  try {
    const response = await fetch(`${API_BASE}/users/auditors`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${currentUser.access_token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(Object.fromEntries(new FormData(form))),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Không thể tạo tài khoản Auditor");
    form.reset();
    if (message) message.textContent = `Đã tạo tài khoản ${data.username}.`;
    await loadUsers(currentUser.access_token);
    await loadDashboard();
  } catch (error) {
    if (message) message.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

document.getElementById("batches-table-body")?.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-batch-id]");
  if (!button) return;

  const token = getCurrentUser().access_token;
  try {
    const response = await fetch(`${API_BASE}/batches/${button.dataset.batchId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Không thể tải chi tiết lô hàng");
    alert(`${data.batch_code}\n${data.product_name}\nTrạng thái: ${data.status}`);
  } catch (error) {
    alert(error.message);
  }
});

function showDashboardSection(sectionId) {
  const sectionIds = ["overview-section", "users-section", "batches-section", "activity-section"];
  const titles = {
    "overview-section": "Tổng quan",
    "users-section": "Quản lý người dùng",
    "batches-section": "Quản lý lô hàng",
    "activity-section": "Nhật ký hoạt động hệ thống",
  };
  sectionIds.forEach((id) => {
    document.getElementById(id)?.classList.toggle("view-hidden", id !== sectionId);
  });
  setTextContent("page-title", titles[sectionId] || "Tổng quan");

  const token = getCurrentUser().access_token;
  const loadView = sectionId === "batches-section" ? loadBatches(token) : sectionId === "activity-section" ? loadAuditTrails(token) : Promise.resolve();
  loadView.catch((error) => alert(error.message));
}

document.querySelectorAll(".sidebar-link").forEach((link) => {
  link.addEventListener("click", () => {
    document.querySelectorAll(".sidebar-link").forEach((item) => item.classList.remove("active"));
    link.classList.add("active");
    showDashboardSection(link.dataset.section);
  });
});

showDashboardSection("overview-section");

document.getElementById("logoutBtn")?.addEventListener("click", logout);
loadDashboard();
