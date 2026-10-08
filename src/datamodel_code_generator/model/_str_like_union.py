"""Detect union members that msgspec cannot keep apart as separate str-like types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from datamodel_code_generator.imports import (
    IMPORT_DATE,
    IMPORT_DATETIME,
    IMPORT_DECIMAL,
    IMPORT_TIME,
    IMPORT_TIMEDELTA,
    IMPORT_UUID,
)
from datamodel_code_generator.model.base import DataModel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from datamodel_code_generator.types import DataType

_STR_LIKE_IMPORT_KEYS: Final = frozenset(
    (import_.from_, import_.import_)
    for import_ in (IMPORT_UUID, IMPORT_DATETIME, IMPORT_DATE, IMPORT_TIME, IMPORT_TIMEDELTA, IMPORT_DECIMAL)
)
_BUILTIN_STR: Final = "str"


def _is_reference_str_like(data_type: DataType, seen: frozenset[int]) -> bool:
    source = data_type.reference.source if data_type.reference else None
    if not isinstance(source, DataModel) or not source.IS_ALIAS or id(source) in seen or len(source.fields) != 1:
        return False
    return _is_str_like(source.fields[0].data_type, seen | {id(source)})


def _is_str_like(data_type: DataType, seen: frozenset[int] = frozenset()) -> bool:
    if data_type.reference:
        return _is_reference_str_like(data_type, seen)
    if data_type.literals or data_type.data_types or data_type.enum_member_literals:
        return False
    if data_type.import_:
        return (data_type.import_.from_, data_type.import_.import_) in _STR_LIKE_IMPORT_KEYS
    return data_type.type == _BUILTIN_STR


def get_colliding_str_like_members(data_type: DataType) -> Sequence[DataType]:
    """Return union members that collide as one str-like type in msgspec."""
    if not data_type.is_union or data_type.is_tuple or data_type.is_dict or data_type.is_list:
        return ()
    str_like = [member for member in data_type.data_types if _is_str_like(member)]
    return str_like if len(str_like) > 1 else ()
