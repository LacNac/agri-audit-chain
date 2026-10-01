(function () {
  const SESSION_KEY = "currentUser";
  const LOGIN_LOCK_KEY = "agriTraceLoginLock";
  const TOKEN_KEYS = ["token", "access_token", "authToken", "auth_token", "jwt"];
  const AUTH_COOKIE_NAMES = new Set(TOKEN_KEYS);

  function parseSession(serialized) {
    if (!serialized) return null;
    try {
      const session = JSON.parse(serialized);
      if (!session || typeof session !== "object" || !session.access_token)
        return null;
      const payload = session.access_token.split(".")[1];
      if (payload) {
        const claims = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
        if (claims.exp && claims.exp * 1000 <= Date.now()) return null;
      }
      return session;
    } catch {
      return null;
    }
  }

  function sessionFromToken(token) {
    if (!token) return null;
    try {
      const payload = token.split(".")[1];
      const claims = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
      const role = String(claims.role || "").toUpperCase();
      if (!claims.exp || claims.exp * 1000 <= Date.now()) return null;
      if (!["FARMER", "AUDITOR", "ADMIN"].includes(role)) return null;
      return { access_token: token, role };
    } catch {
      return null;
    }
  }

  function getSession() {
    const localSession = parseSession(localStorage.getItem(SESSION_KEY));
    const tabSession = parseSession(sessionStorage.getItem(SESSION_KEY));
    let session = localSession || tabSession;

    if (!session) {
      const storedToken = TOKEN_KEYS.map(
        (key) => localStorage.getItem(key) || sessionStorage.getItem(key),
      ).find(Boolean);
      const cookieToken = document.cookie
        .split(";")
        .map((cookie) => cookie.trim().split("="))
        .find(([name]) => AUTH_COOKIE_NAMES.has(name.toLowerCase()))?.[1];
      session = sessionFromToken(storedToken || cookieToken);
    }

    if (session) localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    else clearSession();
    sessionStorage.removeItem(SESSION_KEY);
    return session;
  }

  function clearAuthCookies() {
    document.cookie.split(";").forEach((cookie) => {
      const name = cookie.split("=")[0].trim();
      if (!AUTH_COOKIE_NAMES.has(name.toLowerCase())) return;
      ["/", "/admin", "/auditor", "/farmer"].forEach((path) => {
        document.cookie = `${name}=; Max-Age=0; path=${path}; SameSite=Lax`;
      });
    });
  }

  function clearSession() {
    localStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem(SESSION_KEY);
    TOKEN_KEYS.forEach((key) => {
      localStorage.removeItem(key);
      sessionStorage.removeItem(key);
    });
    clearAuthCookies();
  }

  function saveSession(session) {
    if (!session?.access_token) throw new Error("Phiên đăng nhập không hợp lệ.");
    if (getSession()) throw new Error("Vui lòng đăng xuất tài khoản hiện tại trước.");
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    sessionStorage.removeItem(SESSION_KEY);
  }

  function withLoginLock(operation) {
    const run = async () => {
      if (getSession())
        throw new Error("Vui lòng đăng xuất tài khoản hiện tại trước khi đăng nhập.");
      return operation();
    };

    if (navigator.locks?.request) {
      return navigator.locks.request(
        "agritrace-auth-session",
        { ifAvailable: true },
        (lock) => {
          if (!lock) throw new Error("Một yêu cầu đăng nhập khác đang được xử lý.");
          return run();
        },
      );
    }

    const lockId = `${Date.now()}-${Math.random()}`;
    const existingLock = JSON.parse(localStorage.getItem(LOGIN_LOCK_KEY) || "null");
    if (existingLock?.expiresAt > Date.now())
      return Promise.reject(new Error("Một yêu cầu đăng nhập khác đang được xử lý."));

    localStorage.setItem(
      LOGIN_LOCK_KEY,
      JSON.stringify({ id: lockId, expiresAt: Date.now() + 60000 }),
    );
    const acquiredLock = JSON.parse(localStorage.getItem(LOGIN_LOCK_KEY) || "null");
    if (acquiredLock?.id !== lockId)
      return Promise.reject(new Error("Một yêu cầu đăng nhập khác đang được xử lý."));

    return run().finally(() => {
      const currentLock = JSON.parse(localStorage.getItem(LOGIN_LOCK_KEY) || "null");
      if (currentLock?.id === lockId) localStorage.removeItem(LOGIN_LOCK_KEY);
    });
  }

  function loginPath() {
    const path = location.pathname.toLowerCase();
    if (path.includes("/admin/")) return "./admin_login.html";
    if (path.includes("/farmer/") || path.includes("/auditor/"))
      return "../login.html";
    return "login.html";
  }

  function logout(options = {}) {
    clearSession();
    localStorage.setItem("agriTraceLogoutEvent", String(Date.now()));
    if (options.redirectTo) location.href = options.redirectTo;
  }

  function logoutTo(path) {
    logout({ redirectTo: path });
  }

  function requireRole(role, redirectTo = loginPath()) {
    const session = getSession();
    if (String(session?.role || "").toUpperCase() !== role) {
      location.replace(redirectTo);
      return null;
    }
    return session;
  }

  function requireLogoutBeforeLogin() {
    const session = getSession();
    if (!session) return true;
    const role = String(session.role || "tài khoản hiện tại").toUpperCase();
    if (confirm(`Bạn đang đăng nhập bằng ${role}. Đăng xuất trước khi tiếp tục?`)) {
      logout();
      return true;
    }
    alert("Vui lòng đăng xuất tài khoản hiện tại trước khi đăng nhập tài khoản khác.");
    return false;
  }

  function isLoginPage() {
    return /\/login(?:\.html)?$/i.test(location.pathname) ||
      /\/admin_login\.html$/i.test(location.pathname);
  }

  window.AppAuth = {
    getSession,
    saveSession,
    clearSession,
    withLoginLock,
    logout,
    logoutTo,
    requireRole,
    requireLogoutBeforeLogin,
  };

  window.addEventListener("storage", (event) => {
    if (event.key !== SESSION_KEY && event.key !== "agriTraceLogoutEvent") return;
    if (isLoginPage()) return;
    if (event.key === SESSION_KEY && event.newValue) {
      const incomingSession = parseSession(event.newValue);
      if (incomingSession?.access_token === getSession()?.access_token) return;
    }
    location.replace(loginPath());
  });

  if (/\/farmer\/farmer\.html$/i.test(location.pathname)) {
    requireRole("FARMER", "../login.html");
  } else if (/\/auditor\/(auditdashboard|auditorprofile)\.html$/i.test(location.pathname)) {
    requireRole("AUDITOR", "../login.html");
  } else if (/\/admin\/admin\.html$/i.test(location.pathname)) {
    requireRole("ADMIN", "./admin_login.html");
  }
})();