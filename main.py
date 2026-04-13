from fastapi import FastAPI
from api.routers.compare import router as compare_router
from api.routers.evaluate import router as evaluate_router
from api.routers.improve import router as improve_router

app = FastAPI()


app.include_router(evaluate_router)
app.include_router(compare_router)
app.include_router(improve_router)