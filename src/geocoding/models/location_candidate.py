import math
from dataclasses import dataclass
from enum import StrEnum

import pycountry

LATITUDE_POSITIVE_LIMIT: float = 90
LATITUDE_NEGATIVE_LIMIT: float = -90
LONGITUDE_POSITIVE_LIMIT: float = 180
LONGITUDE_NEGATIVE_LIMIT: float = -180


class OSMType(StrEnum):
    NODE = "node"
    WAY = "way"
    RELATION = "relation"


@dataclass(frozen=True, slots=True)
class LocationCandidate:
    name: str
    country: str
    latitude: float | int
    longitude: float | int
    osm_type: OSMType
    osm_id: int
    region: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "name", _validate_non_white_string("Name", self.name))
        object.__setattr__(self, "country", _validate_country(self.country))
        object.__setattr__(
            self,
            "latitude",
            _validate_coordinate_part(
                "Latitude",
                self.latitude,
                LATITUDE_POSITIVE_LIMIT,
                LATITUDE_NEGATIVE_LIMIT,
            ),
        )
        object.__setattr__(
            self,
            "longitude",
            _validate_coordinate_part(
                "Longitude",
                self.longitude,
                LONGITUDE_POSITIVE_LIMIT,
                LONGITUDE_NEGATIVE_LIMIT,
            ),
        )
        object.__setattr__(self, "osm_type", _validate_osm_type(self.osm_type))
        object.__setattr__(self, "osm_id", _validate_osm_id(self.osm_id))
        if self.region is not None:
            object.__setattr__(
                self, "region", _validate_non_white_string("Region", self.region)
            )


def _validate_country(unvalidated_country: str) -> str:

    validated_country = _validate_non_white_string(
        "Country", unvalidated_country
    ).upper()
    if not pycountry.countries.get(alpha_2=validated_country):
        raise ValueError(
            f"Country '{validated_country}' is not a valid ISO 3166-1 alpha-2 country code"
        )

    return validated_country


def _validate_non_white_string(str_name: str, unvalidated_str: str) -> str:
    if not isinstance(unvalidated_str, str):
        raise TypeError(str_name + " must be a string")
    if not unvalidated_str.strip():
        raise ValueError(
            str_name + " must contain at least one non-whitespace character"
        )
    return unvalidated_str.strip()


def _validate_coordinate_part(
    coordinate_name: str,
    coordinate_part_value: float,
    positive_limit: float,
    negative_limit: float,
) -> float:
    if isinstance(coordinate_part_value, bool):
        raise TypeError(coordinate_name + " cannot be a boolean (True/False) value")
    if isinstance(coordinate_part_value, str):
        raise TypeError(coordinate_name + " cannot be a string")
    if isinstance(coordinate_part_value, float):
        if _is_in_limits(coordinate_part_value, positive_limit, negative_limit):
            return coordinate_part_value
        else:
            raise ValueError(coordinate_name + " value is out of bounds")
    if isinstance(coordinate_part_value, int):
        formatted_value = float(coordinate_part_value)
        if _is_in_limits(formatted_value, positive_limit, negative_limit):
            return formatted_value
        else:
            raise ValueError(coordinate_name + " value is out of bounds")
    else:
        raise TypeError(coordinate_name + " type is not valid")


def _is_in_limits(value: float, positive_limit: float, negative_limit: float) -> bool:
    return math.isfinite(value) and (negative_limit <= value <= positive_limit)


def _validate_osm_type(unvalidated_osm_type: OSMType) -> OSMType:
    if not isinstance(unvalidated_osm_type, OSMType):
        raise TypeError("OSMType must be OSMType")
    return unvalidated_osm_type


def _validate_osm_id(unvalidated_osm_id: int) -> int:
    if isinstance(unvalidated_osm_id, bool):
        raise TypeError("Osm_id cannot be a bool")
    if not isinstance(unvalidated_osm_id, int):
        raise TypeError("Osm_id must be an integer")
    if unvalidated_osm_id <= 0:
        raise ValueError("Osm_id must be greater than 0")
    return unvalidated_osm_id
