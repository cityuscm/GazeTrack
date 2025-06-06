import uvicorn
from fastapi import FastAPI
from wireup.integration.fastapi import setup as wireup_fastapi_setup

from api.routes import router as api_router
from container import container
from lifecycle import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api")

wireup_fastapi_setup(container, app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
