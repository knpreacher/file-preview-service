from pathlib import Path

from ..base import BaseGenerator, GeneratorParams, GeneratorError

class FileGeneratorParams(GeneratorParams):
    path: str

class FileGenerator(BaseGenerator[FileGeneratorParams]):
    async def get_document_path(self) -> Path:
        document_path = Path(self.config.document_root) / self.params.path
        if not document_path.exists():
            raise GeneratorError(f'File not found: {document_path}')
        if not document_path.is_file():
            raise GeneratorError(f'Path is not a file: {document_path}')
        return document_path