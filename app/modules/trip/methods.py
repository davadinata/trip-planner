import json
import logging

from app.utils.openai import oa_client
from app.utils.tavily import tavily_client
from .prompt import TRIP_REPORT_SYSTEM_PROMPT
from .schema import (
    TripInput,
    AttractionsSchema,
    RankedAttractionsSchema,
    SelectedAttractionsSchema,
    ItinerarySchema,
    BudgetSchema,
)

logger = logging.getLogger(__name__)


# Step 2: Search (use Tavily)
def search_attractions(trip: TripInput) -> AttractionsSchema:
    categories = trip.interests.split(",")
    all_results = ""

    for category in categories:
        query = f"top {category.strip()} attractions in {trip.destination}"
        result = tavily_client.search(
            query=query, search_depth="advanced", include_raw_content="markdown"
        )
        all_results += f"\nCategory: {category}\nResults: {json.dumps(result)}\n"

    response = oa_client.chat.completions.parse(
        model="google/gemini-3-flash-preview",
        messages=[
            {
                "role": "system",
                "content": "Extract a clean list of attraction names and brief descriptions from these search results.",
            },
            {"role": "user", "content": all_results},
        ],
        response_format=AttractionsSchema,
    )

    parsed = response.choices[0].message.parsed.model_dump()  # type: ignore
    logger.info(f"Attractions found: {parsed}")
    return AttractionsSchema(**parsed)


# Step 3: Filter (by relevance)
def rank_attractions(trip: TripInput, attractions: AttractionsSchema) -> RankedAttractionsSchema:
    response = oa_client.chat.completions.parse(
        model="google/gemini-3-flash-preview",
        messages=[
            {
                "role": "system",
                "content": (
                    "Rank these attractions based on the user's interests and estimated ratings. "
                    "Prioritize variety and quality."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Interests: {trip.interests}\n"
                    f"Attractions: {json.dumps(attractions.attractions)}"
                ),
            },
        ],
        response_format=RankedAttractionsSchema,
    )

    parsed = response.choices[0].message.parsed.model_dump()  # type: ignore
    logger.info(f"Ranked attractions: {parsed}")
    return RankedAttractionsSchema(**parsed)


# Step 4: Select the top destinations (considering budget and time) 
def select_attractions(trip: TripInput, ranked: RankedAttractionsSchema) -> SelectedAttractionsSchema:
    response = oa_client.chat.completions.parse(
        model="google/gemini-3-flash-preview",
        messages=[
            {
                "role": "system",
                "content": (
                    "Select the best attractions that realistically fit within the given "
                    "budget and number of days. Avoid over-packing the schedule."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Duration: {trip.duration_days} days\n"
                    f"Budget: {trip.total_budget}\n"
                    f"People: {trip.num_people}\n"
                    f"Ranked Attractions: {json.dumps(ranked.ranked)}"
                ),
            },
        ],
        response_format=SelectedAttractionsSchema,
    )

    parsed = response.choices[0].message.parsed.model_dump()  # type: ignore
    logger.info(f"Selected attractions: {parsed}")
    return SelectedAttractionsSchema(**parsed)


# Step 5: Generate
def generate_itinerary(trip: TripInput, selected: SelectedAttractionsSchema) -> ItinerarySchema:
    response = oa_client.chat.completions.parse(
        model="google/gemini-3-flash-preview",
        messages=[
            {
                "role": "system",
                "content": (
                    "Create a day-by-day itinerary by clustering attractions by location. "
                    "Each day should have morning, afternoon, and evening activities. "
                    "Keep it realistic and enjoyable."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Destination: {trip.destination}\n"
                    f"Duration: {trip.duration_days} days\n"
                    f"Selected Attractions: {json.dumps(selected.selected)}"
                ),
            },
        ],
        response_format=ItinerarySchema,
    )

    parsed = response.choices[0].message.parsed.model_dump()  # type: ignore
    logger.info(f"Itinerary: {parsed}")
    return ItinerarySchema(**parsed)


# Step 6: Calculate cost
def estimate_budget(trip: TripInput, itinerary: ItinerarySchema) -> BudgetSchema:
    response = oa_client.chat.completions.parse(
        model="google/gemini-3-flash-preview",
        messages=[
            {
                "role": "system",
                "content": (
                    "Estimate the total trip cost breakdown including accommodation, "
                    "meals, transport, and activities. Flag whether the budget is sufficient."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Destination: {trip.destination}\n"
                    f"Duration: {trip.duration_days} days\n"
                    f"People: {trip.num_people}\n"
                    f"Total Budget: {trip.total_budget}\n"
                    f"Itinerary: {json.dumps(itinerary.days)}"
                ),
            },
        ],
        response_format=BudgetSchema,
    )

    parsed = response.choices[0].message.parsed.model_dump()  # type: ignore
    logger.info(f"Budget estimate: {parsed}")
    return BudgetSchema(**parsed)


# Step 7: Generate report
def generate_report(trip: TripInput, trip_context: str) -> str:
    response = oa_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": TRIP_REPORT_SYSTEM_PROMPT.format(
                    trip_context=trip_context,
                    destination=trip.destination,
                    duration_days=trip.duration_days,
                    total_budget=trip.total_budget,
                    num_people=trip.num_people,
                ),
            },
            {
                "role": "user",
                "content": f"Generate the complete trip plan report for {trip.destination}.",
            },
        ],
        extra_body={"reasoning": {"enabled": True}},
    )

    return response.choices[0].message.content  # type: ignore