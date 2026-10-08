"""Tests for detecting colliding str-like union members."""

from __future__ import annotations

import pytest

from datamodel_code_generator.imports import (
    IMPORT_DATE,
    IMPORT_DATETIME,
    IMPORT_DECIMAL,
    IMPORT_TIME,
    IMPORT_TIMEDELTA,
    IMPORT_UUID,
    Import,
)
from datamodel_code_generator.model._str_like_union import get_colliding_str_like_members
from datamodel_code_generator.types import DataType


def _union(*members: DataType) -> DataType:
    return DataType(data_types=list(members))


def _str() -> DataType:
    return DataType(type="str")


@pytest.mark.parametrize(
    "import_",
    [IMPORT_UUID, IMPORT_DATETIME, IMPORT_DATE, IMPORT_TIME, IMPORT_TIMEDELTA, IMPORT_DECIMAL],
)
def test_stdlib_str_like_member_collides_with_str(import_: Import) -> None:
    """Report every stdlib str-like type that shares a union with str."""
    str_member = _str()
    other = DataType.from_import(import_)
    assert get_colliding_str_like_members(_union(str_member, other)) == [str_member, other]


def test_duplicate_str_members_collide() -> None:
    """Report repeated str members as colliding."""
    assert len(get_colliding_str_like_members(_union(_str(), _str()))) == 2


def test_lone_str_like_member_does_not_collide() -> None:
    """Keep a union with a single str-like member untouched."""
    assert get_colliding_str_like_members(_union(DataType.from_import(IMPORT_UUID), DataType(type="int"))) == ()


def test_same_name_from_other_module_is_not_str_like() -> None:
    """Match imports by module and name instead of the bare type name."""
    custom = DataType.from_import(Import(from_="mypkg.types", import_="UUID"))
    assert get_colliding_str_like_members(_union(_str(), custom)) == ()


def test_aliased_import_is_still_str_like() -> None:
    """Match an aliased stdlib import by its module and name."""
    aliased = DataType.from_import(Import(from_="datetime", import_="date", alias="date_aliased"))
    assert len(get_colliding_str_like_members(_union(_str(), aliased))) == 2


@pytest.mark.parametrize(
    "build",
    [
        lambda a, b: DataType(data_types=[a, b], is_list=True),
        lambda a, b: DataType(data_types=[a, b], is_dict=True),
        lambda a, b: DataType(data_types=[a, b], is_tuple=True),
    ],
)
def test_container_types_are_not_unions(build: object) -> None:
    """Ignore list, dict and tuple containers."""
    assert get_colliding_str_like_members(build(_str(), DataType.from_import(IMPORT_UUID))) == ()
