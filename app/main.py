from fastapi import FastAPI
from app.routes import auth, cliente, user, logs, plano, servico, vendedor, root, contrato, transacao, export
from app.connection.database import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware

# uvicorn app.main:app --reload

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()

origins = [
    "https://pelf-cred.netlify.app",
    "http://localhost:4200",
    "http://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(root.router)
app.include_router(logs.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(cliente.router)
app.include_router(plano.router)
app.include_router(servico.router)
app.include_router(vendedor.router)
app.include_router(contrato.router)
app.include_router(transacao.router)
app.include_router(export.router)