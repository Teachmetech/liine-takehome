# Liine Restaurant API

Take-home assessment for Liine by Varand Abrahamian (contact@varand.me).

## Project Overview

A FastAPI-based REST API that provides information about restaurant opening hours. The API allows users to:
- Query restaurants that are open at a specific date/time
- Perform CRUD operations on restaurant data
- Data is automatically loaded from provided CSV file on startup

### Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Primary database with optimized indexes for query performance
- **Redis**: Caching layer for optimizing query performance
- **SQLAlchemy**: SQL toolkit and ORM
- **Poetry**: Dependency management
- **Docker**: Containerization
- **pytest**: Testing framework

### Key Features

- RESTful API endpoints for restaurant management
- Redis caching for optimized query performance
- Automatic data loading from CSV
- Comprehensive datetime parsing for complex opening hours
- Full CRUD operations support
- Containerized deployment with Docker
- Comprehensive test suite
- Optimized database indexes for scalability
- Proper error handling with meaningful messages
- API documentation with Swagger and ReDoc

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Poetry (for local development)

### Installation & Running

1. Clone the repository:
```bash
git clone https://github.com/varand/liine-takehome.git
cd liine-takehome
```

2. Run with Docker:
```bash
docker-compose up --build
```

3. Run tests:
```bash
docker compose run --rm test
```

The API will be available at `http://localhost:8000`

### Local Development

1. Install dependencies:
```bash
poetry install
```

2. Activate virtual environment:
```bash
poetry shell
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

4. Run tests:
```bash
# Run all tests
pytest

# Run tests with output
pytest -v

# Run specific test
pytest tests/test_endpoints.py::test_overnight_hours -v

# Run tests with coverage
pytest --cov=app tests/
```

## API Endpoints

### Get Open Restaurants
```
GET /api/v1/restaurants/open?datetime={datetime}&use_cache={boolean}
```
- Returns a list of restaurants open at the specified datetime
- datetime format: ISO 8601 (e.g., "2024-03-15T19:30:00")
- use_cache: Optional boolean to bypass cache (default: true)
- Example: `GET /api/v1/restaurants/open?datetime=2024-03-15T19:30:00`

### Create Restaurant
```
POST /api/v1/restaurants/
```
- Creates a new restaurant
- Request body:
```json
{
    "name": "Restaurant Name",
    "hours": "Mon-Sun 11:00 am - 10:00 pm"
}
```

### Update Restaurant
```
PUT /api/v1/restaurants/{name}
```
- Updates an existing restaurant
- Request body same as CREATE

### Delete Restaurant
```
DELETE /api/v1/restaurants/{name}
```
- Deletes a restaurant by name

### Debug Endpoints
```
GET /api/v1/debug/restaurant-hours/{restaurant_name}
GET /api/v1/debug/data-loading
GET /api/v1/debug/cache/{datetime}
POST /api/v1/debug/clear-cache
```
- Created for my own debugging and testing purposes, when I came across issues. Left these in the codebase for the assesment.

## Implementation Details

### Data Storage
- PostgreSQL stores restaurant data with optimized indexes
- Redis caches query results for improved performance
- Cache invalidation occurs on any data modification. This is a simple implementation and could be improved with more sophisticated cache invalidation strategies.

### Database Optimization
- Composite indexes for efficient querying:
  - `idx_restaurant_hours_lookup`: For restaurant-specific queries
  - `idx_hours_search`: For time-based searches
  - `idx_hours_time_range`: For overnight hours
  - `idx_hours_full_search`: For the most common query pattern

### Time Parsing Strategy
- Supports various time formats (am/pm)
- Handles complex hour ranges
- Accounts for overnight hours (e.g., "5 pm - 2 am")
- Day ranges (e.g., "Mon-Fri")
- Multiple time ranges per day
- Proper handling of edge cases (exactly at opening/closing time)

### Caching Strategy
- Redis caches query results by datetime
- Cache TTL: 1 hour
- Automatic cache invalidation on data changes
- Cache bypass option for testing/debugging
- Improves response time for frequently requested times

### Error Handling
- Proper HTTP status codes (400, 404, etc.)
- Meaningful error messages
- Validation for datetime formats
- Proper handling of edge cases
- Debug endpoints for troubleshooting

### Testing
- Comprehensive test suite covering:
  - Regular business hours
  - Overnight hours
  - Complex hour patterns
  - Edge cases
  - Cache behavior
  - Error scenarios
- Integration tests with test database
- Fixtures for database and client setup
- Separate test environment with Docker

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
liine-assessment/
├── app/
│   ├── api/
│   │   └── endpoints.py      # API route handlers
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── time_parser.py   # Time parsing logic
│   ├── db/
│   │   ├── database.py      # Database connection
│   │   └── models.py        # SQLAlchemy models
│   ├── schemas/
│   │   └── restaurant.py    # Pydantic models
│   └── services/
│       ├── cache.py         # Redis caching
│       └── restaurant.py    # Business logic
├── tests/
│   ├── conftest.py          # Test configuration
│   └── test_endpoints.py    # API tests
├── docker-compose.yml       # Docker services config
├── Dockerfile              # API service container
├── pyproject.toml         # Poetry dependencies
└── README.md
```

## Assumptions

- All times are in local timezone
- If a day is not listed, the restaurant is closed
- CSV data is well-formed
- Restaurant names are unique

## Future Improvements

- Add timezone support
- Implement rate limiting
- Add authentication/authorization
- Add more comprehensive error handling
- Implement database migrations
- Add CI/CD pipeline
- Add logging and monitoring
- Implement bulk operations
- Add data validation for hours format