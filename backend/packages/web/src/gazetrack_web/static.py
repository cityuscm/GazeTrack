import pathlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

def include_static(app: FastAPI):
    """Setup static file serving for the embedded UI."""
    current_dir = pathlib.Path(__file__).parent
    ui_dir = current_dir / "ui"
    if not ui_dir.exists():
        logger.warning(f"UI directory not found at {ui_dir}. Frontend will not be served.")
        return
    else:
        logger.info(f"UI directory found at {ui_dir}. Frontend will be served.")
    app.mount("/", StaticFiles(directory=str(ui_dir), html=True), name="ui")