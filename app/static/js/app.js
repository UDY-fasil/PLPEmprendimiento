/* ============================================================
   PLPE - Frontend Admin
   ============================================================ */
"use strict";

/* ---------- Estado global ---------- */
const state = {
  accessToken: localStorage.getItem("plpe_access") || null,
  refreshToken: localStorage.getItem("plpe_refresh") || null,
  user: JSON.parse(localStorage.getItem("plpe_user") || "null"),
  view: "dashboard",
  categories: [],
  businesses: [],
  products: [],
  services: [],
  inquiries: [],
  favorites: [],
  publicTab: "businesses",
  publicBusinesses: [],
  publicProducts: [],
  publicServices: [],
  publicCategories: [],
  requests: [],
  publicDetail: null,
};

const API = ""; // mismo origen

/* ---------- Utilidades DOM ---------- */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function esc(v) {
  if (v === null || v === undefined) return "";
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function fmtDate(v) {
  if (!v) return "-";
  const d = new Date(v);
  if (isNaN(d)) return v;
  return d.toLocaleDateString("es-AR", { day: "2-digit", month: "2-digit", year: "numeric" });
}

function fmtMoney(v) {
  if (v === null || v === undefined || v === "") return "-";
  const n = Number(v);
  if (isNaN(n)) return "-";
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n);
}

function badge(text, extra = "") {
  const cls = "badge badge-" + String(text || "").toLowerCase().replace(/\s+/g, "-");
  return `<span class="${cls} ${extra}">${esc(text || "-")}</span>`;
}

function isAdmin() {
  return !!(state.user && Array.isArray(state.user.roles) && state.user.roles.includes("admin"));
}

function toast(msg, type = "") {
  const el = document.createElement("div");
  el.className = "toast " + type;
  el.textContent = msg;
  $("#toast-container").appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transition = "opacity .3s";
    setTimeout(() => el.remove(), 300);
  }, 3500);
}

/* ---------- Validación de formularios ---------- */
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

const FIELD_LABELS = {
  email: "Email",
  password: "Contraseña",
  current_password: "Contraseña actual",
  new_password: "Nueva contraseña",
  full_name: "Nombre completo",
  name: "Nombre",
  message: "Mensaje",
  price: "Precio",
  stock: "Stock",
  currency: "Moneda",
  business_id: "Emprendimiento",
  city: "Ciudad",
  address: "Dirección",
  phone: "Teléfono",
  website: "Sitio web",
  description: "Descripción",
  duration_minutes: "Duración",
  sender_name: "Nombre",
  sender_email: "Email",
  sender_phone: "Teléfono",
};

function labelForField(el) {
  if (el && el.closest) {
    const group = el.closest(".form-group");
    const lab = group && group.querySelector("label");
    if (lab) return lab.textContent.replace(/\*/g, "").trim();
  }
  return FIELD_LABELS[el && el.name] || (el && el.name) || "este campo";
}

function fieldErrorMessage(el) {
  const val = (el.value || "").trim();
  if (el.required && !val) return `Completá "${labelForField(el)}".`;
  if (el.type === "email" && val && !EMAIL_RE.test(val))
    return "Ingresá un email válido (ej: nombre@dominio.com).";
  if (el.minLength > 0 && val && val.length < el.minLength)
    return `"${labelForField(el)}" debe tener al menos ${el.minLength} caracteres.`;
  if (el.type === "number" && val !== "" && el.min !== "" && Number(val) < Number(el.min))
    return `"${labelForField(el)}" no puede ser menor que ${el.min}.`;
  return null;
}

function markInvalid(el) {
  try {
    el.focus();
    el.scrollIntoView({ block: "center", behavior: "smooth" });
  } catch (e) {
    /* ignore */
  }
  el.classList.add("input-invalid");
  setTimeout(() => el.classList.remove("input-invalid"), 2600);
}

function validateContainer(root) {
  if (!root) return null;
  const fields = Array.from(root.querySelectorAll("input, select, textarea"));
  for (const el of fields) {
    if (el.disabled || el.type === "hidden" || el.type === "checkbox" || el.type === "submit") continue;
    const err = fieldErrorMessage(el);
    if (err) {
      markInvalid(el);
      return err;
    }
  }
  return null;
}

function translateFieldMsg(msg) {
  const m = (msg || "").toLowerCase();
  if (m.includes("valid email")) return "Ingresá un email válido (ej: nombre@dominio.com).";
  if (m.includes("at least 8")) return "Debe tener al menos 8 caracteres.";
  if (m.includes("field required") || m.includes("missing")) return "Este campo es obligatorio.";
  if (m.includes("valid integer")) return "Ingresá un número entero.";
  if (m.includes("valid number")) return "Ingresá un número.";
  if (m.includes("maximum length") || m.includes("at most")) return "El texto es demasiado largo.";
  if (m.includes("not a valid")) return "El valor ingresado no es válido.";
  return msg || "Valor inválido.";
}

function translateBackendMessage(msg) {
  const m = (msg || "").toLowerCase();
  const map = {
    "invalid credentials": "Email o contraseña incorrectos.",
    "email already registered": "Ese email ya está registrado. Probá iniciar sesión.",
    "account is not active": "Tu cuenta no está activa. Contactá a la administración.",
    "account temporarily locked": "La cuenta está bloqueada temporalmente por intentos fallidos. Probá más tarde.",
    "totp code required": "Ingresá el código de verificación en dos pasos (2FA).",
    "invalid totp code": "El código de verificación en dos pasos es incorrecto.",
    "user not found or inactive": "El usuario no existe o está inactivo.",
    "category already exists": "Ya existe una categoría con ese nombre.",
    "category not found": "No se encontró la categoría.",
    "business not found": "No se encontró el emprendimiento.",
    "product not found": "No se encontró el producto.",
    "service not found": "No se encontró el servicio.",
    "not authorized": "No tenés permiso para realizar esta acción.",
    "admin required": "Esta acción es solo para administradores.",
    "not authenticated": "Necesitás iniciar sesión.",
    "invalid or expired token": "El enlace es inválido o venció.",
  };
  return map[m] || msg;
}

function formatApiError(data, status) {
  if (data && typeof data.detail === "string") return translateBackendMessage(data.detail);
  if (data && Array.isArray(data.detail)) {
    const parts = data.detail.map((d) => {
      const field = (d.loc || []).filter((x) => !["body", "query", "path"].includes(x)).join(".");
      const label = field ? FIELD_LABELS[field] || field : "";
      const msg = translateFieldMsg(d.msg || d.detail || "");
      return label ? `${label}: ${msg}` : msg;
    });
    return Array.from(new Set(parts)).join("\n");
  }
  if (status === 401) return "Credenciales inválidas. Revisá tu email y contraseña.";
  if (status === 403) return "No tenés permisos para realizar esta acción.";
  if (status === 404) return "No se encontró lo que buscabas.";
  if (status === 429) return "Demasiados intentos. Esperá un momento e intentá de nuevo.";
  if (status >= 500) return "Hubo un error en el servidor. Intentá de nuevo más tarde.";
  return "Error " + status;
}

/* ---------- Cliente API ---------- */
function setApiStatus(ok) {
  const el = $("#api-status");
  if (!el) return;
  el.textContent = ok ? "Conectado" : "Sin conexión";
  el.classList.toggle("error", !ok);
}

async function apiRequest(path, { method = "GET", body = null, auth = true, retry = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && state.accessToken) headers["Authorization"] = "Bearer " + state.accessToken;

  let res;
  try {
    res = await fetch(API + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    setApiStatus(true);
  } catch (e) {
    setApiStatus(false);
    throw new Error("No se pudo conectar con el servidor");
  }

  if (res.status === 401 && auth && retry && state.refreshToken) {
    const refreshed = await tryRefresh();
    if (refreshed) return apiRequest(path, { method, body, auth, retry: false });
    logout();
    throw new Error("Sesión expirada, vuelva a ingresar");
  }

  if (res.status === 204) return null;

  let data = null;
  const text = await res.text();
  if (text) {
    try { data = JSON.parse(text); } catch { data = text; }
  }

  if (!res.ok) {
    throw new Error(formatApiError(data, res.status));
  }
  return data;
}

async function tryRefresh() {
  try {
    const res = await fetch(API + "/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: state.refreshToken }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    state.accessToken = data.access_token;
    state.refreshToken = data.refresh_token;
    localStorage.setItem("plpe_access", state.accessToken);
    localStorage.setItem("plpe_refresh", state.refreshToken);
    return true;
  } catch {
    return false;
  }
}

function persistSession() {
  if (state.accessToken) localStorage.setItem("plpe_access", state.accessToken);
  if (state.refreshToken) localStorage.setItem("plpe_refresh", state.refreshToken);
  if (state.user) localStorage.setItem("plpe_user", JSON.stringify(state.user));
}

function clearSession() {
  state.accessToken = null;
  state.refreshToken = null;
  state.user = null;
  localStorage.removeItem("plpe_access");
  localStorage.removeItem("plpe_refresh");
  localStorage.removeItem("plpe_user");
}

/* ---------- Autenticación ---------- */
async function doLogin(email, password, totp) {
  const payload = { email, password };
  if (totp) payload.totp_code = totp;
  const data = await apiRequest("/auth/login", { method: "POST", body: payload, auth: false });
  state.accessToken = data.access_token;
  state.refreshToken = data.refresh_token;
  await loadCurrentUser();
  persistSession();
  enterApp();
}

async function doRegister(payload) {
  await apiRequest("/auth/register", { method: "POST", body: payload, auth: false });
  toast("Cuenta creada. Iniciando sesión...");
  await doLogin(payload.email, payload.password);
}

async function loadCurrentUser() {
  state.user = await apiRequest("/users/me");
  persistSession();
}

function logout() {
  if (state.refreshToken) {
    apiRequest("/auth/logout", { method: "POST", body: { refresh_token: state.refreshToken }, auth: false }).catch(() => {});
  }
  clearSession();
  enterPublic();
}

function enterApp() {
  $("#auth-screen").style.display = "none";
  $("#public-screen").style.display = "none";
  $("#app-screen").style.display = "flex";
  renderUserInfo();
  applyRoleToUI();
  switchView("dashboard");
}

function applyRoleToUI() {
  const admin = isAdmin();
  const reqNav = document.querySelector('.nav-item[data-view="requests"]');
  if (reqNav) reqNav.style.display = admin ? "" : "none";
  const newCat = $("#btn-new-category");
  if (newCat) newCat.style.display = admin ? "" : "none";
}

function enterAuth() {
  $("#app-screen").style.display = "none";
  $("#public-screen").style.display = "none";
  $("#auth-screen").style.display = "flex";
}

function renderUserInfo() {
  if (!state.user) return;
  const roleLabel = isAdmin() ? "Administrador" : "Productor";
  $("#user-info").innerHTML =
    `<strong>${esc(state.user.full_name || state.user.email)}</strong>` +
    `<span>${esc(state.user.email)}</span><br><span>${roleLabel}</span>`;
}

/* ---------- Datos de referencia ---------- */
async function ensureBusinesses() {
  if (!state.businesses.length) {
    const data = await apiRequest("/businesses?page_size=100");
    state.businesses = data.businesses;
  }
}

async function ensureCategories() {
  if (!state.categories.length) {
    const data = await apiRequest("/categories?page_size=100");
    state.categories = data.categories;
  }
}

/* ---------- Router de vistas ---------- */
const VIEW_TITLES = {  dashboard: "Panel",
  categories: "Categorías",
  businesses: "Emprendimientos",
  products: "Productos",
  services: "Servicios",
  inquiries: "Consultas",
  requests: "Solicitudes",
  favorites: "Favoritos",
  profile: "Mi Perfil",
};

function openSidebar() {
  const sb = $(".sidebar");
  const ov = $("#sidebar-overlay");
  if (sb) sb.classList.add("open");
  if (ov) ov.classList.add("show");
}

function closeSidebar() {
  const sb = $(".sidebar");
  const ov = $("#sidebar-overlay");
  if (sb) sb.classList.remove("open");
  if (ov) ov.classList.remove("show");
}

function switchView(view) {
  state.view = view;
  $$(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
  $$(".view").forEach((v) => v.classList.toggle("active", v.id === "view-" + view));
  $("#view-title").textContent = VIEW_TITLES[view] || view;
  closeSidebar();
  loadView(view);
}

async function loadView(view) {
  try {
    if (view === "dashboard") await loadDashboard();
    else if (view === "categories") await loadCategories();
    else if (view === "businesses") await loadBusinesses();
    else if (view === "products") await loadProducts();
    else if (view === "services") await loadServices();
    else if (view === "inquiries") await loadInquiries();
    else if (view === "requests") await loadRequests();
    else if (view === "favorites") await loadFavorites();
    else if (view === "profile") fillProfile();
  } catch (e) {
    toast(e.message, "error");
  }
}

/* ---------- Dashboard ---------- */
async function loadDashboard() {
  const admin = isAdmin();
  const [cats, biz, prods, servs] = await Promise.all([
    apiRequest("/categories?page_size=100"),
    apiRequest((admin ? "/businesses" : "/businesses/my") + "?page_size=100"),
    apiRequest((admin ? "/products" : "/products/my") + "?page_size=100&active_only=false"),
    apiRequest((admin ? "/services" : "/services/my") + "?page_size=100&active_only=false"),
  ]);
  state.categories = cats.categories;
  state.businesses = biz.businesses;
  state.products = prods.products;
  state.services = servs.services;

  $("#stats-grid").innerHTML = [
    ["Categorías", cats.total],
    ["Emprendimientos", biz.total],
    ["Productos", prods.total],
    ["Servicios", servs.total],
  ]
    .map(
      ([label, value]) =>
        `<div class="stat-card"><div class="stat-label">${label}</div><div class="stat-value">${value}</div></div>`
    )
    .join("");

  const recent = biz.businesses.slice(0, 5);
  $("#dashboard-businesses").innerHTML = recent.length
    ? recent
        .map(
          (b) =>
            `<div class="mini-item"><div><div class="mini-name">${esc(b.name)}</div>` +
            `<div class="mini-sub">${esc(b.city || "Sin ciudad")} · ${fmtDate(b.created_at)}</div></div>` +
            `${badge(b.status)}</div>`
        )
        .join("")
    : `<div class="empty-row">No hay emprendimientos todavía</div>`;
}

/* ---------- Categorías ---------- */
async function loadCategories() {
  const data = await apiRequest("/categories?page_size=100");
  state.categories = data.categories;
  const tbody = $("#categories-table tbody");
  if (!data.categories.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="5">No hay categorías</td></tr>`;
    return;
  }
  tbody.innerHTML = data.categories
    .map(
      (c) => `<tr>
        <td>${c.id}</td>
        <td><strong>${esc(c.name)}</strong></td>
        <td>${esc(c.description || "-")}</td>
        <td>${c.active ? badge("active", "badge-approved") : badge("inactive")}</td>
        <td>${
          isAdmin()
            ? `<div class="actions">
          <button class="btn btn-ghost btn-sm" data-action="edit-category" data-id="${c.id}">Editar</button>
          <button class="btn btn-danger btn-sm" data-action="del-category" data-id="${c.id}">Eliminar</button>
        </div>`
            : "—"
        }</td>
      </tr>`
    )
    .join("");
}

/* ---------- Emprendimientos ---------- */
async function loadBusinesses() {
  const search = $("#business-search").value.trim();
  const status = $("#business-status-filter").value;
  const params = new URLSearchParams({ page_size: "100" });
  if (search) params.set("search", search);
  if (status) params.set("status", status);
  const data = await apiRequest((isAdmin() ? "/businesses" : "/businesses/my") + "?" + params.toString());
  state.businesses = data.businesses;
  const tbody = $("#businesses-table tbody");
  if (!data.businesses.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="6">No hay emprendimientos</td></tr>`;
    return;
  }
  tbody.innerHTML = data.businesses
    .map((b) => {
      const cats = (b.categories || []).map((c) => esc(c.name)).join(", ") || "-";
      const mine = state.user && b.owner_id === state.user.id;
      const adminBtns =
        isAdmin() && b.status !== "approved"
          ? `<button class="btn btn-ghost btn-sm" data-action="approve-business" data-id="${b.id}">Aprobar</button>`
          : "";
      const adminBtns2 =
        isAdmin() && b.status !== "suspended"
          ? `<button class="btn btn-ghost btn-sm" data-action="suspend-business" data-id="${b.id}">Suspender</button>`
          : "";
      return `<tr>
        <td>${b.id}</td>
        <td><strong>${esc(b.name)}</strong><div class="mini-sub">${esc(b.email || "")}</div></td>
        <td>${esc(b.city || "-")}</td>
        <td>${cats}</td>
        <td>${badge(b.status)}</td>
        <td><div class="actions">
          ${mine ? `<button class="btn btn-ghost btn-sm" data-action="edit-business" data-id="${b.id}">Editar</button>` : ""}
          ${mine ? `<button class="btn btn-danger btn-sm" data-action="del-business" data-id="${b.id}">Eliminar</button>` : ""}
          ${adminBtns}${adminBtns2}
        </div></td>
      </tr>`;
    })
    .join("");
}

/* ---------- Productos ---------- */
async function loadProducts() {
  const search = $("#product-search").value.trim();
  const params = new URLSearchParams({ page_size: "100", active_only: "false" });
  if (search) params.set("search", search);
  const [data] = await Promise.all([
    apiRequest((isAdmin() ? "/products" : "/products/my") + "?" + params.toString()),
    ensureBusinesses(),
  ]);
  state.products = data.products;
  const bizName = (id) => {
    const b = state.businesses.find((x) => x.id === id);
    return b ? b.name : "#" + id;
  };
  const tbody = $("#products-table tbody");
  if (!data.products.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="7">No hay productos</td></tr>`;
    return;
  }
  tbody.innerHTML = data.products
    .map(
      (p) => `<tr>
        <td>${p.id}</td>
        <td><strong>${esc(p.name)}</strong></td>
        <td>${esc(bizName(p.business_id))}</td>
        <td>${fmtMoney(p.price, p.currency)}</td>
        <td>${p.stock ?? "-"}</td>
        <td>${p.active ? badge("active", "badge-approved") : badge("inactive")}</td>
        <td><div class="actions">
          <button class="btn btn-ghost btn-sm" data-action="edit-product" data-id="${p.id}">Editar</button>
          <button class="btn btn-danger btn-sm" data-action="del-product" data-id="${p.id}">Eliminar</button>
        </div></td>
      </tr>`
    )
    .join("");
}

/* ---------- Servicios ---------- */
async function loadServices() {
  const search = $("#service-search").value.trim();
  const params = new URLSearchParams({ page_size: "100", active_only: "false" });
  if (search) params.set("search", search);
  const [data] = await Promise.all([
    apiRequest((isAdmin() ? "/services" : "/services/my") + "?" + params.toString()),
    ensureBusinesses(),
  ]);
  state.services = data.services;
  const bizName = (id) => {
    const b = state.businesses.find((x) => x.id === id);
    return b ? b.name : "#" + id;
  };
  const tbody = $("#services-table tbody");
  if (!data.services.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="7">No hay servicios</td></tr>`;
    return;
  }
  tbody.innerHTML = data.services
    .map(
      (s) => `<tr>
        <td>${s.id}</td>
        <td><strong>${esc(s.name)}</strong></td>
        <td>${esc(bizName(s.business_id))}</td>
        <td>${fmtMoney(s.price, s.currency)}</td>
        <td>${s.duration_minutes ? s.duration_minutes + " min" : "-"}</td>
        <td>${s.active ? badge("active", "badge-approved") : badge("inactive")}</td>
        <td><div class="actions">
          <button class="btn btn-ghost btn-sm" data-action="edit-service" data-id="${s.id}">Editar</button>
          <button class="btn btn-danger btn-sm" data-action="del-service" data-id="${s.id}">Eliminar</button>
        </div></td>
      </tr>`
    )
    .join("");
}

/* ---------- Consultas ---------- */
async function loadInquiries() {
  const status = $("#inquiry-status-filter").value;
  const params = new URLSearchParams({ page_size: "100" });
  if (status) params.set("status", status);
  const data = await apiRequest((isAdmin() ? "/inquiries" : "/inquiries/received") + "?" + params.toString());
  state.inquiries = data.inquiries;
  const tbody = $("#inquiries-table tbody");
  if (!data.inquiries.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="7">No hay consultas</td></tr>`;
    return;
  }
  tbody.innerHTML = data.inquiries
    .map(
      (i) => `<tr>
        <td>${i.id}</td>
        <td>#${i.business_id}</td>
        <td><strong>${esc(i.sender_name)}</strong><div class="mini-sub">${esc(i.sender_email)}</div></td>
        <td title="${esc(i.message)}">${esc((i.message || "").slice(0, 60))}${(i.message || "").length > 60 ? "…" : ""}</td>
        <td>${badge(i.status)}</td>
        <td>${fmtDate(i.created_at)}</td>
        <td><div class="actions">
          <button class="btn btn-ghost btn-sm" data-action="view-inquiry" data-id="${i.id}">Ver</button>
        </div></td>
      </tr>`
    )
    .join("");
}

/* ---------- Solicitudes de contacto ---------- */
async function loadRequests() {
  const status = $("#requests-status-filter").value;
  const params = new URLSearchParams({ page_size: "100" });
  if (status) params.set("status", status);
  const data = await apiRequest("/contact-requests?" + params.toString());
  state.requests = data.requests;
  const tbody = $("#requests-table tbody");
  if (!data.requests.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="8">No hay solicitudes</td></tr>`;
    return;
  }
  tbody.innerHTML = data.requests
    .map(
      (r) => `<tr>
        <td>${r.id}</td>
        <td><strong>${esc(r.name)}</strong></td>
        <td><div>${esc(r.email)}</div><div class="mini-sub">${esc(r.phone || "")}</div></td>
        <td>${r.business_id ? "#" + r.business_id : "-"}</td>
        <td title="${esc(r.message || "")}">${esc((r.message || "-").slice(0, 50))}${(r.message || "").length > 50 ? "…" : ""}</td>
        <td>${badge(r.status)}</td>
        <td>${fmtDate(r.created_at)}</td>
        <td><div class="actions"><button class="btn btn-ghost btn-sm" data-action="view-request" data-id="${r.id}">Ver</button></div></td>
      </tr>`
    )
    .join("");
}

function openRequestModal(req) {
  const body = `
    <div class="form-group"><label>Nombre</label><input disabled value="${esc(req.name)}"></div>
    <div class="form-group"><label>Email</label><input disabled value="${esc(req.email)}"></div>
    <div class="form-group"><label>Teléfono</label><input disabled value="${esc(req.phone || "-")}"></div>
    <div class="form-group"><label>Emprendimiento</label><input disabled value="${req.business_id ? "#" + req.business_id : "General"}"></div>
    <div class="form-group"><label>Mensaje</label><textarea disabled>${esc(req.message || "-")}</textarea></div>
    <div class="form-group"><label>Estado</label>
      <select id="req-status">
        ${["new", "contacted", "closed"].map((s) => `<option value="${s}" ${req.status === s ? "selected" : ""}>${s}</option>`).join("")}
      </select>
    </div>
  `;
  openModal("Solicitud #" + req.id, body, async () => {
    await apiRequest(`/contact-requests/${req.id}`, { method: "PATCH", body: { status: $("#req-status").value } });
    toast("Estado actualizado");
    closeModal();
    await loadRequests();
  });
}

/* ---------- Favoritos ---------- */
async function loadFavorites() {
  const data = await apiRequest("/favorites?page_size=100");
  state.favorites = data.favorites;
  const tbody = $("#favorites-table tbody");
  if (!data.favorites.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="5">No hay favoritos</td></tr>`;
    return;
  }
  tbody.innerHTML = data.favorites
    .map((f) => {
      const type = f.business_id ? "Emprendimiento" : "Producto";
      const ref = f.business_id || f.product_id;
      return `<tr>
        <td>${f.id}</td>
        <td>${type}</td>
        <td>#${ref}</td>
        <td>${fmtDate(f.created_at)}</td>
        <td><div class="actions">
          <button class="btn btn-danger btn-sm" data-action="del-favorite" data-id="${f.id}" data-business="${f.business_id || ""}" data-product="${f.product_id || ""}">Quitar</button>
        </div></td>
      </tr>`;
    })
    .join("");
}

/* ---------- Perfil ---------- */
function fillProfile() {
  if (!state.user) return;
  $("#profile-email").value = state.user.email || "";
  $("#profile-name").value = state.user.full_name || "";
  $("#profile-phone").value = state.user.phone || "";
  $("#profile-city").value = state.user.city || "";
}

/* ============================================================
   Modal / Formularios
   ============================================================ */
let modalSaveHandler = null;

function openModal(title, bodyHtml, onSave) {
  $("#modal-title").textContent = title;
  $("#modal-body").innerHTML = bodyHtml;
  modalSaveHandler = onSave;
  $("#modal-save").style.display = "";
  $("#modal-cancel").textContent = "Cancelar";
  $("#modal-cancel").style.display = "";
  $("#modal").style.display = "flex";
}

function openInfoModal(title, bodyHtml) {
  $("#modal-title").textContent = title;
  $("#modal-body").innerHTML = bodyHtml;
  modalSaveHandler = null;
  $("#modal-save").style.display = "none";
  $("#modal-cancel").textContent = "Cerrar";
  $("#modal").style.display = "flex";
}

function closeModal() {
  $("#modal").style.display = "none";
  $("#modal-body").innerHTML = "";
  modalSaveHandler = null;
}

function categoryOptions(selected = []) {
  if (!state.categories.length) return `<p class="mini-sub">No hay categorías creadas.</p>`;
  return state.categories
    .map(
      (c) => `<label class="form-check" style="margin-bottom:6px">
        <input type="checkbox" name="category_ids" value="${c.id}" ${selected.includes(c.id) ? "checked" : ""}>
        ${esc(c.name)}
      </label>`
    )
    .join("");
}

function businessOptions(selected = null) {
  if (!state.businesses.length) return `<option value="">No hay emprendimientos</option>`;
  return state.businesses
    .map((b) => `<option value="${b.id}" ${b.id === selected ? "selected" : ""}>#${b.id} - ${esc(b.name)}</option>`)
    .join("");
}

function formCategory(data = {}) {
  return `
    <div class="form-group"><label>Nombre *</label><input name="name" required value="${esc(data.name || "")}"></div>
    <div class="form-group"><label>Descripción</label><textarea name="description">${esc(data.description || "")}</textarea></div>
    <div class="form-group"><label>Icono</label><input name="icon" placeholder="ej: 🍎" value="${esc(data.icon || "")}"></div>
    <div class="form-group form-check"><input type="checkbox" name="active" id="f-active" ${data.active !== false ? "checked" : ""}><label for="f-active">Activa</label></div>
  `;
}

function formBusiness(data = {}) {
  const selCats = (data.categories || []).map((c) => c.id);
  return `
    <div class="form-group"><label>Nombre *</label><input name="name" required minlength="3" value="${esc(data.name || "")}"></div>
    <div class="form-group"><label>Descripción</label><textarea name="description">${esc(data.description || "")}</textarea></div>
    <div class="form-cols">
      <div class="form-group"><label>Ciudad</label><input name="city" value="${esc(data.city || "")}"></div>
      <div class="form-group"><label>Dirección</label><input name="address" value="${esc(data.address || "")}"></div>
    </div>
    <div class="form-cols">
      <div class="form-group"><label>Teléfono</label><input name="phone" value="${esc(data.phone || "")}"></div>
      <div class="form-group"><label>Email</label><input type="email" name="email" value="${esc(data.email || "")}"></div>
    </div>
    <div class="form-group"><label>Sitio web</label><input name="website" value="${esc(data.website || "")}"></div>
    <div class="form-group"><label>Categorías</label>${categoryOptions(selCats)}</div>
  `;
}

function formProduct(data = {}) {
  return `
    <div class="form-group"><label>Emprendimiento *</label><select name="business_id" required>${businessOptions(data.business_id)}</select></div>
    <div class="form-group"><label>Nombre *</label><input name="name" required value="${esc(data.name || "")}"></div>
    <div class="form-group"><label>Descripción</label><textarea name="description">${esc(data.description || "")}</textarea></div>
    <div class="form-cols">
      <div class="form-group"><label>Precio (ARS $)</label><input type="number" step="0.01" min="0" name="price" value="${data.price ?? ""}"></div>
      <div class="form-group"><label>Moneda</label><input name="currency" value="ARS" readonly></div>
    </div>
    <div class="form-group"><label>Stock</label><input type="number" min="0" name="stock" value="${data.stock ?? ""}"></div>
    <div class="form-group"><label>URL de imagen</label><input name="image_url" value="${esc(data.image_url || "")}"></div>
    <div class="form-group form-check"><input type="checkbox" name="active" id="p-active" ${data.active !== false ? "checked" : ""}><label for="p-active">Activo</label></div>
  `;
}

function formService(data = {}) {
  return `
    <div class="form-group"><label>Emprendimiento *</label><select name="business_id" required>${businessOptions(data.business_id)}</select></div>
    <div class="form-group"><label>Nombre *</label><input name="name" required value="${esc(data.name || "")}"></div>
    <div class="form-group"><label>Descripción</label><textarea name="description">${esc(data.description || "")}</textarea></div>
    <div class="form-cols">
      <div class="form-group"><label>Precio (ARS $)</label><input type="number" step="0.01" min="0" name="price" value="${data.price ?? ""}"></div>
      <div class="form-group"><label>Moneda</label><input name="currency" value="ARS" readonly></div>
    </div>
    <div class="form-group"><label>Duración (minutos)</label><input type="number" min="0" name="duration_minutes" value="${data.duration_minutes ?? ""}"></div>
    <div class="form-group"><label>URL de imagen</label><input name="image_url" value="${esc(data.image_url || "")}"></div>
    <div class="form-group form-check"><input type="checkbox" name="active" id="s-active" ${data.active !== false ? "checked" : ""}><label for="s-active">Activo</label></div>
  `;
}

function readForm() {
  const form = $("#modal-body");
  const obj = {};
  $$("input[name], select[name], textarea[name]", form).forEach((el) => {
    if (el.type === "checkbox") {
      if (el.name === "category_ids") {
        if (!obj.category_ids) obj.category_ids = [];
        if (el.checked) obj.category_ids.push(Number(el.value));
      } else {
        obj[el.name] = el.checked;
      }
    } else if (el.type === "number") {
      obj[el.name] = el.value === "" ? null : Number(el.value);
    } else {
      obj[el.name] = el.value === "" ? null : el.value;
    }
  });
  return obj;
}

/* ============================================================
   Acciones CRUD
   ============================================================ */
function openCategoryModal(cat = null) {
  openModal(cat ? "Editar categoría" : "Nueva categoría", formCategory(cat || {}), async () => {
    const data = readForm();
    if (cat) await apiRequest(`/categories/${cat.id}`, { method: "PATCH", body: data });
    else await apiRequest("/categories", { method: "POST", body: data });
    toast(cat ? "Categoría actualizada" : "Categoría creada");
    closeModal();
    await loadCategories();
  });
}

function openBusinessModal(biz = null) {
  if (!state.categories.length) {
    toast("Primero creá al menos una categoría", "warning");
    return;
  }
  openModal(biz ? "Editar emprendimiento" : "Nuevo emprendimiento", formBusiness(biz || {}), async () => {
    const data = readForm();
    if (biz) {
      await apiRequest(`/businesses/${biz.id}`, { method: "PATCH", body: data });
      toast("Emprendimiento actualizado");
    } else {
      await apiRequest("/businesses", { method: "POST", body: data });
      toast("Emprendimiento creado");
    }
    closeModal();
    await loadBusinesses();
  });
}

function openProductModal(prod = null) {
  if (!state.businesses.length) {
    toast("Primero creá un emprendimiento", "warning");
    return;
  }
  openModal(prod ? "Editar producto" : "Nuevo producto", formProduct(prod || {}), async () => {
    const data = readForm();
    if (prod) {
      const { business_id, ...upd } = data;
      await apiRequest(`/products/${prod.id}`, { method: "PATCH", body: upd });
      toast("Producto actualizado");
    } else {
      await apiRequest("/products", { method: "POST", body: data });
      toast("Producto creado");
    }
    closeModal();
    await loadProducts();
  });
}

function openServiceModal(serv = null) {
  if (!state.businesses.length) {
    toast("Primero creá un emprendimiento", "warning");
    return;
  }
  openModal(serv ? "Editar servicio" : "Nuevo servicio", formService(serv || {}), async () => {
    const data = readForm();
    if (serv) {
      const { business_id, ...upd } = data;
      await apiRequest(`/services/${serv.id}`, { method: "PATCH", body: upd });
      toast("Servicio actualizado");
    } else {
      await apiRequest("/services", { method: "POST", body: data });
      toast("Servicio creado");
    }
    closeModal();
    await loadServices();
  });
}

async function updateInquiryStatus(id, status) {
  await apiRequest(`/inquiries/${id}/status`, { method: "PATCH", body: { status } });
  toast("Estado actualizado");
  closeModal();
  await loadInquiries();
}

function openInquiryModal(inq) {
  const body = `
    <div class="form-group"><label>Remitente</label><input disabled value="${esc(inq.sender_name)} <${esc(inq.sender_email)}>"></div>
    <div class="form-group"><label>Teléfono</label><input disabled value="${esc(inq.sender_phone || "-")}"></div>
    <div class="form-group"><label>Mensaje</label><textarea disabled>${esc(inq.message)}</textarea></div>
    <div class="form-group"><label>Estado</label>
      <select id="inq-status">
        ${["pending", "read", "responded", "closed"]
          .map((s) => `<option value="${s}" ${inq.status === s ? "selected" : ""}>${s}</option>`)
          .join("")}
      </select>
    </div>
  `;
  openModal("Consulta #" + inq.id, body, async () => {
    await updateInquiryStatus(inq.id, $("#inq-status").value);
  });
}

async function removeFavorite(fav) {
  const params = new URLSearchParams();
  if (fav.business_id) params.set("business_id", fav.business_id);
  if (fav.product_id) params.set("product_id", fav.product_id);
  await apiRequest("/favorites?" + params.toString(), { method: "DELETE" });
  toast("Favorito eliminado");
  await loadFavorites();
}

/* ============================================================
   Sitio público (acceso anónimo)
   ============================================================ */
function enterPublic() {
  $("#app-screen").style.display = "none";
  $("#auth-screen").style.display = "none";
  $("#public-screen").style.display = "flex";
  $("#public-detail").style.display = "none";
  $("#public-home").style.display = "";
  state.publicBusinesses = [];
  state.publicDetail = null;
  $("#public-login-label").textContent = state.user ? "Panel" : "Acceso";
  $("#detail-login-label").textContent = state.user ? "Panel" : "Acceso";
  loadPublicCategories().catch(() => {});
  loadPublicCatalog();
}

async function loadPublicCategories() {
  const data = await apiRequest("/categories?page_size=100");
  state.publicCategories = data.categories;
  const sel = $("#public-category-filter");
  const current = sel.value;
  sel.innerHTML =
    `<option value="">Todas las categorías</option>` +
    data.categories.map((c) => `<option value="${c.id}">${esc(c.name)}</option>`).join("");
  sel.value = current;
}

async function ensurePublicBusinesses() {
  if (!state.publicBusinesses.length) {
    const data = await apiRequest("/businesses?page_size=100");
    state.publicBusinesses = data.businesses.filter((b) => b.status !== "suspended");
  }
}

async function loadPublicCatalog() {
  const grid = $("#public-grid");
  grid.innerHTML = `<div class="loading-block">Cargando...</div>`;
  const search = $("#public-search-input").value.trim();
  const catId = $("#public-category-filter").value;
  try {
    await ensurePublicBusinesses();
    if (state.publicTab === "businesses") {
      const params = new URLSearchParams({ page_size: "100" });
      if (search) params.set("search", search);
      if (catId) params.set("category_id", catId);
      const data = await apiRequest("/businesses?" + params.toString());
      const visible = data.businesses.filter((b) => b.status !== "suspended");
      renderPublicBusinesses(visible);
    } else if (state.publicTab === "products") {
      const params = new URLSearchParams({ page_size: "100" });
      if (search) params.set("search", search);
      const data = await apiRequest("/products?" + params.toString());
      const visibleIds = new Set(state.publicBusinesses.map((b) => b.id));
      renderPublicProducts(data.products.filter((p) => visibleIds.has(p.business_id)));
    } else {
      const params = new URLSearchParams({ page_size: "100" });
      if (search) params.set("search", search);
      const data = await apiRequest("/services?" + params.toString());
      const visibleIds = new Set(state.publicBusinesses.map((b) => b.id));
      renderPublicServices(data.services.filter((s) => visibleIds.has(s.business_id)));
    }
  } catch (e) {
    grid.innerHTML = `<div class="loading-block">Error al cargar: ${esc(e.message)}</div>`;
  }
}

function publicEmpty(msg) {
  return `<div class="loading-block">${esc(msg)}</div>`;
}

function renderPublicBusinesses(list) {
  const grid = $("#public-grid");
  if (!list.length) {
    grid.innerHTML = publicEmpty("No hay emprendimientos para mostrar todavía.");
    return;
  }
  grid.innerHTML = list
    .map((b) => {
      const cats = (b.categories || [])
        .map((c) => `<span class="pub-tag">${esc(c.name)}</span>`)
        .join("");
      return `<article class="pub-card">
        <div class="pub-card-media">${b.logo_url ? `<img src="${esc(b.logo_url)}" alt="">` : "🏪"}</div>
        <div class="pub-card-body">
          <div class="pub-card-title">${esc(b.name)}</div>
          <div class="pub-card-sub">📍 ${esc(b.city || "Sin ubicación")}</div>
          ${cats ? `<div class="pub-tags">${cats}</div>` : ""}
          <div class="pub-card-desc">${esc((b.description || "Sin descripción").slice(0, 130))}</div>
          <div class="pub-card-footer">
            <button class="btn btn-primary btn-sm" data-action="public-view-business" data-id="${b.id}">Ver detalle</button>
          </div>
        </div>
      </article>`;
    })
    .join("");
}

function renderPublicProducts(list) {
  const grid = $("#public-grid");
  if (!list.length) {
    grid.innerHTML = publicEmpty("No hay productos disponibles todavía.");
    return;
  }
  const bizName = (id) => {
    const b = state.publicBusinesses.find((x) => x.id === id);
    return b ? b.name : "Emprendimiento";
  };
  grid.innerHTML = list
    .map(
      (p) => `<article class="pub-card">
        <div class="pub-card-media">${p.image_url ? `<img src="${esc(p.image_url)}" alt="">` : "📦"}</div>
        <div class="pub-card-body">
          <div class="pub-card-title">${esc(p.name)}</div>
          <div class="pub-card-sub">${esc(bizName(p.business_id))}</div>
          <div class="pub-card-desc">${esc((p.description || "Sin descripción").slice(0, 120))}</div>
          <div class="pub-card-price">${fmtMoney(p.price, p.currency)}</div>
          <div class="pub-card-footer">
            <button class="btn btn-ghost btn-sm" data-action="public-view-business" data-id="${p.business_id}">Ver emprendimiento</button>
          </div>
        </div>
      </article>`
    )
    .join("");
}

function renderPublicServices(list) {
  const grid = $("#public-grid");
  if (!list.length) {
    grid.innerHTML = publicEmpty("No hay servicios disponibles todavía.");
    return;
  }
  const bizName = (id) => {
    const b = state.publicBusinesses.find((x) => x.id === id);
    return b ? b.name : "Emprendimiento";
  };
  grid.innerHTML = list
    .map(
      (s) => `<article class="pub-card">
        <div class="pub-card-media">${s.image_url ? `<img src="${esc(s.image_url)}" alt="">` : "✦"}</div>
        <div class="pub-card-body">
          <div class="pub-card-title">${esc(s.name)}</div>
          <div class="pub-card-sub">${esc(bizName(s.business_id))}${s.duration_minutes ? " · " + s.duration_minutes + " min" : ""}</div>
          <div class="pub-card-desc">${esc((s.description || "Sin descripción").slice(0, 120))}</div>
          <div class="pub-card-price">${fmtMoney(s.price, s.currency)}</div>
          <div class="pub-card-footer">
            <button class="btn btn-ghost btn-sm" data-action="public-view-business" data-id="${s.business_id}">Ver emprendimiento</button>
          </div>
        </div>
      </article>`
    )
    .join("");
}

function closePublicDetail() {
  $("#public-detail").style.display = "none";
  $("#public-home").style.display = "";
  state.publicDetail = null;
  window.scrollTo({ top: 0 });
}

function _mapsQuery(b) {
  if (b.latitude != null && b.longitude != null) return `${b.latitude},${b.longitude}`;
  return [b.address, b.city].filter(Boolean).join(", ");
}

function renderBusinessInfo(b) {
  const rows = [];
  if (b.address) rows.push(`<div class="info-row"><span class="info-label">Dirección</span><span>${esc(b.address)}</span></div>`);
  if (b.city) rows.push(`<div class="info-row"><span class="info-label">Ciudad</span><span>${esc(b.city)}</span></div>`);
  if (b.phone) rows.push(`<div class="info-row"><span class="info-label">Teléfono</span><span>${esc(b.phone)}</span></div>`);
  if (b.email) rows.push(`<div class="info-row"><span class="info-label">Email</span><span>${esc(b.email)}</span></div>`);
  if (b.website)
    rows.push(
      `<div class="info-row"><span class="info-label">Sitio</span><span><a href="${esc(b.website)}" target="_blank" rel="noopener">${esc(b.website)}</a></span></div>`
    );

  const q = _mapsQuery(b);
  const link = q
    ? `<a class="btn btn-ghost btn-block" style="margin-top:12px" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(q)}" target="_blank" rel="noopener">Cómo llegar</a>`
    : "";

  if (!rows.length && !link) return `<p class="mini-sub">Sin datos de ubicación.</p>`;
  return `${rows.join("")}${link}`;
}

function renderBusinessMap(b) {
  const hasCoords = b.latitude != null && b.longitude != null;
  if (hasCoords) {
    const d = 0.008;
    const bbox = `${b.longitude - d},${b.latitude - d},${b.longitude + d},${b.latitude + d}`;
    return `<iframe class="detail-map" loading="lazy" title="Mapa de ${esc(b.name)}" src="https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${b.latitude},${b.longitude}"></iframe>`;
  }
  const q = [b.address, b.city].filter(Boolean).join(", ");
  if (!q) return "";
  return `<iframe class="detail-map" loading="lazy" title="Mapa de ${esc(b.name)}" src="https://www.google.com/maps?q=${encodeURIComponent(q)}&z=15&output=embed"></iframe>`;
}

async function openPublicBusinessDetail(id) {
  let business = state.publicBusinesses.find((b) => b.id === id);
  try {
    if (!business) {
      business = await apiRequest(`/businesses/${id}`);
      state.publicBusinesses.push(business);
    }
    state.publicDetail = business;

    const [prods, servs] = await Promise.all([
      apiRequest(`/products?business_id=${id}&page_size=100`),
      apiRequest(`/services?business_id=${id}&page_size=100`),
    ]);

    $("#detail-img").innerHTML = business.logo_url ? `<img src="${esc(business.logo_url)}" alt="">` : "🏪";
    $("#detail-name").textContent = business.name;
    const cats = (business.categories || []).map((c) => `<span class="pub-tag">${esc(c.name)}</span>`).join("");
    $("#detail-meta").innerHTML =
      `<span class="detail-loc">📍 ${esc(business.city || "Sin ubicación")}</span>` +
      (cats ? `<span class="pub-tags">${cats}</span>` : "");
    $("#detail-desc").textContent = business.description || "Sin descripción.";

    $("#detail-products").innerHTML = prods.products.length
      ? `<div class="detail-list">${prods.products
          .map(
            (p) =>
              `<div class="detail-item"><span>${esc(p.name)}</span><span class="di-price">${fmtMoney(p.price, p.currency)}</span></div>`
          )
          .join("")}</div>`
      : `<p class="mini-sub">Sin productos publicados.</p>`;

    $("#detail-services").innerHTML = servs.services.length
      ? `<div class="detail-list">${servs.services
          .map(
            (s) =>
              `<div class="detail-item"><span>${esc(s.name)}${s.duration_minutes ? ` <small>(${s.duration_minutes} min)</small>` : ""}</span><span class="di-price">${fmtMoney(s.price, s.currency)}</span></div>`
          )
          .join("")}</div>`
      : `<p class="mini-sub">Sin servicios publicados.</p>`;

    $("#detail-location").innerHTML = renderBusinessInfo(business);

    const mapHtml = renderBusinessMap(business);
    const mapCard = $("#detail-map-card");
    if (mapHtml) {
      $("#detail-map").innerHTML = mapHtml;
      mapCard.style.display = "";
    } else {
      mapCard.style.display = "none";
    }

    $("#public-home").style.display = "none";
    $("#public-detail").style.display = "block";
    window.scrollTo({ top: 0 });
  } catch (err) {
    toast(err.message, "error");
  }
}

/* ============================================================
   Asistente virtual
   ============================================================ */
function assistantContext() {
  if ($("#app-screen") && $("#app-screen").style.display !== "none") return state.view || "dashboard";
  return "public";
}

function openAssistant() {
  $("#assistant-panel").style.display = "flex";
  if (!state.assistantWelcomed) {
    state.assistantWelcomed = true;
    assistantAddMessage(
      "¡Hola! Soy el asistente de PLPE 🌱 Puedo guiarte para buscar emprendimientos, productos y servicios, " +
        "o para cargar tu propio emprendimiento. ¿Con qué te ayudo?",
      "bot"
    );
    renderAssistantActions(
      [
        { label: "Ver emprendimientos", type: "public_tab", target: "businesses" },
        { label: "¿Cómo funciona?", type: "send", target: "¿Cómo funciona PLPE?" },
        { label: "Iniciar sesión", type: "auth" },
      ],
      []
    );
  }
  setTimeout(() => $("#assistant-input").focus(), 50);
}

function closeAssistant() {
  $("#assistant-panel").style.display = "none";
}

function assistantAddMessage(text, who) {
  const box = $("#assistant-messages");
  if (!box) return;
  const el = document.createElement("div");
  el.className = "assistant-msg " + who;
  el.textContent = text;
  box.appendChild(el);
  box.scrollTop = box.scrollHeight;
}

async function assistantSend(text) {
  const msg = (text || "").trim();
  if (!msg) return;
  assistantAddMessage(msg, "user");
  const input = $("#assistant-input");
  if (input) input.value = "";
  $("#assistant-suggestions").innerHTML = "";

  const typing = document.createElement("div");
  typing.className = "assistant-msg bot assistant-typing";
  typing.textContent = "Escribiendo…";
  $("#assistant-messages").appendChild(typing);
  $("#assistant-messages").scrollTop = $("#assistant-messages").scrollHeight;

  try {
    const res = await apiRequest("/assistant/chat", {
      method: "POST",
      body: { message: msg, context: assistantContext() },
      auth: false,
    });
    typing.remove();
    assistantAddMessage(res.reply, "bot");
    renderAssistantActions(res.actions || [], res.suggestions || []);
  } catch (err) {
    typing.remove();
    assistantAddMessage("Uy, no pude responder en este momento. Probá de nuevo.", "bot");
  }
}

function renderAssistantActions(actions, suggestions) {
  const wrap = $("#assistant-suggestions");
  if (!wrap) return;
  wrap.innerHTML = "";
  (actions || []).forEach((a) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "assistant-action";
    b.textContent = a.label;
    b.addEventListener("click", () => runAssistantAction(a));
    wrap.appendChild(b);
  });
  (suggestions || []).forEach((s) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "assistant-chip";
    b.textContent = s;
    b.addEventListener("click", () => assistantSend(s));
    wrap.appendChild(b);
  });
}

async function runAssistantAction(a) {
  if (!a) return;
  if (a.type === "send") {
    assistantSend(a.target || a.label);
    return;
  }
  closeAssistant();

  if (a.type === "public_tab") {
    enterPublic();
    state.publicTab = a.target || "businesses";
    $$(".public-tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === state.publicTab));
    loadPublicCatalog();
  } else if (a.type === "auth") {
    enterAuth();
  } else if (a.type === "panel") {
    if (state.user) enterApp();
    else enterAuth();
  } else if (a.type === "admin_view") {
    if (!state.user) {
      toast("Iniciá sesión para acceder al panel", "warning");
      enterAuth();
      return;
    }
    if ($("#app-screen").style.display === "none") enterApp();
    switchView(a.target);
  } else if (a.type === "open_form") {
    if (!state.user) {
      toast("Iniciá sesión para continuar", "warning");
      enterAuth();
      return;
    }
    if ($("#app-screen").style.display === "none") enterApp();
    const map = { business: "businesses", product: "products", service: "services", category: "categories" };
    const view = map[a.target] || "dashboard";
    try {
      await ensureCategories();
      await ensureBusinesses();
    } catch (e) {
      /* la vista mostrará el error si falla */
    }
    switchView(view);
    setTimeout(() => {
      if (a.target === "business") openBusinessModal();
      else if (a.target === "product") openProductModal();
      else if (a.target === "service") openServiceModal();
      else if (a.target === "category") openCategoryModal();
    }, 350);
  }
}

/* ============================================================
   Mascota que sigue al mouse y explica cada parte
   ============================================================ */
const HELP_MAP = [
  ["#public-login-btn, #detail-login-btn, .btn-access", "Acceso: iniciá sesión o registrate para gestionar tu emprendimiento."],
  ['.public-tab[data-tab="businesses"]', "Emprendimientos: mirá los productores locales y sus datos."],
  ['.public-tab[data-tab="products"]', "Productos: explorá lo que ofrecen, con su precio en pesos."],
  ['.public-tab[data-tab="services"]', "Servicios: trabajos y prestaciones de los emprendimientos."],
  ["#public-search-input", "Buscador: escribí palabras clave para encontrar por nombre."],
  ["#public-category-filter", "Filtrá por rubro: elegí una categoría."],
  [".btn-search", "Buscá con el texto y la categoría seleccionados."],
  ['[data-action="public-view-business"]', "Ver detalle: ubicación, productos, servicios y formulario de contacto."],
  ["#detail-back-btn", "Volver al catálogo público."],
  ["#detail-contact-form button", "Enviá tu solicitud: la administración de PLPE te contactará."],
  ['.nav-item[data-view="dashboard"]', "Panel: resumen general del sistema."],
  ['.nav-item[data-view="categories"]', "Categorías: los rubros que agrupan a los emprendimientos."],
  ['.nav-item[data-view="businesses"]', "Emprendimientos: creá, editá, aprobá o suspendé."],
  ['.nav-item[data-view="products"]', "Productos: cargá precios en pesos e inventario."],
  ['.nav-item[data-view="services"]', "Servicios que ofrecen los emprendimientos."],
  ['.nav-item[data-view="inquiries"]', "Consultas que los visitantes envían a los emprendimientos."],
  ['.nav-item[data-view="requests"]', "Solicitudes de contacto dejadas por los visitantes."],
  ['.nav-item[data-view="favorites"]', "Favoritos: lo que guardaste."],
  ['.nav-item[data-view="profile"]', "Mi Perfil: tus datos y tu contraseña."],
  ["#btn-new-business", "Crear un emprendimiento nuevo."],
  ["#btn-new-product", "Cargar un producto con su precio en pesos."],
  ["#btn-new-service", "Cargar un servicio con precio y duración."],
  ["#btn-new-category", "Crear una categoría (solo administradores)."],
  ["#business-search, #product-search, #service-search", "Buscador: filtrá la lista por texto."],
  ["#business-status-filter", "Filtrá emprendimientos por estado (pendiente, aprobado, suspendido)."],
  ["#requests-status-filter", "Filtrá las solicitudes por estado."],
  ["#inquiry-status-filter", "Filtrá las consultas por estado."],
  ["#logout-btn", "Cerrar sesión."],
  ["#view-public-btn", "Mirar cómo se ve el sitio para el público."],
  ["#assistant-fab", "Abrir el chat del asistente."],
  ['[data-action="approve-business"]', "Aprobar este emprendimiento (solo admin)."],
  ['[data-action="suspend-business"]', "Suspender este emprendimiento (solo admin)."],
  ['[data-action="edit-business"], [data-action="edit-product"], [data-action="edit-service"], [data-action="edit-category"]', "Editar este registro."],
  ['[data-action="del-business"], [data-action="del-product"], [data-action="del-service"], [data-action="del-category"]', "Eliminar este registro."],
  ['[data-action="view-inquiry"]', "Ver la consulta completa."],
  ['[data-action="view-request"]', "Ver la solicitud y cambiar su estado."],
  ["#modal-save", "Guardar los datos del formulario."],
  ["#modal-cancel, #modal-close", "Cerrar sin guardar."],
];

function helpFor(el) {
  if (!el || typeof el.closest !== "function") return null;
  const explicit = el.closest("[data-help]");
  if (explicit) return explicit.getAttribute("data-help");
  for (const [sel, text] of HELP_MAP) {
    try {
      if (el.closest(sel)) return text;
    } catch (e) {
      /* selector inválido, ignorar */
    }
  }
  return null;
}

const mascotState = {
  inited: false,
  enabled: false,
  raf: null,
  mx: null,
  my: null,
  cx: 0,
  cy: 0,
  lastEl: null,
  bubbleH: 48,
  frame: 0,
  el: null,
  bubble: null,
};

function mascotSetBubble(text) {
  const bubble = mascotState.bubble;
  if (!bubble) return;
  if (!text) {
    bubble.classList.remove("show");
    return;
  }
  if (bubble.textContent !== text) {
    bubble.textContent = text;
    bubble.classList.remove("show");
    void bubble.offsetWidth; // reinicia animación
    mascotState.bubbleH = bubble.offsetHeight || 48;
    bubble.classList.add("show");
  }
}

function mascotLoop() {
  const s = mascotState;
  if (!s.enabled || !s.el) {
    s.raf = null;
    return;
  }
  if (s.mx == null) {
    s.mx = window.innerWidth - 150;
    s.my = window.innerHeight - 170;
    s.cx = s.mx;
    s.cy = s.my;
  }
  s.cx += (s.mx + 20 - s.cx) * 0.18;
  s.cy += (s.my + 16 - s.cy) * 0.18;
  const px = Math.max(4, Math.min(s.cx, window.innerWidth - 258));
  const py = Math.max(8, Math.min(s.cy, window.innerHeight - 64));
  s.el.style.transform = `translate(${px}px, ${py}px)`;

  // Flecha del globito: arriba o abajo según el espacio disponible
  s.bubble.classList.toggle("below", py - 60 - s.bubbleH < 6);

  // Ayuda contextual (se recalcula cada ~6 frames)
  s.frame++;
  if (s.frame % 6 === 0) {
    const el = document.elementFromPoint(s.mx, s.my);
    if (el !== s.lastEl) {
      s.lastEl = el;
      mascotSetBubble(helpFor(el) || null);
    }
  }
  s.raf = requestAnimationFrame(mascotLoop);
}

function updateFollowToggle(active) {
  const btn = $("#assistant-follow-btn");
  if (!btn) return;
  btn.classList.toggle("active", active);
  btn.setAttribute("aria-pressed", active ? "true" : "false");
  const label = btn.querySelector(".assistant-follow-label");
  if (label) label.textContent = active ? "Siguiendo" : "Seguir mouse";
}

function enableAssistantFollow() {
  const s = mascotState;
  if (!s.inited) return;
  s.enabled = true;
  s.el.style.display = "block";
  if (s.mx == null) {
    s.mx = window.innerWidth - 150;
    s.my = window.innerHeight - 170;
  }
  s.cx = s.mx + 20;
  s.cy = s.my + 16;
  if (!s.raf) s.raf = requestAnimationFrame(mascotLoop);
  updateFollowToggle(true);
  mascotSetBubble("¡Listo! Movés el mouse por la pantalla y te explico qué hace cada parte. Clic en mí para chatear 💬");
  setTimeout(() => {
    if (!s.lastEl) mascotSetBubble(null);
  }, 5000);
}

function disableAssistantFollow() {
  const s = mascotState;
  s.enabled = false;
  if (s.raf) {
    cancelAnimationFrame(s.raf);
    s.raf = null;
  }
  if (s.el) s.el.style.display = "none";
  mascotSetBubble(null);
  s.lastEl = null;
  updateFollowToggle(false);
}

function toggleAssistantFollow() {
  if (mascotState.enabled) disableAssistantFollow();
  else enableAssistantFollow();
}

function initCursorMascot() {
  const s = mascotState;
  s.el = $("#cursor-mascot");
  s.bubble = $("#mascot-bubble");
  if (!s.el || !s.bubble) return;
  s.inited = true;

  const track = (e) => {
    if (e.pointerType && e.pointerType !== "mouse") return;
    s.mx = e.clientX;
    s.my = e.clientY;
    if (s.enabled && !s.raf) s.raf = requestAnimationFrame(mascotLoop);
  };
  document.addEventListener("pointermove", track, { passive: true });
  document.addEventListener("mousemove", track, { passive: true });

  const avatar = $("#mascot-avatar");
  if (avatar)
    avatar.addEventListener("click", () => {
      mascotSetBubble(null);
      openAssistant();
    });
}

/* ============================================================
   Eventos
   ============================================================ */
function on(selector, event, handler) {
  const el = $(selector);
  if (el) el.addEventListener(event, handler);
  return el;
}

function onAll(selector, event, handler) {
  $$(selector).forEach((el) => el.addEventListener(event, handler));
}

function bindEvents() {
  // Usamos nuestra propia validación (mensajes en español)
  $$("form").forEach((f) => f.setAttribute("novalidate", ""));

  // Sitio público
  on("#public-login-btn", "click", () => {
    if (state.user) enterApp();
    else enterAuth();
  });
  onAll(".public-tab", "click", (e) => {
    const tab = e.currentTarget;
    $$(".public-tab").forEach((t) => t.classList.toggle("active", t === tab));
    state.publicTab = tab.dataset.tab;
    loadPublicCatalog();
  });
  let publicTimer;
  on("#public-search-input", "input", () => {
    clearTimeout(publicTimer);
    publicTimer = setTimeout(loadPublicCatalog, 350);
  });
  on("#public-search-form", "submit", (e) => {
    e.preventDefault();
    loadPublicCatalog();
  });
  on("#public-category-filter", "change", () => {
    if ($("#public-category-filter").value && state.publicTab !== "businesses") {
      state.publicTab = "businesses";
      $$(".public-tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === "businesses"));
    }
    loadPublicCatalog();
  });

  // Detalle público (pantalla completa)
  on("#detail-back-btn", "click", closePublicDetail);
  on("#detail-login-btn", "click", () => {
    if (state.user) enterApp();
    else enterAuth();
  });
  on("#detail-contact-form", "submit", async (e) => {
    e.preventDefault();
    const form = e.target;
    const invalid = validateContainer(form);
    if (invalid) {
      toast(invalid, "error");
      return;
    }
    const btn = form.querySelector("button");
    if (btn) btn.disabled = true;
    try {
      const fd = new FormData(form);
      await apiRequest("/contact-requests", {
        method: "POST",
        body: {
          business_id: state.publicDetail ? state.publicDetail.id : null,
          name: fd.get("name").trim(),
          email: fd.get("email").trim(),
          phone: fd.get("phone").trim() || null,
          message: fd.get("message").trim() || null,
        },
        auth: false,
      });
      toast("¡Solicitud enviada! La administración te contactará.");
      form.reset();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      if (btn) btn.disabled = false;
    }
  });

  // Auth tabs
  onAll(".auth-tab", "click", (e) => {
    const tab = e.currentTarget;
    $$(".auth-tab").forEach((t) => t.classList.toggle("active", t === tab));
    $("#login-form").style.display = tab.dataset.tab === "login" ? "block" : "none";
    $("#register-form").style.display = tab.dataset.tab === "register" ? "block" : "none";
  });

  on("#login-form", "submit", async (e) => {
    e.preventDefault();
    const invalid = validateContainer(e.target);
    if (invalid) {
      toast(invalid, "error");
      return;
    }
    const btn = e.target.querySelector("button");
    if (btn) btn.disabled = true;
    try {
      await doLogin(
        $("#login-email").value.trim(),
        $("#login-password").value,
        $("#login-totp").value.trim()
      );
    } catch (err) {
      if (/totp|2fa/i.test(err.message)) $("#login-totp-group").style.display = "block";
      toast(err.message, "error");
    } finally {
      if (btn) btn.disabled = false;
    }
  });

  on("#register-form", "submit", async (e) => {
    e.preventDefault();
    const invalid = validateContainer(e.target);
    if (invalid) {
      toast(invalid, "error");
      return;
    }
    const btn = e.target.querySelector("button");
    if (btn) btn.disabled = true;
    try {
      await doRegister({
        email: $("#reg-email").value.trim(),
        password: $("#reg-password").value,
        full_name: $("#reg-name").value.trim() || null,
        phone: $("#reg-phone").value.trim() || null,
        city: $("#reg-city").value.trim() || null,
      });
    } catch (err) {
      toast(err.message, "error");
    } finally {
      if (btn) btn.disabled = false;
    }
  });

  on("#logout-btn", "click", logout);
  on("#view-public-btn", "click", enterPublic);
  on("#auth-back-btn", "click", enterPublic);

  // Navegación
  onAll(".nav-item", "click", (e) => switchView(e.currentTarget.dataset.view));
  on("#menu-toggle", "click", openSidebar);
  on("#sidebar-overlay", "click", closeSidebar);

  // Botones crear
  on("#btn-new-category", "click", () => openCategoryModal());
  on("#btn-new-business", "click", () => openBusinessModal());
  on("#btn-new-product", "click", () => openProductModal());
  on("#btn-new-service", "click", () => openServiceModal());

  // Filtros
  let searchTimer;
  on("#business-search", "input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => loadBusinesses().catch((e) => toast(e.message, "error")), 350);
  });
  on("#business-status-filter", "change", () => loadBusinesses().catch((e) => toast(e.message, "error")));
  on("#product-search", "input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => loadProducts().catch((e) => toast(e.message, "error")), 350);
  });
  on("#service-search", "input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => loadServices().catch((e) => toast(e.message, "error")), 350);
  });
  on("#inquiry-status-filter", "change", () => loadInquiries().catch((e) => toast(e.message, "error")));
  on("#requests-status-filter", "change", () => loadRequests().catch((e) => toast(e.message, "error")));

  // Delegación de acciones en tablas
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;
    const id = Number(btn.dataset.id);
    const action = btn.dataset.action;
    try {
      if (action === "edit-category") openCategoryModal(state.categories.find((c) => c.id === id));
      else if (action === "del-category") {
        if (confirm("¿Eliminar esta categoría?")) {
          await apiRequest(`/categories/${id}`, { method: "DELETE" });
          toast("Categoría eliminada");
          await loadCategories();
        }
      } else if (action === "edit-business") openBusinessModal(state.businesses.find((b) => b.id === id));
      else if (action === "del-business") {
        if (confirm("¿Eliminar este emprendimiento?")) {
          await apiRequest(`/businesses/${id}`, { method: "DELETE" });
          toast("Emprendimiento eliminado");
          await loadBusinesses();
        }
      } else if (action === "approve-business") {
        await apiRequest(`/businesses/${id}/approve`, { method: "POST" });
        toast("Emprendimiento aprobado");
        await loadBusinesses();
      } else if (action === "suspend-business") {
        await apiRequest(`/businesses/${id}/suspend`, { method: "POST" });
        toast("Emprendimiento suspendido");
        await loadBusinesses();
      } else if (action === "edit-product") openProductModal(state.products.find((p) => p.id === id));
      else if (action === "del-product") {
        if (confirm("¿Eliminar este producto?")) {
          await apiRequest(`/products/${id}`, { method: "DELETE" });
          toast("Producto eliminado");
          await loadProducts();
        }
      } else if (action === "edit-service") openServiceModal(state.services.find((s) => s.id === id));
      else if (action === "del-service") {
        if (confirm("¿Eliminar este servicio?")) {
          await apiRequest(`/services/${id}`, { method: "DELETE" });
          toast("Servicio eliminado");
          await loadServices();
        }
      } else if (action === "view-inquiry") openInquiryModal(state.inquiries.find((i) => i.id === id));
      else if (action === "view-request") openRequestModal(state.requests.find((r) => r.id === id));
      else if (action === "public-view-business") openPublicBusinessDetail(id);
      else if (action === "del-favorite") {
        const fav = state.favorites.find((f) => f.id === id);
        if (fav && confirm("¿Quitar de favoritos?")) await removeFavorite(fav);
      }
    } catch (err) {
      toast(err.message, "error");
    }
  });

  // Asistente virtual
  on("#assistant-fab", "click", openAssistant);
  on("#assistant-follow-btn", "click", toggleAssistantFollow);
  on("#assistant-close", "click", closeAssistant);
  on("#assistant-form", "submit", (e) => {
    e.preventDefault();
    assistantSend($("#assistant-input").value);
  });

  // Modal
  on("#modal-close", "click", closeModal);
  on("#modal-cancel", "click", closeModal);
  on("#modal", "click", (e) => { if (e.target.id === "modal") closeModal(); });
  on("#modal-save", "click", async () => {
    if (!modalSaveHandler) return;
    const invalid = validateContainer($("#modal-body"));
    if (invalid) {
      toast(invalid, "error");
      return;
    }
    const btn = $("#modal-save");
    btn.disabled = true;
    try {
      await modalSaveHandler();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      btn.disabled = false;
    }
  });

  // Perfil
  on("#profile-form", "submit", async (e) => {
    e.preventDefault();
    const invalid = validateContainer(e.target);
    if (invalid) {
      toast(invalid, "error");
      return;
    }
    try {
      const updated = await apiRequest("/users/me", {
        method: "PATCH",
        body: {
          full_name: $("#profile-name").value.trim() || null,
          phone: $("#profile-phone").value.trim() || null,
          city: $("#profile-city").value.trim() || null,
        },
      });
      state.user = { ...state.user, ...updated };
      persistSession();
      renderUserInfo();
      toast("Perfil actualizado");
    } catch (err) {
      toast(err.message, "error");
    }
  });

  on("#password-form", "submit", async (e) => {
    e.preventDefault();
    const invalid = validateContainer(e.target);
    if (invalid) {
      toast(invalid, "error");
      return;
    }
    try {
      await apiRequest("/users/me/change-password", {
        method: "POST",
        body: {
          current_password: $("#current-password").value,
          new_password: $("#new-password").value,
        },
      });
      toast("Contraseña cambiada. Volviendo a ingresar...");
      setTimeout(logout, 1200);
    } catch (err) {
      toast(err.message, "error");
    }
  });
}

/* ============================================================
   Tablas responsivas (etiquetas para vista de tarjetas en móvil)
   ============================================================ */
function applyTableLabels(table) {
  const heads = [...table.querySelectorAll("thead th")].map((th) => th.textContent.trim());
  table.querySelectorAll("tbody tr").forEach((tr) => {
    [...tr.children].forEach((td, i) => {
      if (heads[i]) td.setAttribute("data-label", heads[i]);
      else td.removeAttribute("data-label");
    });
  });
}

function initResponsiveTables() {
  [
    "#categories-table",
    "#businesses-table",
    "#products-table",
    "#services-table",
    "#inquiries-table",
    "#requests-table",
    "#favorites-table",
  ].forEach((sel) => {
    const table = $(sel);
    if (!table) return;
    const tbody = table.querySelector("tbody");
    if (!tbody) return;
    const apply = () => applyTableLabels(table);
    new MutationObserver(apply).observe(tbody, { childList: true });
    apply();
  });
}

/* ============================================================
   Inicialización
   ============================================================ */
async function init() {
  bindEvents();
  initCursorMascot();
  initResponsiveTables();
  if (state.accessToken) {
    try {
      await loadCurrentUser();
      enterApp();
      return;
    } catch {
      clearSession();
    }
  }
  enterPublic();
}

document.addEventListener("DOMContentLoaded", init);
