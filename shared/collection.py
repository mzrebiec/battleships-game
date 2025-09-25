from collections.abc import Callable, Generator, Iterator, Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Self, TypeVar

from .error import (
    AppInputValueException,
    AppOperationException,
    AppOutOfRangeValueException,
)


T = TypeVar("T")
CollectionIType = list[T]
CollectionInputType = CollectionIType[T] | None


class UndefinedValue:
    """
    A class for undefined values.
    """

    def __repr__(self) -> str:
        return "UndefinedValue"

    def __copy__(self: T) -> T:
        return self

    def __reduce__(self) -> str:
        return "UndefinedValue"

    def __deepcopy__(self: T, _: Any) -> T:
        return self


Undefined = UndefinedValue()


class CriterionExistence(Enum):
    """
    Enumeration of existence criteria for filtering collections.
    """

    EXISTS = 1
    NOT_EXISTS = 2


class CriterionComparison(Enum):
    """
    Enumeration of comparison criteria for filtering collections.
    """

    EQUAL = 3
    NOT_EQUAL = 4
    GREATER = 5
    GREATER_EQUAL = 6
    LESS = 7
    LESS_EQUAL = 8
    IS_NONE = 9
    IS_NOT_NONE = 10


CRITERION_EXISTS = CriterionExistence.EXISTS
CRITERION_NEXISTS = CriterionExistence.NOT_EXISTS

CRITERION_EQUALS = CriterionComparison.EQUAL
CRITERION_NEQUALS = CriterionComparison.NOT_EQUAL
CRITERION_GT = CriterionComparison.GREATER
CRITERION_GTE = CriterionComparison.GREATER_EQUAL
CRITERION_LT = CriterionComparison.LESS
CRITERION_LTE = CriterionComparison.LESS_EQUAL
CRITERION_IS_NONE = CriterionComparison.IS_NONE
CRITERION_IS_NOT_NONE = CriterionComparison.IS_NOT_NONE


@dataclass
class FilterCriterionExistenceCondition:
    """
    A criterion dataclass for filtering collections to match items where an attribute exists or not.
    """

    attribute: str
    comparison: CriterionExistence = CRITERION_EXISTS


@dataclass
class FilterCriterionAttributeCondition:
    """
    A criterion dataclass for filtering collections to match items with certain attributes' values.
    """

    attribute: str
    value: Any
    comparison: CriterionComparison = CRITERION_EQUALS


FilterCriterionCallableConditionType = Callable[[T, CollectionIType[T]], bool]


CollectionFilterConditionType = (
    FilterCriterionExistenceCondition | FilterCriterionAttributeCondition | FilterCriterionCallableConditionType[T]
)

CollectionFilterConditionInputType = CollectionFilterConditionType[T] | None


class ItemsCollectionIterator(Iterator[T]):
    """
    Iterator class to help in iterations through collections.
    """

    _items: CollectionIType[T]
    _index: int

    def __init__(self, items: CollectionIType[T]) -> None:
        """
        Constructor. Accepts a list of items to iterate through.

        Args:
            items (CollectionIType[T]): A list of items to iterate through.
        """
        super().__init__()

        self._items = items
        self._index = 0

    def __next__(self) -> T:
        """
        Implementation of `Iterator.__next__()` method to move forward in iteration.

        Raises:
            StopIteration: A standard exception to stop the iteration then all items have been iterated thorugh.

        Returns:
            T: Single item from the list.
        """
        try:
            result = self._items[self._index]
            self._index += 1
            return result
        except IndexError as ex:
            self._index = 0
            raise StopIteration from ex

    def __iter__(self) -> Self:
        """
        Implementation of `Iterator.__iter__()` method to return an object for iteration.

        Returns:
            Self: The object for iterations.
        """
        return self


class ItemsCollectionBase(Iterable[T]):
    """
    Base for collection of items of any type.
    """

    _total: int

    def __init__(
        self,
        items: CollectionInputType[T] = None,
        unique: bool = True,
    ) -> None:
        """
        Constructor.

        Args:
            items (CollectionInputType[T], optional): Initial list of items. Defaults to None.
            unique (bool, optional): A flag to mark whether the collection should contain unique items.
                                     Defaults to True.
        """
        super().__init__()

        self._unique = unique
        self._collection = self._create_items(items)

    @property
    def total(self) -> int:
        """
        Returns the number of total items in the collection.

        Returns:
            int: The number of items in the collection.
        """
        if not hasattr(self, "_total"):
            self._update_total_len()
        return self._total

    @property
    def len(self) -> int:
        """
        An alias for `ItemsCollectionBase.total`.

        Returns:
            int: The number of items in the collection.
        """
        return self.total

    def __len__(self) -> int:
        """
        A magic method to enable counting items in the collection with `len()` function.

        Returns:
            int: The number of items in the collection.
        """
        return self.total

    def _update_total_len(self) -> Self:
        """
        Updates the inner counter of items in the collection.

        Returns:
            Self: Collection instance to allow chaining.
        """
        self._total = len(self._collection)
        return self

    @property
    def unique(self) -> bool:
        """
        Returns an information whether the collection is contains unique items or not.

        Returns:
            bool: `True` if the collection contains unique elements, `False` otherwise.
        """
        return self._unique

    def __iter__(self) -> ItemsCollectionIterator[T]:
        """
        A method that returns the iterator to enable going through the items in the collection.

        Returns:
            ItemsCollectionIterator[T]: Iterator instance with a copy of items list.
        """
        return ItemsCollectionIterator(self.items())

    def items(self) -> CollectionIType[T]:
        """
        Returns a copy of inner items collection.

        Returns:
            CollectionIType[T]: A list of items (copy).
        """
        return self._collection.copy()

    def reversed(self) -> Iterator[T]:
        """
        Returns a copy of the inner list of items in reversed order.

        Returns:
            Iterator[T]: A reverrse-ordered list of items.
        """
        return reversed(self._collection.copy())

    def first(
        self,
        condition: CollectionFilterConditionInputType[T] = None,
    ) -> T | None:
        """
        Returns the first item in the collection (if it exists) or `None`. With optional argument provided,
        it filters the collection of items by the provided condition and then returns the first item
        from the results (or None if the list is empty).

        Args:
            condition (CollectionFilterConditionInputType[T], optional): A condition to filter the collection by
                                                                         before returning the first item.
                                                                         Defaults to None.

        Returns:
            T | None: The first item from the collection or `None` if the item does not exist.
        """
        if condition is not None:
            return next(
                (itm for itm in self.items() if self._item_matches_condition(itm, condition)),
                None,
            )

        return self.at_index(index=0, suppress_error=True)

    def last(
        self,
        condition: CollectionFilterConditionInputType[T] = None,
    ) -> T | None:
        """
        Returns the last item in the collection (if it exists) or `None`. With optional argument provided,
        it filters the collection of items by the provided condition and then returns the last item
        from the results (or None if the list is empty).

        Args:
            condition (CollectionFilterConditionInputType[T], optional): A condition to filter the collection by
                                                                         before returning the last item.
                                                                         Defaults to None.

        Returns:
            T | None: The last item from the collection or `None` if the item does not exist.
        """
        if condition is not None:
            return next(
                (itm for itm in self.reversed() if self._item_matches_condition(itm, condition)),
                None,
            )

        return self.at_index(index=-1, suppress_error=True)

    def at_index(self, index: int, suppress_error: bool = False) -> T | None:
        """
        Returns an item at provided index. If the item does not exist, it returns `None`.

        The method accepts any positive or negative integer. If a negative number is given, the indexes will be counted
        from the end of the list.

        If the flag (the second argument) is `True`, `None` will be returned if an item does not exist. Otherwise,
        an exception will be raised.

        Args:
            index (int): An index to return the item from. Can be a negative number.
            suppress_error (bool, optional): A flag to indicate whether an exception should be raised.
                                             Defaults to False.

        Raises:
            AppOutOfRangeValueException: When an index does not exist and the flag `suppress_error` is `False`.

        Returns:
            T | None: The item at given index or `None` if it does not exist and the flag `suppress_error` is `True`.
        """
        try:
            item = self._collection[index]
        except IndexError as ex:
            if suppress_error:
                return None

            raise AppOutOfRangeValueException(f"collection index [{index}] out of range") from ex

        return item

    def get_index(self, item: T, suppress_error: bool = True) -> int | None:
        """
        Returns the index of the provided item in the collection.

        The method checks whether the item exists in the collection. If it does, the index is returned.

        If the item does not exist, the result depends on the value of the `suppress_error` flag. If the flag is `True`,
        then `None` is returned. If the flag is `False`, an exception is raised.

        Args:
            item (T): An item to find its index in the collection.
            suppress_error (bool, optional): A flag to decide whether the exception should (`False`)
                                             or should not be raised (`True`) if the item does not exist.
                                             Defaults to True.

        Raises:
            AppInputValueException: When the item does not exist and the flag `suppress_error` is `False`.

        Returns:
            int: The index of the given item or `None` if it does not exist and the flag `suppress_error` is `True`.
        """
        idx: int | None

        try:
            idx = self._collection.index(item)
        except ValueError as ex:
            if suppress_error:
                idx = None

            raise AppInputValueException("failed to get an index of an item") from ex

        return idx

    def is_empty(self) -> bool:
        """
        Checks whether the collection has any items.

        Returns:
            bool: `True` If the collection is empty, `False` otherwise.
        """
        return self.total == 0

    def has(self, item: T) -> bool:
        """
        Checks whether given item exists in the collection.

        Args:
            item (T): An item to check for.

        Returns:
            bool: `True` if the item exists, `False` otherwise.
        """
        return item in self._collection

    def can_add(self, item: T) -> bool:
        """
        Checks whether given item can be added to the collection.

        Args:
            item (T): An item to check whether it can be added.

        Returns:
            bool: `True` if the item can be added, `False` otherwise.
        """
        return not self.has(item) if self._unique else True

    def _add(self, item: T) -> int | None:
        if not self.can_add(item):
            return -1

        self._collection.append(item)
        self._update_total_len()

        return self._total - 1

    def add(self, item: T) -> bool:
        idx = self._add(item)
        return idx is not None

    def add_item(self, item: T) -> int:
        idx = self._add(item)

        if idx is None:
            raise AppOperationException("failed to add an item to the collection")

        return idx

    def can_remove(self, item: T) -> bool:
        """
        Checks whether given item can be removed from the collection.

        Args:
            item (T): An item to check whether it can be removed.

        Returns:
            bool: `True` if the item can be removed, `False` otherwise.
        """
        return self.has(item)

    def _remove(self, item: T) -> int | None:
        if not self.can_remove(item):
            return None

        idx = self.get_index(item)

        if idx is None:
            return None

        self._collection.remove(item)
        self._update_total_len()

        return idx

    def remove(self, item: T) -> bool:
        idx = self._remove(item)
        return idx is not None

    def remove_item(self, item: T) -> int:
        idx = self._remove(item)

        if idx is None:
            raise AppOperationException("failed to remove an item from the collection")

        return idx

    def pop(self, index: int = -1, suppress_error: bool = False) -> T | None:
        try:
            item = self._collection.pop(index)

            if not self.can_remove(item=item):
                raise AppOperationException("the item cannot be removed from the collection")

            self._update_total_len()
        except IndexError as ex:
            if suppress_error:
                return None

            raise AppOperationException("failed to pop out an item from a collection") from ex

        return item

    def _create_chunk(self, items: list[T]) -> Self:
        return self.__class__(items)

    def get_chunks(self, size: int) -> Generator[Self, None, None]:
        for i in range(0, self.total, size):
            limit = i + size
            yield self._create_chunk(self._collection[i:limit])

    def get_chunk(self, start: int = 0, max_size: int | None = None) -> Self:
        limit = self.total

        if max_size is not None:
            if max_size <= 0:
                raise AppInputValueException(
                    f"the maximum size of a chunk cannot be lower or equal to zero [got: {max_size}]"
                )

            if start < 0:
                limit = start
                start = limit - max_size
            elif start >= 0:
                limit = start + max_size

        chunk = self._collection[start:limit]
        return self._create_chunk(chunk)

    def filter(self, condition: CollectionFilterConditionType[T]) -> Self:
        return self._create_chunk([itm for itm in self._collection if self._item_matches_condition(itm, condition)])

    def _item_matches_condition(
        self,
        item: T,
        condition: CollectionFilterConditionType[T],
    ) -> bool:
        if isinstance(condition, FilterCriterionExistenceCondition):
            has_attr = hasattr(item, condition.attribute)
            return (has_attr and condition.comparison == CRITERION_EXISTS) or (
                not has_attr and condition.comparison == CRITERION_NEXISTS
            )
        elif isinstance(condition, FilterCriterionAttributeCondition):
            return self._compare_item_attribute(item=item, condition=condition)
        else:
            return condition(item, self.items())

    def _create_items(self, items: CollectionInputType[T]) -> CollectionIType[T]:
        if not isinstance(items, list):
            return []

        return [self._prepare_item(itm) for itm in items if self._should_assign_item(itm)]

    def _prepare_item(self, item: T) -> T:
        return item

    def _should_assign_item(self, item: T) -> bool:
        return True

    def _get_attr_value(
        self,
        item: T,
        attr_name: str,
        default: Any = Undefined,
    ) -> Any:
        return getattr(item, attr_name, default)

    def _compare_item_attribute(
        self,
        item: T,
        condition: FilterCriterionAttributeCondition,
        default: Any = Undefined,
    ) -> bool:
        has_attr = hasattr(item, condition.attribute)

        if not has_attr:
            return False

        match condition.comparison:
            case CriterionComparison.GREATER:
                result = self._compare_attr_gt(
                    item=item,
                    condition=condition,
                    default=default,
                )
            case CriterionComparison.GREATER_EQUAL:
                result = self._compare_attr_gte(
                    item=item,
                    condition=condition,
                    default=default,
                )
            case CriterionComparison.LESS:
                result = self._compare_attr_lt(
                    item=item,
                    condition=condition,
                    default=default,
                )
            case CriterionComparison.LESS_EQUAL:
                result = self._compare_attr_lte(
                    item=item,
                    condition=condition,
                    default=default,
                )
            case CriterionComparison.IS_NONE:
                result = self._compare_attr_is_none(
                    item=item,
                    condition=condition,
                    default=default,
                )
            case CriterionComparison.IS_NOT_NONE:
                result = self._compare_attr_is_not_none(
                    item=item,
                    condition=condition,
                    default=default,
                )
            case CriterionComparison.NOT_EQUAL:
                result = self._compare_attr_not_equal(
                    item=item,
                    condition=condition,
                    default=default,
                )
            case _:
                result = self._compare_attr_equal(
                    item=item,
                    condition=condition,
                    default=default,
                )

        return result

    def _compare_attr_equal(
        self,
        item: T,
        condition: FilterCriterionAttributeCondition,
        default: Any = Undefined,
    ) -> bool:
        return self._get_attr_value(item, condition.attribute, default) == condition.value

    def _compare_attr_not_equal(
        self,
        item: T,
        condition: FilterCriterionAttributeCondition,
        default: Any = Undefined,
    ) -> bool:
        return self._get_attr_value(item, condition.attribute, default) != condition.value

    def _compare_attr_gt(
        self,
        item: T,
        condition: FilterCriterionAttributeCondition,
        default: Any = Undefined,
    ) -> bool:
        return self._get_attr_value(item, condition.attribute, default) > condition.value

    def _compare_attr_gte(
        self,
        item: T,
        condition: FilterCriterionAttributeCondition,
        default: Any = Undefined,
    ) -> bool:
        return self._get_attr_value(item, condition.attribute, default) >= condition.value

    def _compare_attr_lt(
        self,
        item: T,
        condition: FilterCriterionAttributeCondition,
        default: Any = Undefined,
    ) -> bool:
        return self._get_attr_value(item, condition.attribute, default) < condition.value

    def _compare_attr_lte(
        self,
        item: T,
        condition: FilterCriterionAttributeCondition,
        default: Any = Undefined,
    ) -> bool:
        return self._get_attr_value(item, condition.attribute, default) <= condition.value

    def _compare_attr_is_none(
        self,
        item: T,
        condition: FilterCriterionAttributeCondition,
        default: Any = Undefined,
    ) -> bool:
        return (
            self._get_attr_value(
                item=item,
                attr_name=condition.attribute,
                default=default,
            )
            is None
        )

    def _compare_attr_is_not_none(
        self,
        item: T,
        condition: FilterCriterionAttributeCondition,
        default: Any = Undefined,
    ) -> bool:
        return (
            self._get_attr_value(
                item=item,
                attr_name=condition.attribute,
                default=default,
            )
            is not None
        )


class FauxImmutableItemsCollectionBase(ItemsCollectionBase[T]):

    def __init__(self, items: list[T], unique: bool = True) -> None:
        self._locked = True
        super().__init__(items=items, unique=unique)
        self._locked = False

    def can_add(self, item: T) -> bool:
        if self._locked:
            return False
        return super().can_add(item)

    def can_remove(self, item: T) -> bool:
        if self._locked:
            return False
        return super().can_remove(item)

    def _add(self, item: T) -> int | None:
        if self._locked:
            return None
        return super()._add(item)

    def _remove(self, item: T) -> int | None:
        if self._locked:
            return None
        return super()._remove(item)

    def add(self, item: T) -> bool:
        if self._locked:
            return False
        return super().add(item)

    def add_item(self, item: T) -> int:
        if self._locked:
            raise AppOperationException("unable to add additional item to the collection as it is immutable")
        return super().add_item(item)

    def remove(self, item: T) -> bool:
        if self._locked:
            return True
        return super().remove(item)

    def remove_item(self, item: T) -> int:
        if self._locked:
            raise AppOperationException("unable to remove an item from the collection as it is immutable")

        return super().remove_item(item)

    def pop(self, index: int = -1, suppress_error: bool = False) -> T | None:
        if self._locked:
            if suppress_error:
                return None

            raise AppOperationException("unable to pop out an item from an immutable collection")

        return super().pop(index, suppress_error)


class StringsCollection(ItemsCollectionBase[str]):
    """
    A collection for strings.
    """


class NumbersCollection(ItemsCollectionBase[int]):
    """
    A collection for numbers (integers).
    """


class StringsImmutableCollection(FauxImmutableItemsCollectionBase[str]):
    """
    An immutable collection for strings.
    """


class NumbersImmutableCollection(FauxImmutableItemsCollectionBase[int]):
    """
    An immutable collection for numbers.
    """
