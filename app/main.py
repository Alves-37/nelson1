import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import health, produtos, usuarios, clientes, vendas, auth, categorias, ws
from app.routers import metricas, relatorios, empresa_config, admin, dividas, abastecimentos
from app.db.session import engine
from app.db.base import DeclarativeBase

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Verificar e criar tabelas se necessário
    print("Iniciando backend...")
    try:
        async with engine.begin() as conn:
            print("Verificando estrutura do PostgreSQL...")
            await conn.run_sync(DeclarativeBase.metadata.create_all)
            print("Estrutura do banco verificada!")
    except Exception as e:
        print(f"Erro ao conectar com o banco: {e}")
        # Continue mesmo com erro de banco para permitir healthcheck
        pass
    
    yield
    
    # Shutdown
    print("Encerrando backend...")
    try:
        await engine.dispose()
    except:
        pass

app = FastAPI(
    title="PDV3 Hybrid Backend",
    description="API for PDV3 online/offline synchronization.",
    version="0.1.0",
    lifespan=lifespan
)

# CORS (Cross-Origin Resource Sharing)
default_origins = [
    "https://neopdv1.vercel.app",
    "http://localhost:5173",
    "http://localhost:4173",
]

env_origins = os.getenv("CORS_ALLOW_ORIGINS")
if env_origins:
    allowed_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
else:
    allowed_origins = default_origins

allow_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router)
app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(vendas.router)
app.include_router(metricas.router)
app.include_router(auth.router)
app.include_router(ws.router)
app.include_router(relatorios.router)
app.include_router(empresa_config.router)
app.include_router(admin.router)
app.include_router(dividas.router)
app.include_router(abastecimentos.router)

@app.get("/")
async def read_root():
    return {"message": "PDV3 Backend is running!"}
