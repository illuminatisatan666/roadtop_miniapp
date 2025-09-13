from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import init_db
from bot import run_bot

# --- 🔹 ОПРЕДЕЛЕНИЕ lifespan ДО ЕГО ИСПОЛЬЗОВАНИЯ ---
@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()  # Инициализируем базу данных при старте
    import threading
    threading.Thread(target=run_bot, daemon=True).start()  # Запускаем бота в фоновом потоке
    yield  # Приложение запущено
    # Здесь можно добавить cleanup-логику при shutdown (если нужно)

# --- 🔹 СОЗДАЁМ app ПОСЛЕ ОПРЕДЕЛЕНИЯ lifespan ---
app = FastAPI(lifespan=lifespan)  # ✅ Теперь lifespan уже существует!
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Модели ---
from models import PlaceCreate, UserAuth
import aiosqlite

# --- Эндпоинты ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/auth")
async def auth(user: UserAuth):
    from security import generate_token
    async with aiosqlite.connect("roadtop.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
            (user.telegram_id, user.username or f"user_{user.telegram_id}")
        )
        await db.commit()
    return {
        "token": generate_token(user.telegram_id, user.username),
        "user_id": user.telegram_id
    }

@app.post("/api/place")
async def add_place(place: PlaceCreate):
    async with aiosqlite.connect("roadtop.db") as db:
        await db.execute(
            "INSERT INTO places (name, category, lat, lon, photo_url, review, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (place.name, place.category, place.lat, place.lon, place.photo_url, place.review, place.user_id)
        )
        await db.execute(
            "UPDATE users SET places_count = places_count + 1 WHERE telegram_id = ?",
            (place.user_id,)
        )
        count_cursor = await db.execute(
            "SELECT places_count FROM users WHERE telegram_id = ?", (place.user_id,)
        )
        count = (await count_cursor.fetchone())[0]

        if count > 50:
            level = "Легенда дорог"
        elif count > 30:
            level = "Топ-куратор"
        elif count > 10:
            level = "Искатель"
        else:
            level = "Новичок"

        await db.execute(
            "UPDATE users SET level = ? WHERE telegram_id = ?", (level, place.user_id)
        )
        await db.commit()

    return {"status": "ok"}

@app.get("/api/places")
async def get_places():
    async with aiosqlite.connect("roadtop.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT p.*, u.username FROM places p JOIN users u ON p.user_id = u.telegram_id"
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "category": r["category"],
                "lat": r["lat"],
                "lon": r["lon"],
                "photo_url": r["photo_url"],
                "review": r["review"],
                "username": r["username"]
            }
            for r in rows
        ]