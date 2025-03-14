from fastapi import APIRouter
from fastapi.responses import Response

from events.events import PlaybackEvent, PlaylistEvent, UserAccountEvent

router = APIRouter(prefix='/events', tags=['Events'])


@router.post('/playback')
async def post_playback_event(user_id: int, event_data: PlaybackEvent.VALIDATION_SCHEMA):
    """Отправка события проигрывателя"""
    PlaybackEvent(user_id, event_data.dict()).send()
    return Response(status_code=200)


@router.post('/playlist')
async def post_playlist_event(user_id: int, event_data: PlaylistEvent.VALIDATION_SCHEMA):
    """Отправка события плейлиста"""
    PlaylistEvent(user_id, event_data.dict()).send()
    return Response(status_code=200)


@router.post('/user')
async def post_user_account_event(user_id: int, event_data: UserAccountEvent.VALIDATION_SCHEMA):
    """Отправка события аккаунта пользователя"""
    UserAccountEvent(user_id, event_data.dict()).send()
    return Response(status_code=200)
