import csv
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.db.database import engine, get_db
from app.db import models
from app.api import endpoints
from app.schemas import restaurant as schemas
from app.services import restaurant as restaurant_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application"""
    # Startup: Load initial data
    db = next(get_db())
    try:
        load_initial_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Liine Restaurant API", lifespan=lifespan)

# Create database tables
models.Base.metadata.create_all(bind=engine)


def load_initial_data(db: Session):
    """Load initial data from CSV file"""
    try:
        # First, check how many restaurants are already in the database
        existing_count = db.query(models.Restaurant).count()
        logger.info(f"Found {existing_count} existing restaurants in database")

        # Read and process restaurants from CSV
        with open("restaurants.csv", "r") as file:
            # Count total restaurants
            total_restaurants = sum(1 for _ in csv.DictReader(file))
            logger.info(f"Found {total_restaurants} restaurants in CSV")

            # Only proceed if we need to add restaurants
            if existing_count < total_restaurants:
                logger.info(
                    f"Loading {total_restaurants - existing_count} new restaurants from CSV"
                )

                # Reset file pointer and skip header
                file.seek(0)
                csv_reader = csv.DictReader(file)

                # Keep track of processed restaurants
                processed = 0

                for row in csv_reader:
                    restaurant_name = row["Restaurant Name"]
                    # Check if restaurant already exists
                    if (
                        not db.query(models.Restaurant)
                        .filter_by(name=restaurant_name)
                        .first()
                    ):
                        try:
                            restaurant = schemas.RestaurantCreate(
                                name=restaurant_name, hours=row["Hours"]
                            )
                            restaurant_service.create_restaurant(db, restaurant)
                            processed += 1
                            logger.info(f"Added restaurant: {restaurant_name}")
                        except Exception as e:
                            logger.error(
                                f"Error adding restaurant {restaurant_name}: {str(e)}"
                            )
                    else:
                        logger.debug(f"Restaurant already exists: {restaurant_name}")

                logger.info(f"Successfully processed {processed} new restaurants")
            else:
                logger.info("All restaurants already loaded in database")

    except Exception as e:
        logger.error(f"Error loading initial data: {str(e)}")
        raise


app.include_router(endpoints.router, prefix="/api/v1")
