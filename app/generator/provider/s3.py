import mimetypes

from typing import Optional
from pathlib import Path

from ...utils.s3_clent import S3Client
from ...logger import logger

from ..base import BaseGenerator, GeneratorParams, GeneratorError

class S3GeneratorParams(GeneratorParams):
    path: str
    upload_to: Optional[str] = None

class S3Generator(BaseGenerator[S3GeneratorParams]):
    
    @property
    def client(self)->S3Client:
        return S3Client()
    
    async def upload(self, result_path: Path):
        bucket_exists = await self.client.check_bucket_exists()
        if not bucket_exists:
            raise GeneratorError(f'Bucket {self.config.s3_bucket} does not exist')
        
        _bytes = result_path.read_bytes()
        try:
            mime_type = mimetypes.guess_type(result_path)[0]
        except Exception:
            mime_type = 'application/octet-stream'
        
        _upload_to = self.params.upload_to % {
            'filename': result_path.name
        }
            
        logger.info(f'Uploading file to S3: {_upload_to}')
        
        await self.client.upload(_upload_to, _bytes, mime_type)
        
        return _upload_to
    
    async def get_document_path(self) -> Path:
        bucket_exists = await self.client.check_bucket_exists()
        if not bucket_exists:
            raise GeneratorError(f'Bucket {self.config.s3_bucket} does not exist')
        _path = Path(self.params.path)
        
        file_name = _path.name
        
        document_path = Path(self.cache_dir) / file_name
        
        s3_doc = await self.client.download(self.params.path, str(document_path))
        logger.info(f'File {self.params.path} downloaded from S3')
        logger.info(f'File saved as: {document_path}')
        logger.info(f'File: {s3_doc}')
        
        if not document_path.exists():
            raise GeneratorError(f'File not found: {document_path}')
        if not document_path.is_file():
            raise GeneratorError(f'Path is not a file: {document_path}')
        return document_path