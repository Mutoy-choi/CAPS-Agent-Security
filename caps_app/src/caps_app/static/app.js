const state = {
  mode: "pending",
  termsVersion: "",
  conversationId: crypto.randomUUID(),
  messages: [],
};

const consentModal = document.querySelector("#consent");
const shell = document.querySelector(".shell");
const messagesEl = document.querySelector("#messages");
const promptEl = document.querySelector("#prompt");
const sendButton = document.querySelector("#send");
const modeBadge = document.querySelector("#mode-badge");
const announcer = document.querySelector("#announcer");

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch (_) {
      // Keep the HTTP status message.
    }
    throw new Error(detail);
  }
  return response;
}

function announce(message) {
  announcer.textContent = "";
  window.setTimeout(() => {
    announcer.textContent = message;
  }, 10);
}

function setConsentOpen(open) {
  consentModal.classList.toggle("hidden", !open);
  shell.inert = open;
  consentModal.setAttribute("aria-hidden", String(!open));
  if (open) {
    window.setTimeout(() => document.querySelector("#research-start").focus(), 0);
  }
}

async function bootstrap() {
  const response = await api("/api/bootstrap");
  const data = await response.json();
  state.mode = data.mode;
  state.termsVersion = data.terms_version;
  document.querySelector("#app-name").textContent = data.public_name;
  document.title = `${data.public_name} · ${data.model}`;
  document.querySelector("#model-badge").textContent = data.model;
  updateMode();
  setConsentOpen(state.mode === "pending");
}

async function chooseMode(mode) {
  await api("/api/consent", {
    method: "POST",
    body: JSON.stringify({ mode, accepted: true, terms_version: state.termsVersion }),
  });
  state.mode = mode;
  setConsentOpen(false);
  updateMode();
  announce(mode === "research" ? "Research mode가 활성화됐습니다." : "Private mode가 활성화됐습니다.");
  promptEl.focus();
}

function updateMode() {
  modeBadge.textContent =
    state.mode === "research" ? "Research mode" : state.mode === "private" ? "Private mode" : "선택 필요";
  modeBadge.dataset.mode = state.mode;
  document.querySelector("#withdraw").disabled = state.mode !== "research";
}

function appendMessage(role, content, options = {}) {
  const article = document.createElement("article");
  article.className = `message ${role}${options.error ? " error" : ""}${options.loading ? " loading" : ""}`;
  article.setAttribute("aria-label", role === "user" ? "사용자 메시지" : "어시스턴트 메시지");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;
  article.appendChild(bubble);
  messagesEl.appendChild(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return article;
}

async function sendMessage(event) {
  event.preventDefault();
  const content = promptEl.value.trim();
  if (!content || state.mode === "pending") return;

  state.messages.push({ role: "user", content });
  appendMessage("user", content);
  promptEl.value = "";
  sendButton.disabled = true;
  sendButton.setAttribute("aria-busy", "true");
  sendButton.textContent = "생성 중";
  const loading = appendMessage("assistant", "답변을 생성하고 있습니다", { loading: true });

  try {
    const response = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        conversation_id: state.conversationId,
        messages: state.messages.slice(-24),
      }),
    });
    const data = await response.json();
    loading.remove();
    state.messages.push(data.message);
    appendMessage("assistant", data.message.content);
    announce("모델 답변이 도착했습니다.");
  } catch (error) {
    loading.remove();
    appendMessage("assistant", `요청을 처리하지 못했습니다: ${error.message}`, { error: true });
    announce("요청 처리에 실패했습니다.");
  } finally {
    sendButton.disabled = false;
    sendButton.removeAttribute("aria-busy");
    sendButton.textContent = "보내기";
    promptEl.focus();
  }
}

async function exportData() {
  try {
    const response = await api("/api/data/export");
    const data = await response.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "caps-my-data.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    announce("내 데이터 파일을 만들었습니다.");
  } catch (error) {
    announce(`내보내기에 실패했습니다: ${error.message}`);
  }
}

async function withdraw() {
  if (!window.confirm("저장된 대화와 연구 레코드를 삭제하고 Private mode로 전환할까요?")) return;
  await api("/api/consent/withdraw", { method: "POST", body: "{}" });
  state.mode = "private";
  state.messages = [];
  state.conversationId = crypto.randomUUID();
  messagesEl.replaceChildren();
  appendMessage("assistant", "Private mode로 전환했습니다. 무엇을 같이 살펴볼까요?");
  updateMode();
  announce("연구 동의가 철회됐고 저장 데이터가 삭제되었습니다.");
  promptEl.focus();
}

async function deleteData() {
  if (!window.confirm("이 브라우저 세션에 연결된 모든 저장 데이터를 삭제할까요?")) return;
  await api("/api/data", { method: "DELETE" });
  window.location.reload();
}

function trapConsentFocus(event) {
  if (event.key !== "Tab" || consentModal.classList.contains("hidden")) return;
  const controls = [...consentModal.querySelectorAll("button, a[href]")];
  if (!controls.length) return;
  const first = controls[0];
  const last = controls[controls.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

document.querySelector("#research-start").addEventListener("click", () => chooseMode("research"));
document.querySelector("#private-start").addEventListener("click", () => chooseMode("private"));
document.querySelector("#chat-form").addEventListener("submit", sendMessage);
document.querySelector("#export-data").addEventListener("click", exportData);
document.querySelector("#withdraw").addEventListener("click", withdraw);
document.querySelector("#delete-data").addEventListener("click", deleteData);
consentModal.addEventListener("keydown", trapConsentFocus);
promptEl.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    document.querySelector("#chat-form").requestSubmit();
  }
});

bootstrap().catch((error) => {
  setConsentOpen(false);
  appendMessage("assistant", `서비스 초기화에 실패했습니다: ${error.message}`, { error: true });
  announce("서비스 초기화에 실패했습니다.");
});
