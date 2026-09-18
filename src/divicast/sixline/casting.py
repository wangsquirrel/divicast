"""Six-line input protocols; preserve legacy codes without guessing coin faces."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


CoinSide = Literal["text", "back"]


class CastingInput(BaseModel):
    """Immutable input provenance; JSON values preserve initial-to-top ordering."""

    model_config = ConfigDict(frozen=True)

    input_format: Literal["legacy_yaogua", "line_values", "coin_counts", "random_three_coins"] = Field(
        description="输入协议：旧版0–3编码、标准6–9爻值、传统铜钱计数或模拟三硬币"
    )
    values: tuple[int, ...] | None = Field(
        default=None, min_length=6, max_length=6, description="手动输入的原始六值，初爻到上爻；随机起卦不伪造此记录"
    )
    coin_side: CoinSide | None = Field(default=None, description="仅用于coin_counts：text=传统字面、back=传统背面")

    @field_serializer("values")
    def serialize_values(self, values: tuple[int, ...] | None) -> list[int] | None:
        # Keep model_dump() compatible with JSON Schema, while storing an immutable tuple.
        return list(values) if values is not None else None


def check_legacy_code(value: int) -> None:
    if type(value) is not int or not 0 <= value <= 3:
        raise ValueError("legacy yao code must be an integer in 0..3 (bool is not accepted)")


def _six_values(values: Sequence[int], minimum: int, maximum: int) -> tuple[int, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValueError("casting input must be a sequence of six integers, initial line first")
    snapshot = tuple(values)
    if len(snapshot) != 6 or any(type(value) is not int or not minimum <= value <= maximum for value in snapshot):
        raise ValueError(f"casting input must contain exactly six integers in {minimum}..{maximum}")
    return snapshot


def normalize_casting(
    cnts: Sequence[int] | None = None,
    *,
    line_values: Sequence[int] | None = None,
    coin_counts: Sequence[int] | None = None,
    coin_side: CoinSide | None = None,
) -> tuple[tuple[int, ...], CastingInput]:
    """Return immutable legacy codes and the actual input provenance."""
    if sum(value is not None for value in (cnts, line_values, coin_counts)) > 1:
        raise ValueError("cnts, line_values and coin_counts are mutually exclusive")
    if coin_counts is not None:
        if coin_side not in ("text", "back"):
            raise ValueError("coin_counts requires coin_side='text' or 'back'")
        values = _six_values(coin_counts, 0, 3)
        # Traditional text=2 and back=3. The sum is 6..9; engine code=sum-6.
        codes = tuple(3 - count if coin_side == "text" else count for count in values)
        return codes, CastingInput(input_format="coin_counts", values=values, coin_side=coin_side)
    if coin_side is not None:
        raise ValueError("coin_side can only be used with coin_counts")
    if line_values is not None:
        values = _six_values(line_values, 6, 9)
        return tuple(value - 6 for value in values), CastingInput(input_format="line_values", values=values)
    if cnts is not None:
        values = _six_values(cnts, 0, 3)
        return values, CastingInput(input_format="legacy_yaogua", values=values)
    codes = tuple(random.randrange(8).bit_count() for _ in range(6))
    return codes, CastingInput(input_format="random_three_coins")
