"""msgspec allows one str-like type per union, so colliding members must collapse to str."""

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


def test_msgspec_str_like_unions(output_file: Path) -> None:
    """Collapse colliding str-like members and keep lone UUID fields and named schemas."""
    run_main_and_assert(
        input_path=OPEN_API_DATA_PATH / "msgspec_str_like_unions.json",
        output_path=output_file,
        input_file_type="openapi",
        assert_func=assert_file_content,
        expected_file="msgspec_str_like_unions.py",
        extra_args=[
            "--output-model-type",
            "msgspec.Struct",
            "--target-python-version",
            "3.12",
            "--field-constraints",
            "--use-standard-primitive-types",
            "--collapse-root-models",
            "--disable-timestamp",
            "--formatters",
            "builtin",
        ],
    )
    payloads = {
        "non_uuid_id": {"id": "not-a-uuid", "plain_id": "123e4567-e89b-12d3-a456-426614174000"},
        "empty_url": {"id": "x", "url": ""},
        "http_url": {"id": "x", "url": "https://example.com"},
        "null_url": {"id": "x", "url": None},
        "mixed_values": {"id": "x", "mixed": "2020-01-01T00:00:00Z", "ids": ["a", "b"], "shared": "free text"},
        "bad_plain_id": {"id": "x", "plain_id": "not-a-uuid"},
    }
    with _generated_model(output_file, "msgspec_str_like_unions", "Item") as item:
        results = {name: _convert(item, payload) for name, payload in payloads.items()}
    assert_output(f"{json.dumps(results, indent=2)}\n", EXPECTED_OPENAPI_PATH / "msgspec_str_like_unions_runtime.txt")
