from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import models, database,requests

models.Base.metadata.create_all(bind=database.engine)

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

@app.get("/search-book")
def fetch_books(search: str, request: Request):
    db = database.Session

    url = f"https://openlibrary.org/search.json?q={search.replace(" ", "+")}&limit=10"
    response = requests.get(url).json()

    results = response.get("docs", [])[:10]

    formatted_results = []

    for book_data in results:
        clean_book = {
            "title": book_data.get("title"),
            "author": book_data.get("author_name", "Unknown"),
            "cover_id": book_data.get("cover_i"),
            "total_pages": book_data.get("number_of_pages_median", 0),
            "avg_rating": book_data.get("ratings_average", 0.0)
        }
        formatted_results.append(clean_book)

    db.close()
    return templates.TemplateResponse("library.html", request, {"books": formatted_results})