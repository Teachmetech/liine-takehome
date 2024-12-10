from uuid import UUID
from datetime import time
from typing import List
from pydantic import BaseModel, ConfigDict


class RestaurantHoursBase(BaseModel):
    day_of_week: int
    open_time: time
    close_time: time

    model_config = ConfigDict(from_attributes=True)


class RestaurantHours(RestaurantHoursBase):
    id: UUID
    restaurant_id: UUID


class RestaurantBase(BaseModel):
    name: str


class RestaurantCreate(RestaurantBase):
    hours: str  # String format for input


class RestaurantUpdate(RestaurantCreate):
    pass


class Restaurant(RestaurantBase):
    id: UUID
    hours: List[RestaurantHoursBase]  # List of hours for output

    model_config = ConfigDict(from_attributes=True)
