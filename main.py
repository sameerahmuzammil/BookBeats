from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")

@app.get("/library", include_in_schema=False)
def library(request: Request):
    return templates.TemplateResponse(request, "library.html")

@app.get("/packages", include_in_schema=False)
def packages(request: Request):
    return templates.TemplateResponse(request, "packages.html")

@app.get("/dashboard", include_in_schema=False)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")