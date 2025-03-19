import datetime
import json
from typing import Literal, Type

from kafka import KafkaProducer
from pydantic import create_model, BaseModel

from config import KAFKA_TOPICS_CONFIG, logger


class EventBase:
    """
    Events fabric based on config.py
    To create new event class use EventBase.make_event:
    """
    TOPIC = None
    PRODUCER: KafkaProducer = None
    VALIDATION_SCHEMA: Type[BaseModel] = None

    def __init__(self, user_id: int, event_data: dict):
        self.event_type = event_data.get('event_type')
        self.user_id = user_id
        self.event_data = event_data | {'timestamp': datetime.datetime.now().isoformat(),
                                        'user_id': self.user_id,
                                        'event_type': self.event_type}

    @classmethod
    def _publish(cls, event_type: str, event_data: dict) -> None:
        def on_send_success(record_metadata):
            logger.info(f"sent {record_metadata.topic} {record_metadata.partition} {record_metadata.offset}")

        def on_send_error(excp):
            logger.error('SEND ERROR', exc_info=excp)

        message = json.dumps(event_data).encode('utf-8')
        cls.PRODUCER.send(topic=cls.TOPIC, value=message, key=event_type.encode('utf-8')).add_callback(
            on_send_success).add_errback(on_send_error)

    def send(self) -> None:
        self.__class__._publish(self.event_type, self.event_data)

    @classmethod
    def _make_validation_model(cls, name: str, dict_def: dict) -> Type[BaseModel]:
        fields = {}
        for field_name, value in dict_def.items():
            if isinstance(value, tuple):
                fields[field_name] = value
            elif isinstance(value, dict):
                fields[field_name] = (cls._make_validation_model(f'{name}_{field_name}', value), ...)
            else:
                raise ValueError(f"Field {field_name}:{value} has invalid syntax")
        return create_model(name, **fields)

    @classmethod
    def make_event(cls, name: str, topic: str) -> Type:
        """
        Create new event class inherited from EventBase
        :param name: Event class name
        :param topic: Topic name from config.KAFKA_TOPICS_CONFIG
        :return: Event class
        """
        return type(
            f'{name}',
            (cls,),
            {'TOPIC': topic,
             'EVENT_KEYS': KAFKA_TOPICS_CONFIG.get(topic).get('keys'),
             'VALIDATION_SCHEMA': cls._make_validation_model(
                 f'{topic}_schema',
                 KAFKA_TOPICS_CONFIG.get(topic).get('class_fields') |
                 {'event_type': (
                     Literal[tuple(KAFKA_TOPICS_CONFIG.get(topic).get('keys'))], ...)}
             ),
             'PRODUCER': KafkaProducer(**KAFKA_TOPICS_CONFIG[topic]['producer_config'])
             })


PlaybackEvent = EventBase.make_event('PlaybackEvent', 'playback_events')

PlaylistEvent = EventBase.make_event('PlaylistEvent', 'playlist_events')

UserAccountEvent = EventBase.make_event('UserAccountEvent', 'user_account_events')
