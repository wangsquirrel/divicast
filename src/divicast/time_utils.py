from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, NamedTuple, TypedDict, cast

from tyme4py import solar  # type: ignore
from tyme4py.eightchar.provider.impl import DefaultEightCharProvider, LunarSect2EightCharProvider

from divicast.entities.ganzhi import Dizhi, SixtyJiazi, Tiangan


ZiHourRule = Literal["default_next_day", "lunar_sect2_day_same"]


class CalendarRules(TypedDict):
    zi_hour: ZiHourRule


def normalize_calc_rules(calc_rules: Mapping[str, str] | None = None) -> CalendarRules:
    """Copy and validate per-call rules, without reading or changing a global provider."""
    if calc_rules is not None and not isinstance(calc_rules, Mapping):
        raise ValueError("calc_rules must be a mapping")
    rules = dict(calc_rules) if calc_rules is not None else {}
    if rules.keys() - {"zi_hour"}:
        raise ValueError("the only supported calendar rule is 'zi_hour'")
    rule = rules.get("zi_hour", "default_next_day")
    if rule not in ("default_next_day", "lunar_sect2_day_same"):
        raise ValueError("zi_hour must be 'default_next_day' or 'lunar_sect2_day_same'")
    return {"zi_hour": cast(ZiHourRule, rule)}


@dataclass(frozen=True)
class CalendarConvention:
    """Actual per-call calendar conventions; unknown rules remain absent for supplied pillars."""

    time_basis: Literal["caller_normalized_naive"] = field(
        default="caller_normalized_naive",
        metadata={"description": "调用方已归一化的无时区时间；库不做时区或真太阳时转换"},
    )
    solar_terms: Literal["tyme_UTC+08:00"] | None = field(
        default="tyme_UTC+08:00", metadata={"description": "节气时刻采用tyme的UTC+08:00基准；显式四柱时未知"}
    )
    year_boundary: Literal["lichun"] | None = field(
        default="lichun", metadata={"description": "按立春交接时刻换年；显式四柱时未知"}
    )
    month_boundary: Literal["jie"] | None = field(
        default="jie", metadata={"description": "按十二节交接时刻换月，不按公历或农历月初；显式四柱时未知"}
    )
    day_boundary: Literal["23:00", "00:00"] | None = field(
        default="23:00", metadata={"description": "本次日柱换日时刻；时柱算法由zi_hour标识；显式四柱时未知"}
    )
    zi_hour: ZiHourRule | None = field(
        default="default_next_day", metadata={"description": "本次实际采用的Tyme晚子时算法；显式四柱时未知"}
    )
    pillar_source: Literal["time", "provided"] = field(
        default="time", metadata={"description": "time=按显示时间推算；provided=调用方提供，不保证与显示时间一致"}
    )

    @classmethod
    def from_rules(cls, calc_rules: Mapping[str, str] | None = None) -> CalendarConvention:
        rule = normalize_calc_rules(calc_rules)["zi_hour"]
        return cls(day_boundary="23:00" if rule == "default_next_day" else "00:00", zi_hour=rule)

    @classmethod
    def for_provided_pillars(cls) -> CalendarConvention:
        # A caller-supplied Bazi has no provable relationship to the displayed time.
        return cls(
            solar_terms=None,
            year_boundary=None,
            month_boundary=None,
            day_boundary=None,
            zi_hour=None,
            pillar_source="provided",
        )


def check_naive_datetime(dt: datetime) -> datetime:
    if not isinstance(dt, datetime):
        raise ValueError("chart time must be a datetime")
    if dt.tzinfo is not None:
        raise ValueError(f"{dt} must be a naive datetime that has already been normalized ")
    return dt


class GanzhiPair(NamedTuple):
    gan: Tiangan
    zhi: Dizhi

    def __str__(self) -> str:
        return f"{self.gan}{self.zhi}"

    def as_sixty_jiazi(self) -> SixtyJiazi:
        return SixtyJiazi(self.gan, self.zhi)


class FourPillars(NamedTuple):
    year: GanzhiPair
    month: GanzhiPair
    day: GanzhiPair
    hour: GanzhiPair

    def __str__(self) -> str:
        return f"{self.year} {self.month} {self.day} {self.hour}"


def _from_tyme_ganzhi(value) -> GanzhiPair:
    return GanzhiPair(
        Tiangan[value.get_heaven_stem().get_name()],
        Dizhi[value.get_earth_branch().get_name()],
    )


def create_four_pillars(dt: datetime, *, calc_rules: Mapping[str, str] | None = None) -> FourPillars:
    """Calculate at second precision using an explicit provider; default day rollover is 23:00."""
    dt = check_naive_datetime(dt)
    rule = normalize_calc_rules(calc_rules)["zi_hour"]
    provider = DefaultEightCharProvider() if rule == "default_next_day" else LunarSect2EightCharProvider()
    lunar_hour = solar.SolarTime.from_ymd_hms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second).get_lunar_hour()
    eight_char = provider.get_eight_char(lunar_hour)
    return FourPillars(
        year=_from_tyme_ganzhi(eight_char.get_year()),
        month=_from_tyme_ganzhi(eight_char.get_month()),
        day=_from_tyme_ganzhi(eight_char.get_day()),
        hour=_from_tyme_ganzhi(eight_char.get_hour()),
    )


def create_kongwang(day_ganzhi: GanzhiPair | object) -> tuple[Dizhi, Dizhi]:
    if isinstance(day_ganzhi, GanzhiPair):
        return day_ganzhi.as_sixty_jiazi().get_kongwang()
    gan = getattr(day_ganzhi, "gan")
    zhi = getattr(day_ganzhi, "zhi")
    return SixtyJiazi(gan, zhi).get_kongwang()
