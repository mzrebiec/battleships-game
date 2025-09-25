from typing import Literal


GridAxisDirectionType = Literal["horizontal", "vertical"]

GridMoveOrientationType = GridAxisDirectionType | Literal["diagonal"]

GridDirectionType = Literal[
    "n",  # north
    "N",  # north
    "ne",  # north-east
    "NE",  # north-east
    "nw",  # north-west
    "NW",  # north-west
    "s",  # south
    "S",  # south
    "se",  # south-east
    "SE",  # south-east
    "sw",  # south-west
    "SW",  # south-west
    "e",  # east
    "E",  # east
    "w",  # west
    "W",  # west
]
