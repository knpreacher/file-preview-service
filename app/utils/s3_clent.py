import aioboto3
from botocore.exceptions import ClientError

from ..logger import logger
from ..config import Settings, settings as _settings

session = aioboto3.Session()


class S3Client:
    def __init__(self, settings: Settings = _settings):
        self.settings = settings
        self.bucket = settings.s3_bucket

    async def get_client(self):
        return session.client(
            's3',
            endpoint_url=self.settings.s3_endpoint_url,
            aws_access_key_id=self.settings.s3_access_key,
            aws_secret_access_key=self.settings.s3_secret_key,
            region_name=self.settings.s3_region,
        )

    async def check_bucket_exists(self):
        """Проверяет, существует ли бакет"""
        async with await self.get_client() as s3: # type: ignore
            try:
                await s3.head_bucket(Bucket=self.bucket)
                logger.info(f'Bucket {self.bucket} already exists')
                return True
            except ClientError:
                logger.warning(f'Bucket {self.bucket} does not exist')
                return False

    async def download(self, object_name: str, local_path: str):
        """Скачивает файл из бакета"""
        async with await self.get_client() as s3: # type: ignore
            return await s3.download_file(self.bucket, object_name, local_path)
    
    async def upload(
        self, object_name: str, file_bytes, content_type: str = 'application/octet-stream'
    ):
        """Загружает файл в бакет"""
        async with await self.get_client() as s3: # type: ignore
            await s3.put_object(
                Bucket=self.bucket, Key=object_name, Body=file_bytes, ContentType=content_type
            )

    async def delete(self, object_name: str):
        """Удаляет объект из бакета"""
        async with await self.get_client() as s3: # type: ignore
            try:
                await s3.delete_object(Bucket=self.bucket, Key=object_name)
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchKey':
                    raise

    async def generate_presigned_url(self, object_name: str, expires_in: int = 3600) -> str:
        """Генерирует временный URL для скачивания"""
        async with await self.get_client() as s3: # type: ignore
            url = await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expires_in,
            )
            return url
