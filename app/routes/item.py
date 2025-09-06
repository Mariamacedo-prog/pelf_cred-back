from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.connection.database import get_db
from app.schemas.Item import ItemCreate
from fastapi import APIRouter

router = APIRouter()


@router.get("/items", tags=["Items"])
async def read_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("select * from items;"))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]



@router.get("/items/{id}", tags=["Items"])
async def read_item(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM items WHERE id = :id"), {"id": id})
    row = result.fetchone()
    if row:
        return dict(row._mapping)
    return {"error": "Item não localizado"}

@router.post("/items", tags=["Items"])
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    query = text("""
        INSERT INTO items (name, description, price)
        VALUES (:name, :description, :price)
        RETURNING *
    """)
    result = await db.execute(query, item.dict())
    await db.commit()
    new_item = result.fetchone()
    return dict(new_item._mapping)

@router.put("/items/{id}", tags=["Items"])
async def update_item(id: int, item: ItemCreate, db: AsyncSession = Depends(get_db)):
    query = text("""
        UPDATE items
        SET name = :name, description = :description, price = :price
        WHERE id = :id
        RETURNING *
    """)
    result = await db.execute(query, {**item.dict(), "id": id})
    await db.commit()
    updated_item = result.fetchone()

    if updated_item:
        return dict(updated_item._mapping)
    return {"error": "Item not found"}


@router.delete("/items/{id}", tags=["Items"])
async def delete_item(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("DELETE FROM items WHERE id = :id RETURNING id"), {"id": id})
    await db.commit()
    deleted = result.fetchone()

    if deleted:
        return {"message": f"Item {id} deletado com sucesso"}
    return {"error": "Item não encontrado"}
