# ✈️ Trip Planner AI

An agentic AI workflow that generates a personalized trip planning report in PDF format based on your destination, budget, duration, and interests.

## 🔄 Workflow (7 Steps)

1. **Input** – User provides destination, budget, duration, and interests
2. **Search Attractions** – Tavily searches attractions by category
3. **Rank Attractions** – LLM ranks results by user interests and ratings
4. **Select Attractions** – LLM filters top picks that fit budget and time
5. **Generate Itinerary** – LLM clusters attractions into a day-by-day plan
6. **Estimate Budget** – LLM calculates cost breakdown per category
7. **Generate Report** – Final trip plan compiled into a PDF report

## 🛠️ Tech Stack

- **FastAPI** – REST API
- **Celery** – Async task queue
- **Redis** – Message broker
- **Tavily** – Web search for attractions
- **OpenRouter** – LLM provider (Gemini Flash + GPT)
- **WeasyPrint** – PDF generation

## ⚙️ Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Docker (for Redis)
- [GTK3 for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) (WeasyPrint dependency)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/davadinata/trip-planner.git
cd trip-planner
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Setup environment variables

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 4. Run the services (3 separate terminals)

**Terminal 1 – Redis**

```bash
docker run -d -p 6379:6379 redis
```

**Terminal 2 – FastAPI**

```bash
make dev
```

**Terminal 3 – Celery Worker**

```bash
make celery
```

## 📬 API Usage

### POST `/trip`

```json
{
  "destination": "Yogyakarta",
  "duration_days": 7,
  "total_budget": "10000000 IDR",
  "num_people": 2,
  "interests": "culture, nature, culinary"
}
```

The task runs asynchronously. Once completed, the output PDF will be saved as `trip-report.pdf` in the project root.
