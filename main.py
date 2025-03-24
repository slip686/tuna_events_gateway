import sentry_sdk
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

from config import HOST, PORT
from utils import create_topics, connect_routers
import routers

sentry_sdk.init(
    dsn="https://61f234e115e13cf5f11a1c92185bc696@o4509033998909440.ingest.de.sentry.io/4509034287792208",
    send_default_pii=True,
)

app = FastAPI(root_path='/events_gateway', docs_url='/docs', title='Шлюз событий',
              description='Сервис для публикации событий',
              swagger_ui_parameters={"docExpansion": "none", "defaultModelsExpandDepth": -1})


connect_routers(app, routers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc):
    return PlainTextResponse(str(exc), status_code=400)


if __name__ == "__main__":
    create_topics()
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False, workers=3)
