const state = {
  mode: "pending",
  termsVersion: "",
  conversationId: crypto.randomUUID(),
  messages: [],
};

const consentModal = document.querySelector("#consent");
const messagesEl = document.querySelector("#messages");
const promptEl = document.querySelector("#prompt");
const sendButton = document.querySelector("#send");
const modeBadge = document.querySelector("#mode-badge");

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

async function bootstrap() {
  const response = await api("/api/bootstrap");
  const data = await response.json();
  state.mode = data.mode;
  state.termsVersion = data.terms_version;
  document.querySelector("#app-name").textContent = data.public_name;
  document.querySelector("#model-badge").textContent = data.model;
  updateMode();
  if (state.mode === "pending") consentModal.classList.remove("hidden");
}

async function chooseMode(mode) {
  await api("/api/consent", {
    method: "POST",
    body: JSON.stringify({ mode, accepted: true, terms_version: state.termsVersion }),
  });
  state.mode = mode;
  consentModal.classList.add("hidden");
  updateMode();
  promptEl.focus();
}

function updateMode() {
  modeBadge.textContent =
    state.mode === "research" ? "Research mode" : state.mode === "private" ? "Private mode" : "선택 필요";
  modeBadge.dataset.mode = state.mode;
  document.querySelector("#withdraw").disabled = state.mode !== "research";
}

function appendMessage(role, content) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;
  article.appendChild(bubble);
  messagesEl.appendChild(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendMessage(event) {
  event.preventDefault();
  const content = promptEl.value.trim();
  if (!content || state.mode === "pending") return;

  state.messages.push({ role: "user", content });
  appendMessage("user", content);
  promptEl.value = "";
  sendButton.disabled = true;
  sendButton.textContent = "생성 중";

  try {
    const response = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        conversation_id: state.conversationId,
        messages: state.messages.slice(-24),
      }),
    });
    const data = await response.json();
    state.messages.push(data.message);
    appendMessage("assistant", data.message.content);
  } catch (error) {
    appendMessage("assistant", `요청을 처리하지 못했습니다: ${error.message}`);
  } finally {
    sendButton.disabled = false;
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
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    alert(`내보내기에 실패했습니다: ${error.message}`);
  }
}

async function withdraw() {
  if (!confirm("저장된 대화와 연구 레코드를 삭제하고 Private mode로 전환할까요?")) return;
  await api("/api/consent/withdraw", { method: "POST", body: "{}" });
  state.mode = "private";
  state.messages = [];
  state.conversationId = crypto.randomUUID();
  updateMode();
  alert("연구 동의가 철회됐고 이 세션의 저장 데이터가 삭제되었습니다.");
}

async function deleteData() {
  if (!confirm("이 브라우저 세션에 연결된 모든 저장 데이터를 완전히 삭제할까요?")) return;
  await api("/api/data", { method: "DELETE" });
  location.reload();
}

document.querySelector("#research-start").addEventListener("click", () => chooseMode("research"));
document.querySelector("#private-start").addEventListener("click", () => chooseMode("private"));
document.querySelector("#chat-form").addEventListener("submit", sendMessage);
document.querySelector("#export-data").addEventListener("click", exportData);
document.querySelector("#withdraw").addEventListener("click", withdraw);
document.querySelector("#delete-data").addEventListener("click", deleteData);

bootstrap().catch((error) => {
  appendMessage("assistant", `서비스 초기화에 실패했습니다: ${error.message}`);
});
