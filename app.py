import joblib
import numpy as np
 
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
 
from config.paths_config import MODEL_OUTPUT_PATH
 
app = FastAPI(title="Hotel Reservation Prediction")
 
app.mount("/static", StaticFiles(directory="static"), name="static")
 
templates = Jinja2Templates(directory="templates")
 
loaded_model = joblib.load(MODEL_OUTPUT_PATH)
 
 
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"prediction": None}
    )
 
 
@app.post("/", response_class=HTMLResponse)
async def predict(
    request: Request,
    lead_time: int = Form(...),
    no_of_special_request: int = Form(...),
    avg_price_per_room: float = Form(...),
    arrival_month: int = Form(...),
    arrival_date: int = Form(...),
    market_segment_type: int = Form(...),
    no_of_week_nights: int = Form(...),
    no_of_weekend_nights: int = Form(...),
    type_of_meal_plan: int = Form(...),
    room_type_reserved: int = Form(...)
):
 
    features = np.array([[
        lead_time,
        no_of_special_request,
        avg_price_per_room,
        arrival_month,
        arrival_date,
        market_segment_type,
        no_of_week_nights,
        no_of_weekend_nights,
        type_of_meal_plan,
        room_type_reserved
    ]])
 
    prediction = loaded_model.predict(features)[0]
 
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"prediction": int(prediction)}
    )