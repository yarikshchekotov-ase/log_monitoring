from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import asyncio
from fastapi.exceptions import HTTPException
app = FastAPI()


logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] | [%(asctime)s] | %(name)s | %(message)s")

logger = logging.getLogger(__name__)

Instrumentator().instrument(app).expose(app)


@app.get("/")
def home():
    return {
        "test": "sucessful"
    }

@app.get("/favicon.ico")
def get_favico_ico():
    return {
        "error": "No conectet"
    }

@app.get("/site", response_class=HTMLResponse)
def site():
    return FileResponse("index.html")
    
@app.get("/break/timeout")
async def timeout():
    await asyncio.sleep(5)

@app.get("/home")
async def home():
    await asyncio.sleep(7)
    return {
        "page": "home"
    }

@app.get("/404", status_code=404)
async def ret_404():
    return {
        "ststus": "404"
    }

@app.get("/break/critical", status_code=500)
async def critical():
    logging.critical("Тестовая ошибка")
    raise HTTPException(status_code=500, detail="сообщение")