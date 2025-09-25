from dataclasses import dataclass
from enum import Enum
import string
from typing import Literal


class GameboardConstants(Enum):

    AXIS_SIZE_DEFAULT = 10
    AXIS_SIZE_MIN = 8
    AXIS_SIZE_MAX = len(string.ascii_uppercase)

    SELECTION_MIN_LENGTH_DEFAULT = 1
    SELECTION_STRICT_LENGTH_DEFAULT = False


class GameboardMoveDirection(Enum):

    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    NORTH_EAST = "North-East"
    NORTH_WEST = "North-West"
    SOUTH_EAST = "South-East"
    SOUTH_WEST = "South-West"


ShipType = Literal["carrier", "battleship", "cruiser", "destroyer"]


@dataclass(frozen=True)
class WarshipInfo:

    ship_class: ShipType
    ship_size: int


class WarshipType(Enum):

    CARRIER = WarshipInfo(ship_class="carrier", ship_size=5)
    BATTLESHIP = WarshipInfo(ship_class="battleship", ship_size=4)
    CRUISER = WarshipInfo(ship_class="cruiser", ship_size=3)
    DESTROYER = WarshipInfo(ship_class="destroyer", ship_size=2)
