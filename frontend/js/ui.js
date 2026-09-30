/* ============================================
   SWACHHSETU — UI HELPERS
   Toast, Loader, Formatters, Badges, Modal
   ============================================ */

/* ============ TOASTS ============ */
function ensureToastContainer() {
  let el = document.getElementById("toasts");
  if (!el) {
    el = document.createElement("div");
    el.id = "toasts";
    document.body.appendChild(el);
  }
  return el;
}

const TOAST_ICONS = {
  success: "✅",
  error: "❌",
  info: "ℹ️",
  warn: "⚠️",
};

function toast(message, type = "info", duration = 3000) {
  const container = ensureToastContainer();
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.innerHTML = `<span>${TOAST_ICONS[type] || ""}</span><span>${message}</span>`;
  container.appendChild(el);

  setTimeout(() => {
    el.classList.add("fade-out");
    setTimeout(() => el.remove(), 300);
  }, duration);
}

/* ============ LOADER ============ */
function showLoader(targetOrSelector, text = "") {
  const target =
    typeof targetOrSelector === "string"
      ? document.querySelector(targetOrSelector)
      : targetOrSelector;
  if (!target) return;
  target.innerHTML = `
    <div class="loader"></div>
    ${text ? `<p class="text-center text-muted">${text}</p>` : ""}
  `;
}

function buttonLoading(btn, loadingText = "Loading...") {
  if (!btn) return () => {};
  const original = btn.innerHTML;
  const wasDisabled = btn.disabled;
  btn.disabled = true;
  btn.innerHTML = `<span class="loader loader-sm"></span> ${loadingText}`;
  return () => {
    btn.innerHTML = original;
    btn.disabled = wasDisabled;
  };
}

/* ============ EMPTY STATE ============ */
function emptyState(emoji, title, subtitle = "", actionHTML = "") {
  return `
    <div class="empty">
      <span class="emoji">${emoji}</span>
      <h3>${title}</h3>
      ${subtitle ? `<p>${subtitle}</p>` : ""}
      ${actionHTML}
    </div>
  `;
}

/* ============ FORMATTERS ============ */
function formatDate(iso) {
  if (!iso) return "-";
  try {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return "-";
    return d.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "-";
  }
}

function timeAgo(iso) {
  if (!iso) return "-";
  const d = new Date(iso);
  const diff = Math.floor((Date.now() - d.getTime()) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hr ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)} days ago`;
  return formatDate(iso);
}

/* ============ CATEGORY LABELS ============ */
const CATEGORY_LABELS = {
  overflow: "Overflowing Bin",
  road: "Garbage on Road",
  illegal: "Illegal Dumping",
  missed: "Missed Collection",
  other: "Other",
};

function categoryLabel(cat) {
  return CATEGORY_LABELS[cat] || cat || "Unknown";
}

function categoryBadge(cat) {
  const label = categoryLabel(cat);
  return `<span class="badge badge-${cat || "other"}">${label}</span>`;
}

/* ============ STATUS LABELS ============ */
const STATUS_LABELS = {
  submitted: "Submitted",
  acknowledged: "Acknowledged",
  in_progress: "In Progress",
  resolved: "Resolved",
  closed: "Closed",
};

function statusLabel(status) {
  return STATUS_LABELS[status] || status || "Unknown";
}

function statusBadge(status) {
  const cls = status === "in_progress" ? "progress" : status;
  return `<span class="badge badge-${cls || "closed"}">${statusLabel(status)}</span>`;
}

/* ============ PRIORITY BADGE (NLP) ============ */
function priorityBadge(priority) {
  if (!priority) return "";
  const icons = { high: "🔴", medium: "🟡", low: "🟢" };
  return `<span class="badge badge-${priority}">${icons[priority] || ""} ${priority.toUpperCase()}</span>`;
}

/* ============ TEXT UTILITIES ============ */
function escapeHTML(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function truncate(str, n = 60) {
  if (!str) return "";
  return str.length > n ? str.slice(0, n) + "..." : str;
}

function initials(name) {
  if (!name) return "?";
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

/* ============ NAVBAR ============ */
function initNavbar() {
  const nav = document.querySelector(".navbar");
  if (!nav) return;
  window.addEventListener("scroll", () => {
    if (window.scrollY > 20) nav.classList.add("scrolled");
    else nav.classList.remove("scrolled");
  });
}

/* ============ FORM HELPERS ============ */
function formToObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function resetForm(form) {
  form.reset();
}

/* ============ MODAL ============ */
function showModal(contentHTML, onClose) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `<div class="modal">${contentHTML}</div>`;
  document.body.appendChild(overlay);

  const close = () => {
    overlay.remove();
    if (typeof onClose === "function") onClose();
  };

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });

  return { el: overlay, close };
}

/* ============ CLIPBOARD ============ */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    toast("Copied to clipboard!", "success", 1500);
  } catch {
    toast("Copy failed", "error");
  }
}

/* ============ EXPORT TO WINDOW ============ */
window.toast = toast;
window.showLoader = showLoader;
window.buttonLoading = buttonLoading;
window.emptyState = emptyState;
window.formatDate = formatDate;
window.timeAgo = timeAgo;
window.categoryLabel = categoryLabel;
window.categoryBadge = categoryBadge;
window.statusLabel = statusLabel;
window.statusBadge = statusBadge;
window.priorityBadge = priorityBadge;
window.escapeHTML = escapeHTML;
window.truncate = truncate;
window.initials = initials;
window.initNavbar = initNavbar;
window.formToObject = formToObject;
window.resetForm = resetForm;
window.showModal = showModal;
window.copyToClipboard = copyToClipboard;

/* Auto-init navbar scroll */
document.addEventListener("DOMContentLoaded", initNavbar);