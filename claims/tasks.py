# <your_app>/tasks.py

from celery import shared_task

@shared_task
def your_task_name(args):
    # Task implementation
    pass
