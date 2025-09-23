from fastapi.responses import FileResponse
from .generator.generate import GeneratorError, generate, GeneratorParams
from .logger import logger
from .config import AppConfig
from fastapi import FastAPI, HTTPException

from fastapi_cli.logging import setup_logging

setup_logging()
config = AppConfig()


def on_startup():
    logger.info('Current config: ' + str(config))


app = FastAPI(
    on_startup=[on_startup],
    debug=config.debug
)


@app.post("/generate")
async def root(params: GeneratorParams):
    try:
        # return str(generate(params))
        return FileResponse(generate(params))
    except GeneratorError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    # return {"message": "Hello World"}


if __name__ == "__main__":
    pass
