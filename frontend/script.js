const messagesEl = document.getElementById("messages");
const questionEl = document.getElementById("question");
const sendBtn = document.getElementById("send");

async function sendMessage() {
  const question = questionEl.value.trim();
  if (!question) return;

  appendMessage("You", question);
  questionEl.value = "";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    appendMessage("Bot", data.answer);
  } catch (err) {
    appendMessage("Bot", "Error reaching the server: " + err.message);
  }
}

function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.innerHTML = `<strong>${sender}:</strong> ${text}`;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

sendBtn.addEventListener("click", sendMessage);
questionEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});