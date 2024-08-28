# Разработка распределённых приложений (семестр осень 2023)
## Проект A2 - Бронирование комнат (Air BnB)

Прототип распределённого приложения для бронирования жилья (как в AirBnB). Клиент после регистрации аккаунта ищет комнату, свободную в желаемые даты, бронирует её, комната блокируется в Redis до символической оплаты.

### Используемые технологии
- docker
- docker compose для оркестрации и запуска кластера
- mongodb как хранилище данных о пользователях и о комнатах
- elasticsearch для полнотекстового поиска свободных дат и бронирования 
- redis для блокировки комнаты на время бронирования
- python 3.11 в качестве основного языка программирования
- fastapi для rest-api приложения

### Состав кластера:
- mongodb - режим кластера, mongo01:27017, mongo02:27018, mongo03:27019 + один инициализирующий mongoinit
- elasticsearch - режим кластера, es01:9201, es02:9202, es03:9203 + kibana:5601
- redis - redis:6379
- приложение на python - app:8000 (кастомный docker-контейнер на основе bookworm python)

### Запуск кластера в docker
Перед запуском:
```
sudo sysctl -w vm.max_map_count=262144
sudo sysctl vm.overcommit_memory=1
```
Запуск:
```
docker compose up
```

### Поведение под нагрузкой
| Состояние          | Работа (чтение/запись) | Отчёт | Дополнительные комментарии|
|---|---|---|---|
| 3 контейнера Mongo | да/да | rs.status(): https://pastebin.com/RTikbku9 | Штатный режим работы кластера. Чтение: [скриншот](https://fastpic.org/view/123/2024/0301/acff4e6955725492b7c2b80f36df51b0.png.html), запись: [скриншот](https://fastpic.org/view/123/2024/0301/5599b1e453b9f9846a34782f2e69bc5c.png.html)
| 2 контейнера Mongo | да/да | rs.status(): https://pastebin.com/b2kGnMu8 | Остановлен PRIMARY-контейнер mongo01. Чтение: [скриншот](https://fastpic.org/view/123/2024/0301/685e9585e4f8c3d891cae48f82a7e862.png.html), запись: [скриншот](https://fastpic.org/view/123/2024/0301/275d9efc462ee224b4c94c9ba90ed8e1.png.html) 
| 3 контейнера ES | да/да | curl -X GET "localhost:9201/_cat/nodes?v=true&pretty": https://pastebin.com/uV5bcsGc | Штатный режим работы кластера. Чтение: [скриншот](https://fastpic.org/view/123/2024/0301/dd6735390e9cc48f0a4937b8aa3217c4.png.html), запись: [скриншот](https://fastpic.org/view/123/2024/0301/_c55263403275f28a9976909221fb23b6.png.html)
| 2 контейнера ES | да/да | curl -X GET "localhost:9201/_cat/nodes?v=true&pretty": https://pastebin.com/zwnE4p0U | Остановлен PRIMARY-контейнер es03. Чтение: [скриншот](https://fastpic.org/view/123/2024/0301/452ca130af689e309c9335ccb7001f93.png.html), запись: [скриншот](https://fastpic.org/view/123/2024/0301/_ab426f4e7e50f58bc361446546b0d4c8.png.html)

### Конфигурация rest-api приложения
Переменные окружения передаются в контейнер app с помощью docker-compose.yml
|Переменная|Назначение|
|--------|-----------------------------------|
|MONGO_URI|строка подключения к mongodb|
|DB_NAME|используемая база данных mongodb|
|ELASTICSEARCH_URI|строка подключения к elasticsearch|
|REDIS_URI|строка подключения к redis|
|USER_PARSER_PATH|путь к Users.xml|
|USER_DATA_PATH|путь к Users.сsv|
|ROOM_DATA_PATH|путь к tomslee_airbnb_auckland_0534_2016-08-19.csv|

### Сценарии использования
- получить всех пользователей
- создать нового пользователя
- получить пользователя по id
- получить список всех комнат
- создать новую комнату
- найти свободные на заданные даты комнаты
- получить список всех бронирований
- забронировать комнату
- получить бронирование по id
