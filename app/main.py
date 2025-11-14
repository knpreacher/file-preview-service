from fastapi.responses import FileResponse
from .generator import GeneratorError, FileGenerator, FileGeneratorParams, S3Generator, S3GeneratorParams
from datetime import datetime
from contextlib import asynccontextmanager
from .logger import logger
from .config import settings
from fastapi import FastAPI, HTTPException

import schedule

from .utils.cleaner import delete_files
from .utils.scheduler import run_continuously

from fastapi_cli.logging import setup_logging

setup_logging()

def delete_files_job():
    logger.info('[AUTO] Cleaning cache...')
    removed, errors = delete_files(directory=settings.cache_root, age_seconds=settings.autoclean_inerval)
    logger.info(f'[AUTO] Removed {len(removed)} files, {len(errors)} errors')

start_date: datetime | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global start_date
    start_date = datetime.now()
    logger.info('Service started at ' + str(start_date))
    logger.info('Current config: ' + str(settings))
    if settings.autoclean_inerval > 0:
        logger.info('>>>>> Autoclean enabled <<<<<')
        logger.info(f'Cleaning cache every {settings.autoclean_inerval} seconds')
    
    schedule.every(settings.autoclean_inerval).seconds.do(delete_files_job)
    stop_run_continuously = run_continuously()
    yield
    stop_run_continuously.set()
    logger.info('Service stopped at ' + str(datetime.now()))

app = FastAPI(
    lifespan=lifespan,
    debug=settings.debug
)


@app.post("/generate/file")
async def generate_from_file(params: FileGeneratorParams):
    try:
        return FileResponse(await FileGenerator(params).generate())
    except GeneratorError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate/s3")
async def generate_from_file(params: S3GeneratorParams):
    try:
        # return str(generate(params))
        generator = S3Generator(params)
        res = await generator.generate()
        logger.info(f'Generated file: {res}')
        if params.upload_to:
            _upload_path = await generator.upload(res)
            logger.info(f'File uploaded to S3: {_upload_path}')
            return _upload_path
        else:
            return FileResponse(res)
    except GeneratorError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok", "start_date": str(start_date)}

@app.post("/clean")
async def clean():
    removed, errors = delete_files(directory=settings.cache_root, age_seconds=0)
    return {
        "removed": removed,
        "errors": errors
    }

if __name__ == "__main__":
    pass
