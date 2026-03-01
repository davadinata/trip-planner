from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

app = FastAPI() 

@app.post("/trip-plan")
def create_travel_plan():
    return {"message": "Trip plan is processing..."}

@app.get("/scalar")
def get_scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )
    

