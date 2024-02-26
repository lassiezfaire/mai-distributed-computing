from pydantic import Field, BaseModel

from databases.mongo_repository import MongoRepository


class User(MongoRepository):
    name: str = Field(...)


class UserUpdate(BaseModel):
    name: str