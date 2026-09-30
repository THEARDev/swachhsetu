/* ============================================
   SWACHHSETU — API WRAPPER
   JWT attach, 401 redirect, logout protection
   Back button se bhi protect karta hai
   ============================================ */

const API_BASE = "/api";

/* ============ TOKEN HELPERS ============ */
const getToken = () => localStorage.getItem("token");
const getUser = () => ({
  name: localStorage.getItem("name"),
  role: localStorage.getItem("role"),
});
const isLoggedIn = () => !!getToken();
const isAdmin = () => localStorage.getItem("role") === "admin";

function saveAuth({ token, role, name }) {
  localStorage.setItem("token", token);
  localStorage.setItem("role", role);
  localStorage.setItem("name", name);
}

function clearAuth() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  localStorage.removeItem("name");
}

/**
 * Logout — home page pe redirect
 * replace() use kiya taaki back button se wapas na aa sake
 */
function logout() {
  clearAuth();
  window.location.replace("/");
}

/* ============ GUARDS ============ */
function requireAuth() {
  if (!isLoggedIn()) {
    window.location.replace("/login.html");
    return false;
  }
  return true;
}

function requireAdmin() {
  if (!isLoggedIn() || !isAdmin()) {
    window.location.replace("/login.html");
    return false;
  }
  return true;
}

/* ============ CORE FETCH ============ */
async function api(path, method = "GET", body = null, isForm = false) {
  const headers = {};

  if (!isForm) headers["Content-Type"] = "application/json";

  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;

  const options = { method, headers };
  if (body) options.body = isForm ? body : JSON.stringify(body);

  let res;
  try {
    res = await fetch(API_BASE + path, options);
  } catch (err) {
    throw new Error("Network error — server se connect nahi ho paya");
  }

  // 401 — token invalid → logout
  if (res.status === 401) {
    clearAuth();
    if (!window.location.pathname.includes("login")) {
      window.location.replace("/login.html");
    }
    throw new Error("Session expired. Please login again.");
  }

  if (res.status === 204) return {};

  let data = {};
  try {
    data = await res.json();
  } catch (_) {
    data = {};
  }

  if (!res.ok) {
    throw new Error(data.msg || data.error || `Request failed (${res.status})`);
  }

  return data;
}

/* ============ CONVENIENCE ============ */
const apiGet = (path) => api(path, "GET");
const apiPost = (path, body) => api(path, "POST", body);
const apiPatch = (path, body) => api(path, "PATCH", body);
const apiDelete = (path) => api(path, "DELETE");
const apiForm = (path, formData) => api(path, "POST", formData, true);

/* ============ BACK BUTTON PROTECTION ============ */
function protectPage() {
  const protectedPages = ["dashboard", "admin", "report", "track"];
  const currentPath = window.location.pathname.toLowerCase();
  const isProtected = protectedPages.some((p) => currentPath.includes(p));

  if (isProtected && !isLoggedIn()) {
    window.location.replace("/login.html");
    return false;
  }
  return true;
}

document.addEventListener("DOMContentLoaded", protectPage);

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") {
    protectPage();
  }
});

window.addEventListener("pageshow", (e) => {
  if (e.persisted) {
    protectPage();
  }
});

/* ============ EXPORT TO WINDOW ============ */
window.api = api;
window.apiGet = apiGet;
window.apiPost = apiPost;
window.apiPatch = apiPatch;
window.apiDelete = apiDelete;
window.apiForm = apiForm;
window.getToken = getToken;
window.getUser = getUser;
window.isLoggedIn = isLoggedIn;
window.isAdmin = isAdmin;
window.saveAuth = saveAuth;
window.clearAuth = clearAuth;
window.logout = logout;
window.requireAuth = requireAuth;
window.requireAdmin = requireAdmin;
window.protectPage = protectPage;