from fastapi import FastAPI
from scripture.routes.api import router

app = FastAPI()
app.include_router(router)
