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

function showCard(name) {
  const targetId = CARD_IDS[name];
  if (!targetId) return;

  Object.values(CARD_IDS).forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.hidden = id !== targetId;
  });

  const panel = document.querySelector(".panel");
  if (panel)
    panel.scrollTo({
      top: 0,
      behavior: "instant" in window ? "instant" : "auto",
    });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Bắt tất cả phần tử có [data-goto] (nút, thẻ a, logo...)
document.addEventListener("click", (e) => {
  const trigger = e.target.closest("[data-goto]");
  if (!trigger) return;
  e.preventDefault();
  showCard(trigger.getAttribute("data-goto"));
});

// Hiện / ẩn mật khẩu
document.querySelectorAll("[data-toggle]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const input = document.getElementById(btn.getAttribute("data-toggle"));
    if (!input) return;
    const isHidden = input.type === "password";
    input.type = isHidden ? "text" : "password";
    btn.textContent = isHidden ? "Ẩn" : "Hiện";
  });
});

// ================================================================
// ĐĂNG KÝ — gom dữ liệu bước 1 + bước 2, gọi API /auth/register
// ================================================================
let registerData = {};

const formStep1 = document.getElementById("form-register-1");
if (formStep1) {
  formStep1.addEventListener("submit", (e) => {
    e.preventDefault();

    const password = document.getElementById("r1-pass").value;
    const password2 = document.getElementById("r1-pass2").value;

    if (password !== password2) {
      alert("Mật khẩu xác nhận không khớp!");
      return;
    }
    if (password.length < 6) {
      alert("Mật khẩu phải có tối thiểu 6 ký tự!");
      return;
    }

    registerData.full_name = document.getElementById("r1-name").value.trim();
    registerData.phone = document.getElementById("r1-phone").value.trim();
    registerData.email = document.getElementById("r1-email").value.trim();
    registerData.password = password;

    showCard("register-2");
  });
}

const formStep2 = document.getElementById("form-register-2");
if (formStep2) {
  formStep2.addEventListener("submit", async (e) => {
    e.preventDefault();

    registerData.business_type = document.getElementById("r2-type").value;
    registerData.product_type = document
      .getElementById("r2-category")
      .value.trim();
    registerData.business_name = document
      .getElementById("r2-company")
      .value.trim();
    registerData.tax_code = document.getElementById("r2-tax").value.trim();

    const submitBtn = formStep2.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Đang xử lý...";

    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registerData),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Đăng ký thất bại");
      }

      alert(`Đăng ký thành công! Chào mừng ${data.username}`);
      registerData = {};
      formStep1.reset();
      formStep2.reset();
      showCard("landing");
    } catch (err) {
      alert("Lỗi: " + err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
}

// ================================================================
// ĐĂNG NHẬP — Doanh nghiệp (email)
// ================================================================
const formLoginDn = document.getElementById("form-login-dn");
if (formLoginDn) {
  formLoginDn.addEventListener("submit", async (e) => {
    e.preventDefault();

    const identifier = document.getElementById("dn-email").value.trim();
    const password = document.getElementById("dn-pass").value;

    const submitBtn = formLoginDn.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Đang đăng nhập...";

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Đăng nhập thất bại");

      const role = String(data.role || "").toUpperCase();
      sessionStorage.setItem("currentUser", JSON.stringify(data));
      localStorage.setItem("currentUser", JSON.stringify(data));

      if (role === "FARMER") {
        window.location.href = "./farmer/farmer.html";
      } else if (role === "ADMIN") {
        window.location.href = "./admin/admin.html";
      } else if (role === "AUDITOR") {
        window.location.href = "./auditor/auditdashboard.html";
      } else {
        throw new Error("Vai trò tài khoản không hợp lệ");
      }
    } catch (err) {
      alert("Lỗi: " + err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
}

// ================================================================
// ĐĂNG NHẬP — Kiểm định (ID = username)
// ================================================================
const formLoginKd = document.getElementById("form-login-kd");
if (formLoginKd) {
  formLoginKd.addEventListener("submit", async (e) => {
    e.preventDefault();

    const identifier = document.getElementById("kd-email").value.trim();
    const password = document.getElementById("kd-pass").value;

    const submitBtn = formLoginKd.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Đang đăng nhập...";

    try {
      const res = await fetch(`${API_BASE}/auth/login-auditor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Đăng nhập thất bại");

      const role = String(data.role || "").toUpperCase();
      sessionStorage.setItem("currentUser", JSON.stringify(data));
      localStorage.setItem("currentUser", JSON.stringify(data));

      if (role === "AUDITOR") {
        window.location.href = "./auditor/auditdashboard.html";
      } else if (role === "ADMIN") {
        window.location.href = "./admin/admin.html";
      } else if (role === "FARMER") {
        window.location.href = "./farmer/farmer.html";
      } else {
        throw new Error("Vai trò tài khoản không hợp lệ");
      }
    } catch (err) {
      alert("Lỗi: " + err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
}

// ==========================================
// TỰ ĐỘNG ĐỔI MÀU NÚT KHI ĐIỀN ĐỦ THÔNG TIN
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll("form");

  forms.forEach((form) => {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return;

    function validateForm() {
      const isValid = form.checkValidity();
      if (isValid) {
        submitBtn.removeAttribute("disabled");
        submitBtn.classList.add("is-ready");
      } else {
        submitBtn.setAttribute("disabled", "disabled");
        submitBtn.classList.remove("is-ready");
      }
    }

    form.addEventListener("input", validateForm);
    form.addEventListener("change", validateForm);
    validateForm();
  });
});
