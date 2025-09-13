from fastapi import FastAPI
from app.routes import root, auth, item, user
from app.connection.database import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware

# uvicorn app.main:app --reload

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root.router)
app.include_router(auth.router)
app.include_router(user.router)


