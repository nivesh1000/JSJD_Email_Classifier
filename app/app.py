import os
import json
import redis
import asyncio
from celery import Celery
from datetime import datetime, timedelta

from logger import JsJdLogger, LineFileProvider


from apscheduler.schedulers.background import BackgroundScheduler


from config import CELERY_BROKER, CELERY_BACKEND

logger = JsJdLogger()





def main():
    "Entry Point"

    # celery configuration
    celery = Celery("", broker="CELERY_BROKER", backend="CELERY_BACKEND")


if __name__ == "__main__":
    main()
