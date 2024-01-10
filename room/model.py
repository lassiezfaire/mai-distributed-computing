from typing_extensions import TypedDict
from pydantic import BaseModel


class Address(TypedDict, total=False):
    address: str
    city: str
    country: str


class Room(BaseModel):
    id: int
    full_address: Address
    description: str
    attributes: str
