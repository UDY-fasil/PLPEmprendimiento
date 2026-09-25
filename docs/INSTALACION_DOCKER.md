# PLPE — Instalación con Docker en Linux (Debian y Ubuntu)

Guía paso a paso para levantar todo el sistema (backend, base de datos MariaDB,
MongoDB, Adminer y Mongo Express) usando Docker en **Debian** y **Ubuntu**.

---

## 1. Requisitos

- **Debian 11/12** o **Ubuntu 20.04 / 22.04 / 24.04** (64 bits)
- Usuario con permisos `sudo`
- Conexión a internet (solo para la instalación)
- Puertos libres: `8000`, `3306`, `27017`, `8081`, `8567`

Verificá la distro:

```bash
cat /etc/os-release
```

---

## 2. Instalar Docker y Docker Compose

### Opción A — Repositorio oficial (recomendado)

**Paso 1: dependencias base**

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
```

**Paso 2: clave GPG de Docker**

```bash
# Debian:
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Ubuntu (reemplazá el anterior si usás Ubuntu):
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

**Paso 3: agregar el repositorio**

```bash
# Debian:
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Ubuntu:
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**Paso 4: instalar Docker Engine + Compose**

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Opción B — Script automático (más rápido)

```bash
curl -fsSL https://get.docker.com | sudo sh
```

### Post-instalación: usar Docker sin `sudo`

```bash
sudo usermod -aG docker $USER
newgrp docker        # o cerrá sesión y volvé a entrar
```

### Verificar

```bash
docker --version
docker compose version
sudo systemctl status docker
```

> El sistema usa **Docker Compose v2** (`docker compose`, con espacio). Si en tu
> sistema aparece `docker-compose` (con guion) también funciona, pero la guía usa `docker compose`.

---

## 3. Obtener el proyecto

Copiá la carpeta del proyecto a una ubicación, por ejemplo `/opt/plpe` o `~/Docker/PLPE`:

```bash
# Si lo tenés comprimido:
unzip PLPE.zip -d ~/Docker/
cd ~/Docker/PLPE

# O si usás git:
# git clone <URL-del-repo> PLPE && cd PLPE
```

Asegurate de estar dentro de la carpeta que contiene `docker-compose.yml`.

---

## 4. Configurar variables de entorno

El proyecto incluye un archivo `.env`. Revisalo y **cambiá los valores sensibles**:

```bash
nano .env
```

```env
PROJECT_NAME="PLPE - Plataforma Local de Productores y Emprendimientos"
MARIADB_URL="mysql+aiomysql://plpe_user:plpe_password@mariadb:3306/plpe_db"
MONGODB_URL="mongodb://admin:adminpassword@mongodb:27017/?authSource=admin"
SECRET_KEY="tu_secret_key_super_segura_aqui"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> ⚠️ **Importante:** en producción cambiá `SECRET_KEY` y las contraseñas de las
> bases de datos. Si cambiás las contraseñas, actualizá también los `environment`
> de `docker-compose.yml` para que coincidan.

Generar una clave secreta segura:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## 5. Levantar el sistema

```bash
docker compose up -d --build
```

Esto **construye la imagen** de la aplicación y levanta:

| Servicio        | Contenedor          | Puerto host |
|-----------------|---------------------|-------------|
| Aplicación web  | `plpe_web`          | `8000`      |
| MariaDB         | `plpe_mariadb`      | `3306`      |
| MongoDB         | `plpe_mongodb`      | `27017`     |
| Adminer         | `plpe_adminer`      | `8567`      |
| Mongo Express   | `plpe_mongo_express`| `8081`      |

Esperá unos **15–20 segundos** a que MariaDB y MongoDB terminen de iniciar.

---

## 6. Verificar que está corriendo

```bash
docker compose ps
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{"status":"ok","app":"PLPE"}
```

Ver los logs de la aplicación:

```bash
docker compose logs -f web
```

---

## 7. Crear las tablas (migraciones de Alembic)

El esquema de MariaDB se crea con Alembic:

```bash
docker compose exec web alembic upgrade head
```

---

## 8. Crear el usuario administrador

```bash
docker compose exec web python scripts/setup_admin.py
```

Credenciales por defecto:

- **Usuario:** `admin@plpe.com`
- **Contraseña:** `admin1234`

Para usar otras credenciales:

```bash
docker compose exec -e ADMIN_EMAIL="tu@email.com" -e ADMIN_PASSWORD="TuClaveSegura" web python scripts/setup_admin.py
```

> **(Opcional)** Cargar datos ficticios de ejemplo (⚠️ borra los datos actuales):
> ```bash
> docker compose exec web python scripts/seed_data.py
> ```

---

## 9. Acceder al sistema

- **Aplicación:** http://localhost:8000
- **Adminer (gestor MariaDB):** http://localhost:8567
  - Servidor: `mariadb` · Usuario: `plpe_user` · Contraseña: `plpe_password` · Base: `plpe_db`
- **Mongo Express:** http://localhost:8081 (usuario `admin` / contraseña `admin123`)

Desde el navegador, en la app entrá con el **admin** (paso 8) desde el botón **Acceso**.

---

## 10. Comandos útiles

```bash
# Estado de los contenedores
docker compose ps

# Logs en vivo
docker compose logs -f web
docker compose logs -f mariadb

# Reiniciar / detener
docker compose restart
docker compose stop
docker compose start

# Apagar (conserva los datos)
docker compose down

# Apagar y BORRAR los datos (volúmenes)  ⚠️
docker compose down -v

# Reconstruir tras cambios en el código
docker compose up -d --build
```

---

## 11. Respaldar y restaurar la base de datos

**Respaldo:**

```bash
docker compose exec mariadb mysqldump -u root -prootpassword plpe_db > backup_$(date +%F).sql
```

**Restaurar:**

```bash
docker compose exec -T mariadb mysql -u root -prootpassword plpe_db < backup_2026-01-01.sql
```

---

## 12. Empezar de cero (base vacía)

```bash
# Borra contenedores y datos, y reconstruye
docker compose down -v
docker compose up -d --build
docker compose exec web alembic upgrade head
docker compose exec web python scripts/setup_admin.py
```

---

## 13. Reinicio automático al encender el equipo

El `docker-compose.yml` ya deja la app con `restart: unless-stopped`. Para las
bases de datos se recomienda lo mismo. Editá `docker-compose.yml` y agregá
`restart: unless-stopped` a los servicios `mariadb` y `mongodb`:

```yaml
  mariadb:
    image: mariadb:10.11
    restart: unless-stopped
    # ...

  mongodb:
    image: mongo:7.0
    restart: unless-stopped
    # ...
```

Y asegurate de que el servicio de Docker arranque con el sistema:

```bash
sudo systemctl enable docker
```

---

## 14. Solución de problemas

**`permission denied` al usar Docker**
```bash
sudo usermod -aG docker $USER && newgrp docker
# o ejecutá los comandos con sudo
```

**Un puerto está ocupado (ej. 8000 o 3306)**
```bash
sudo ss -ltnp | grep :8000
```
Cambiá el puerto en `docker-compose.yml` (columna izquierda de `ports`, ej. `"8001:8000"`)
y volvé a levantar: `docker compose up -d`.

**Error `Can't connect to MySQL server on 'mariadb'`**
Esperá a que MariaDB termine de iniciar y reiniciá la app:
```bash
docker compose restart web
docker compose logs -f mariadb
```

**Los contenedores de bases se detienen al reiniciar el equipo**
Agregá `restart: unless-stopped` (ver sección 13) y `sudo systemctl enable docker`.

**Ver / limpiar todo**
```bash
docker compose logs -f web          # ver errores
docker compose down -v              # ⚠️ borra datos
docker compose up -d --build
```

**Error de permisos en imágenes subidas**
Las imágenes se guardan en `app/static/uploads/` (creadas por el contenedor como
root). Si necesitás editarlas desde el host: `sudo chown -R $USER app/static/uploads`.

---

## 15. Notas para producción (opcional)

- Quitá el `--reload` del `CMD` en el `dockerfile` y usá workers:
  ```
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
  ```
- Definí un `SECRET_KEY` fuerte y contraseñas de base de datos robustas.
- Poné un **proxy inverso** (Nginx/Traefik) con **HTTPS** delante de la app.
- Restringí o deshabilitá **Adminer** y **Mongo Express** en producción.

---

## Resumen rápido (para copiar y pegar)

```bash
# 1) Instalar Docker (Ubuntu/Debian) — opción rápida
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER && newgrp docker

# 2) Entrar al proyecto
cd ~/Docker/PLPE

# 3) Levantar
docker compose up -d --build

# 4) Crear tablas y admin
docker compose exec web alembic upgrade head
docker compose exec web python scripts/setup_admin.py

# 5) Abrir
#    http://localhost:8000   (admin@plpe.com / admin1234)
```
