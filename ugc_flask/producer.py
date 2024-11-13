import json

from kafka import KafkaProducer

from settings import BOOTSTRAP_SERVERS


producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


def send_message_to_kafka(topic: str, body: dict):
    producer.send(
        topic,
        value=body,
        partition=None,
    )
