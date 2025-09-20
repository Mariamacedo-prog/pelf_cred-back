from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.connection.database import get_db
from fastapi import APIRouter

router = APIRouter()

@router.delete("/api/v1/log", tags=["Logs"])
async def delete_all_logs( db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("DELETE FROM log"))
    await db.commit()

    if result.rowcount > 0:
        return {"message": f"{result.rowcount} log(s) deletado(s) com sucesso"}
    else:
        return {"message": "Nenhum log encontrado para deletar"}
