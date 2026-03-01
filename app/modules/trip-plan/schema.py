from pydantic import BaseModel, Field


class TripInput(BaseModel):
    destination: str
    duration_days: int
    total_budget: str
    num_people: int
    interests: str

class Destination(BaseModel):
    attractions: list[str] = Field(description="List of destination from search")

class RankSchema(BaseModel):
    ranked: list[str] = Field(description="Destination rank")


class Selected(BaseModel):
    selected: list[str] = Field(description="Top attractions that fit budget and time")


class ItinerarySchema(BaseModel):
    days: list[str] = Field(description="Day-by-day itinerary grouped by location")


class BudgetSchema(BaseModel):
    breakdown: list[str] = Field(description="Cost breakdown per category")
    total_estimate: str
    is_sufficient: bool