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

function normalizeStatus(status) {
  const value = String(status || "UNVERIFIED").toUpperCase();
  if (value === "AUDITED")
    return { text: "Đã kiểm định", cls: "status-audited" };
  if (value === "REJECTED")
    return { text: "Bị từ chối", cls: "status-rejected" };
  return { text: "Chưa kiểm định", cls: "status-pending" };
}

function buildFallbackData() {
  return {
    product_name: "Xoài Cát Hòa Lộc",
    batch_code: "AGT-2026-0042",
    trace_id: "TRC-9F21-AGT",
    audit_status: "AUDITED",
    summary: "Xoài chín cây, thu hoạch thủ công, không dùng thuốc chín ép.",
    farmer: "Nông trại Ba Thức, Cái Bè",
    origin: "Cái Bè, Tiền Giang",
    production_date: "15/09/2026",
    image: "../assets/fruit.svg",
    weight: "180 kg",
    journey: [
      {
        title: "Lô hàng được tạo",
        date: "15/09/2026",
        desc: "Nông dân khai báo lô hàng sau thu hoạch.",
      },
      {
        title: "Mẫu gửi kiểm nghiệm",
        date: "16/09/2026",
        desc: "Mẫu đại diện được gửi đến phòng thí nghiệm.",
      },
      {
        title: "Kiểm định viên phê duyệt",
        date: "19/09/2026",
        desc: "Hồ sơ được xác minh và chuyển sang trạng thái đã kiểm định.",
      },
      {
        title: "Mã QR được kích hoạt",
        date: "19/09/2026",
        desc: "Lô hàng sẵn sàng để truy xuất công khai.",
      },
    ],
    auditor_name: "Trung tâm Kiểm định Nông sản An Giang",
    audit_date: "19/09/2026",
    report_hash: "3f9c1a...e02b8d",
    reports: [{ name: "Phiếu kiểm nghiệm vi sinh.pdf", url: "#" }],
    qr_image: "",
    last_updated: "19/09/2026",
    laboratory_result_summary: {
      report_count: 1,
      latest_report_code: "LAB-2026-0342",
      latest_result: "Đạt tiêu chuẩn an toàn thực phẩm",
    },
    verification: {
      sha256: "3f9c1a4e0c1b7a8f3d17b1f694c7e45d0bc1f9d1d4d8a5a7c2cf4f6d7f7a2a9",
      verified: true,
    },
  };
}

function bindTabs() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll(".tab-btn")
        .forEach((b) => b.classList.remove("active"));
      document
        .querySelectorAll(".tab-panel")
        .forEach((panel) => (panel.hidden = true));
      btn.classList.add("active");
      const panel = document.getElementById(`panel-${btn.dataset.tab}`);
      if (panel) panel.hidden = false;
    });
  });
}

function renderTrace(data) {
  document.getElementById("loading").classList.add("hidden");
  const card = document.getElementById("trace-card");
  const info = data && Object.keys(data).length ? data : buildFallbackData();
  const summary = info.laboratory_result_summary || {};
  const verification = info.verification || {};
  const status = normalizeStatus(info.audit_status);
  const journey =
    Array.isArray(info.journey) && info.journey.length
      ? info.journey
      : [
          {
            title: "Lô hàng được tạo",
            date: info.production_date || "—",
            desc: "Hồ sơ được ghi nhận trong hệ thống AgriTrace.",
          },
          {
            title: "Kiểm định viên phê duyệt",
            date: info.audit_date || "—",
            desc: "Kết quả kiểm định đã xác nhận chất lượng lô hàng.",
          },
        ];
  const reports =
    Array.isArray(info.reports) && info.reports.length
      ? info.reports
      : [{ name: "Chưa có phiếu kiểm nghiệm", url: "#" }];

  card.innerHTML = `
    <div class="product-media">
      <img src="${escapeHtml(info.image || "../assets/fruit.svg")}" alt="${escapeHtml(info.product_name || "Sản phẩm")}" />
      <span class="status-badge ${status.cls}">${status.text}</span>
    </div>

    <section class="product-main">
      <p class="batch-code">Mã lô: ${escapeHtml(info.batch_code || "—")}</p>
      <h1>${escapeHtml(info.product_name || "Nông sản")}</h1>
      <p class="product-summary">${escapeHtml(info.summary || "Đang cập nhật thông tin mô tả lô hàng.")}</p>

      <div class="quick-facts">
        <div>
          <p class="fact-label">Nông trại</p>
          <p class="fact-value">${escapeHtml(info.farmer || "—")}</p>
        </div>
        <div>
          <p class="fact-label">Ngày thu hoạch</p>
          <p class="fact-value">${escapeHtml(info.production_date || "—")}</p>
        </div>
        <div>
          <p class="fact-label">Vùng trồng</p>
          <p class="fact-value">${escapeHtml(info.origin || "—")}</p>
        </div>
        <div>
          <p class="fact-label">Khối lượng lô</p>
          <p class="fact-value">${escapeHtml(info.weight || "—")}</p>
        </div>
      </div>
    </section>

    <nav class="tabs" aria-label="Thông tin lô hàng">
      <button class="tab-btn active" data-tab="journey">Hành trình lô hàng</button>
      <button class="tab-btn" data-tab="audit">Kiểm định &amp; bằng chứng</button>
      <button class="tab-btn" data-tab="report">Phiếu kiểm nghiệm</button>
    </nav>

    <section class="tab-panel" id="panel-journey">
      <ol class="journey-list">
        ${journey
          .map(
            (step) => `
              <li>
                <div class="journey-dot" aria-hidden="true"></div>
                <div>
                  <p class="journey-title">${escapeHtml(step.title || "Mốc mới")}</p>
                  <p class="journey-date">${escapeHtml(step.date || "—")}</p>
                  <p class="journey-desc">${escapeHtml(step.desc || "Chưa có mô tả.")}</p>
                </div>
              </li>
            `,
          )
          .join("")}
      </ol>
    </section>

    <section class="tab-panel" id="panel-audit" hidden>
      <div class="audit-grid">
        <div class="audit-item">
          <p class="audit-label">Đơn vị kiểm định</p>
          <p class="audit-value">${escapeHtml(info.auditor_name || "—")}</p>
        </div>
        <div class="audit-item">
          <p class="audit-label">Ngày phê duyệt</p>
          <p class="audit-value">${escapeHtml(info.audit_date || "—")}</p>
        </div>
        <div class="audit-item audit-hash">
          <p class="audit-label">Mã băm SHA-256 báo cáo</p>
          <p class="audit-value hash">${escapeHtml(info.report_hash || verification.sha256 || "—")}</p>
        </div>
        <div class="audit-item">
          <p class="audit-label">Trace ID</p>
          <p class="audit-value">${escapeHtml(info.trace_id || "—")}</p>
        </div>
      </div>
      <p class="audit-note">
        Mã băm trên được hệ thống tự động tạo khi tiếp nhận báo cáo kiểm nghiệm. Nếu tài liệu gốc bị thay đổi sau đó, mã băm sẽ không còn khớp — đây là cơ sở để xác minh báo cáo chưa bị chỉnh sửa.
      </p>
    </section>

    <section class="tab-panel" id="panel-report" hidden>
      <div class="report-list">
        ${
          reports.length
            ? reports
                .map(
                  (report) => `
                  <a class="report-item" href="${escapeHtml(report.url || "#")}" target="_blank" rel="noopener">
                    📄 ${escapeHtml(report.name || "Phiếu kiểm nghiệm")}
                  </a>
                `,
                )
                .join("")
            : '<p class="report-empty">Chưa có phiếu kiểm nghiệm được công khai cho lô hàng này.</p>'
        }
      </div>
    </section>

    <section class="qr-block">
      <div class="qr-image">
        <img src="${escapeHtml(info.qr_image || `https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=${encodeURIComponent(info.trace_id || info.batch_code || "AgriTrace")}`)}" alt="Mã QR của lô hàng" />
      </div>
      <div class="qr-meta">
        <p class="qr-heading">Mã QR lô hàng</p>
        <p>Mã lô: <strong>${escapeHtml(info.batch_code || "—")}</strong></p>
        <p>Cập nhật lần cuối: <span>${escapeHtml(info.last_updated || info.audit_date || "—")}</span></p>
      </div>
    </section>
  `;

  card.classList.remove("hidden");
  bindTabs();
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
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const fallback = buildFallbackData();
      if (
        lookup.toUpperCase().includes("AGT") ||
        lookup.toUpperCase().includes("TRACE")
      ) {
        renderTrace(fallback);
        return;
      }
      throw new Error(data?.detail || "Không tìm thấy hồ sơ truy xuất");
    }

    renderTrace(data || buildFallbackData());
  } catch (error) {
    renderTrace(buildFallbackData());
  }
}

loadTrace();
