import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.connection.base_class import Base
from app.models.EnderecoModel import EnderecoModel
from app.models.UserModel import UserModel
from app.models.LogModel import LogModel
from app.models.ClienteModel import ClienteModel
from app.models.PlanoModel import PlanoModel
from app.models.ServicoModel import ServicoModel
from app.models.VendedorModel import VendedorModel
from app.models.AnexoModel import AnexoModel

from app.models.ParcelamentoModel import ParcelamentoModel
from app.models.ContratoModel import ContratoModel
from app.models.AssinaturaEvidenciaModel import AssinaturaEvidenciaModel


load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())