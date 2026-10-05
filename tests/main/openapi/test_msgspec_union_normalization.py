"""Generated msgspec annotations must be accepted and decode correctly at runtime."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import msgspec
import pytest

from tests.conftest import assert_output
from tests.main.conftest import EXPECTED_OPENAPI_PATH, OPEN_API_DATA_PATH, _generated_model, run_main_and_assert
from tests.main.openapi.conftest import assert_file_content

if TYPE_CHECKING:
    from pathlib import Path

INPUT_PATH = OPEN_API_DATA_PATH / "msgspec_union_normalization.json"
MSGSPEC_ARGS = [
    "--output-model-type",
    "msgspec.Struct",
    "--target-python-version",
    "3.12",
    "--field-constraints",
    "--use-standard-primitive-types",
    "--collapse-root-models",
    "--naming-strategy",
    "primary-first",
    "--disable-timestamp",
    "--formatters",
    "builtin",
]


def test_msgspec_union_normalization(output_file: Path) -> None:
    """Merge colliding str-like members, drop tuple lengths and keep primary names."""
    run_main_and_assert(
        input_path=INPUT_PATH,
        output_path=output_file,
        input_file_type="openapi",
        assert_func=assert_file_content,
        expected_file="msgspec_union_normalization.py",
        extra_args=MSGSPEC_ARGS,
    )
    payloads = {
        "mixed_id_offset_url_device": {
            "id": "not-a-uuid",
            "offset": [1, 2],
            "url": "https://example.com",
            "device_type": "abc_1",
        },
        "empty_url": {"id": "x", "url": ""},
        "null_url": {"id": "x", "url": None},
        "bad_device_type": {"id": "x", "device_type": "BAD"},
    }

    def convert(item: Any, payload: dict[str, Any]) -> Any:
        try:
            return msgspec.to_builtins(msgspec.convert(payload, type=item))
        except msgspec.ValidationError as exc:
            return f"ValidationError: {exc}"

    with _generated_model(output_file, "msgspec_union_normalization", "Item") as item:
        results = {name: convert(item, payload) for name, payload in payloads.items()}
    assert_output(
        f"{json.dumps(results, indent=2)}\n", EXPECTED_OPENAPI_PATH / "msgspec_union_normalization_runtime.txt"
    )


@pytest.mark.parametrize("output_model_type", ["pydantic_v2.BaseModel", "dataclasses.dataclass"])
def test_primary_first_keeps_component_name_over_inline_alias(output_model_type: str, output_file: Path) -> None:
    """Keep the components/schemas name when an earlier inline alias derives the same name."""
    run_main_and_assert(
        input_path=INPUT_PATH,
        output_path=output_file,
        input_file_type="openapi",
        assert_func=assert_file_content,
        expected_file=f"primary_first_inline_alias_{output_model_type.split('.', maxsplit=1)[0]}.py",
        extra_args=[
            "--output-model-type",
            output_model_type,
            "--naming-strategy",
            "primary-first",
            "--disable-timestamp",
            "--formatters",
            "builtin",
        ],
    )
