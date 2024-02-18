from pydantic import BaseModel, Field, validator
from Databases.mongoRepository import MongoRepository


class User(MongoRepository):
    name: str = Field(...)
