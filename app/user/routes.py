from typing import List

from fastapi import APIRouter, Body, HTTPException, status

from .user import User, UserUpdate

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
def create(user: UserUpdate = Body(...)):
    print(f"Создаём нового пользователя {user.name}...", end='')
    user = User(name = user.name)
    user.save()
    print(f"успешно")
    return user
