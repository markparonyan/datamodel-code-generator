"""msgspec rejects length constraints on fixed-shape tuples, so they must not be emitted."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import msgspec

from tests.conftest import assert_output
from tests.main.conftest import EXPECTED_OPENAPI_PATH, OPEN_API_DATA_PATH, _generated_model, run_main_and_assert
from tests.main.openapi.conftest import assert_file_content

if TYPE_CHECKING:
    from pathlib import Path


def _convert(model: Any, payload: dict[str, Any]) -> Any:
    try:
        return msgspec.to_builtins(msgspec.convert(payload, type=model))
    except msgspec.ValidationError as exc:
        return f"ValidationError: {exc}"


def test_msgspec_fixed_tuple_length(output_file: Path) -> None:
    """Drop min/max length on fixed tuples while keeping them on variadic arrays."""
    run_main_and_assert(
        input_path=OPEN_API_DATA_PATH / "msgspec_fixed_tuple_length.json",
        output_path=output_file,
        input_file_type="openapi",
        assert_func=assert_file_content,
        expected_file="msgspec_fixed_tuple_length.py",
        extra_args=[
            "--output-model-type",
            "msgspec.Struct",
            "--target-python-version",
            "3.12",
            "--field-constraints",
            "--use-annotated",
            "--disable-timestamp",
            "--formatters",
            "builtin",
        ],
    )
    payloads = {
        "valid": {"offset": [1, 2], "pair": ["a", 1], "tags": ["x"]},
        "null_offset": {"offset": None},
        "too_many_tags": {"tags": ["a", "b", "c", "d"]},
    }
    with _generated_model(output_file, "msgspec_fixed_tuple_length", "Item") as item:
        results = {name: _convert(item, payload) for name, payload in payloads.items()}
    assert_output(
        f"{json.dumps(results, indent=2)}\n", EXPECTED_OPENAPI_PATH / "msgspec_fixed_tuple_length_runtime.txt"
    )
