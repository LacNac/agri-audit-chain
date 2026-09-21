const API_BASE = "http://127.0.0.1:8000";
const fallbackQueue = [
  {
    id: 42,
    batch_code: "AGT-2026-0042",
    product_name: "Xoài Cát Hòa Lộc",
    producer_name: "Nông trại Ba Trúc",
    origin: "An Giang",
    quantity: 180,
    unit: "kg",
    expiry_date: "2026-09-14",
    created_at: "2026-09-15",
  },
  {
    id: 43,
    batch_code: "AGT-2026-0043",
    product_name: "Chè Thái Nguyên",
    producer_name: "Vườn trà chị Chợ Lạch",
    origin: "Thái Nguyên",
    quantity: 120,
    unit: "kg",
    expiry_date: "2026-09-14",
    created_at: "2026-09-19",
  },
  {
    id: 40,
    batch_code: "AGT-2026-0040",
    product_name: "Cà phê Robusta",
    producer_name: "Hợp tác xã Tân Cương",
    origin: "Đắk Lắk",
    quantity: 260,
    unit: "kg",
    expiry_date: "2026-09-13",
    created_at: "2026-09-19",
  },
  {
    id: 44,
    batch_code: "AGT-2026-0044",
    product_name: "Gạo Tám thơm",
    producer_name: "Nông trại Hải Hậu",
    origin: "Nam Định",
    quantity: 500,
    unit: "kg",
    expiry_date: "2026-09-12",
    created_at: "2026-09-19",
  },
  {
    id: 41,
    batch_code: "AGT-2026-0041",
    product_name: "Sầu riêng Ri6",
    producer_name: "Hợp tác xã Cư M’gar",
    origin: "Đắk Lắk",
    quantity: 180,
    unit: "kg",
    expiry_date: "2026-09-12",
    created_at: "2026-09-19",
  },
];
const getToken = () => {
  try {
    return (
      JSON.parse(
        sessionStorage.getItem("currentUser") ||
          localStorage.getItem("currentUser") ||
          "{}",
      ).access_token || ""
    );
  } catch {
    return "";
  }
};
const escapeHtml = (value) =>
  String(value ?? "-")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
const formatDate = (value) =>
  value
    ? new Date(String(value).replace(" ", "T")).toLocaleDateString("vi-VN")
    : "-";
let queue = [];
async function loadQueue() {
  try {
    const response = await fetch(`${API_BASE}/auditor/queue`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!response.ok) throw new Error();
    queue = await response.json();
  } catch {
    queue = fallbackQueue;
  }
  renderQueue(queue);
}
function renderQueue(items) {
  const body = document.getElementById("queue-body");
  if (!body) return;
  body.innerHTML =
    items
      .map(
        (item) =>
          `<tr data-id="${item.id}"><td><b>${escapeHtml(item.batch_code)}</b></td><td>${escapeHtml(item.product_name)}</td><td>${formatDate(item.created_at)}</td><td>${escapeHtml(item.producer_name)}</td></tr>`,
      )
      .join("") || '<tr><td colspan="4">Không có lô hàng phù hợp</td></tr>';
  const count = document.getElementById("pending-count");
  if (count) count.textContent = items.length;
}
function openDetail(id) {
  sessionStorage.setItem(
    "selectedBatch",
    JSON.stringify(
      queue.find((item) => String(item.id) === String(id)) || fallbackQueue[0],
    ),
  );
  window.location.href = `pendingdetail.html?id=${id}`;
}
function populateDetail() {
  let item;
  try {
    item = JSON.parse(sessionStorage.getItem("selectedBatch") || "null");
  } catch {
    item = null;
  }
  item ||= fallbackQueue[0];
  const values = {
    "detail-code": item.batch_code,
    "detail-product": item.product_name,
    "detail-farmer": item.producer_name,
    "detail-expiry": formatDate(item.expiry_date),
    "detail-quantity": `${item.quantity || "-"} ${item.unit || "kg"}`,
    "detail-created": formatDate(item.created_at),
    "detail-origin": item.origin,
  };
  Object.entries(values).forEach(([id, value]) => {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  });
  const sample = item.samples?.[0];
  if (sample) {
    document.getElementById("sample-label").textContent =
      `Sample #${sample.sample_code}`;
    document.getElementById("sample-date").textContent =
      `Lấy mẫu ${formatDate(sample.sample_date)}`;
  }
  const select = document.getElementById("sample-select");
  if (select)
    (item.samples || [{ id: "", sample_code: "SMP-HN-2026-005" }]).forEach(
      (sample) => select.add(new Option(sample.sample_code, sample.id)),
    );
  window.selectedBatch = item;
}
async function postJson(url, body) {
  const response = await fetch(`${API_BASE}${url}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${getToken()}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Thao tác không thành công");
  return data;
}
function bindDashboard() {
  loadQueue();
  document.getElementById("queue-body")?.addEventListener("click", (event) => {
    const row = event.target.closest("tr[data-id]");
    if (row) openDetail(row.dataset.id);
  });
  document
    .querySelectorAll("[data-refresh]")
    .forEach((button) => button.addEventListener("click", loadQueue));
  document.getElementById("search-button")?.addEventListener("click", () => {
    const form = new FormData(document.getElementById("filter-form"));
    renderQueue(
      queue.filter(
        (item) =>
          String(item.batch_code)
            .toLowerCase()
            .includes(String(form.get("batch") || "").toLowerCase()) &&
          String(item.product_name)
            .toLowerCase()
            .includes(String(form.get("product") || "").toLowerCase()) &&
          String(item.producer_name)
            .toLowerCase()
            .includes(String(form.get("farmer") || "").toLowerCase()),
      ),
    );
  });
}
function bindDetail() {
  populateDetail();
  const id = window.selectedBatch?.id;
  document
    .getElementById("create-sample")
    ?.addEventListener("click", async () => {
      try {
        const data = await postJson("/samples", {
          batch_id: id,
          sample_id: `SMP-${Date.now()}`,
          sampling_date: new Date().toISOString().slice(0, 10),
          sample_quantity: 1,
          sample_unit: "mẫu",
          sampling_location: window.selectedBatch?.origin || "Tại nông trại",
          sampling_method: "Lấy mẫu ngẫu nhiên",
        });
        document.getElementById("sample-label").textContent =
          `Sample #${data.sample_code}`;
        alert("Đã tạo sample mới.");
      } catch (error) {
        alert(error.message);
      }
    });
  document
    .getElementById("scroll-report")
    ?.addEventListener("click", () =>
      document
        .getElementById("report-form")
        ?.scrollIntoView({ behavior: "smooth" }),
    );
  document
    .getElementById("report-form")
    ?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const message = document.getElementById("report-message");
      const data = new FormData(event.currentTarget);
      data.append("batch_id", id);
      try {
        const response = await fetch(`${API_BASE}/auditor/reports`, {
          method: "POST",
          headers: { Authorization: `Bearer ${getToken()}` },
          body: data,
        });
        if (!response.ok)
          throw new Error(
            (await response.json()).detail || "Không thể upload báo cáo",
          );
        message.textContent = "Đã upload báo cáo và tạo SHA-256.";
      } catch (error) {
        message.textContent = getToken()
          ? error.message
          : "Đã lưu biểu mẫu demo. Cần đăng nhập Auditor để gửi lên hệ thống.";
      }
    });
  document
    .getElementById("approve-button")
    ?.addEventListener("click", () => decide("approve", "Đã duyệt lô hàng."));
  document
    .getElementById("reject-button")
    ?.addEventListener("click", () => decide("reject", "Đã từ chối lô hàng."));
}
async function decide(action, success) {
  const reason = document.getElementById("reject-reason")?.value.trim();
  if (action === "reject" && !reason) {
    alert("Vui lòng nhập lí do từ chối.");
    return;
  }
  try {
    await postJson(`/auditor/batches/${window.selectedBatch.id}/${action}`, {
      reason: reason || "Đạt tiêu chuẩn",
    });
    alert(success);
    window.location.href = "pendingdashboard.html";
  } catch (error) {
    alert(getToken() ? error.message : `${success} (chế độ demo)`);
  }
}
document.querySelector("[data-logout]")?.addEventListener("click", () => {
  sessionStorage.removeItem("currentUser");
  localStorage.removeItem("currentUser");
  window.location.href = "../login.html";
});
document
  .querySelector("[data-sidebar-toggle]")
  ?.addEventListener("click", () =>
    document.getElementById("sidebar")?.classList.toggle("open"),
  );
if (document.body.dataset.page === "dashboard") bindDashboard();
if (document.body.dataset.page === "detail") bindDetail();
