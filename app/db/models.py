import uuid
from sqlalchemy import Column, String, SmallInteger, Time, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    hours = relationship(
        "RestaurantHours", back_populates="restaurant", cascade="all, delete-orphan"
    )


class RestaurantHours(Base):
    __tablename__ = "restaurant_hours"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(
        UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE")
    )
    day_of_week = Column(SmallInteger)  # 0=Sunday, 1=Monday, ..., 6=Saturday
    open_time = Column(Time)
    close_time = Column(Time)

    restaurant = relationship("Restaurant", back_populates="hours")

    # Composite indexes for efficient querying
    __table_args__ = (
        # Index for looking up hours by restaurant
        Index("idx_restaurant_hours_lookup", "restaurant_id", "day_of_week"),
        # Index for finding restaurants open at a specific time on a specific day
        Index("idx_hours_search", "day_of_week", "open_time", "close_time"),
        # Index for time range queries (helps with overnight hours)
        Index("idx_hours_time_range", "day_of_week", "open_time"),
        Index("idx_hours_time_range_close", "day_of_week", "close_time"),
        # Composite index for the most common query pattern
        Index(
            "idx_hours_full_search",
            "day_of_week",
            "open_time",
            "close_time",
            "restaurant_id",
        ),
    )
