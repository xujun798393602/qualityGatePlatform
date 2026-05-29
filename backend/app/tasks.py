from app.core.celery_app import celery_app

@celery_app.task
def example_task():
    """Example background task"""
    return "Task completed"