from datetime import date
from typing import ClassVar

from pydantic import BaseModel, Field

from Booking.SchedulePeriod import SchedulePeriod
from Databases.esRepository import es_client
from Databases.mongoRepository import MongoRepository


class Address(BaseModel):
    address: str = Field(...)
    city: str
    country: str


class Room(MongoRepository):
    full_address: Address = Field(...)
    name: str = Field(...)  # Название
    description: str | None = Field(...)  # Описание (участвует в полнотекстовом поиске)
    sleeps: int = Field(...)  # Количество мест
    es_index_name: ClassVar[str] = 'rooms'

    def save(self):
        self.id = self.name  # DEBUG
        save_result = super().save()
        es_client.index(index=self.es_index_name, id=self.id, document=self.model_dump(exclude=['id']))
        if save_result.upserted_id is not None:
            # для вновь созданных комнат создаём в графике (ElasticSearch) незанятый интервал...
            booking_period = SchedulePeriod(room_id=save_result.upserted_id)
            booking_period.save()

    @classmethod
    def find_availables(cls, start_date: date, end_date: date, description='', address='', sleeps=0) -> list:
        vacant_ids = SchedulePeriod.find_available_rooms_ids(start_date, end_date)
        conditions = [{"ids": {"values": vacant_ids}}]
        if description != '':  # поиск в поле description
            conditions.append({"match": {"description": description}})
        if address != '':  # поиск в полях адреса
            conditions.append({"multi_match": {
                "query": address,
                "fields": ["full_address.address", "full_address.city", "full_address.country"],
                "type": "most_fields"
            }})
        if int(sleeps) > 0:  # отбор комнат по количеству мест
            conditions.append({"range": {"sleeps": {"gte": sleeps}}})
        query = {
            "bool": {"must": conditions}
        }
        es_result = es_client.search(index=cls.es_index_name, query=query)
        room_ids = []
        for room in es_result['hits']['hits']:
            room_ids.append(room['_id'])
        rooms = cls.get_by_ids(room_ids)
        return rooms
