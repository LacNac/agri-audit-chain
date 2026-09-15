// ===================================================================
// AgriTrace — điều hướng giữa các màn hình (SPA đơn giản, không reload)
// ===================================================================

(function () {
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

    // Cuộn lên đầu panel khi chuyển màn hình (hữu ích trên mobile)
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

  // Chặn submit thật (đây là bản demo giao diện) và điều hướng tiếp theo hợp lý
  const flows = {
    "form-register-1": "register-2",
    "form-register-2": "landing",
    "form-login-kd": null,
    "form-login-dn": null,
  };

  Object.entries(flows).forEach(([formId, nextScreen]) => {
    const form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (nextScreen) showCard(nextScreen);
    });
  });
})();

// ==========================================
// TỰ ĐỘNG ĐỔI MÀU NÚT KHI ĐIỀN ĐỦ THÔNG TIN
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll("form");

  forms.forEach((form) => {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return;

    function validateForm() {
      // Kiểm tra xem tất cả các ô có chữ thuộc tính required đã điền chưa
      const isValid = form.checkValidity();

      if (isValid) {
        submitBtn.removeAttribute("disabled");
        submitBtn.classList.add("is-ready"); // Thêm class để CSS nhận màu #1D12C3
      } else {
        submitBtn.setAttribute("disabled", "disabled");
        submitBtn.classList.remove("is-ready");
      }
    }

    // Lắng nghe mỗi khi người dùng gõ chữ hoặc tích chọn checkbox
    form.addEventListener("input", validateForm);
    form.addEventListener("change", validateForm);

    // Chạy kiểm tra ngay lần đầu tải trang
    validateForm();
  });
});
