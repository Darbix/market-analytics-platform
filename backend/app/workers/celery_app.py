from celery import Celery
from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "market_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.task_routes = {
    # Send all tasks from app.workers.tasks to 'analytics' queue
    "app.workers.tasks.*": {"queue": "analytics"}
}

celery_app.autodiscover_tasks(["app.workers"])
