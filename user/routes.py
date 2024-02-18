from typing import List

from fastapi import APIRouter, Body, HTTPException, status

from .User import User

router = APIRouter()


@router.get("/", summary="Получить всех пользователей", response_model=List[User])
def all(limit: int = 100):
    print("Запрос всех пользователей...", end='')
    rooms = User.get_all()
    print("  успешно")
    return rooms


@router.get("/{id}", summary="Получить пользователя по id", response_model=User)
def get(id: str):
    print(f"Запрос пользователя с id = {id}...", end='')
    if (user := User.get(id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователь с ID = {id} не найден")
    print(" успешно")
    return user


@router.post("/", summary="Создать нового пользователя")
def create(user: User = Body(...)):
    print(f"Создаём нового пользователя...", end='')
    created_id = user.create()
    print(f"успешно...", end='')
    return created_id
