import random
import time
from datetime import date, timedelta

from booking.booking import Booking
from booking.schedule_period import SchedulePeriod, es_schedule
from databases.mongo_repository import mongo_database
from room.room import Room, Address
from user.user import User


# Создаём базу данных, удаляя предыдущие данные, если они были
def create_database():
    mongo_collections = mongo_database.list_collection_names()
    for collection in ["Room", "User", "Booking"]:
        if collection in mongo_collections:
            mongo_database.drop_collection(collection)
    if es_schedule.indices.exists(index=SchedulePeriod.INDEX_NAME):
        es_schedule.indices.delete(index=SchedulePeriod.INDEX_NAME)
        mapping = {
            "properties": {
                "room_id": {"type": "keyword", "ignore_above": 36},
                "booking_id": {"type": "keyword", "ignore_above": 36},
                "start_date": {"type": "date",
                               "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"},
                "end_date": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"}
            }
        }
        es_schedule.indices.create(index=SchedulePeriod.INDEX_NAME, mappings=mapping)
        time.sleep(1)


def seed_users():
    names = ["Вася", "Петя", "Федя"]
    for name in names:
        user = User(name=name)
        user.save()


def seed_rooms():
    rooms = [
        {
            "name": "small",
            "description": "Маленькая уютная комната",
            "full_address": {"address": "Красная площадь, 1", "city": "Москва", "country": "Россия"},
            "attributes": ["Холодильник", "Телевизор"],
            "sleeps": 1
        },
        {
            "name": "middle",
            "description": "Комната на двоих",
            "full_address": {"address": "Тверская улица, 3", "city": "Москва", "country": "Россия"},
            "attributes": ["Холодильник", "Телевизор"],
            "sleeps": 2
        },
        {
            "name": "big",
            "description": "Просторная комната на троих",
            "full_address": {"address": "Тверская улица, 3", "city": "Москва", "country": "Россия"},
            "attributes": ["Холодильник", "Телевизор"],
            "sleeps": 3
        },
        {
            "name": "nice",
            "description": "Очень милая комната с дизайнерским ремонтом",
            "full_address": {"address": "Тверская улица, 3", "city": "Москва", "country": "Россия"},
            "attributes": ["Холодильник", "Телевизор", "Вид из окна"],
            "sleeps": 2
        },
    ]

    for room in rooms:
        room["full_address"] = Address(**room["full_address"])
        room = Room(**room)
        room.save()


def book_room(user_id, start_date, end_date, room_id=None):
    if room_id is None:
        room_ids = SchedulePeriod.find_available_rooms_ids(start_date, end_date)
        if len(room_ids) == 0:
            print(f"Не найдены свободные комнаты на период c {start_date} до {end_date}")
            return
        room_id = room_ids[0]
    booking = Booking(user_id=user_id, room_id=room_id, start_date=start_date, end_date=end_date)
    booking.save()
    room = Room.get(room_id)
    print(f"Создано бронирование для комнаты {booking.room_id} на период с {booking.start_date} до {booking.end_date}")


init = 1
if init == 1:
    create_database()
    SchedulePeriod.refresh_index()
    seed_rooms()
    seed_users()
    # SchedulePeriod.refresh_index()
    print("Базы данных инициализированы")
#    exit(0)
for _ in range(100):
    user = User.get_random()
    start_date = date(2024, random.randint(1, 12), random.randint(1, 28))
    end_date = start_date + timedelta(days=random.randint(1, 7))
    try:
        book_room(user.id, start_date, end_date)
    except Exception as ex:
        print(ex)
