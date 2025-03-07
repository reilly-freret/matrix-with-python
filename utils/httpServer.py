from typing import Callable
from fastapi import FastAPI, APIRouter
import uvicorn
import threading
from pydantic import BaseModel

from utils.logging import get_logger


class BrightnessRequest(BaseModel):
    brightness: int


logger = get_logger("fastapi")


def health():
    logger.info("/health")
    return {"status": "healthy"}


class HTTP_SERVER:
    def __init__(
        self,
        next_app: Callable,
        prev_app: Callable,
        page_up: Callable,
        page_down: Callable,
        matrix_wrapper,
    ):
        self.next_app = next_app
        self.prev_app = prev_app
        self.page_up = page_up
        self.page_down = page_down
        self.matrix_wrapper = matrix_wrapper

        self.router = APIRouter()
        self.__add_routes__()
        self.app = FastAPI()
        self.app.include_router(self.router)

    def __add_routes__(self):
        self.router.add_api_route("/health", health, methods=["GET"])
        self.router.add_api_route("/next_app", self.route_next_app, methods=["POST"])
        self.router.add_api_route("/prev_app", self.route_prev_app, methods=["POST"])
        self.router.add_api_route("/page_up", self.route_page_up, methods=["POST"])
        self.router.add_api_route("/page_down", self.route_page_down, methods=["POST"])
        self.router.add_api_route(
            "/set_brightness", self.route_set_brightness, methods=["POST"]
        )
        self.router.add_api_route("/get_state", self.route_get_state, methods=["GET"])

    def route_set_brightness(self, request: BrightnessRequest):
        logger.info("/set_brightness")
        brightness = request.brightness
        self.matrix_wrapper.matrix.brightness = brightness
        return {"error": False, "brightness": self.matrix_wrapper.matrix.brightness}

    def route_get_state(self):
        logger.info("/get_state")
        return {"brightness": self.matrix_wrapper.matrix.brightness}

    def route_next_app(self):
        logger.info("/next_app")
        self.next_app()
        return {"error": False}

    def route_prev_app(self):
        logger.info("/prev_app")
        self.prev_app()
        return {"error": False}

    def route_page_up(self):
        logger.info("/page_up")
        self.page_up()
        return {"error": False}

    def route_page_down(self):
        logger.info("/page_down")
        self.page_down()
        return {"error": False}

    def __run_api__(self):
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=8008,
            log_level="info",
            access_log=False,
            log_config=None,
        )

    def start(self):
        api_thread = threading.Thread(target=self.__run_api__, daemon=True)
        api_thread.start()
        logger.info("fastapi started")
