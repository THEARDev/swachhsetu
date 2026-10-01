/* ============================================
   SWACHHSETU — MAIN.JS
   Scroll progress, animations, spotlight,
   confetti, dark mode
   (Custom cursor disabled — native cursor active)
   ============================================ */

/* ============ SCROLL PROGRESS ============ */
function initScrollProgress() {
  const bar = document.querySelector(".scroll-progress");
  if (!bar) return;

  window.addEventListener("scroll", () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = pct + "%";
  }, { passive: true });
}

/* ============ SCROLL ANIMATIONS ============ */
function initScrollAnimations() {
  const els = document.querySelectorAll("[data-animate]");
  if (!els.length) return;

  if (!("IntersectionObserver" in window)) {
    els.forEach((el) => el.classList.add("in-view"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  els.forEach((el) => observer.observe(el));
}

/* ============ NAVBAR SCROLL ============ */
function initNavbar() {
  const nav = document.querySelector(".navbar");
  if (!nav) return;

  const onScroll = () => {
    if (window.scrollY > 20) nav.classList.add("scrolled");
    else nav.classList.remove("scrolled");
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

/* ============ SPOTLIGHT (mouse-follow glow) ============ */
function initSpotlight() {
  const selector = ".spotlight, .fb-card, .feature-card, .stat-card, .qa-card, .card";
  document.querySelectorAll(selector).forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty("--mx", x + "px");
      card.style.setProperty("--my", y + "px");
    });
  });
}

/* ============ CURSOR (NORMAL / NATIVE) ============ */
function initCursorBlob() {
  // Custom cursor blob disabled — using native cursor for better UX
  return;
}

/* ============ CONFETTI ============ */
function fireConfetti(count = 60) {
  const colors = ["#4A7C59", "#C77D8C", "#4A7C8C", "#D9825F", "#FFFFFF"];
  for (let i = 0; i < count; i++) {
    const piece = document.createElement("div");
    piece.className = "confetti-piece";
    piece.style.left = Math.random() * 100 + "vw";
    piece.style.top = "-20px";
    piece.style.background = colors[Math.floor(Math.random() * colors.length)];
    piece.style.width = (Math.random() * 8 + 6) + "px";
    piece.style.height = (Math.random() * 8 + 6) + "px";
    piece.style.borderRadius = Math.random() > 0.5 ? "50%" : "2px";
    piece.style.animationDuration = (Math.random() * 1.5 + 2) + "s";
    piece.style.animationDelay = (Math.random() * 0.3) + "s";
    document.body.appendChild(piece);
    setTimeout(() => piece.remove(), 3500);
  }
}

/* ============ DARK MODE ============ */
function initTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "dark") {
    document.body.classList.add("dark");
  }

  const nav = document.querySelector(".nav-links");
  if (nav && !document.querySelector(".theme-toggle")) {
    const btn = document.createElement("button");
    btn.className = "theme-toggle";
    btn.innerHTML = document.body.classList.contains("dark") ? "☀️" : "🌙";
    btn.title = "Toggle theme";
    btn.onclick = () => {
      document.body.classList.toggle("dark");
      const isDark = document.body.classList.contains("dark");
      localStorage.setItem("theme", isDark ? "dark" : "light");
      btn.innerHTML = isDark ? "☀️" : "🌙";
    };
    nav.appendChild(btn);
  }
}

/* ============ NAVBAR GREETING ============ */
function updateNavbarAuth() {
  const navLinks = document.querySelector(".nav-links");
  if (!navLinks) return;

  const token = localStorage.getItem("token");
  const name = localStorage.getItem("name");
  const role = localStorage.getItem("role");

  const isLanding =
    window.location.pathname === "/" ||
    window.location.pathname.endsWith("index.html");

  if (token && isLanding) {
    const dashLink = role === "admin" ? "admin.html" : "dashboard.html";
    const firstName = name ? name.split(" ")[0] : "User";

    const themeBtn = navLinks.querySelector(".theme-toggle");
    navLinks.innerHTML = `
      <a href="${dashLink}" class="btn btn-primary btn-sm">👋 Hi, ${firstName}</a>
    `;
    if (themeBtn) navLinks.appendChild(themeBtn);
  }
}

/* ============ SMOOTH SCROLL ============ */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (id === "#" || id.length < 2) return;
      const target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
}

/* ============ INIT ============ */
document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initScrollProgress();
  initScrollAnimations();
  initSpotlight();
  initCursorBlob();   // No-op now — native cursor active
  initSmoothScroll();
  initTheme();
  updateNavbarAuth();

  setTimeout(initScrollAnimations, 500);
});

window.fireConfetti = fireConfetti;
window.initScrollAnimations = initScrollAnimations;
window.initSpotlight = initSpotlight;