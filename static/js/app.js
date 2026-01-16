const box = document.getElementById("messages");
const input = document.getElementById("text");
const typing = document.getElementById("typing");


function showTyping() {
  typing.classList.remove("hidden");
  scrollToBottom();
}

function hideTyping() {
  typing.classList.add("hidden");
}

/* CSRF helper */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
 
window.addEventListener("load", () => {
    fetch("/api/chat/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ message: "" }),
    })
    .then(res => res.json())
    .then(data => {
       hideTyping();
        if (data.reply) {
            addAIMessage(data.reply);
            scrollToBottom();
        }
    });
});
 
/* Add USER message (RIGHT) */
function addUserMessage(text) {
  const div = document.createElement("div");
  div.className = "message user";
  div.textContent = text;
  box.appendChild(div);
  scrollToBottom();
}

/* Add AI message (LEFT, markdown enabled) */
function addAIMessage(text) {
  const div = document.createElement("div");
  div.className = "message ai";
  div.innerHTML = marked.parse(text);
  box.appendChild(div);
   scrollToBottom();
 // box.insertBefore(div, typing);
}

/* Auto scroll */
function scrollToBottom() {
  box.scrollTop = box.scrollHeight;
}

/* Send message */
async function send(msg = null) {
  const input = document.getElementById("text");

  const text = msg || input.value.trim();
  if (!text) return;

  addUserMessage(text);
  input.value = "";
  scrollToBottom();
  showTyping();
  try {
    const res = await fetch("/api/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) {
      throw new Error("Server error");
    }

    const data = await res.json();
    hideTyping();  
    addAIMessage(data.reply);

  } catch (err) {
    addAIMessage("⚠️ Server error. Please try again.");
  }

  scrollToBottom();
}

  input.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault(); // stop new line
    send();
  }
});

/* Voice input */
function voice() {
  const rec = new webkitSpeechRecognition();
  rec.lang = "en-IN";
  rec.onresult = e => send(e.results[0][0].transcript);
  rec.start();
}
