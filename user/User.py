from pydantic import Field

from Databases.mongoRepository import MongoRepository


class User(MongoRepository):
    name: str = Field(...)
