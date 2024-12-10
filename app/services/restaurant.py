from typing import List, Optional
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
import logging
from app.db import models
from app.schemas import restaurant as schemas
from app.core.time_parser import parse_hours_string

logger = logging.getLogger(__name__)


def get_restaurants(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Restaurant]:
    return db.query(models.Restaurant).offset(skip).limit(limit).all()


def get_open_restaurants(db: Session, datetime_str: str) -> List[str]:
    """Get all restaurants open at the specified datetime"""
    try:
        # Parse the datetime string
        dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        current_time = dt.time()
        day_of_week = dt.weekday()

        # Convert Python's weekday (0=Monday) to our format (0=Sunday)
        day_of_week = (day_of_week + 1) % 7
        previous_day = (day_of_week - 1) % 7

        logger.debug(
            f"Checking restaurants open on day {day_of_week} at time {current_time}"
        )

        # Build the query with proper time conditions
        query = (
            db.query(models.Restaurant.name)
            .join(models.RestaurantHours)
            .filter(
                or_(
                    # Case 1: Current day's normal hours
                    and_(
                        models.RestaurantHours.day_of_week == day_of_week,
                        models.RestaurantHours.open_time <= current_time,
                        models.RestaurantHours.close_time > current_time,
                        models.RestaurantHours.close_time
                        > models.RestaurantHours.open_time,
                    ),
                    # Case 2: Current day's overnight hours (open today, closes after midnight)
                    and_(
                        models.RestaurantHours.day_of_week == day_of_week,
                        models.RestaurantHours.open_time <= current_time,
                        models.RestaurantHours.close_time
                        < models.RestaurantHours.open_time,
                    ),
                    # Case 3: Previous day's overnight hours (opened yesterday, closes today)
                    and_(
                        models.RestaurantHours.day_of_week == previous_day,
                        models.RestaurantHours.close_time
                        < models.RestaurantHours.open_time,
                        current_time < models.RestaurantHours.close_time,
                    ),
                )
            )
            .distinct()
            .order_by(models.Restaurant.name)
        )

        results = [restaurant.name for restaurant in query.all()]
        logger.debug(
            f"Found {len(results)} open restaurants at {current_time} on day {day_of_week}"
        )
        return results

    except ValueError as e:
        logger.error(f"Error parsing datetime '{datetime_str}': {str(e)}")
        raise ValueError(
            f"Invalid datetime format. Please use ISO format (e.g., '2024-03-15T19:30:00')"
        )


def create_restaurant(
    db: Session, restaurant: schemas.RestaurantCreate
) -> models.Restaurant:
    """Create a restaurant with its hours"""
    db_restaurant = models.Restaurant(name=restaurant.name)
    db.add(db_restaurant)
    db.flush()  # Get the ID without committing

    # Parse hours and create RestaurantHours entries
    hours_entries = parse_hours_string(restaurant.hours)
    for entry in hours_entries:
        db_hours = models.RestaurantHours(
            restaurant_id=db_restaurant.id,
            day_of_week=entry.day_of_week,
            open_time=entry.open_time,
            close_time=entry.close_time,
        )
        db.add(db_hours)

    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


def get_restaurant_by_name(db: Session, name: str) -> Optional[models.Restaurant]:
    return db.query(models.Restaurant).filter(models.Restaurant.name == name).first()


def update_restaurant(
    db: Session, name: str, restaurant: schemas.RestaurantUpdate
) -> Optional[models.Restaurant]:
    """Update a restaurant and its hours"""
    db_restaurant = get_restaurant_by_name(db, name)
    if db_restaurant:
        # Update name
        db_restaurant.name = restaurant.name

        # Delete existing hours
        for hour in db_restaurant.hours:
            db.delete(hour)

        # Add new hours
        hours_entries = parse_hours_string(restaurant.hours)
        for entry in hours_entries:
            db_hours = models.RestaurantHours(
                restaurant_id=db_restaurant.id,
                day_of_week=entry.day_of_week,
                open_time=entry.open_time,
                close_time=entry.close_time,
            )
            db.add(db_hours)

        db.commit()
        db.refresh(db_restaurant)
    return db_restaurant


def delete_restaurant(db: Session, name: str) -> bool:
    db_restaurant = get_restaurant_by_name(db, name)
    if db_restaurant:
        db.delete(db_restaurant)
        db.commit()
        return True
    return False


def get_all_restaurants(db: Session) -> List[models.Restaurant]:
    """Get all restaurants from the database"""
    return db.query(models.Restaurant).all()


def verify_data_loading(db: Session) -> dict:
    """Verify that all data was loaded correctly"""
    restaurants = db.query(models.Restaurant).all()
    hours = db.query(models.RestaurantHours).all()

    return {
        "total_restaurants": len(restaurants),
        "total_hours_entries": len(hours),
        "restaurants": [
            {"name": r.name, "hours_entries": len(r.hours)} for r in restaurants
        ],
    }
