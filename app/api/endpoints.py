from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import restaurant as schemas
from app.services import restaurant as restaurant_service
from app.services import cache as cache_service

router = APIRouter()


@router.get("/restaurants/open", response_model=List[str])
def get_open_restaurants(
    datetime: str, use_cache: bool = True, db: Session = Depends(get_db)
):
    """Get all restaurants open at the specified datetime"""
    try:
        if use_cache:
            # Check cache first
            cached_result = cache_service.get_cached_restaurants(datetime)
            if cached_result is not None:
                return cached_result

        # Query database
        restaurants = restaurant_service.get_open_restaurants(db, datetime)

        if use_cache:
            # Cache the result
            cache_service.set_cached_restaurants(datetime, restaurants)

        return restaurants
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/restaurants/", response_model=schemas.Restaurant)
def create_restaurant(
    restaurant: schemas.RestaurantCreate, db: Session = Depends(get_db)
):
    """Create a new restaurant"""
    db_restaurant = restaurant_service.get_restaurant_by_name(db, restaurant.name)
    if db_restaurant:
        raise HTTPException(status_code=400, detail="Restaurant already exists")

    result = restaurant_service.create_restaurant(db, restaurant)
    cache_service.invalidate_cache()
    return result


@router.put("/restaurants/{name}", response_model=schemas.Restaurant)
def update_restaurant(
    name: str, restaurant: schemas.RestaurantUpdate, db: Session = Depends(get_db)
):
    """Update a restaurant by name"""
    db_restaurant = restaurant_service.update_restaurant(db, name, restaurant)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    cache_service.invalidate_cache()
    return db_restaurant


@router.delete("/restaurants/{name}")
def delete_restaurant(name: str, db: Session = Depends(get_db)):
    """Delete a restaurant by name"""
    success = restaurant_service.delete_restaurant(db, name)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    cache_service.invalidate_cache()
    return {"message": "Restaurant deleted successfully"}


@router.get("/restaurants/", response_model=List[schemas.Restaurant])
def get_all_restaurants(db: Session = Depends(get_db)):
    """Get all restaurants"""
    return restaurant_service.get_all_restaurants(db)


@router.get("/debug/data-loading")
def check_data_loading(db: Session = Depends(get_db)):
    """Temporary endpoint to verify data loading"""
    return restaurant_service.verify_data_loading(db)


@router.get("/debug/restaurant-hours/{restaurant_name}")
def get_restaurant_hours(restaurant_name: str, db: Session = Depends(get_db)):
    """Debug endpoint to view a restaurant's hours"""
    restaurant = restaurant_service.get_restaurant_by_name(db, restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return {
        "name": restaurant.name,
        "hours": [
            {
                "day": h.day_of_week,
                "open_time": h.open_time.strftime("%H:%M"),
                "close_time": h.close_time.strftime("%H:%M"),
            }
            for h in restaurant.hours
        ],
    }


@router.post("/debug/clear-cache")
def clear_cache():
    """Clear all cached data"""
    cache_service.invalidate_cache()
    return {"message": "Cache cleared"}


@router.get("/debug/cache/{datetime}")
def check_cache(datetime: str):
    """Check what's in the cache for a given datetime"""
    cached = cache_service.get_cached_restaurants(datetime)
    return {
        "datetime": datetime,
        "cached_data": cached,
        "is_cached": cached is not None,
    }
