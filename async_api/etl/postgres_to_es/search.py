import json
from pprint import pprint

from elasticsearch import Elasticsearch

from settings import settings


class Search:
    def __init__(self):
        self.es = Elasticsearch(
            hosts=settings.es_settings.elasticsearch_host
        )
        client_info = self.es.info()
        print('Выполнено подключение к Elasticsearch.')
        pprint(client_info.body)

    def create_index(self, index_name, settings, mappings):
        self.es.indices.delete(index=index_name, ignore_unavailable=True)
        self.es.indices.create(
            index=index_name,
            settings=settings,
            mappings=mappings
        )

    def get_index_information(self, index_name):
        index_info = self.es.indices.get(index=index_name)

    def insert_document(self, index_name, document, id):
        response = self.es.index(index=index_name, body=document, id=id)

    def insert_documents(self, index_name, documents):
        operations = []
        for document in documents:
            operations.append({
                'index': {
                    '_index': f'{index_name}',
                    '_id': document['id']
                }
            })
            operations.append(document)
        return self.es.bulk(operations=operations)

    def reindex(self, index_name, file_path_to_json_file):
        self.create_index(index_name=index_name)
        with open(f'{file_path_to_json_file}', 'rt') as f:
            documents = json.loads(f.read())
        return self.insert_documents(
            index_name=index_name,
            documents=documents
        )
