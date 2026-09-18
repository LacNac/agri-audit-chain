const API_BASE = "http://127.0.0.1:8001";

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
  } catch (error) {
    alert(error.message);
    window.location.href = "./login.html";
  }
}

document.getElementById("logoutBtn")?.addEventListener("click", logout);
loadDashboard();
