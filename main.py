from Databases.mongoRepository import mongo_database, mongo_client
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import dotenv_values
from Room.routes import router as room_router
from User.routes import router as user_router
from Booking.routes import router as booking_router

global app
config = dotenv_values(".env")
app = FastAPI()


@app.get("/", description="Точка входа", summary="Вход", include_in_schema=False)
def home_page():
    return RedirectResponse("/docs")


@app.on_event("startup")
def startup_db_client():
    config = dotenv_values(".env")
    app.mongodb_client = mongo_client
    app.database = mongo_database

    print("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(user_router, tags=["Пользователи"], prefix="/user")
app.include_router(room_router, tags=["Комнаты"], prefix="/room")
app.include_router(booking_router, tags=["Бронирования"], prefix="/booking")

# run this command in cmd:
# uvicorn main:app --reload --host 0.0.0.0
