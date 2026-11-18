const API_BASE = "http://127.0.0.1:8000";

function getAuthHeaders() {
  const rawUser =
    sessionStorage.getItem("currentUser") ||
    localStorage.getItem("currentUser");
  const user = rawUser ? JSON.parse(rawUser) : null;
  return user?.access_token
    ? { Authorization: `Bearer ${user.access_token}` }
    : {};
}

async function loadAuditorProfile() {
  const response = await fetch(`${API_BASE}/auditor/profile`, {
    headers: getAuthHeaders(),
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(data.detail || "Không thể tải hồ sơ auditor.");

  document.getElementById("sidebar-user-name").textContent = data.full_name;
  document.getElementById("profile-name").textContent = data.full_name;
  const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(data.full_name)}&background=5c33cf&color=fff`;
  document.getElementById("sidebar-user-avatar").src = avatarUrl;
  document.getElementById("profile-avatar").src = avatarUrl;
  document.getElementById("profile-code").textContent =
    `Mã Auditor: ${data.auditor_code}`;
  document.getElementById("profile-status").textContent = data.status;
  document.getElementById("profile-email").textContent =
    data.email || "Chưa cập nhật";
  document.getElementById("profile-phone").textContent =
    data.phone || "Chưa cập nhật";
  document.getElementById("stat-approved").textContent =
    data.statistics.approved;
  document.getElementById("stat-rejected").textContent =
    data.statistics.rejected;
  document.getElementById("stat-sealed").textContent =
    data.statistics.sealed_reports;
}

loadAuditorProfile().catch((error) => {
  document.getElementById("profile-status").textContent = error.message;
});
