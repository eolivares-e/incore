# Insurance Core

Monorepo para el core de seguros con Next.js (frontend) y FastAPI (backend).

## Estructura del Proyecto

```
incore/
├── frontend/          # Next.js + TypeScript
├── backend/           # FastAPI + Python 3.12
└── docker-compose.yml
```

## Requisitos

- Node.js 20+
- Python 3.12+
- Yarn
- Docker y Docker Compose
- uv (gestor de paquetes Python)

## Instalación de uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Configuración Local

### Frontend

```bash
cd frontend
yarn install
cp .env.example .env
yarn dev
```

El frontend estará disponible en `http://localhost:3000`

### Backend

```bash
cd backend
cp .env.example .env
uv pip install -e .
uvicorn app.main:app --reload
```

El backend estará disponible en `http://localhost:8000`

Documentación API: `http://localhost:8000/docs`

## Docker

### Iniciar todos los servicios

```bash
docker-compose up
```

### Iniciar en modo detached

```bash
docker-compose up -d
```

### Detener servicios

```bash
docker-compose down
```

## Testing

### Frontend

```bash
cd frontend
yarn test
```

### Backend

```bash
cd backend
uv pip install -e ".[dev]"
pytest tests/ -v
```

O usar el script:

```bash
cd backend
./run_tests.sh
```

## Desarrollo

### Frontend
- Framework: Next.js 14 con App Router
- Lenguaje: TypeScript
- Testing: Vitest
- Puerto: 3000

### Backend
- Framework: FastAPI
- Lenguaje: Python 3.12
- Testing: pytest
- Puerto: 8000

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc
