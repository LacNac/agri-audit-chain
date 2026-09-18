const API_BASE = "http://127.0.0.1:8000";

function getCurrentUser() {
  try {
    return JSON.parse(sessionStorage.getItem("currentUser") || "{}");
  } catch (error) {
    return {};
  }
}

function logout() {
  sessionStorage.removeItem("currentUser");
  window.location.href = "./login.html";
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

  if (!token || currentUser.role !== "ADMIN") {
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
      throw new Error(errorData.detail || "Không thể tải dashboard");
    }

    const data = await response.json();
    const summary = data.summary || {};

    document.getElementById("users-count").textContent = summary.users ?? 0;
    document.getElementById("farmers-count").textContent = summary.farmers ?? 0;
    document.getElementById("auditors-count").textContent = summary.auditors ?? 0;
    document.getElementById("batches-count").textContent = summary.batches ?? 0;
    document.getElementById("audited-count").textContent = summary.audited_batches ?? 0;
    document.getElementById("rejected-count").textContent = summary.rejected_batches ?? 0;
    document.getElementById("pending-count").textContent = summary.pending_batches ?? 0;

    renderList("new-batches", data.lists?.new_batches || [], "Không có batch mới");
    renderList("pending-batches", data.lists?.pending_batches || [], "Không có batch chờ kiểm định");
    renderList("rejected-batches", data.lists?.rejected_batches || [], "Không có batch bị reject");
    await loadUsers(token);
  } catch (error) {
    alert(error.message);
    window.location.href = "./login.html";
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
  message.textContent = "Đang tạo tài khoản...";

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
    message.textContent = `Đã tạo tài khoản ${data.username}.`;
    await loadUsers(currentUser.access_token);
    await loadDashboard();
  } catch (error) {
    message.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

document.getElementById("logoutBtn")?.addEventListener("click", logout);
loadDashboard();
