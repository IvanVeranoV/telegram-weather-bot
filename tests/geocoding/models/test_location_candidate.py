import math

import pytest

from src.geocoding.models.location_candidate import LocationCandidate, OSMType


def test_correct_creation():
    location_candidate = LocationCandidate(
        "Móstoles", "es", -45.23, 89.23, OSMType.WAY, 8, None
    )
    assert location_candidate.country == "ES"


@pytest.mark.parametrize("country", ["XX", "123"])
def test_false_country(country: str):
    with pytest.raises(
        ValueError,
        match=f"Country '{country}' is not a valid ISO 3166-1 alpha-2 country code",
    ):
        LocationCandidate("Móstoles", country, -45.23, 89.23, OSMType.WAY, 8, None)


@pytest.mark.parametrize("country", ["", "   "])
def test_empty_country(country: str):
    with pytest.raises(
        ValueError,
        match="Country must contain at least one non-whitespace character",
    ):
        LocationCandidate("Móstoles", country, -45.23, 89.23, OSMType.WAY, 8, None)


@pytest.mark.parametrize("country", [None, 123, True])
def test_invalid_country_type(country):
    with pytest.raises(TypeError, match="Country must be a string"):
        LocationCandidate("Móstoles", country, -45.23, 89.23, OSMType.WAY, 8, None)


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        (91, 0),
        (-91, 0),
        (0, 181),
        (0, -181),
    ],
)
def test_coordinates_out_of_bounds(latitude, longitude):
    with pytest.raises(ValueError):
        LocationCandidate("Móstoles", "ES", latitude, longitude, OSMType.WAY, 8)


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        (True, 0),
        (False, 0),
        (0, True),
        (0, False),
    ],
)
def test_coordinates_boolean(latitude, longitude):
    with pytest.raises(TypeError):
        LocationCandidate("Móstoles", "ES", latitude, longitude, OSMType.WAY, 8)


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        ("40.32", 0),
        (0, "-3.86"),
        (None, 0),
        (0, None),
    ],
)
def test_coordinates_invalid_type(latitude, longitude):
    with pytest.raises(TypeError):
        LocationCandidate("Móstoles", "ES", latitude, longitude, OSMType.WAY, 8)


@pytest.mark.parametrize(
    "coordinate",
    [
        math.nan,
        math.inf,
        -math.inf,
    ],
)
@pytest.mark.parametrize("is_latitude", [True, False])
def test_coordinates_not_finite(coordinate, is_latitude):
    latitude = coordinate if is_latitude else 0
    longitude = 0 if is_latitude else coordinate

    with pytest.raises(ValueError):
        LocationCandidate("Móstoles", "ES", latitude, longitude, OSMType.WAY, 8)


def test_integer_coordinates_are_normalized_to_float():
    location_candidate = LocationCandidate("Móstoles", "ES", 40, -3, OSMType.WAY, 8)

    assert isinstance(location_candidate.latitude, float)
    assert isinstance(location_candidate.longitude, float)
    assert location_candidate.latitude == 40.0
    assert location_candidate.longitude == -3.0
