import datetime
import json
from typing import Literal

from kafka import KafkaProducer
from pydantic import create_model, BaseModel

from config import KAFKA_TOPICS_CONFIG, logger


class EventBase:
    PRODUCER: KafkaProducer = None
    TOPIC = None

    def __init__(self, user_id, event_data: dict):
        self.event_type = event_data.get('event_type')
        self.user_id = user_id
        self.timestamp = datetime.datetime.now().timestamp()
        self.event_data = event_data | {'timestamp': self.timestamp, 'user_id': self.user_id}

    @classmethod
    def _publish(cls, event_type: str, event_data: dict):
        def on_send_success(record_metadata):
            logger.info(f"sent {record_metadata.topic} {record_metadata.partition} {record_metadata.offset}")

        def on_send_error(excp):
            logger.error('I am an errback', exc_info=excp)

        message = json.dumps(event_data).encode('utf-8')
        cls.PRODUCER.send(topic=cls.TOPIC, value=message, key=event_type.encode('utf-8')).add_callback(
            on_send_success).add_errback(on_send_error)

    @classmethod
    def make_validation_model(cls, name: str, dict_def: dict):
        fields = {}
        for field_name, value in dict_def.items():
            if isinstance(value, tuple):
                fields[field_name] = value
            elif isinstance(value, dict):
                fields[field_name] = (cls.make_validation_model(f'{name}_{field_name}', value), ...)
            else:
                raise ValueError(f"Field {field_name}:{value} has invalid syntax")
        return create_model(name, **fields, __base__=BaseModel)


class PlaybackEvent(EventBase):
    TOPIC = 'playback_events'
    EVENT_KEYS = KAFKA_TOPICS_CONFIG.get(TOPIC).get('keys')
    VALIDATION_SCHEMA = EventBase.make_validation_model(
        f'{TOPIC}_schema',
        KAFKA_TOPICS_CONFIG.get(TOPIC).get('class_fields') |
        {'event_type': (Literal[tuple(KAFKA_TOPICS_CONFIG.get(TOPIC).get('keys'))], ...)})
    PRODUCER = KafkaProducer(**KAFKA_TOPICS_CONFIG[TOPIC]['producer_config'])

    def send(self):
        PlaybackEvent._publish(self.event_type, self.event_data)


class PlaylistEvent(EventBase):
    TOPIC = 'playlist_events'
    EVENT_KEYS = KAFKA_TOPICS_CONFIG.get(TOPIC).get('keys')
    VALIDATION_SCHEMA = EventBase.make_validation_model(
        f'{TOPIC}_schema',
        KAFKA_TOPICS_CONFIG.get(TOPIC).get('class_fields') |
        {'event_type': (Literal[tuple(KAFKA_TOPICS_CONFIG.get(TOPIC).get('keys'))], ...)})
    PRODUCER = KafkaProducer(**KAFKA_TOPICS_CONFIG[TOPIC]['producer_config'])

    def send(self):
        PlaylistEvent._publish(self.event_type, self.event_data)


class UserAccountEvent(EventBase):
    TOPIC = 'user_account_events'
    EVENT_KEYS = KAFKA_TOPICS_CONFIG.get(TOPIC).get('keys')
    VALIDATION_SCHEMA = EventBase.make_validation_model(
        f'{TOPIC}_schema',
        KAFKA_TOPICS_CONFIG.get(TOPIC).get('class_fields') |
        {'event_type': (Literal[tuple(KAFKA_TOPICS_CONFIG.get(TOPIC).get('keys'))], ...)})
    PRODUCER = KafkaProducer(**KAFKA_TOPICS_CONFIG[TOPIC]['producer_config'])

    def send(self):
        UserAccountEvent._publish(self.event_type, self.event_data)
