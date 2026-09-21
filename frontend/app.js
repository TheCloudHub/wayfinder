const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send-btn");
const welcome = document.getElementById("welcome");
const clearBtn = document.getElementById("clear-btn");

function autoGrow() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 180) + "px";
}
input.addEventListener("input", autoGrow);

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    input.value = chip.textContent;
    autoGrow();
    input.focus();
    form.requestSubmit();
  });
});

clearBtn.addEventListener("click", () => {
  messagesEl.innerHTML = "";
  messagesEl.appendChild(welcome);
  welcome.style.display = "block";
});

// Minimal, safe markdown-ish rendering (escaped first, then limited formatting).
function renderText(text) {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return escaped
    .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/^\s*[-*]\s+(.*)$/gm, "<li>$1</li>")
    .replace(/(<li>[\s\S]*?<\/li>)/g, "<ul>$1</ul>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\n{2,}/g, "<br/><br/>")
    .replace(/\n/g, "<br/>");
}

function addMessage(role, text, sources) {
  welcome.style.display = "none";
  const msg = document.createElement("div");
  msg.className = `msg ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "◐";

  const body = document.createElement("div");
  body.className = "body";
  if (role === "assistant") {
    body.innerHTML = renderText(text);
    if (sources && sources.length) {
      const s = document.createElement("div");
      s.className = "sources";
      s.innerHTML =
        '<div class="sources-title">Sources</div>' +
        sources
          .map((src) => `<span class="source-pill">${src.source}</span>`)
          .join("");
      body.appendChild(s);
    }
  } else {
    body.textContent = text;
  }

  msg.appendChild(avatar);
  msg.appendChild(body);
  messagesEl.appendChild(msg);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return body;
}

function addTyping() {
  const body = addMessage("assistant", "");
  body.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
  return body.parentElement;
}

async function sendMessage(question) {
  addMessage("user", question);
  const typingEl = addTyping();
  sendBtn.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    typingEl.remove();
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      addMessage("assistant", `⚠️ ${err.detail || "Something went wrong."}`);
      return;
    }
    const data = await res.json();
    addMessage("assistant", data.answer, data.sources);
  } catch (e) {
    typingEl.remove();
    addMessage("assistant", "⚠️ Network error. Is the server running?");
  } finally {
    sendBtn.disabled = false;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (!question) return;
  input.value = "";
  autoGrow();
  sendMessage(question);
});
