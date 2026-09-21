const API_BASE = "http://127.0.0.1:8000";

// Auth Guard: Kiểm tra nếu đã có phiên Admin thì vào thằng admin.html
function checkExistingSession() {
  try {
    const serializedUser = sessionStorage.getItem("currentUser") || localStorage.getItem("currentUser");
    if (serializedUser) {
      const user = JSON.parse(serializedUser);
      if (user.access_token && String(user.role || "").toUpperCase() === "ADMIN") {
        window.location.href = "./admin.html";
      }
    }
  } catch (e) {
    sessionStorage.removeItem("currentUser");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  checkExistingSession();

  const form = document.getElementById("adminLoginForm");
  const emailInput = document.getElementById("adminEmail");
  const passwordInput = document.getElementById("adminPassword");
  const togglePasswordBtn = document.getElementById("togglePasswordBtn");
  const submitBtn = document.getElementById("submitBtn");
  const errorMessage = document.getElementById("errorMessage");

  // Toggle ẩn/hiện mật khẩu
  togglePasswordBtn?.addEventListener("click", () => {
    const isPassword = passwordInput.type === "password";
    passwordInput.type = isPassword ? "text" : "password";
    togglePasswordBtn.textContent = isPassword ? "Ẩn" : "Hiện";
  });

  // Xử lý gửi Form Đăng nhập
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    
    errorMessage.textContent = "";
    submitBtn.disabled = true;
    submitBtn.textContent = "Đang xác thực...";

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    try {
      const response = await fetch(`${API_BASE}/auth/login-admin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          identifier: email,
          password: password,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || "Email hoặc mật khẩu không chính xác.");
      }

      // Kiểm tra xem có đúng quyền ADMIN không
      const userRole = String(data.role || "").toUpperCase();
      if (userRole !== "ADMIN") {
        throw new Error("Tài khoản của bạn không có quyền truy cập cổng Admin.");
      }

      // Lưu thông tin phiên đăng nhập
      const adminSession = {
        access_token: data.access_token,
        role: "ADMIN",
        email: data.email || email,
        name: data.name || "Admin",
      };

      sessionStorage.setItem("currentUser", JSON.stringify(adminSession));
      window.location.href = "./admin.html";
    } catch (error) {
      errorMessage.textContent = error.message;
      submitBtn.disabled = false;
      submitBtn.textContent = "Đăng nhập Admin";
    }
  });
});