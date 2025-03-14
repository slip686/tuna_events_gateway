import logging
import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST') or '127.0.0.1'
PORT = int(os.getenv('PORT') or 3040)

LOG_FORMAT = '[%(levelname) -3s %(asctime)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

KAFKA_HOST = os.getenv('KAFKA_HOST') or '127.0.0.1'
KAFKA_PORT = int(os.getenv('KAFKA_PORT') or 9092)
KAFKA_BOOTSTRAP_SERVERS = [f'{KAFKA_HOST}:{KAFKA_PORT}']
KAFKA_TOPIC_COMMON_CONFIG = {
    'num_partitions': 3,
    'replication_factor': 3,
    'topic_configs': {'cleanup.policy': 'delete',
                      'retention.ms': '86400000',
                      'min.insync.replicas': '2'}
}
KAFKA_PRODUCER_COMMON_CONFIG = {'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS,
                                'retries': 5,
                                'batch_size': 100,
                                'linger_ms': 50}

TRACK_FIELDS = {'track_id': (int, ...),
                'track_year': (int, ...),
                'track_name': (str, ...),
                'track_genres': (List[str], ...),
                'artists_names': (List[str], ...),
                'album_name': (str, ...),
                'album_id': (int, ...),
                'track_duration': (int, ...),
                'track_elapsed_duration': (int, ...)}
PLAYLIST_FIELDS = {'playlist_id': (int, ...),
                   'playlist_name': (str, ...),
                   'owner_id': (int, ...),
                   'tracks_count': (int, ...),
                   'tracks': (List[int], ...)}
USER_ACCOUNT_FIELDS = {'user_name': (str, ...),
                       'user_gender': (str, ...),
                       'user_age': (int, ...),
                       'user_subscribed': (bool, ...)}

KAFKA_TOPICS_CONFIG = {
    'playback_events': {
        'keys': ['play', 'pause', 'next', 'previous', 'repeat_one_on',
                 'repeat_one_off', 'like', 'unlike'],
        'producer_config': KAFKA_PRODUCER_COMMON_CONFIG,
        'topic_config': KAFKA_TOPIC_COMMON_CONFIG,
        'class_fields': TRACK_FIELDS | USER_ACCOUNT_FIELDS
    },
    'playlist_events': {
        'keys': ['post', 'delete', 'add_track', 'remove_track', 'like', 'unlike', 'shuffle_on', 'shuffle_off',
                 'repeat_on', 'repeat_off'],
        'producer_config': KAFKA_PRODUCER_COMMON_CONFIG,
        'topic_config': KAFKA_TOPIC_COMMON_CONFIG,
        'class_fields': PLAYLIST_FIELDS | USER_ACCOUNT_FIELDS
    },
    'user_account_events': {
        'keys': ['login', 'logout', 'sign_up', 'change_password', 'subscribe', 'unsubscribe'],
        'producer_config': KAFKA_PRODUCER_COMMON_CONFIG,
        'topic_config': KAFKA_TOPIC_COMMON_CONFIG,
        'class_fields': USER_ACCOUNT_FIELDS
    }
}
