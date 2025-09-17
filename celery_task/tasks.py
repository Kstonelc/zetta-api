from . import celery
import time


@celery.task(bind=True, max_retries=2)
def long_running_task(self, data):
    try:
        # 模拟一些耗时操作
        time.sleep(10)
        return {"status": "success", "data": []}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
