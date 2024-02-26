import os

from elasticsearch import Elasticsearch
# from dotenv import dotenv_values

# Глобальная переменная для подключения к ElasticSearch
# config = dotenv_values('../.env')
global es_client
es_connection_string = os.environ.get('ELASTICSEARCH_URI')
es_nodes = es_connection_string.split(',')
es_client = Elasticsearch(es_nodes)
