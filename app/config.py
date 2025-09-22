import os
from dotenv import load_dotenv

ENV_PREFIX = 'FPS_'


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def cast_env_value(value: str):
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    if value.isdigit():
        return int(value)
    if value.isnumeric():
        return float(value)
    return value


class AppConfig(metaclass=SingletonMeta):
    debug: bool
    document_root: str
    cache_root: str

    watermark_path: str
    watermark_light_path: str
    watermark_dark_path: str

    def __init__(self):
        self._load_config()

    def _load_config(self):
        load_dotenv()

        for key, value in os.environ.items():
            if key.startswith(ENV_PREFIX):
                if value is not None:
                    setattr(
                        self,
                        key[len(ENV_PREFIX):].lower(),
                        cast_env_value(value)
                    )

    def __str__(self):
        return str(self.__dict__)
