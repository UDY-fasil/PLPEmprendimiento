# PLPE — Plataforma Local de Productores y Emprendimientos

Aplicación para **visibilizar y conectar emprendedores y productores locales**:
catálogo público, panel de gestión por usuario (cada uno con su propio entorno),
asistente virtual, carga de productos/servicios con imágenes y solicitudes de contacto.

## Stack

- **Backend:** FastAPI (Python 3.11) + SQLAlchemy (async)
- **Base de datos:** MariaDB (datos) + MongoDB (auditoría)
- **Frontend:** HTML/CSS/JS servido por el propio backend
- **Infraestructura:** Docker + Docker Compose (MariaDB, MongoDB, Adminer, Mongo Express, Web)

## Inicio rápido

```bash
docker compose up -d --build
docker compose exec web alembic upgrade head
docker compose exec web python scripts/setup_admin.py
```

Acceso: http://localhost:8000 → **admin@plpe.com** / **admin1234**

📖 **Documentación completa de instalación (Debian y Ubuntu):**
[`docs/INSTALACION_DOCKER.md`](docs/INSTALACION_DOCKER.md)

## Estructura

```
app/                 Backend FastAPI + frontend estático
  core/              Configuración, seguridad, base de datos
  modules/           auth, business, audit, contact, assistant, uploads
  static/            Frontend (index.html, css, js) e imágenes subidas
alembic/             Migraciones de base de datos
scripts/             setup_admin.py, seed_data.py
docs/                Documentación
docker-compose.yml   Servicios
dockerfile           Imagen de la aplicación
```

## Comandos útiles

```bash
docker compose ps                 # estado
docker compose logs -f web        # logs
docker compose down               # detener (conserva datos)
docker compose down -v            # detener y borrar datos
docker compose up -d --build      # reconstruir
```
