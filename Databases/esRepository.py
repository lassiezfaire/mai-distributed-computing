from elasticsearch import Elasticsearch
from dotenv import dotenv_values

# Глобальная переменная для подключения к ElasticSearch
config = dotenv_values('.env')
global es_client
es_client = Elasticsearch([config['ELASTICSEARCH_URI']])
