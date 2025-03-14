import importlib

from fastapi import FastAPI
from kafka.admin import KafkaAdminClient, NewTopic
from pydantic import create_model

from config import KAFKA_HOST, KAFKA_PORT, KAFKA_TOPICS_CONFIG, KAFKA_TOPIC_COMMON_CONFIG


def create_topics():
    admin_client = KafkaAdminClient(bootstrap_servers=[f'{KAFKA_HOST}:{KAFKA_PORT}'], client_id='admin')

    existing_topics = set(admin_client.list_topics())
    topic_names = set(list(KAFKA_TOPICS_CONFIG.keys())).difference(existing_topics)

    topics = [NewTopic(**{'name': topic} | KAFKA_TOPICS_CONFIG[topic].get('topic_config', KAFKA_TOPIC_COMMON_CONFIG))
              for topic in topic_names]
    admin_client.create_topics(topics, timeout_ms=1000, validate_only=False)


def connect_routers(app: FastAPI, routers: __import__):
    for mod in routers.__loader__.get_resource_reader().contents():
        name = mod.split('.py')[0]
        if name not in ['__init__', '__pycache__']:
            cls = getattr(importlib.import_module(f'routers.{name}'), 'router')
            app.include_router(cls)


# def make_validation_model(name: str, dict_def: dict):
#     fields = {}
#     for field_name, value in dict_def.items():
#         if isinstance(value, tuple):
#             fields[field_name] = value
#         elif isinstance(value, dict):
#             fields[field_name] = (make_validation_model(f'{name}_{field_name}', value), ...)
#         else:
#             raise ValueError(f"Field {field_name}:{value} has invalid syntax")
#     return create_model(name, **fields)
