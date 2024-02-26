import os
import uuid

# from dotenv import dotenv_values
from pydantic import BaseModel, Field
from pymongo import MongoClient

global mongo_database

# Подключение к MongoDB, определённое глобально
# config = dotenv_values('../.env')
mongo_client = MongoClient(os.environ.get("MONGO_URI"))
mongo_database = mongo_client[os.environ["DB_NAME"]]

print(mongo_database)

'''
Базовый класс для сохранения и получения объектов в/из MongoDB
'''


class MongoRepository(BaseModel):
    id: str = Field(alias="_id", default_factory=lambda: uuid.uuid4().__str__())

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @classmethod
    def collection_name(cls):
        return cls.__name__

    def save(self):
        collection = self.collection_name()
        return mongo_database[collection].update_one({'_id': self.id}, {"$set": self.model_dump(exclude='id')}, upsert=True)

    # return mongo_database[collection].update_one({'_id': self.id}, {"$set": jsonable_encoder(self)}, upsert=True)

    @classmethod
    def get_all(cls, limit=100):
        collection = cls.collection_name()
        items = list(mongo_database[collection].find(limit=limit))
        return items

    @classmethod
    def get(cls, id: str):
        collection = cls.collection_name()
        item = mongo_database[collection].find_one({"_id": id})
        if not item:
            return None
        return cls.model_validate(item)

    @classmethod
    def get_random(cls):
        collection = cls.collection_name()
        pipeline = [{'$sample': {'size': 1}}]
        items = list(mongo_database[collection].aggregate(pipeline))
        if not items:
            return None
        return cls.model_validate(items[0])

    @classmethod
    def get_by_ids(cls, ids: list) -> list:
        query = {"_id": {"$in": ids}}
        collection = cls.collection_name()
        items = mongo_database[collection].find(query)
        return list(items)
