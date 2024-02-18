from Room.Room import Room
from datetime import date

rooms = Room.find_availables(start_date=date(2024, 1, 1), end_date=date(2024, 1, 6))
print(rooms)
