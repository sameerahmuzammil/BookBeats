from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

books = [
    {
        'id': 1,
        'book_name': 'Eleanor And Park',
        'author': 'Rainbow Rowell',
        'cover_url': 'https://picsum.photos',
        'total_pages': 476,
        'status': 'Currently Reading',
        'current_page': 145,
        'last_read': '2026-07-26',
        'user_rating': 4,
        'favorite': False
    },
    {
        'id': 2,
        'book_name': 'Better Than the Movies',
        'author': 'Lynn Painter',
        'cover_url': 'https://picsum.photos',
        'total_pages': 368,
        'status': 'Currently Reading',
        'current_page': 203,
        'last_read': '2026-07-26',
        'user_rating': 5,
        'favorite': True
    },
    {
        'id': 3,
        'book_name': 'Six of Crows',
        'author': 'Leigh Bardugo',
        'cover_url': 'https://picsum.photos',
        'total_pages': 496,
        'status': 'To Be Read',
        'current_page': 0,
        'last_read': None,
        'user_rating': 4,
        'favorite': False
    }
]

@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {'books': books})

@app.get("/library", include_in_schema=False)
def library(request: Request):
    return templates.TemplateResponse(request, "library.html")

@app.get("/packages", include_in_schema=False)
def packages(request: Request):
    return templates.TemplateResponse(request, "packages.html")

@app.get("/dashboard", include_in_schema=False)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")