from typing import Annotated, Any

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationInfo,
)

from .types import GridAxisDirectionType
from .vars import GameboardConstants


class GameConfigValidator:
    """
    Game configuration validator for Pydantic.
    """

    @staticmethod
    def ensure_axis_size_within_range(value: Any, info: ValidationInfo) -> int:
        """
        Ensures the size of the an axis is within the expected range.

        Args:
            value (Any): The value for the field, preferably an integer.
            info (ValidationInfo): Field's validation information.

        Raises:
            ValueError: When the input is not an integer and is not castable to it,
                        or when the input is out of expected range.

        Returns:
            int: The value for the size of an axis.
        """
        if isinstance(value, str) and value.isdigit():
            value = int(value)

        if not isinstance(value, int):
            raise ValueError(f"{info.field_name} should be an integer")

        if value < GameboardConstants.AXIS_SIZE_MIN.value:
            raise ValueError(
                f"{info.field_name} must not be less than {GameboardConstants.AXIS_SIZE_MIN.value}"
            )

        if value > GameboardConstants.AXIS_SIZE_MAX.value:
            raise ValueError(
                f"{info.field_name} must not be greater than {GameboardConstants.AXIS_SIZE_MAX.value}"
            )

        return value

    @staticmethod
    def ensure_letter_axis_value(
        value: Any,
        info: ValidationInfo,
    ) -> GridAxisDirectionType:
        """
        Ensures the value for the axis that is enumerated by letters is valid.

        Args:
            value (Any): Input value
            info (ValidationInfo): Field's validation information.

        Raises:
            ValueError: When the input is not a valid string.

        Returns:
            GridAxisDirectionType: The value for letters axis (either "horizontal" or "vertical"),
        """
        if not isinstance(value, str):
            raise ValueError(
                f"{info.field_name} should be a string [got: {type(value)}]"
            )

        match value.lower():
            case "h" | "horizontal":
                return "horizontal"
            case "v" | "vertical":
                return "vertical"
            case _:
                raise ValueError(f"invalid value for {info.field_name} [got: {value}]")


class GameboardConfig(BaseModel):

    model_config = ConfigDict(frozen=True)

    _grid_size: int = PrivateAttr()

    axis_size: int = Field(
        default=GameboardConstants.AXIS_SIZE_DEFAULT.value,
        ge=GameboardConstants.AXIS_SIZE_MIN.value,
        le=GameboardConstants.AXIS_SIZE_MAX.value,
    )

    letters_axis: Annotated[
        GridAxisDirectionType,
        BeforeValidator(GameConfigValidator.ensure_letter_axis_value),
    ] = Field(default="horizontal")

    @property
    def numerical_axis(self) -> GridAxisDirectionType:
        """
        Returns the information which of the axes is for numbers.

        Returns:
            GridAxisDirectionType: Information which axis is enumerated with numbers.
        """
        return "vertical" if self.letters_axis == "horizontal" else "horizontal"

    @property
    def grid_size(self) -> int:
        """
        Returns the size of the whole grid by multiplying the size of an axis by itself.

        Returns:
            int: The number of cells in the grid.
        """
        return self._grid_size

    def model_post_init(self, context: Any) -> None:
        """
        Post initialization method.

        Args:
            context (Any): Initialization context.

        Returns:
            None
        """
        self._grid_size = self.axis_size * self.axis_size
        return super().model_post_init(context)


class WarshipsConfig(BaseModel):

    carriers: int = Field(default=1, ge=0)
    battleships: int = Field(default=2, ge=0)
    cruisers: int = Field(default=3, ge=0)
    destroyers: int = Field(default=5, ge=0)


class GameConfig(BaseModel):
    """
    Game configuration object.
    """

    model_config = ConfigDict(frozen=True)

    board: GameboardConfig = Field(default_factory=lambda: GameboardConfig())


class HasGameConfig:
    """
    A mixin for all classes that require game configuration object.
    """

    def __init__(self, config: GameConfig, *args: Any, **kwargs: Any) -> None:
        """
        Constructor.

        Args:
            config (GameConfig): Ganme configuration object.
        """
        self._config = config
        super().__init__(*args, **kwargs)

    @property
    def config(self) -> GameConfig:
        """
        Returns game configuration object.

        Returns:
            GameConfig: Configuration object.
        """
        return self._config


class HasGameboardConfig:
    """
    A mixin for all classes that require game board configuration object.
    """

    def __init__(self, config: GameboardConfig, *args: Any, **kwargs: Any) -> None:
        """
        Constructor.

        Args:
            config (GameboardConfig): Ganme board configuration object.
        """
        self._config = config
        super().__init__(*args, **kwargs)

    @property
    def config(self) -> GameboardConfig:
        """
        Returns game board configuration object.

        Returns:
            GameConfig: Configuration object.
        """
        return self._config
