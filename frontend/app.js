const state = {
  token: localStorage.getItem("el_token") || "",
  name: localStorage.getItem("el_name") || "",
  projectId: localStorage.getItem("el_project") || "",
  source: null,
};

const $ = (id) => document.getElementById(id);

function headers() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${state.token}`,
  };
}

function setSession() {
  $("session").textContent = state.token ? `Signed in as ${state.name}` : "Not signed in";
  $("story-form").hidden = !state.token;
}

async function api(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

function render(project) {
  state.projectId = project.id;
  localStorage.setItem("el_project", project.id);
  $("project-title").textContent = project.title;
  $("status-pill").textContent = project.status.replaceAll("_", " ");
  $("gates").innerHTML = Object.entries(project.gates)
    .map(([k, v]) => `<span class="gate ${v ? "on" : ""}">${k.replaceAll("_", " ")}</span>`)
    .join("");
  $("flags").innerHTML = (project.risk_flags || [])
    .map((f) => `<span>${f.code}: ${f.detail}</span>`)
    .join("");
  $("timeline").innerHTML = project.events
    .slice()
    .reverse()
    .map((e) => `<li><div class="actor">${e.actor} · ${e.type}</div><div>${e.summary}</div></li>`)
    .join("");
  if (!project.artifacts.length) {
    $("artifact-list").innerHTML = `<p class="muted">Scripts, stems, clearances, and masters will land here.</p>`;
  } else {
    $("artifact-list").innerHTML = project.artifacts
      .slice()
      .reverse()
      .map((a) => `<article class="artifact"><strong>${a.title}</strong><div class="muted">${a.kind}</div><pre>${escapeHtml(a.content)}</pre></article>`)
      .join("");
  }
  $("approve").disabled = !project.artifacts.some((a) => a.kind === "script") || project.gates.script_approval;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

function listen(projectId) {
  if (state.source) state.source.close();
  state.source = new EventSource(`/api/projects/${projectId}/events?token=${encodeURIComponent(state.token)}`);
  state.source.addEventListener("agent", async () => {
    await poll(projectId);
  });
}

async function poll(projectId) {
  try {
    const project = await api(`/api/projects/${projectId}`, { headers: headers() });
    render(project);
  } catch (err) {
    console.warn(err);
  }
}

$("auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = $("name").value.trim();
  const data = await api("/api/auth/demo", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  state.token = data.access_token;
  state.name = name;
  localStorage.setItem("el_token", state.token);
  localStorage.setItem("el_name", name);
  setSession();
});

$("story-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const project = await api("/api/projects", {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      title: $("title").value,
      story: $("story").value,
      style_preferences: $("style").value,
      package_type: $("package").value,
    }),
  });
  render(project);
  listen(project.id);
});

$("approve").addEventListener("click", async () => {
  const project = await api(`/api/projects/${state.projectId}/approve-script`, {
    method: "POST",
    headers: headers(),
  });
  render(project);
});

$("refresh").addEventListener("click", () => {
  if (state.projectId) poll(state.projectId);
});

setSession();
if (state.token && state.projectId) poll(state.projectId);
