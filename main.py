#this file only uses get and post method as i'm not using javascript
#this file currently assumes user id to be 1

from fastapi import FastAPI, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,  RedirectResponse
import models, database,requests
from passlib.context import CryptContext

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

#login and signup forms don't have assocoiated actions yet in frontend.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/signup")
def signup_user(first_name: str = Form(), last_name: str = Form(), email: str = Form(), password: str = Form()):
    db = database.Session()
    email_taken = False
    all_users = db.query(models.User).all()

    for user in all_users:
        if user.email == email:
            email_taken = True
            break

    if email_taken:
        db.close()
        return {"error": "An account with this email already exists!"}
    else:
        hashed_pass = pwd_context.hash(password)
        new_user = models.User(first_name=first_name, last_name=last_name, email=email, password=hashed_pass)
        db.add(new_user)
        db.commit()

    db.close()

    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/login")
def login_user(request: Request, email: str = Form(), password: str = Form()):
    db = database.Session()
    user_record = None
    account_found = False
    all_users = db.query(models.User).all()

    for user in all_users:
        if user.email == email:
            user_record = user
            account_found = True
            break

    if account_found:
        hashed_pass = pwd_context.hash(password)
        if hashed_pass == user_record.password:
            request.session["user_id"] = user_record.user_id
            db.close()
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        else:
            db.close()
            return {"error": "Incorrect password. Please try again."}
    
    db.close()
    return {"error": "No account associated with this email address. Please sign up first."}

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

@app.get("/search-book") #frontend to be written
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

@app.post("/library/tbr") #frontend to be written
def add_to_tbr(title: str = Form(), author: str = Form(), cover_id: int = Form(), total_pages: int = Form(), avg_rating: float = Form()):
    db = database.Session()
    found = False
    all_books = db.query(models.Book).all()

    for book in all_books:
        if title == book.title:
            id = book.book_id
            found = True
            break

    if found:
        new_tbr_book = models.TbrBook(book_id = id, user_id = 1)
        db.add(new_tbr_book)
    else:
        new_book_row = models.Book(title = title, author = author, cover_id = cover_id, total_pages = total_pages, avg_rating = avg_rating)
        db.add(new_book_row)
        db.flush()    
        new_tbr_book = models.TbrBook(book_id = new_book_row.book_id, user_id = 1)
        db.add(new_tbr_book)

    db.commit()
    db.close()

    return {"status": "success"}