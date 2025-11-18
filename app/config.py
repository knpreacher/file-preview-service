import os
from typing import TypeVar, Generic, cast
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from logger import logger

ENV_PREFIX = 'FPS_'

load_dotenv()

def bool_wrapper(value) -> bool:
    if value is str:
        return value.lower() in ['true', 't', '1', 'yes', 'y']
    return False

T = TypeVar('T')

class EnvProp(Generic[T]):
    _key: str | None = None
    _attr_name: str | None = None
    _default: T | None = None

    @property
    def active_key(self) -> str:
        assert self._key or self._attr_name, 'key or attr_name must be set'
        return self._key or self._attr_name or ''

    @property
    def env_key(self):
        if self.is_native_key:
            return self.active_key
        return f'{ENV_PREFIX}{self.active_key.upper()}'

    def __set_name__(self, owner, attr_name: str) -> None:
        self._attr_name = attr_name

    def __init__(self, key=None, _default: T = None, is_native_key=False, wrapper_fn=None):
        self.is_native_key = is_native_key
        self._key = key
        self.wrapper_fn = wrapper_fn or (lambda x: x)
        self._default = _default

    def __get__(self, instance, owner):
        _v = os.environ.get(self.env_key, self._default)
        logger.info(f'Loading env {self.env_key}: {_v}')
        if _v is None:
            return None
        return self.wrapper_fn(_v)


class Settings(BaseSettings):
    debug:bool = cast(bool, EnvProp(wrapper_fn=bool_wrapper))
    document_root: str = cast(str, EnvProp())
    cache_root: str = cast(str, EnvProp())
    
    autoclean_inerval: int = cast(int, EnvProp(_default=0, wrapper_fn=int))

    watermark_path: str|None = cast(str, EnvProp())
    watermark_light_path: str|None = cast(str, EnvProp())
    watermark_dark_path: str|None = cast(str, EnvProp())
    
    s3_secure: bool = cast(bool, EnvProp(_default=False, wrapper_fn=bool_wrapper))
    s3_host: str = cast(str, EnvProp(_default='127.0.0.1'))
    s3_port: int = cast(int, EnvProp(_default=9000, wrapper_fn=int))
    s3_access_key: str = cast(str, EnvProp(_default='minioadmin'))
    s3_secret_key: str = cast(str, EnvProp(_default='minioadmin'))
    s3_region: str = cast(str, EnvProp(_default='us-east-1'))
    s3_bucket: str = cast(str, EnvProp(_default='general'))

    @property
    def s3_endpoint_url(self) -> str:
        return f'http{"s" if self.s3_secure else ""}://{self.s3_host}:{self.s3_port}'
settings = Settings()