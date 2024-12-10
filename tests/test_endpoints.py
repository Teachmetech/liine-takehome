import pytest


@pytest.fixture
def test_restaurant(client):
    """Create a test restaurant with standard hours"""
    response = client.post(
        "/api/v1/restaurants/",
        json={"name": "Test Restaurant", "hours": "Mon-Sun 11:00 am - 10:00 pm"},
    )
    return response.json()


@pytest.fixture
def overnight_restaurant(client):
    """Create a restaurant with overnight hours"""
    response = client.post(
        "/api/v1/restaurants/",
        json={"name": "Night Owl Restaurant", "hours": "Mon-Sun 5:00 pm - 2:00 am"},
    )
    return response.json()


@pytest.fixture
def complex_hours_restaurant(client):
    """Create a restaurant with different hours on different days"""
    response = client.post(
        "/api/v1/restaurants/",
        json={
            "name": "Complex Hours Restaurant",
            "hours": "Mon-Thu 11:00 am - 10:00 pm / Fri-Sat 11:00 am - 1:30 am / Sun 10:00 am - 9:00 pm",
        },
    )
    return response.json()


def test_regular_hours(client, test_restaurant):
    """Test regular business hours"""
    # Test just after opening
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T11:01:00")
    assert test_restaurant["name"] in response.json()

    # Test during middle of day
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T15:00:00")
    assert test_restaurant["name"] in response.json()

    # Test just before closing
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T21:59:00")
    assert test_restaurant["name"] in response.json()


def test_closed_hours(client, test_restaurant):
    """Test when restaurant should be closed"""
    # Test just before opening
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T10:59:00")
    assert test_restaurant["name"] not in response.json()

    # Test just after closing
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T22:01:00")
    assert test_restaurant["name"] not in response.json()

    # Test middle of night
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T03:00:00")
    assert test_restaurant["name"] not in response.json()


def test_overnight_hours(client, overnight_restaurant):
    """Test restaurant with hours that go past midnight"""
    # Test evening (should be open)
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T20:00:00")
    assert overnight_restaurant["name"] in response.json()

    # Test after midnight (should be open)
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-16T01:30:00")
    assert overnight_restaurant["name"] in response.json()

    # Test after closing time (should be closed)
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-16T02:30:00")
    assert overnight_restaurant["name"] not in response.json()


def test_complex_hours(client, complex_hours_restaurant):
    """Test restaurant with different hours on different days"""
    # Test Friday late night (should be open)
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T23:30:00")
    assert complex_hours_restaurant["name"] in response.json()

    # Test Sunday evening (should be open)
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-17T20:00:00")
    assert complex_hours_restaurant["name"] in response.json()

    # Test Sunday late (should be closed)
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-17T21:30:00")
    assert complex_hours_restaurant["name"] not in response.json()


def test_edge_cases(client, test_restaurant):
    """Test edge cases like exactly at opening/closing time"""
    # Test exactly at opening time (should be open)
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T11:00:00")
    assert test_restaurant["name"] in response.json()

    # Test exactly at closing time (should be closed)
    response = client.get("/api/v1/restaurants/open?datetime=2024-03-15T22:00:00")
    assert test_restaurant["name"] not in response.json()


def test_invalid_datetime_format(client):
    """Test invalid datetime format"""
    response = client.get("/api/v1/restaurants/open?datetime=invalid-format")
    assert response.status_code == 400
    assert "Invalid datetime format" in response.json()["detail"]


def test_cache_behavior(client, test_restaurant):
    """Test that caching works correctly"""
    # First request (cache miss)
    datetime_str = "2024-03-15T15:00:00"
    response1 = client.get(f"/api/v1/restaurants/open?datetime={datetime_str}")

    # Check cache
    cache_response = client.get(f"/api/v1/debug/cache/{datetime_str}")
    assert cache_response.json()["is_cached"] == True

    # Clear cache
    client.post("/api/v1/debug/clear-cache")

    # Verify cache is cleared
    cache_response = client.get(f"/api/v1/debug/cache/{datetime_str}")
    assert cache_response.json()["is_cached"] == False


def test_create_restaurant(client):
    """Test creating a restaurant"""
    response = client.post(
        "/api/v1/restaurants/",
        json={"name": "Test Restaurant", "hours": "Mon-Sun 11:00 am - 10:00 pm"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Restaurant"
    assert len(data["hours"]) == 7  # Should have 7 days of hours

    # Verify hours structure
    for hour in data["hours"]:
        assert "day_of_week" in hour
        assert "open_time" in hour
        assert "close_time" in hour
