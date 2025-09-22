from pathlib import Path
from typing import Literal
from pydantic import BaseModel
from ..logger import logger
from ..config import AppConfig

from PIL import Image, ImageStat

from preview_generator.manager import PreviewManager


class GeneratorError(Exception):
    pass


class WatermarkParams(BaseModel):
    theme: Literal['dark', 'light', 'auto'] = 'auto'
    opacity: float = 0.5
    size: int = -1  # -1 = fill
    position: Literal['top_left', 'top_right',
                      'bottom_left', 'bottom_right', 'center'] = 'center'
    repeat: bool = False


class GeneratorParams(BaseModel):
    width: int = 500
    height: int = 500
    format: str = 'jpeg'
    quality: int = 1
    page: int = -1

    watermark: WatermarkParams | None

    path: str


def _validate_paths(params: GeneratorParams, config: AppConfig) -> Path:
    document_path = Path(config.document_root) / params.path
    if not document_path.exists():
        raise GeneratorError(f'File not found: {document_path}')
    if not document_path.is_file():
        raise GeneratorError(f'Path is not a file: {document_path}')
    logger.info(f'Generating preview for {document_path}')
    cache_root = Path(config.cache_root)
    if not cache_root.exists():
        raise Exception(f'Cache root not found: {cache_root}')

    return document_path


def generate(params: GeneratorParams):
    config = AppConfig()
    logger.info("Requested generator params: " + str(params))
    document_path = _validate_paths(params, config)
    logger.info(f"Generating preview for {document_path}")

    manager = PreviewManager(
        str(config.cache_root),
        create_folder=False
    )

    result_path = manager.get_jpeg_preview(
        str(document_path),
        page=params.page,
        width=params.width,
        height=params.height
    )

    logger.info(f'Generated preview: {result_path}')

    wm_result_path = create_watermark(
        Path(result_path),
        params.watermark,
        config
    )

    return wm_result_path


def _is_image_dark(image_path: Path, threshold: int = 50):
    img = Image.open(image_path).convert('L')
    stat = ImageStat.Stat(img)
    mean_brightness = stat.mean[0]
    return mean_brightness < threshold


def get_watermark_image(
    theme: Literal['dark', 'light'],
    config: AppConfig
):
    themed_wm_path = getattr(config, f'watermark_{theme}_path')
    if themed_wm_path and Path(themed_wm_path).is_file():
        return themed_wm_path

    wm_path = Path(config.watermark_path)
    if wm_path.is_file():
        return wm_path

    return None


def create_watermark(
    image_path: Path,
    wm_params: WatermarkParams,
    config: AppConfig
):
    theme = wm_params.theme
    if theme == 'auto':
        theme = 'dark' if _is_image_dark(image_path) else 'light'

    wm_path = get_watermark_image(theme, config)
    if not wm_path:
        raise GeneratorError(f'Watermark not found for theme: {theme}')

    original_image = Image.open(image_path)
    watermark_image = Image.open(wm_path)

    watermark_image = watermark_image.resize(
        size=(original_image.width, original_image.height),
        resample=Image.Resampling.LANCZOS
    )

    result_image = original_image.copy()
    result_image.paste(
        watermark_image,
        original_image.getbbox(),
        watermark_image
    )

    target_path = Path(
        image_path.parent,
        f'{image_path.stem}-wm.{image_path.suffix}'
    )

    result_image.save(target_path)

    return target_path
