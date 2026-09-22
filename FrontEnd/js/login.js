// ===================================================================
// AgriTrace — điều hướng giữa các màn hình (SPA đơn giản, không reload)
// ===================================================================

const API_BASE = "http://127.0.0.1:8000";

const CARD_IDS = {
  landing: "card-landing",
  "register-1": "card-register-1",
  "register-2": "card-register-2",
  "login-kd": "card-login-kd",
  "login-dn": "card-login-dn",
};

const authManager = {
  saveSession(user) {
    const serializedUser = JSON.stringify(user);
    sessionStorage.setItem("currentUser", serializedUser);
    localStorage.setItem("currentUser", serializedUser);
  },
};

function showCard(name) {
  const targetId = CARD_IDS[name];
  if (!targetId) return;

  Object.values(CARD_IDS).forEach((id) => {
    const card = document.getElementById(id);
    if (card) card.hidden = id !== targetId;
  });
}

document.addEventListener("click", (event) => {
  const trigger = event.target.closest("[data-goto]");
  if (!trigger) return;
  event.preventDefault();
  showCard(trigger.getAttribute("data-goto"));
});

document.querySelectorAll("[data-toggle]").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.getElementById(button.dataset.toggle);
    if (!input) return;
    input.type = input.type === "password" ? "text" : "password";
    button.textContent = input.type === "password" ? "Hiện" : "Ẩn";
  });
});

let registerData = {};
const formStep1 = document.getElementById("form-register-1");
const formStep2 = document.getElementById("form-register-2");

formStep1?.addEventListener("submit", (event) => {
  event.preventDefault();
  const password = document.getElementById("r1-pass").value;
  const confirmation = document.getElementById("r1-pass2").value;

  if (password !== confirmation) {
    alert("Mật khẩu xác nhận không khớp!");
    return;
  }

  registerData = {
    full_name: document.getElementById("r1-name").value.trim(),
    phone: document.getElementById("r1-phone").value.trim(),
    email: document.getElementById("r1-email").value.trim(),
    password,
  };
  showCard("register-2");
});

async function submitAuthForm(form, endpoint, identifierId, passwordId) {
  const button = form.querySelector('button[type="submit"]');
  const identifierInput = form.querySelector(`#${identifierId}`);
  const passwordInput = form.querySelector(`#${passwordId}`);

  if (!button || !identifierInput || !passwordInput) {
    alert("Không tìm thấy đầy đủ trường đăng nhập trên trang.");
    return;
  }

  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = "Đang xử lý...";

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        identifier: identifierInput.value.trim(),
        password: passwordInput.value,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Đăng nhập thất bại");

    authManager.saveSession(data);

    if (String(data.role || "").toUpperCase() === "ADMIN") {
      window.location.href = "./admin.html";
      return;
    }

    if (String(data.role || "").toUpperCase() === "AUDITOR") {
      window.location.href = "./auditor.html";
      return;
    }

    if (String(data.role || "").toUpperCase() === "FARMER") {
      window.location.href = "./farmer.html";
      return;
    }

    alert(`Xin chào ${data.full_name}!`);
    form.reset();
  } catch (error) {
    alert(`Lỗi: ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
}

function formatApiError(detail, fallbackMessage) {
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item.loc)
          ? item.loc[item.loc.length - 1]
          : "Dữ liệu";
        const messages = {
          full_name: "Họ và tên",
          phone: "Số điện thoại",
          email: "Email",
          password: "Mật khẩu",
          business_name: "Tên doanh nghiệp",
          business_type: "Loại hình hoạt động",
          product_type: "Chủng loại sản phẩm",
          tax_code: "Mã số thuế",
        };
        return `${messages[field] || field}: ${item.msg || "Dữ liệu không hợp lệ"}`;
      })
      .join("; ");
  }
  return typeof detail === "string" ? detail : fallbackMessage;
}

formStep2?.addEventListener("submit", async (event) => {
  event.preventDefault();
  registerData.business_type = document.getElementById("r2-type").value;
  registerData.product_type = document
    .getElementById("r2-category")
    .value.trim();
  registerData.business_name = document
    .getElementById("r2-company")
    .value.trim();
  registerData.tax_code = document.getElementById("r2-tax").value.trim();

  const button = formStep2.querySelector('button[type="submit"]');
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = "Đang xử lý...";

  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(registerData),
    });
    const data = await response.json();
    if (!response.ok)
      throw new Error(formatApiError(data.detail, "Đăng ký thất bại"));

    alert(`Đăng ký thành công! Chào mừng ${data.username}`);
    registerData = {};
    formStep1.reset();
    formStep2.reset();
    showCard("landing");
  } catch (error) {
    alert(`Lỗi: ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
});

document
  .getElementById("form-login-dn")
  ?.addEventListener("submit", (event) => {
    event.preventDefault();
    submitAuthForm(event.currentTarget, "/auth/login", "dn-email", "dn-pass");
  });

document
  .getElementById("form-login-kd")
  ?.addEventListener("submit", (event) => {
    event.preventDefault();
    submitAuthForm(
      event.currentTarget,
      "/auth/login-auditor",
      "kd-email",
      "kd-pass",
    );
  });

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach((form) => {
    const button = form.querySelector('button[type="submit"]');
    if (!button) return;

    const updateButtonState = () => {
      button.disabled = !form.checkValidity();
      button.classList.toggle("is-ready", !button.disabled);
    };

    form.addEventListener("input", updateButtonState);
    form.addEventListener("change", updateButtonState);
    updateButtonState();
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const mode = urlParams.get("mode");
  const role = urlParams.get("role");

  if (mode === "register" || (role === "auditor" && mode !== "login")) {
    // Bấm "Tạo tài khoản" -> Chuyển thẳng sang form Đăng ký bước 1
    showCard("register-1");
  } else if (mode === "login") {
    if (role === "auditor") {
      // Chỉ khi URL là login.html?mode=login&role=auditor mới vào kiểm định
      showCard("login-kd");
    } else if (role === "farmer" || role === "dn") {
      // Chỉ khi URL có đích danh doanh nghiệp mới vào login-dn
      showCard("login-dn");
    } else {
      // Bấm nút Đăng nhập chung từ trang chủ -> Hiện màn hình chọn vai trò (Landing)
      showCard("landing");
    }
  } else {
    // Mặc định không có tham số gì
    showCard("landing");
  }
});
