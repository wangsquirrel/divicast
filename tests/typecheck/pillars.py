"""Static examples of the shared domain values and chart views."""

from collections.abc import Iterator
from datetime import datetime
from typing import assert_type

from divicast.birth_chart.birth import BirthChart, ZhuInfo
from divicast.entities.daemon import Daemon
from divicast.entities.ganzhi import Canggan, Dizhi, Nayin, Shishen, SixtyJiazi, Tiangan, TwelveZhangsheng
from divicast.entities.pillars import FourPillars
from divicast.entities.protocols import HasGanzhi
from divicast.sixline import DivinatorySymbol
from divicast.time_utils import create_four_pillars


def stem_of(value: HasGanzhi) -> Tiangan:
    return value.gan


def inspect_charts(birth_chart: BirthChart, sixline: DivinatorySymbol) -> None:
    assert_type(birth_chart.pillars, FourPillars)
    assert_type(sixline.bazi, FourPillars)
    assert_type(birth_chart.pillars.hour, SixtyJiazi)
    assert_type(birth_chart.dayzhu.gan, Tiangan)
    assert_type(stem_of(birth_chart.dayzhu), Tiangan)


pillars = create_four_pillars(datetime(2024, 1, 1, 12))
assert_type(pillars, FourPillars)
assert_type(iter(pillars), Iterator[SixtyJiazi])
assert_type(pillars.day, SixtyJiazi)
assert_type(stem_of(pillars.day), Tiangan)

info = ZhuInfo(pillars.day, day_master=pillars.day.gan, shensha=())
assert_type(info.sixty_jiazi, SixtyJiazi)
assert_type(info.gan, Tiangan)
assert_type(info.zhi, Dizhi)
assert_type(info.nayin, Nayin)
assert_type(info.kongwang, tuple[Dizhi, Dizhi])
assert_type(info.zhuxing, Shishen)
assert_type(info.canggan, list[Canggan])
assert_type(info.fuxing, list[Shishen])
assert_type(info.xingyun, TwelveZhangsheng)
assert_type(info.zizuo, TwelveZhangsheng)
assert_type(info.shensha, list[Daemon])
