from fastapi import FastAPI

from lifespan.app_lifespan import lifespan
from routes.transactions import router as transaction_router
from routes.users import router as user_router
from routes.register_middleware import register_middleware
from routes.authentication import router as auth_router
app = FastAPI(lifespan=lifespan, docs_url="/docs")

register_middleware(app)
app.include_router(user_router)
app.include_router(transaction_router)
app.include_router(auth_router)
