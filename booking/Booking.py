from datetime import datetime, timedelta
from enum import Enum

from fastapi import HTTPException, status
from pydantic import Field

from Booking.SchedulePeriod import SchedulePeriod
from Databases.mongoRepository import MongoRepository
from Databases.redisRepository import redlock_client
from Room.Room import Room
from User.User import User


class BookingStatus(str, Enum):
    DEFAULT = "DEFAULT"  # Ожидает оплаты
    RESERVED = "RESERVED"  # Забронирован без оплаты
    PAID = "PAID"  # Забронирован и оплачен


class Booking(MongoRepository):
    room_id: str
    user_id: str
    start_date: datetime
    end_date: datetime
    status: BookingStatus = Field(default='DEFAULT')

    def __str__(self):
        return "Бронирование: комната " + self.room_id + " c " + self.start_date.__str__() + " по " + self.end_date.__str__()

    def save(self):
        if User.get(self.user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"При попытке создания брони не удалось найти пользователя с Id = {self.room_id}")
        if Room.get(self.room_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"При попытке создания брони не удалось найти комнату с Id = {self.room_id}")

        tries = 4
        while --tries > 0:
            period = SchedulePeriod.get_vacant_period(self.room_id, self.start_date, self.end_date)
            if period is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"При попытке создания брони не удалось найти свободный период на указанные "
                                           f"даты")
            locked = redlock_client.lock(period.id, 1000)
            if locked:
                break
        super().save()
        one_day = timedelta(days=1)
        if period.start_date != self.start_date:
            previous_vacant_period = SchedulePeriod(room_id=self.room_id, start_date=period.start_date,
                                                    end_date=self.start_date - one_day)
            previous_vacant_period.save()
        booked_period = SchedulePeriod(room_id=self.room_id, start_date=self.start_date, end_date=self.end_date,
                                       booking_id=self.id)
        booked_period.save()
        if self.end_date != period.end_date:
            subsequent_vacant_period = SchedulePeriod(room_id=self.room_id, start_date=self.end_date + one_day,
                                                      end_date=period.end_date)
            subsequent_vacant_period.save()
        period.delete()
        SchedulePeriod.refresh_index()
        redlock_client.unlock(locked)
