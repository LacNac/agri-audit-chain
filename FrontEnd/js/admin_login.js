const API_BASE = "https://agri-audit-chain-backend.onrender.com";

document.addEventListener("DOMContentLoaded", () => {
  AppAuth.requireLogoutBeforeLogin();

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
      await AppAuth.withLoginLock(async () => {
        const response = await fetch(`${API_BASE}/auth/login-admin`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identifier: email, password }),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok)
          throw new Error(data.detail || "Email hoặc mật khẩu không chính xác.");

        if (String(data.role || "").toUpperCase() !== "ADMIN") {
          throw new Error("Tài khoản của bạn không có quyền truy cập cổng Admin.");
        }

        AppAuth.saveSession({
          access_token: data.access_token,
          role: "ADMIN",
          email: data.email || email,
          name: data.name || "Admin",
        });
      });
      window.location.href = "./admin.html";
    } catch (error) {
      errorMessage.textContent = error.message;
      submitBtn.disabled = false;
      submitBtn.textContent = "Đăng nhập Admin";
    }
  });
});
