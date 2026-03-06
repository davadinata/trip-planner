# main.py
from fastapi import FastAPI
from app.modules.trip.schema import TripInput
from app.modules.trip.task import trip_task 
from scalar_fastapi import get_scalar_api_reference
app = FastAPI()

@app.post("/trip")
def create_trip(trip: TripInput):
    trip_task.delay(
        destination=trip.destination,
        duration_days=trip.duration_days,
        total_budget=trip.total_budget,
        num_people=trip.num_people,
        interests=trip.interests,
    )
    return {"message": "Trip planning started!"}

@app.get("/scalar")
def get_scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )
    
