from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from typing import List
from datetime import date
from .Booking import Booking

router = APIRouter()


@router.get("/", summary="Список всех бронирований", response_model=List[Booking])
def all(limit: int = 100):
    bookings = Booking.get_all(limit)
    return bookings


@router.get("/{id}", summary="Получить бронирование по id", response_model=Booking)
def get(id: str):
    if (booking := Booking.get(id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Бронирование с ID = {id} не найдено")
    return booking


@router.post("/", summary="Забронировать комнату",
             description="Пытаемся забронировать для пользователя комнату в указанный период", response_model=Booking)
def create(user_id: str, room_id: str, start_date: date, end_date: date):
    print(f"Пытаемся забронировать комнату {room_id} для пользователя {user_id} с {start_date} по {end_date}",
          end='...')
    booking = Booking(user_id=user_id, room_id=room_id, start_date=start_date, end_date=end_date)
    booking.save()
    print(' успешно.')

    return booking
