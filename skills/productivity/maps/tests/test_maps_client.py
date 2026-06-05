import pytest
import math
from skills.productivity.maps.scripts.maps_client import haversine_m

def test_haversine_same_point():
    """Distance between the same point should be 0."""
    lat, lon = 51.5074, -0.1278 # London
    distance = haversine_m(lat, lon, lat, lon)
    assert distance == 0.0

def test_haversine_known_distance():
    """Distance between Paris and London should be approximately 343 km."""
    # Paris: 48.8566 N, 2.3522 E
    # London: 51.5074 N, 0.1278 W (-0.1278)
    paris_lat, paris_lon = 48.8566, 2.3522
    london_lat, london_lon = 51.5074, -0.1278

    distance = haversine_m(paris_lat, paris_lon, london_lat, london_lon)
    # Expected distance is ~343,500 meters
    expected_distance = 343500

    # 1% tolerance due to Earth being an oblate spheroid and our fixed radius assumption
    tolerance = expected_distance * 0.01
    assert abs(distance - expected_distance) <= tolerance

def test_haversine_antipodal_points():
    """Distance between antipodal points should be exactly half circumference."""
    # North Pole: 90, 0
    # South Pole: -90, 0
    np_lat, np_lon = 90.0, 0.0
    sp_lat, sp_lon = -90.0, 0.0

    distance = haversine_m(np_lat, np_lon, sp_lat, sp_lon)
    R = 6_371_000
    expected_distance = math.pi * R

    # Check with very small tolerance for floating point variations
    assert math.isclose(distance, expected_distance, rel_tol=1e-9)

def test_haversine_invalid_inputs():
    """Invalid inputs like strings or None should raise TypeError."""
    with pytest.raises(TypeError):
        haversine_m("51.5074", "-0.1278", 48.8566, 2.3522)

    with pytest.raises(TypeError):
        haversine_m(51.5074, -0.1278, None, 2.3522)
