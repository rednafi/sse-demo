from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING, AsyncGenerator

from celery import Celery
from celery.result import AsyncResult
from starlette.applications import Starlette
from starlette.responses import StreamingResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response

logging.basicConfig(level=logging.INFO)


templates = Jinja2Templates(directory="./")

celery_app = Celery("tasks", backend="redis://", broker="redis://")


@celery_app.task()
def background() -> str:
    time.sleep(5)
    return "Hello from background task..."


async def index(request: Request) -> Response:
    task_id = background.apply_async(queue="default")
    logging.info("Task id: %s", task_id)
    response = templates.TemplateResponse("index.html", {"request": request})
    response.set_cookie("task_id", task_id)
    return response


async def task_status(request: Request) -> StreamingResponse:
    task_id = request.path_params["task_id"]

    async def stream() -> AsyncGenerator[str, None]:
        task = AsyncResult(task_id, app=celery_app)
        logging.info("Task state: %s", task.state)
        attempt = 0
        while True:
            data = {
                "state": task.state,
                "result": task.result,
            }
            logging.info("Server sending data: %s", data)

            yield f"data: {json.dumps(data)}\n\n"
            attempt += 1

            if data.get("state") == "SUCCESS":
                break

            if attempt > 10:
                data["state"] = "UNFINISHED"
                data["result"] = "Task is taking too long to complete."
                yield f"data: {json.dumps(data)}\n\n"
                break

            time.sleep(1)

    response = StreamingResponse(
        stream(),
        headers={
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
        },
    )
    return response


routes = [
    Route("/index", endpoint=index),
    Route("/task_status/{task_id}", endpoint=task_status),
]

# Add session middleware
app = Starlette(debug=True, routes=routes)
