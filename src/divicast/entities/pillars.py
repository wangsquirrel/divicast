"""六爻与八字共用的四柱值对象。"""

from collections.abc import Iterator
from dataclasses import dataclass

from divicast.entities.ganzhi import SixtyJiazi


@dataclass(frozen=True, slots=True)
class FourPillars:
    """按年、月、日、时定位的四个合法干支。

    仅表达四柱的值，不保存排盘时间、历法规则或命盘分析结果，也不保证
    四柱对应某个实际时刻。遍历和字符串表示均采用年、月、日、时顺序。
    """

    year: SixtyJiazi
    month: SixtyJiazi
    day: SixtyJiazi
    hour: SixtyJiazi

    def __post_init__(self) -> None:
        for name, pillar in (
            ("year", self.year),
            ("month", self.month),
            ("day", self.day),
            ("hour", self.hour),
        ):
            if not isinstance(pillar, SixtyJiazi):
                raise TypeError(f"{name} must be a SixtyJiazi")

    def __iter__(self) -> Iterator[SixtyJiazi]:
        yield self.year
        yield self.month
        yield self.day
        yield self.hour

    def __str__(self) -> str:
        return " ".join(map(str, self))
