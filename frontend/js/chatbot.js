/* ============================================
   SWACHHSETU — AI CHATBOT
   ============================================ */

(function () {
  "use strict";

  let isOpen = false;
  let isTyping = false;
  let hasGreeted = false;

  function createChatbotHTML() {
    const div = document.createElement("div");
    div.id = "chatbot-root";
    div.innerHTML = `
      <button class="chatbot-toggle" id="chatbotToggle" aria-label="Open chat">
        <span class="chatbot-toggle-icon">💬</span>
        <span class="chatbot-toggle-badge" id="chatbotBadge">1</span>
      </button>

      <div class="chatbot-window" id="chatbotWindow">
        <div class="chatbot-header">
          <div class="chatbot-header-info">
            <div class="chatbot-avatar">🤖</div>
            <div>
              <div class="chatbot-title">SwachhSetu AI</div>
              <div class="chatbot-status">
                <span class="chatbot-status-dot"></span>
                Online · Instant replies
              </div>
            </div>
          </div>
          <button class="chatbot-close" id="chatbotClose" aria-label="Close chat">✕</button>
        </div>

        <div class="chatbot-messages" id="chatbotMessages"></div>

        <div class="chatbot-suggestions" id="chatbotSuggestions">
          <button class="chatbot-suggestion" data-msg="How do I report a waste issue?">📸 How to report?</button>
          <button class="chatbot-suggestion" data-msg="How to track my complaint?">📍 Track complaint</button>
          <button class="chatbot-suggestion" data-msg="What is SwachhSetu?">🌿 About project</button>
        </div>

        <div class="chatbot-input-area">
          <input
            type="text"
            id="chatbotInput"
            class="chatbot-input"
            placeholder="Type your message..."
            maxlength="500"
            autocomplete="off"
          >
          <button class="chatbot-send" id="chatbotSend" aria-label="Send">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(div);
  }

  function addMessage(text, sender = "bot") {
    const messagesEl = document.getElementById("chatbotMessages");
    const msg = document.createElement("div");
    msg.className = `chatbot-msg chatbot-msg-${sender}`;

    const formatted = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");

    msg.innerHTML = `<div class="chatbot-bubble">${formatted}</div>`;
    messagesEl.appendChild(msg);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showTyping() {
    const messagesEl = document.getElementById("chatbotMessages");
    const typing = document.createElement("div");
    typing.className = "chatbot-msg chatbot-msg-bot";
    typing.id = "chatbotTyping";
    typing.innerHTML = `
      <div class="chatbot-bubble chatbot-typing">
        <span></span><span></span><span></span>
      </div>
    `;
    messagesEl.appendChild(typing);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    isTyping = true;
  }

  function hideTyping() {
    const typing = document.getElementById("chatbotTyping");
    if (typing) typing.remove();
    isTyping = false;
  }

  async function sendMessage(text) {
    text = (text || "").trim();
    if (!text || isTyping) return;

    addMessage(text, "user");
    document.getElementById("chatbotInput").value = "";
    showTyping();

    try {
      const token = localStorage.getItem("token");
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = "Bearer " + token;

      const res = await fetch("/api/chatbot/message", {
        method: "POST",
        headers,
        body: JSON.stringify({ message: text }),
      });

      const data = await res.json();
      hideTyping();

      if (data.reply) {
        setTimeout(() => addMessage(data.reply, "bot"), 250);
      } else {
        addMessage("Sorry, kuch problem aa gayi. Dobara try karein.", "bot");
      }
    } catch (err) {
      hideTyping();
      addMessage("Network issue. Please try again.", "bot");
      console.error("Chatbot error:", err);
    }
  }

  function toggleChat() {
    isOpen = !isOpen;
    const win = document.getElementById("chatbotWindow");
    const btn = document.getElementById("chatbotToggle");
    const badge = document.getElementById("chatbotBadge");

    if (isOpen) {
      win.classList.add("open");
      btn.classList.add("active");
      badge.style.display = "none";

      if (!hasGreeted) {
        hasGreeted = true;
        setTimeout(() => {
          addMessage(
            "Namaste! 🙏 Main SwachhSetu AI Assistant hoon.\n\nKuch bhi puchein — complaint report karna, tracking, ya kuch aur. Hindi ya English dono chalega!",
            "bot"
          );
        }, 400);
      }

      setTimeout(() => document.getElementById("chatbotInput").focus(), 350);
    } else {
      win.classList.remove("open");
      btn.classList.remove("active");
    }
  }

  function init() {
    createChatbotHTML();
    document.getElementById("chatbotToggle").addEventListener("click", toggleChat);
    document.getElementById("chatbotClose").addEventListener("click", toggleChat);
    document.getElementById("chatbotSend").addEventListener("click", () => {
      sendMessage(document.getElementById("chatbotInput").value);
    });
    document.getElementById("chatbotInput").addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(e.target.value);
      }
    });
    document.querySelectorAll(".chatbot-suggestion").forEach((btn) => {
      btn.addEventListener("click", () => {
        sendMessage(btn.dataset.msg);
        document.getElementById("chatbotSuggestions").style.display = "none";
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();