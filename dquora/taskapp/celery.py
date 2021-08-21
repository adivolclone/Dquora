import os

from django.apps import apps, AppConfig
from django.conf import settings

from celery import Celery

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# 创建celery 实例
app = Celery('dquora')

# 从django的settings配置文件内加载CELERY_ 的配置
app.config_from_object('django.conf:settings', namespace='CELERY')


class CeleryAppConfig(AppConfig):
    name = 'dquora.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.requset!r}')  # pragma: no cover
