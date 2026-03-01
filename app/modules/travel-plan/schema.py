from pydantic import BaseModel, Field

class QueriesSchema(BaseModel): 
    query: list[str] =  Field(description="List of queries to generate travel plan")
    
class TravelPlan(BaseModel):
    plan : str 