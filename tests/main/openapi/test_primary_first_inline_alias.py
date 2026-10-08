"""An inline alias parsed before a same-named primary schema must not take its name."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.main.conftest import OPEN_API_DATA_PATH, run_main_and_assert
from tests.main.openapi.conftest import assert_file_content

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    ("output_model_type", "expected_file"),
    [
        ("pydantic_v2.BaseModel", "primary_first_inline_alias_pydantic_v2.py"),
        ("dataclasses.dataclass", "primary_first_inline_alias_dataclass.py"),
        ("msgspec.Struct", "primary_first_inline_alias_msgspec.py"),
    ],
)
def test_primary_first_keeps_component_name_over_inline_alias(
    output_model_type: str, expected_file: str, output_file: Path
) -> None:
    """Keep the components/schemas name and suffix the inline alias instead."""
    run_main_and_assert(
        input_path=OPEN_API_DATA_PATH / "primary_first_inline_alias.json",
        output_path=output_file,
        input_file_type="openapi",
        assert_func=assert_file_content,
        expected_file=expected_file,
        extra_args=[
            "--output-model-type",
            output_model_type,
            "--target-python-version",
            "3.12",
            "--field-constraints",
            "--naming-strategy",
            "primary-first",
            "--disable-timestamp",
            "--formatters",
            "builtin",
        ],
    )
