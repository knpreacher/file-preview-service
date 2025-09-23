import math

from pathlib import Path
from typing import Literal
from pydantic import BaseModel
from ..logger import logger
from ..config import AppConfig

from PIL import Image, ImageStat

from preview_generator.manager import PreviewManager


class GeneratorError(Exception):
    pass


WatermarkPosition = Literal['top_left', 'top_right',
                            'bottom_left', 'bottom_right', 'center']


class WatermarkParams(BaseModel):
    theme: Literal['dark', 'light', 'auto'] = 'auto'
    opacity: float = 0.5
    size: int = -1  # -1 = fill
    rotate: int = 0
    position: WatermarkPosition = 'center'
    repeat: bool = False


class GeneratorParams(BaseModel):
    width: int = 500
    height: int = 500
    format: str = 'jpeg'
    quality: int = 100
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

    result_path = Path(result_path)

    result_image = create_watermark(
        result_path,
        params.watermark,
        config
    )

    target_path = Path(
        result_path.parent,
        f'{result_path.stem}-wm.jpg'
    )

    result_image.save(
        target_path,
        subsampling=0,
        quality=params.quality,
        optimize=True
    )

    return target_path


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


def get_watermark_offset(
    position: WatermarkPosition,
    wm: Image,
    image: Image
):
    if position == 'top_left':
        return 0, 0
    elif position == 'top_right':
        return image.width - wm.width, 0
    elif position == 'bottom_left':
        return 0, image.height - wm.height
    elif position == 'bottom_right':
        return image.width - wm.width, image.height - wm.height
    elif position == 'center':
        return (image.width - wm.width) // 2, (image.height - wm.height) // 2


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

    wm_aspect_ratio = watermark_image.width / watermark_image.height

    wm_size = (
        original_image.width if wm_params.size == -1 else int(wm_params.size),
        int(original_image.width / wm_aspect_ratio) if wm_params.size == -
        1 else int(wm_params.size / wm_aspect_ratio)
    )

    watermark_image = watermark_image.resize(
        size=wm_size,
        resample=Image.Resampling.LANCZOS
    ).convert('RGBA')

    wm_c = watermark_image.copy()
    wm_c.putalpha(
        int(wm_params.opacity * 255)
    )

    watermark_image.paste(
        wm_c, (0, 0), watermark_image
    )

    watermark_image = watermark_image.rotate(
        wm_params.rotate,
        resample=Image.Resampling.NEAREST,
        expand=True
    )

    result_image = original_image.copy().convert('RGBA')

    if wm_params.repeat:
        for i in range(math.ceil(result_image.width / watermark_image.width)):
            for j in range(math.ceil(result_image.height / watermark_image.height)):
                result_image.paste(
                    watermark_image,
                    (i * watermark_image.width, j * watermark_image.height),
                    watermark_image
                )

    else:
        width_offset, height_offset = get_watermark_offset(
            wm_params.position,
            watermark_image,
            result_image
        )

        result_image.paste(
            watermark_image,
            (width_offset, height_offset),
            watermark_image
        )

    return result_image.convert('RGB')
