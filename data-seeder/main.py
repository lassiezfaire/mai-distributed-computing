import asyncio
import csv
from typing import List
import motor.motor_asyncio

from validator.users import *
from validator.rooms import *


def read_user_data(file_path: str) -> List[User]:
    data = []
    with open(file_path, mode='r', encoding='utf-8') as user_csv:
        csv_reader = csv.DictReader(user_csv)
        for row in csv_reader:
            user = User(id=int(row['Id']),
                        name=row['DisplayName'])
            data.append(user)
    return data


def read_room_data(file_path: str) -> List[Room]:
    data = []
    with open(file_path, mode='r', encoding='utf-8') as room_csv:
        csv_reader = csv.DictReader(room_csv)
        for row in csv_reader:
            address = Address(country='Denmark',
                              city='Aarhus',
                              address=row['neighborhood'])
            room = Room(id=int(row['room_id']),
                        full_address=address,
                        description=row['room_type'],
                        attributes='Number of reviews: ' + row['reviews'])
            data.append(room)
    return data


async def insert_user_data_mongodb(data: List[User]):
    await collection.insert_many([user.model_dump() for user in data])


async def insert_room_data_mongodb(data: List[Room]):
    await collection.insert_many([room.model_dump() for room in data])


client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://192.168.1.96:27017/')
db = client['booking_project_bd']
collection = db['user']

user_data_path = 'data/Users.csv'
data = read_user_data(user_data_path)

# Для асинхронной работы с MongoDB вам нужно будет использовать event loop
asyncio.get_event_loop().run_until_complete(insert_user_data_mongodb(data))

collection = db['room']

room_data_path = 'data/tomslee_airbnb_auckland_0534_2016-08-19.csv'
data = read_room_data(room_data_path)

asyncio.get_event_loop().run_until_complete(insert_room_data_mongodb(data))