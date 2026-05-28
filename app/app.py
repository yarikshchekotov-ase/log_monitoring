from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

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

@app.get("/metrics")
def metrics():
    pass

@app.get("/site", response_class=HTMLResponse)
def site():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()