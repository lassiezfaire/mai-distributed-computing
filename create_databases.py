from Databases.mongoRepository import mongo_database
from Booking.SchedulePeriod import es_schedule


def create_database():
    collections = mongo_database.list_collections()
    if 'User' in collections:
        mongo_database.drop_collection('User')
    if 'Room' in collections:
        mongo_database.drop_collection('Room')
    if 'Booing' in collections:
        mongo_database.drop_collection('Booking')

    if es_schedule.es_database.indices.exists(index=es_schedule.INDEX_NAME):
        es_schedule.es_database.indices.delete(index=es_schedule.INDEX_NAME)
    es_schedule.es_database.indices.create(index=es_schedule.INDEX_NAME, mappings={"properties": {
        "booking_id": {"type": "keyword"},
        "user_id": {"type": "keyword"},
        "room_id": {"type": "keyword"},
        "start_date": {"type": "date"},
        "end_date": {"type": "date"}
    }})
