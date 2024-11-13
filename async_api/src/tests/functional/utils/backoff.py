import logging
import time
from functools import wraps


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=100):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            t = start_sleep_time * (factor**2)
            while t < border_sleep_time:
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    logging.error(error)
                    print(f'Ожидание подключения к сервису: {t} сек.')
                    time.sleep(t)
                t = t * (factor**2)
        return inner
    return func_wrapper
