from datetime import date
from typing import List

from fastapi import APIRouter, Body, HTTPException, status

from .room import Room

router = APIRouter()


@router.get("/", summary="Список всех комнат", response_model=List[Room])
def all_rooms(limit: int = 100):
    print("Запрос всех комнат...", end='')
    rooms = Room.get_all(limit)
    print(f" получено записей: {len(rooms)}.")
    return rooms


@router.get("/find", summary="Найти свободные на заданные даты комнаты")
def find_vacant_rooms(start_date: date, end_date: date, description: str = "", address: str = "", sleeps=0):
    print(f"Запрос свободных комнат на даты с {start_date} по {end_date}... ", end='')
    rooms = Room.find_availables(start_date, end_date, description, address, sleeps)
    print(f" найдено комнат: {len(rooms)}.")
    return rooms


@router.get("/{id}", summary="Получить комнату по id", response_model=Room)
def get_room(id: str):
    print(f"Запрос комнаты с id = {id}... ", end='')
    if (room := Room.get(id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Комната с  ID = {id} not не найдена")
    print(' успешно.')
    return room


@router.post("/", summary="Создать новую комнату", response_model=Room)
def create_room(room: Room = Body(...)):
    print("Создаём новую комнату...", end='')
    created_room = room.save()
    print(' успешно.')
    return created_room
