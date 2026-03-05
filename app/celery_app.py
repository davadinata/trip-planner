from celery import Celery

celery_app = Celery(
    "trip_planner",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.modules.trip.task"] 
)