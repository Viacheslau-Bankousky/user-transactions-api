from fastapi import FastAPI

from lifespan.app_lifespan import lifespan
from routes.users import router as user_router

app = FastAPI(lifespan=lifespan, docs_url="/docs")

app.include_router(user_router)
