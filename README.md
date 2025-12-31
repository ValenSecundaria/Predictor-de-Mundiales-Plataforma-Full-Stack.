# ⚽ Proyecto Predictor Mundial — Plantilla Base (FastAPI + Next.js + Chakra UI + Bootstrap)

---

## 🧱 Descripción General

Este proyecto es una **plantilla base moderna** para aplicaciones **full-stack** que integran:

- **Frontend:** [Next.js](https://nextjs.org/) (App Router)
- **UI:** [Chakra UI](https://chakra-ui.com/) + [Bootstrap](https://getbootstrap.com/)
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
- **Infraestructura:** [Docker Compose](https://docs.docker.com/compose/) + [Nginx](https://nginx.org/en/)
- **Despliegue:** Un solo servidor (VPS) con un reverse proxy centralizado

La aplicación actual sirve como base del **Predictor de Partidos del Mundial**, pero su arquitectura es genérica y puede reutilizarse para cualquier proyecto analítico o de machine learning con frontend moderno.

---

## 🚀 Estructura General

predictor-mundial/
├─ README.md
├─ .gitignore
├─ .env.example # variables de entorno de referencia (sin secretos)
├─ docs/
│ ├─ arquitectura.md # decisiones, ADRs, diagramas, endpoints
│ └─ api-spec.yaml # contrato OpenAPI (si querés mantenerlo aparte)
│
├─ infra/
│ ├─ docker-compose.yml # orquesta todo
│ ├─ .env # prod/staging (no subir a git)
│ ├─ traefik/
│ │ └─ dynamic.yml # middlewares, rate-limit, headers, etc.
│ ├─ letsencrypt/ # certificados (Traefik los maneja)
│ ├─ scripts/
│ │ ├─ bootstrap.sh # alta inicial del servidor, usuarios, firewall
│ │ ├─ backup_db.sh # dumps programados
│ │ └─ deploy.sh # pull + compose up -d (si usás CI)
│ └─ monitoring/
│ ├─ prometheus.yml # opcional
│ └─ grafana/ # opcional
│
├─ backend/
│ ├─ Dockerfile
│ ├─ pyproject.toml | requirements.txt
│ ├─ .env.sample # variables específicas del backend
│ └─ app/
│ ├─ main.py # arranque de la app / registro de routers y middlewares
│ ├─ config/
│ │ ├─ settings.py # lectura de envs, ALLOWED_ORIGINS, DB_URL, etc.
│ │ └─ logging.py # formato de logs, nivel, handlers
│ ├─ api/
│ │ ├─ routers/
│ │ │ ├─ health.py # /health
│ │ │ ├─ teams.py # /teams, /teams/{id}
│ │ │ ├─ matches.py # /matches, filtros
│ │ │ └─ predict.py # /predict (entrada: equipos/params → salida: probabilidades)
│ │ └─ deps.py # dependencias (DB, cache, auth)
│ ├─ core/
│ │ ├─ entities.py # modelos de dominio
│ │ ├─ errors.py # excepciones de dominio
│ │ └─ interfaces.py # interfaces base / puertos
│ ├─ data/
│ │ ├─ ingestion/ # conectores (API, CSV, DB)
│ │ ├─ cleaning/ # normalización, validaciones
│ │ ├─ storage/
│ │ │ ├─ repositories/ # ORM o consultas SQL
│ │ │ └─ schemas/ # DTOs / serialización
│ │ └─ pipelines/ # jobs ETL
│ ├─ analytics/
│ │ ├─ features/ # construcción de variables
│ │ ├─ probability/ # Poisson, bayes, regresión
│ │ ├─ models/ # entrenamiento ML
│ │ └─ evaluation/ # métricas, backtesting
│ ├─ services/
│ │ ├─ prediction_service.py
│ │ └─ match_service.py
│ ├─ adapters/
│ │ ├─ http_clients/
│ │ └─ cache/
│ ├─ tasks/
│ │ ├─ scheduler.py
│ │ └─ jobs.py
│ ├─ tests/
│ │ ├─ unit/
│ │ ├─ integration/
│ │ └─ e2e/
│ └─ migrations/
│
├─ frontend/
│ ├─ Dockerfile
│ ├─ package.json
│ ├─ .env.example
│ ├─ public/
│ │ └─ favicon.svg
│ └─ src/
│ ├─ app/
│ │ ├─ layout.(tsx)
│ │ ├─ page.(tsx)
│ │ └─ predict/
│ │ └─ page.(tsx)
│ ├─ components/
│ ├─ lib/
│ ├─ styles/
│ └─ types/
│
└─ .github/
└─ workflows/
├─ ci-backend.yml
└─ ci-frontend.yml

---

## 🧩 Arquitectura Técnica

### 🔹 Backend (FastAPI)

El backend implementa una arquitectura por capas:

1. **Extracción de datos:** obtención desde APIs, archivos o DB (mock en esta plantilla).
2. **Limpieza / Analítica:** filtros y conteos base.
3. **Intermediaria (API):** expone `/api/v1/analisis` vía FastAPI.

> En desarrollo local corre en `http://localhost:8000`.

### 🔹 Frontend (Next.js + Chakra + Bootstrap)

- Usa el **App Router moderno** (`src/app/`).
- Chakra UI y Bootstrap coexisten para usar componentes de ambos ecosistemas.
- Llama al endpoint del backend (`/api/v1/analisis`) y muestra los resultados.

> En desarrollo local corre en `http://localhost:3000`.

### 🔹 Comunicación entre ambos

- En **desarrollo local**, Next.js tiene un proxy configurado en `next.config.js`:
  ```js
  rewrites() {
    return [{ source: '/api/:path*', destination: 'http://localhost:8000/api/:path*' }];
  }
  Esto evita errores CORS y permite usar rutas relativas (fetch('/api/v1/analisis')).
  ```

En producción (Docker), el tráfico pasa por Nginx, que redirige:

/api/... → backend (FastAPI)

/... → frontend (Next.js)

🧰 Entorno de Desarrollo Local (sin Docker)
1️⃣ Instalar dependencias del frontend

Desde la raíz del proyecto:

cd frontend
npm install

2️⃣ Correr ambos servidores en paralelo
npm run dev

3️⃣ Probar el backend por separado (opcional)
cd backend
python -m uvicorn app.main:app --reload --port 8000

Flujo de datos:
Usuario → Frontend (Next.js)
→ /api/v1/analisis
→ Proxy interno (Next.js o Nginx)
→ Backend (FastAPI)
→ Extracción → Limpieza → Analítica
← Resultado JSON
← Renderizado en interfaz con Chakra + Bootstrap
