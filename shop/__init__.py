from __future__ import absolute_import, unicode_literals

# Это необходимо для того, чтобы Celery мог обнаружить задачи
from .celery import app as celery_app

__all__ = ("celery_app",)
