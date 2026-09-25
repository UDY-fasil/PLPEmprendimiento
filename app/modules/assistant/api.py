"""API del asistente virtual de PLPE.

Motor de respuestas basado en reglas (sin dependencias externas). Guía al
usuario por el sistema y devuelve acciones que el frontend ejecuta
(navegar a secciones, abrir formularios, iniciar sesión, etc.).

Puede reemplazarse fácilmente por un LLM: basta con reescribir
`build_response` para llamar a un modelo y devolver el mismo formato.
"""
import unicodedata

from fastapi import APIRouter

from app.modules.assistant.schemas import (
    AssistantAction,
    AssistantChatRequest,
    AssistantChatResponse,
)

assistant_router = APIRouter(prefix="/assistant", tags=["Asistente"])


def _norm(text: str) -> str:
    """Minúsculas y sin acentos para comparar palabras clave."""
    text = (text or "").lower().strip()
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def _resp(reply, actions=None, suggestions=None) -> AssistantChatResponse:
    return AssistantChatResponse(
        reply=reply,
        actions=[AssistantAction(**a) for a in (actions or [])],
        suggestions=suggestions or [],
    )


def build_response(message: str, context: str | None = None) -> AssistantChatResponse:
    text = _norm(message)

    def has(*words: str) -> bool:
        return any(w in text for w in words)

    # --- Saludos / cortesía -------------------------------------------------
    if has("hola", "buenas", "buen dia", "buenas tardes", "buenas noches", "que tal", "hey", "holaa"):
        return _resp(
            "¡Hola! Soy el asistente virtual de PLPE 🌱 Te ayudo a recorrer la plataforma. "
            "¿Qué querés hacer?",
            actions=[
                {"label": "Ver emprendimientos", "type": "public_tab", "target": "businesses"},
                {"label": "Ver productos", "type": "public_tab", "target": "products"},
                {"label": "Ver servicios", "type": "public_tab", "target": "services"},
            ],
            suggestions=[
                "¿Cómo busco por categoría?",
                "¿Cómo contacto a un emprendimiento?",
                "¿Cómo inicio sesión?",
            ],
        )

    if has("gracias", "muchas gracias", "genial", "perfecto", "buenisimo"):
        return _resp("¡De nada! 🌱 ¿Necesitás algo más?", suggestions=["¿Cómo funciona PLPE?"])

    if has("chau", "adios", "hasta luego", "nos vemos", "bye"):
        return _resp("¡Hasta luego! Éxitos con tu emprendimiento 🌱")

    # --- Cargar / crear (acciones de gestión) -------------------------------
    if has("emprendimiento", "negocio", "productor") and has(
        "carg", "crea", "creo", "agreg", "registr", "suma", "public", "dar de alta"
    ):
        return _resp(
            "Para cargar tu emprendimiento primero iniciá sesión. Después, en el panel, "
            "entrá a **Emprendimientos** y usá “+ Nuevo emprendimiento”. Vas a poder poner "
            "nombre, ciudad, categorías y datos de contacto.",
            actions=[
                {"label": "Iniciar sesión", "type": "auth"},
                {"label": "Cargar emprendimiento", "type": "open_form", "target": "business"},
            ],
            suggestions=["¿Cómo cargo un producto?", "¿Cómo eligen las categorías?"],
        )

    if has("producto", "articulo") and has("carg", "crea", "creo", "agreg", "registr", "suma", "public"):
        return _resp(
            "Para cargar un producto iniciá sesión y andá a **Productos** → “+ Nuevo producto”. "
            "Elegí el emprendimiento, el nombre y el precio en pesos argentinos (ARS).",
            actions=[
                {"label": "Iniciar sesión", "type": "auth"},
                {"label": "Cargar producto", "type": "open_form", "target": "product"},
            ],
        )

    if has("servicio") and has("carg", "crea", "creo", "agreg", "registr", "suma", "public"):
        return _resp(
            "Para cargar un servicio iniciá sesión y andá a **Servicios** → “+ Nuevo servicio”. "
            "Podés indicar precio en pesos y duración en minutos.",
            actions=[
                {"label": "Iniciar sesión", "type": "auth"},
                {"label": "Cargar servicio", "type": "open_form", "target": "service"},
            ],
        )

    if has("categoria", "rubro") and has("carg", "crea", "creo", "agreg", "registr", "suma", "public"):
        return _resp(
            "Las categorías las administra la administración de PLPE. Si sos admin, "
            "entrá a **Categorías** y usá “+ Nueva categoría”.",
            actions=[{"label": "Ir a Categorías", "type": "admin_view", "target": "categories"}],
        )

    # --- Moderación / administración ---------------------------------------
    if has("aprobar", "suspender", "moderar", "habilitar", "rechazar"):
        return _resp(
            "Como administrador podés aprobar o suspender emprendimientos desde **Emprendimientos**, "
            "con los botones “Aprobar” y “Suspender”. Solo los aprobados se destacan en el sitio público.",
            actions=[{"label": "Ir a Emprendimientos", "type": "admin_view", "target": "businesses"}],
        )

    if has("solicitud", "solicitudes", "pedido de contacto", "pedidos de contacto"):
        return _resp(
            "En **Solicitudes** vas a ver los pedidos de contacto que dejan los visitantes desde el "
            "detalle de un emprendimiento. Podés marcarlos como *Contactada* o *Cerrada*.",
            actions=[{"label": "Ver Solicitudes", "type": "admin_view", "target": "requests"}],
        )

    if has("consulta") and has("ver", "listar", "panel", "recibi", "recibidas", "mensajes"):
        return _resp(
            "En **Consultas** están los mensajes que enviaron a los emprendimientos. "
            "Podés verlos y cambiar su estado.",
            actions=[{"label": "Ver Consultas", "type": "admin_view", "target": "inquiries"}],
        )

    if has("favorito"):
        return _resp(
            "En **Favoritos** ves los emprendimientos y productos que guardaste.",
            actions=[{"label": "Ver Favoritos", "type": "admin_view", "target": "favorites"}],
        )

    if has("perfil", "mi cuenta", "contrasena", "contraseña", "cambiar clave"):
        return _resp(
            "En **Mi Perfil** podés actualizar tus datos y cambiar tu contraseña.",
            actions=[{"label": "Ir a Mi Perfil", "type": "admin_view", "target": "profile"}],
        )

    # --- Contacto -----------------------------------------------------------
    if has("contacto", "contactar", "contacten", "comunicar", "comunicarme", "que me llamen") or (
        has("consulta") and not has("panel")
    ):
        return _resp(
            "Entrá al detalle de un emprendimiento (botón “Ver detalle”) y completá el formulario "
            "**“Solicitar ser contactado”**. Tu pedido lo recibe la administración de PLPE, que se "
            "va a comunicar con vos. No necesitás crear una cuenta.",
            actions=[{"label": "Ver emprendimientos", "type": "public_tab", "target": "businesses"}],
        )

    # --- Filtro por categoría ----------------------------------------------
    if has("categoria", "rubro", "filtrar", "filtro"):
        return _resp(
            "En el inicio usá el selector **“Todas las categorías”** que está en el buscador. "
            "Al elegir una, la lista muestra solo los emprendimientos de ese rubro.",
            actions=[{"label": "Ir al inicio", "type": "public_tab", "target": "businesses"}],
        )

    # --- Precios ------------------------------------------------------------
    if has("precio", "cuesta", "cuanto", "costo", "moneda", "peso", "pesos", "barato", "caro", "valor"):
        return _resp(
            "Todos los precios se muestran en **pesos argentinos (ARS)**, con el formato "
            "$ 1.234,56. Los ves en las tarjetas de productos y servicios y en el detalle.",
            actions=[
                {"label": "Ver productos", "type": "public_tab", "target": "products"},
                {"label": "Ver servicios", "type": "public_tab", "target": "services"},
            ],
        )

    # --- Acceso / cuenta ----------------------------------------------------
    if has("iniciar sesion", "ingresar", "login", "acceso", "entrar", "mi cuenta", "registrarme", "registrarse", "cuenta"):
        return _resp(
            "Hacé clic en **“Acceso”** (arriba a la derecha). Si todavía no tenés cuenta, "
            "podés registrarte desde la misma pantalla.",
            actions=[{"label": "Ir a Acceso", "type": "auth"}],
        )

    # --- Búsquedas ----------------------------------------------------------
    if has("producto", "productos", "comprar", "venden", "vende"):
        return _resp(
            "Podés ver todos los productos en la pestaña **Productos**. Cada uno muestra su "
            "emprendimiento y su precio en pesos argentinos.",
            actions=[{"label": "Ver productos", "type": "public_tab", "target": "products"}],
            suggestions=["¿Cómo contacto al vendedor?", "Ver emprendimientos"],
        )

    if has("servicio", "servicios"):
        return _resp(
            "Mirá los servicios disponibles en la pestaña **Servicios**. Incluyen precio en pesos "
            "y, en muchos casos, su duración.",
            actions=[{"label": "Ver servicios", "type": "public_tab", "target": "services"}],
        )

    if has("emprendimiento", "negocio", "productor", "vendedor", "comercio"):
        return _resp(
            "Mirá los emprendimientos en la pestaña **Emprendimientos** del inicio. Podés buscar "
            "por nombre o filtrar por categoría, y entrar al detalle para ver su ubicación.",
            actions=[{"label": "Ver emprendimientos", "type": "public_tab", "target": "businesses"}],
            suggestions=["¿Cómo filtro por categoría?", "¿Cómo contacto a un emprendimiento?"],
        )

    # --- Ayuda general ------------------------------------------------------
    if has("ayuda", "ayudar", "como funciona", "guia", "guiame", "guiar", "no se", "que puedo hacer", "empezar", "funciona"):
        return _resp(
            "Te cuento cómo funciona PLPE 🌱\n"
            "• En el inicio explorás **emprendimientos, productos y servicios** sin registrarte.\n"
            "• Usá el **buscador** y el **filtro por categoría**.\n"
            "• Entrá al **detalle** de un emprendimiento para ver su ubicación y **solicitar que "
            "la administración te contacte**.\n"
            "• Con una cuenta podés **cargar tu emprendimiento, productos y servicios**.",
            actions=[
                {"label": "Ver emprendimientos", "type": "public_tab", "target": "businesses"},
                {"label": "Iniciar sesión", "type": "auth"},
                {"label": "Cargar emprendimiento", "type": "open_form", "target": "business"},
            ],
            suggestions=["¿Cómo busco por categoría?", "Ver productos", "¿Cómo contacto a un emprendimiento?"],
        )

    # --- Fallback -----------------------------------------------------------
    return _resp(
        "No estoy seguro de eso 🤔. Puedo ayudarte a: buscar emprendimientos, productos y "
        "servicios, filtrar por categoría, contactar a un emprendimiento o cargar tu "
        "emprendimiento. ¿Qué querés hacer?",
        actions=[
            {"label": "Ver emprendimientos", "type": "public_tab", "target": "businesses"},
            {"label": "Ver productos", "type": "public_tab", "target": "products"},
            {"label": "Iniciar sesión", "type": "auth"},
        ],
        suggestions=["¿Cómo funciona PLPE?", "¿Cómo contacto a un emprendimiento?", "¿Cómo cargo mi emprendimiento?"],
    )


@assistant_router.post("/chat", response_model=AssistantChatResponse)
async def assistant_chat(data: AssistantChatRequest):
    """Devuelve la respuesta del asistente y las acciones sugeridas."""
    return build_response(data.message, data.context)
