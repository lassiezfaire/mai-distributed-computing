from datetime import date, timedelta
import time
import csv
import random
import os
import xml.etree.ElementTree as et

# from dotenv import dotenv_values

from booking.booking import Booking
from booking.schedule_period import SchedulePeriod, es_schedule
from databases.mongo_repository import mongo_database
from room.room import Room, Address
from user.user import User


# Создаём базу данных, удаляя предыдущие данные, если они были
def init_database():
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


def data_parser(user_parser_path, user_data_path):
    input_path = user_parser_path
    output_path = user_data_path

    # Открываем исходный XML-файл
    tree = et.parse(input_path)
    root = tree.getroot()

    # Открываем CSV-файл для записи
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        # Создаем объект writer
        fieldnames = ["Id", "Reputation", "CreationDate", "DisplayName", "LastAccessDate", "WebsiteUrl", "Location",
                      "AboutMe", "Views", "UpVotes", "DownVotes", "AccountId"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Записываем заголовки столбцов
        writer.writeheader()

        # Парсим XML и записываем данные в CSV
        for row in root.findall('row'):
            data = {
                "Id": row.get('Id'),
                "Reputation": row.get('Reputation'),
                "CreationDate": row.get('CreationDate'),
                "DisplayName": row.get('DisplayName'),
                "LastAccessDate": row.get('LastAccessDate'),
                "WebsiteUrl": row.get('WebsiteUrl'),
                "Location": row.get('Location'),
                # "AboutMe": row.get('AboutMe'),
                "Views": row.get('Views'),
                "UpVotes": row.get('UpVotes'),
                "DownVotes": row.get('DownVotes'),
                "AccountId": row.get('AccountId')
            }
            writer.writerow(data)


def seed_users(user_data_path):
    with open(user_data_path, mode='r', encoding='utf-8') as user_csv:
        csv_reader = csv.DictReader(user_csv)
        for row in csv_reader:
            user = User(name=row['DisplayName'])
            user.save()


# def seed_all_users():
#     my_client = MongoClient(config["MONGO_URI"])
#     db = my_client[config["DB_NAME"]]
#     collection = db["User"]
#
#     user_data_path = config['USER_DATA_PATH']
#     data = []
#     with open(user_data_path, mode='r', encoding='utf-8') as user_csv:
#         csv_reader = csv.DictReader(user_csv)
#         for row in csv_reader:
#             user = {
#                 'name': row['DisplayName']
#             }
#             data.append(user)
#         collection.insert_many(data)


def seed_rooms(room_data_path):
    with open(room_data_path, mode='r', encoding='utf-8') as room_csv:
        csv_reader = csv.DictReader(room_csv)
        for row in csv_reader:
            if isinstance(row['bedrooms'], int):
                sleeps = row['bedrooms']
            else:
                sleeps = 1
            room = Room(full_address=Address(address=row['neighborhood'],
                                             city='Aarhus',
                                             country='Denmark'),
                        description=row['room_type'],
                        sleeps=sleeps)
            room.save()


# def seed_all_rooms():
#     my_client = MongoClient(config["MONGO_URI"])
#     db = my_client[config["DB_NAME"]]
#     collection = db["Room"]
#
#     room_data_path = config['ROOM_DATA_PATH']
#     data = []
#     with open(room_data_path, mode='r', encoding='utf-8') as room_csv:
#         csv_reader = csv.DictReader(room_csv)
#         for row in csv_reader:
#             if isinstance(row['bedrooms'], int):
#                 sleeps = row['bedrooms']
#             else:
#                 sleeps = 1
#             room = {
#                 'full_address': {
#                     'address': row['neighborhood'],
#                     'city': 'Aarhus',
#                     'country': 'Denmark'
#                 },
#                 'description': row['room_type'],
#                 'sleeps': sleeps
#             }
#             data.append(room)
#         collection.insert_many(data)


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


# config = dotenv_values('data.env')
user_parser_path = os.environ.get('USER_PARSER_PATH')
user_data_path = os.environ.get('USER_DATA_PATH')
room_data_path = os.environ.get('ROOM_DATA_PATH')

data_parser(user_parser_path, user_data_path)

init = 1
if init == 1:
    init_database()
    SchedulePeriod.refresh_index()
    seed_users(user_data_path)
    seed_rooms(room_data_path)
    # SchedulePeriod.refresh_index()
    print("Базы данных инициализированы")
for _ in range(1000):
    user = User.get_random()
    start_date = date(2024, random.randint(1, 12), random.randint(1, 28))
    end_date = start_date + timedelta(days=random.randint(1, 7))
    try:
        book_room(user.id, start_date, end_date)
    except Exception as ex:
        print(ex)
