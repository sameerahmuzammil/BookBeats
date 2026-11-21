#this file only uses get and post method as i'm not using javascript
#change all code to make it scalable and fix bugs before proceeding to write new code

from fastapi import FastAPI, Request, Form, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,  RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime, timedelta
import models, database, requests, hashlib, time

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="bookbeats-2008-2026")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/signup")
def signup_user(request: Request, first_name: str = Form(), last_name: str = Form(), email: str = Form(), password: str = Form(), confirm_pass: str = Form()):
    domain = request.headers.get("host")

    if confirm_pass != password:
        return RedirectResponse(url=f"https://{domain}/signup?error=Passwords+do+not+match", status_code=status.HTTP_303_SEE_OTHER)

    db = database.Session()
    existing_user = db.query(models.User).filter(models.User.email == email.strip()).first()

    if existing_user:
        db.close()
        return RedirectResponse(url=f"https://{domain}/login?error=Email+already+registered", status_code=status.HTTP_303_SEE_OTHER)
    else:
        hashed_pass = hash_password(password)
        new_user = models.User(first_name=first_name.strip(), last_name=last_name.strip(), email=email.strip(), password=hashed_pass)
        db.add(new_user)
        db.commit()

    db.close()

    return RedirectResponse(url=f"https://{domain}/login", status_code=status.HTTP_303_SEE_OTHER)

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
        if hash_password(password) == user_record.password:
            request.session["user_id"] = user_record.user_id
            db.close()
            domain = request.headers.get("host")
            return RedirectResponse(url=f"http://{domain}/", status_code=status.HTTP_303_SEE_OTHER)
        else:
            db.close()
            return {"error": "Incorrect password. Please try again."}
    
    db.close()
    return {"error": "No account associated with this email address. Please sign up first."}

@app.get("/login", include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/signup", include_in_schema=False)
def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html")

@app.get("/", include_in_schema=False)
def home(request: Request):
    current_user = request.session.get("user_id")
    db = database.Session()
    books = []

    if current_user:
        tbr_books = db.query(models.TbrBook).all()
        for book in tbr_books:
            if book.user_id == current_user and book.status.lower() == "currently reading":
                all_books = db.query(models.Book).all()
                for home_book in all_books:
                    if book.book_id == home_book.book_id:
                        current_book = {
                            'book_id': home_book.get("book_id"),
                            'title': home_book.get("title"),
                            'cover_id': home_book.get("cover_id"),
                            'author': home_book.get("author"),
                            'avg_rating': home_book.get("avg_rating"),
                            'current_page': book.get("current_page"),
                            'total_pages': home_book.get("total_pages"),
                            'last_read': book.get("last_read")
                        }
                        books.append(current_book)
        else:
            raise HTTPException(status_code=404, detail="User Not Found")
    
    db.close()
    return templates.TemplateResponse(request, "home.html", {'books': books})

@app.get("/library", include_in_schema=False)
def library(request: Request):
    return templates.TemplateResponse(request, "library.html")

@app.get("/library/tbr", include_in_schema=False)
def tbr(request: Request):
    current_user = request.session.get("user_id")
    db = database.Session()
    books = []

    if current_user:
        tbr_books = db.query(models.TbrBook).all()
        for book in tbr_books:
            if book.user_id == current_user:
                all_books = db.query(models.Book).all()
                for home_book in all_books:
                    if home_book.book_id == book.book_id:
                        tbr_book = {
                            'book_id': home_book.get("book_id"),
                            'title': home_book.get("title"),
                            'cover_id': home_book.get("cover_id"),
                            'author': home_book.get("author"),
                            'avg_rating': home_book.get("avg_rating"),
                            'total_pages': home_book.get("total_pages"),
                        }
                        books.append(tbr_book)
    else:
        raise HTTPException(status_code=404, detail="User Not Found")

    db.close()
    return templates.TemplateResponse(request, "library.html", {'books': books})

@app.get("/packages", include_in_schema=False)
def packages(request: Request):
    return templates.TemplateResponse(request, "packages.html")

@app.get("/dashboard", include_in_schema=False)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/search-book") #frontend to be written
def fetch_books(search: str, request: Request):
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
  
    return templates.TemplateResponse(request, "library.html", {"books": formatted_results})

@app.post("/library/tbr") #frontend to be written
def add_to_tbr(request: Request, title: str = Form(), author: str = Form(), cover_id: int = Form(), total_pages: int = Form(), avg_rating: float = Form()):
    current_user_id = request.session.get("user_id")
    if not current_user_id:
        domain = request.headers.get("host")
        return RedirectResponse(url=f"https://{domain}/login", status_code=status.HTTP_303_SEE_OTHER)
    
    db = database.Session()
    found = False
    assigned_id = None
    all_books = db.query(models.Book).all()

    for book in all_books:
        if title == book.title:
            assigned_id = book.book_id
            found = True
            break

    if found:
        new_tbr_book = models.TbrBook(book_id = assigned_id, user_id = current_user_id)
        db.add(new_tbr_book)
    else:
        new_book_row = models.Book(title = title, author = author, cover_id = cover_id, total_pages = total_pages, avg_rating = avg_rating)
        db.add(new_book_row)
        db.flush()    
        new_tbr_book = models.TbrBook(book_id = new_book_row.book_id, user_id = current_user_id)
        db.add(new_tbr_book)

    db.commit()
    db.close()

    return {"status": "success"}

@app.post("/update-status") #add a hidden input that gives bookid in frontend | frontend to be written
def update_status(request: Request, book_id: int = Form(), selected_status: str = Form()):
    current_user_id = request.session.get("user_id")
    if not current_user_id:
        domain = request.headers.get("host")
        return RedirectResponse(url=f"https://{domain}/login", status_code=status.HTTP_303_SEE_OTHER)
    
    db = database.Session()
    all_books = db.query(models.TbrBook).all()
    status_updated = False

    for book in all_books:
        if book.book_id == book_id and book.user_id == current_user_id:
            book.status = selected_status
            db.commit()
            status_updated = True

    if status_updated:
        db.close()
        domain = request.headers.get("host")
        return RedirectResponse(url=f"https://{domain}/library", status_code=status.HTTP_303_SEE_OTHER)
    else:
        db.close()
        return {"error": "Book not found in TBR."}

@app.post("/start-session")
def start_session(request: Request, book_id: int = Form()):
    current_user = request.session.get("user_id")
    db = database.Session()
    all_books = db.query(models.TbrBook).all()

    for book in all_books:
        if book.book_id == book_id and book.user_id == current_user:
            if book.session_started_at != None:
                db.close()
                domain = request.headers.get("host")
                return RedirectResponse(url=f"https://{domain}/stop-session", status_code=status.HTTP_303_SEE_OTHER)
            else:
                book.session_started_at = time.time()
                db.commit()
                db.close()
                domain = request.headers.get("host")
                return RedirectResponse(url=f"https://{domain}/stop-session", status_code=status.HTTP_303_SEE_OTHER)

    db.close()
    domain = request.headers.get("host")
    return RedirectResponse(url=f"https://{domain}/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/stop-session")
def stop_session(request: Request, book_id: int = Form()):
    current_user = request.session.get("user_id")
    db = database.Session()
    all_books = db.query(models.TbrBook).all()

    for book in all_books:
        if book.book_id == book_id and book.user_id == current_user:
            if book.session_ended_at != None:
                db.close()
                domain = request.headers.get("host")
                return RedirectResponse(url=f"https://{domain}/start-session", status_code=status.HTTP_303_SEE_OTHER)
            else:
                book.session_ended_at = time.time()

                today = datetime.fromtimestamp(book.session_ended_at).date()
                user = models.User(user_id = current_user)
                if user.last_read_date:
                    saved_user_date = user.last_read_date
                else: 
                    saved_user_date = None
                if saved_user_date == today:
                    pass
                elif saved_user_date == today - timedelta(days=1):
                    user.reading_streak = user.reading_streak + 1
                    user.last_read_date = datetime.fromtimestamp(book.session_ended_at)
                else:
                    user.reading_streak = 1
                    user.last_read_date = datetime.fromtimestamp(book.session_ended_at)

                db.commit()
                db.close()
                domain = request.headers.get("host")
                return RedirectResponse(url=f"https://{domain}/start-session", status_code=status.HTTP_303_SEE_OTHER)

    db.close()
    domain = request.headers.get("host")
    return RedirectResponse(url=f"https://{domain}/", status_code=status.HTTP_303_SEE_OTHER)

def reading_speed_book_specific(prev_speed, new_speed):
    return round((prev_speed + new_speed) / 2, 1)

@app.post("/save-progress")
def save_progress(request: Request, book_id: int = Form(), current_page: int = Form()):
    current_user = request.session.get("user_id")
    db = database.Session()
    all_books = db.query(models.TbrBook).all()
    time_taken = None
    last_page = None
    reading_speed = 0

    for book in all_books:
        if book.book_id == book_id and book.user_id == current_user:
            if book.session_started_at != None and book.session_ended_at != None:
                book.last_read = datetime.fromtimestamp(book.session_ended_at)
                db.flush()
                time_taken = book.session_ended_at - book.session_started_at
                last_page = book.current_page
                reading_speed = (current_page - last_page) / time_taken
                book.pages_per_min = reading_speed_book_specific(book.pages_per_min, reading_speed)
                db.flush()
                book.current_page = current_page
                db.flush()
                book.progress = round((current_page / models.Book(book_id = book_id).total_pages) * 100)
                db.commit()

    db.close()
    domain = request.headers.get("host")
    return RedirectResponse(url=f"https://{domain}/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/update-{book_id}-rating")
def update_book_rating(request: Request, book_id: int = Form(), rating: int = Form()):
    current_user = request.session.get("user_id")
    db = database.Session()
    all_books = db.query(models.TbrBook).all()

    for book in all_books:
        if book.book_id == book_id and book.user_id == current_user:
            book.user_rating = rating
            db.commit()

    db.close()
    domain = request.headers.get("host")
    return RedirectResponse(url=f"https://{domain}/library", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/update-{book_id}-favourite")
def is_favourite(request: Request, book_id: int = Form(), is_fav: str = Form()):
    current_user = request.session.get("user_id")
    db = database.Session()
    all_books = db.query(models.TbrBook).all()

    for book in all_books:
        if book.book_id == book_id and book.user_id == current_user:
            if is_fav.lower() == "yes":
                book.favourite = True
            else:
                book.favourite = False
                db.commit()

    db.close()
    domain = request.headers.get("host")
    return RedirectResponse(url=f"https://{domain}/library", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/reading-speed")
def average_reading_speed(request: Request):
    user = request.session.get("user_id")
    speed_sum = 0
    count = 0
    db = database.Session()
    all_books = db.query(models.TbrBook).all()

    for book in all_books:
        if book.user_id == user and (book.status.lower() == "read" or book.status.lower() == "currently reading"):
            speed_sum += book.pages_per_min
            count += 1

    avg_reading_spd = speed_sum / count
    models.User(user_id = user, average_reading_speed = avg_reading_spd)
    db.commit()
    db.close()
    return {"status": "Successful!"}

@app.post("/delete-tbr/{book-id}")
def delete_tbr_book(request: Request, book_id: int = Form()):
        user = request.session.get("user_id")
        db = database.Session()
        all_books = db.query(models.TbrBook).all()

        for book in all_books:
            if book.user_id == user and book.book_id == book_id:
                try:
                    db.delete(book)
                    db.commit()
                except:
                    raise HTTPException(status_code=500, detail="Internal Server Error")

        db.close()
        return {"status": "Successful!"}

@app.post("/delete-tbr")
def delete_all_tbr_items(request: Request):
        user = request.session.get("user_id")
        db = database.Session()
        all_books = db.query(models.TbrBook).all()

        for book in all_books:
            if book.user_id == user:
                try:
                    db.delete(book)
                    db.flush()
                except:
                    raise HTTPException(status_code=404, detail="TBR Not Found")

        db.commit()
        db.close()
        return {"status": "Successful! TBR List deleted."}

@app.post("/delete-account")
def delete_user(request: Request):
    current_user_id = request.session.get("user_id")
    if not current_user_id:
        domain = request.headers.get("host")
        return RedirectResponse(url=f"http://{domain}/login", status_code=status.HTTP_303_SEE_OTHER)

    db = database.Session()
    try:
        user_to_delete = db.query(models.User).filter(models.User.user_id == current_user_id).first()
        
        if user_to_delete:
            db.delete(user_to_delete)
            db.commit()
            request.session.clear()
        else:
            raise HTTPException(status_code=404, detail="User Not Found")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        db.close()

    domain = request.headers.get("host")
    return RedirectResponse(url=f"http://{domain}/signup", status_code=status.HTTP_303_SEE_OTHER)