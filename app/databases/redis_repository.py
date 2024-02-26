import os

from redlock import Redlock
# from dotenv import dotenv_values

# config = dotenv_values('../.env')
redis_uri = os.environ.get('REDIS_URI')
redis_host = str(redis_uri.split(':')[0])
redis_port = str(redis_uri.split(':')[1])
redlock_client = Redlock([{"host": redis_host, "port": redis_port, "db": 0}])
