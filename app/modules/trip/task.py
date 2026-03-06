import json
from markdown import markdown
from weasyprint import HTML
from datetime import datetime
from app.celery_app import celery_app

from app.modules.trip.methods import (
    search_attractions,
    rank_attractions,
    select_attractions,
    generate_itinerary,
    estimate_budget,
    generate_report,
)
from app.modules.trip.schema import TripInput

CSS_STYLE = """
<style>
    @page {
        margin: 40px 60px;
    }
    body { 
        font-family: Georgia, serif; 
        font-size: 13px; 
        line-height: 1.8; 
        color: #222; 
    }
    h1 { 
        font-size: 22px; 
        border-bottom: 2px solid #1a1a2e; 
        padding-bottom: 10px;
        margin-bottom: 4px;
        color: #1a1a2e;
    }
    h2 { 
        font-size: 16px; 
        color: #1a1a2e; 
        margin-top: 28px; 
        margin-bottom: 8px;
        border-bottom: 1px solid #ddd;
        padding-bottom: 4px;
    }
    h3 { 
        font-size: 14px; 
        color: #333;
        margin-top: 14px;
        margin-bottom: 6px;
    }
    p { 
        margin-bottom: 10px; 
        text-align: justify;
    }
    ul { 
        padding-left: 18px; 
        margin-bottom: 10px;
    }
    ul li { 
        margin-bottom: 5px; 
        line-height: 1.7;
    }
    ol li {
        margin-bottom: 5px;
        line-height: 1.7;
    }
    strong { 
        color: #111; 
    }
    hr { 
        border: none; 
        border-top: 1px solid #ddd; 
        margin: 16px 0; 
    }
    /* Header meta info */
    em {
        color: #555;
        font-size: 12px;
    }
    /* Section spacing */
    h2 + p, h2 + ul, h3 + p, h3 + ul {
        margin-top: 6px;
    }
</style>
"""

def plan_trip(trip: TripInput):
    # Step 2: Search
    attractions = search_attractions(trip)

    # Step 3: Rank
    ranked = rank_attractions(trip, attractions)

    # Step 4: Select
    selected = select_attractions(trip, ranked)

    # Step 5: Itinerary
    itinerary = generate_itinerary(trip, selected)

    # Step 6: Budget
    budget = estimate_budget(trip, itinerary)

    # Build context for report
    trip_context = f"""
    Attractions Found: {json.dumps(attractions.attractions)}

    Selected Attractions: {json.dumps(selected.selected)}

    Day-by-Day Itinerary:
    {chr(10).join(f"Day {i+1}: {day}" for i, day in enumerate(itinerary.days))}

    Budget Breakdown:
    {chr(10).join(budget.breakdown)}
    Total Estimate: {budget.total_estimate}
    Budget Sufficient: {"Yes" if budget.is_sufficient else "No"}
    """

    # Step 7: Report
    report_result = generate_report(trip=trip, trip_context=trip_context)
    if not report_result:
        raise ValueError("No trip report generated")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trip-{trip.destination}-{timestamp}.pdf"
    
    result = markdown(text=report_result, output_format="html")
    full_html = f"<html><head>{CSS_STYLE}</head><body>{result}</body></html>"
    HTML(string=full_html).write_pdf(filename)


@celery_app.task
def trip_task(
    destination: str,
    duration_days: int,
    total_budget: str,
    num_people: int,
    interests: str,
):
    trip = TripInput(
        destination=destination,
        duration_days=duration_days,
        total_budget=total_budget,
        num_people=num_people,
        interests=interests,
    )
    plan_trip(trip)