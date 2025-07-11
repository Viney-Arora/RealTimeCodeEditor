let quill = new Quill('#editor', { theme: 'snow' });

// ✅ Define custom blot to store tooltip message
const Inline = Quill.import('blots/inline');

class SuggestionBlot extends Inline {
  static create(message) {
    let node = super.create();
    node.setAttribute('data-message', message);
    return node;
  }
  static formats(node) {
    return node.getAttribute('data-message');
  }
}

SuggestionBlot.blotName = 'ai-suggestion';
SuggestionBlot.tagName = 'span';
SuggestionBlot.className = 'ai-suggestion';

Quill.register(SuggestionBlot);

let ws = null;
let currentDocId = null;
let token = localStorage.getItem("token");
let applyingRemote = false;

// ✅ Redirect to /login if not logged in
if (!token) window.location = "/login";

// Load docs on page load
fetchDocs();

async function fetchDocs() {
  const res = await fetch("/allDocs", {
    headers: { "Authorization": "Bearer " + token }
  });
  const docs = await res.json();
  document.getElementById("docsList").innerHTML =
    docs.map(d =>
      `<button class='btn btn-outline-primary btn-sm m-1' onclick='openDoc(${d.id})'>${d.title}</button>`
    ).join("");
}

async function createDoc() {
  const title = prompt("Document title:");
  if (!title) return;
  const res = await fetch("/create_doc?title=" + encodeURIComponent(title), {
    method: "POST",
    headers: { "Authorization": "Bearer " + token }
  });
  if (res.ok) {
    fetchDocs();
  } else {
    const err = await res.text();
    alert("Failed to create: " + err);
  }
}

async function openDoc(docId) {
  currentDocId = docId;
  const res = await fetch(`/get_doc/${docId}`, {
    headers: { "Authorization": "Bearer " + token }
  });
  const doc = await res.json();
  applyingRemote = true;
  quill.setContents(quill.clipboard.convert(doc.content));
  applyingRemote = false;

  if (ws) {
    ws.close();
    ws = null;
  }

  let protocol = window.location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${protocol}://${location.host}/ws/${docId}`);

  ws.onopen = () => console.log("✅ WebSocket opened for docId=", docId);
  ws.onclose = () => console.log("❌ WebSocket closed for docId=", docId);
  ws.onerror = (e) => console.error("WebSocket error", e);

  ws.onmessage = e => {
    try {
      const delta = JSON.parse(e.data);
      applyingRemote = true;
      quill.updateContents(delta);
      applyingRemote = false;
    } catch (err) {
      console.error("Failed to apply delta:", err);
    }
  };
}

quill.on('text-change', (delta, oldDelta, source) => {
  if (source === 'user' && ws && ws.readyState === 1) {
    ws.send(JSON.stringify(delta));
  }
});

async function saveVersion() {
  if (!currentDocId) return alert("Open a document first!");
  const content = quill.root.innerHTML;
  const res = await fetch(`/save_version/${currentDocId}`, {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ content })
  });
  if (res.ok) alert("✅ Version saved!");
  else {
    const err = await res.text();
    alert("❌ Failed to save: " + err);
  }
}

async function loadVersions() {
  if (!currentDocId) return alert("Open a document first!");
  const res = await fetch(`/versions/${currentDocId}`, {
    headers: { "Authorization": "Bearer " + token }
  });
  const versions = await res.json();
  alert("Versions:\n" + versions.map(v => v.timestamp).join("\n"));
}

async function getSuggestions() {
  const text = quill.getText();
  try {
    const res = await fetch("/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const suggestions = await res.json();

    document.getElementById("suggestions").innerHTML =
      suggestions.map(s => `<li>${s.message}</li>`).join("");

    quill.formatText(0, quill.getLength(), 'ai-suggestion', false);

    suggestions.forEach(s => {
      const offset = s.offset;
      const length = s.length || 5;
      quill.formatText(offset, length, 'ai-suggestion', s.message);
    });
  } catch (err) {
    console.error("Error fetching suggestion:", err);
  }
}

// ✅ Redirect correctly on logout
function logout() {
  localStorage.removeItem("token");
  window.location = "/login";
}
