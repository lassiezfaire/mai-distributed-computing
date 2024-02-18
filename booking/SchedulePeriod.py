from datetime import date, datetime
from Databases.esRepository import es_client as es_schedule

'''
Класс SchedulePeriod используется для хранения в ElasticSearch информации о периодах занятости или доступности комнаты.

Каждый экземпляр класса является документом в индексе INDEX_NAME,
который содержит информацию об id комнаты (ссылка на MongoDB.Room), 
начальной и конечной дате периода, id бронирования (ссылка на MongoDB.Booking) 
Если свойство id бронирования является пустым, то это период, когда комната свободна

При появлении в системе новой комнаты для неё создаётся свободный период
 с start_date = date.min() и end_date = date.max(), что означает что комната свободна в любой день.

При создании бронирования тот период доступности, на который приходится период бронирования, удаляется из индекса, 
и вместо него сохраняются три периода: доступный "до" созданного бронирования, занятый на время бронирования и 
доступный "после" бронирования Занятый период, хотя и не используется для определения доступности комнаты, 
в перспективе потребуется для функционала отмены брони'''


class SchedulePeriod:
    id: str | None = None
    room_id: str
    start_date: str
    end_date: str
    booking_id: str = ''
    INDEX_NAME = 'schedule'

    def __init__(self, room_id='', start_date=date.min, end_date=date.max, booking_id='', elasticsearch_doc=None):
        if elasticsearch_doc is not None:  # Заполняем свойства значениями из документа ElasticSearch
            self.id = elasticsearch_doc['_id']
            self.room_id = elasticsearch_doc['_source']['room_id']
            self.start_date = datetime.strptime(elasticsearch_doc['_source']['start_date'][0:10], '%Y-%m-%d').date()
            self.end_date = datetime.strptime(elasticsearch_doc['_source']['end_date'][0:10], '%Y-%m-%d').date()
            self.booking_id = elasticsearch_doc['_source']['booking_id']
        else:  # Иначе заполняем свойства из параметров конструктора
            self.id = None
            self.room_id = room_id
            self.start_date = start_date
            self.end_date = end_date
            self.booking_id = booking_id

    def save(self):
        es_doc = {
            'room_id': self.room_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'booking_id': self.booking_id,
        }
        es_schedule.index(index=self.INDEX_NAME, document=es_doc, id=self.id)

    def __str__(self):
        return "Период: комната " + self.room_id + " c " + self.start_date.__str__() + " по " + self.end_date.__str__()

    def parse_es_doc(self, es_doc):
        self.id = es_doc['_id']
        self.room_id = es_doc['_source']['room_id']
        self.start_date = es_doc['_source']['start_date']
        self.end_date = es_doc['_source']['end_date']
        self.booking_id = es_doc['_source']['booking_id']

    def delete(self):
        try:
            es_schedule.delete(index=self.INDEX_NAME, id=self.id)
        except Exception as ex:
            print(__name__, ': 69, id=', self.id, ex)

    @classmethod
    def find_available_rooms_ids(cls, start_date, end_date):
        query = {"bool": {
            "must": [
                {"range": {"start_date": {"lte": start_date.__str__()}}},
                {"range": {"end_date": {"gte": end_date.__str__()}}},
                {"term": {"booking_id": ""}}
            ]
        }}
        results = es_schedule.search(index=cls.INDEX_NAME, query=query)
        rooms = []
        for result in results['hits']['hits']:
            rooms.append(result['_source']["room_id"])
        return rooms

    @classmethod
    def get_vacant_period(cls, room_id: str, start_date: date, end_date: date):
        # возвращает id свободного периода для данной комнаты, в который помещается указанный диапазон дат
        query = {
            "bool": {
                "must": [
                    {"range": {"start_date": {"lte": start_date.__str__()}}},
                    {"range": {"end_date": {"gte": end_date.__str__()}}},
                    {"term": {"room_id": room_id}},
                    {"term": {"booking_id": ""}}
                ]
            }
        }
        result = es_schedule.search(index=cls.INDEX_NAME, query=query)
        if result['hits']['total']['value'] == 0:
            return None
        period = SchedulePeriod(elasticsearch_doc=result['hits']['hits'][0])
        return period

    @classmethod
    def refresh_index(cls):
        # Ожидает, пока elasticsearch выполнит все обновления индекса. Без него изменение индекса становится видным
        # только через некоторое время после обновления
        es_schedule.indices.refresh(index=cls.INDEX_NAME)
