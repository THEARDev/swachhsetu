/* ============================================
   SWACHHSETU — MAIN.JS
   Scroll progress, animations, spotlight,
   custom cursor, confetti, dark mode
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

/* ============ SPOTLIGHT ============ */
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

/* ============ CUSTOM CURSOR BLOB ============ */
function initCursorBlob() {
  if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
  if (window.innerWidth < 900) return;

  const blob = document.createElement("div");
  blob.className = "cursor-blob";
  document.body.appendChild(blob);
  document.body.classList.add("cursor-enabled");

  let mouseX = 0, mouseY = 0;
  let blobX = 0, blobY = 0;

  document.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function animate() {
    blobX += (mouseX - blobX) * 0.18;
    blobY += (mouseY - blobY) * 0.18;
    blob.style.transform = `translate(${blobX}px, ${blobY}px) translate(-50%, -50%)`;
    requestAnimationFrame(animate);
  }
  animate();

  document.querySelectorAll("a, button, .btn, input, select, textarea").forEach((el) => {
    el.addEventListener("mouseenter", () => {
      blob.style.width = "44px";
      blob.style.height = "44px";
    });
    el.addEventListener("mouseleave", () => {
      blob.style.width = "24px";
      blob.style.height = "24px";
    });
  });
}

/* ============ CONFETTI ============ */
function fireConfetti(count = 60) {
  const colors = ["#B4FF3D", "#FF2E93", "#00D4B8", "#FF7A00", "#FFFFFF"];
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
  initCursorBlob();
  initSmoothScroll();
  initTheme();
  updateNavbarAuth();

  setTimeout(initScrollAnimations, 500);
});

window.fireConfetti = fireConfetti;
window.initScrollAnimations = initScrollAnimations;
window.initSpotlight = initSpotlight;