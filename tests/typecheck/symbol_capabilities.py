"""Static consumer examples; check with mypy alongside entities/protocols.py."""

from typing import assert_type

from divicast.entities.ganzhi import Dizhi, Nayin, SixtyJiazi, Tiangan
from divicast.entities.misc import Gender
from divicast.entities.protocols import HasGanzhi, HasWuxing, HasYinYang
from divicast.entities.trigram import Trigram
from divicast.entities.wuxing import Wuxing, YinYang


def wuxing_of(symbol: HasWuxing) -> Wuxing:
    return symbol.wuxing


def yinyang_of(symbol: HasYinYang) -> YinYang:
    return symbol.yinyang


def stem_of(pillar: HasGanzhi) -> Tiangan:
    return pillar.gan


def inspect_unknown(value: object) -> None:
    if isinstance(value, HasWuxing):
        assert_type(value.wuxing, Wuxing)
    if isinstance(value, HasYinYang):
        assert_type(value.yinyang, YinYang)
    if isinstance(value, HasGanzhi):
        assert_type(value.gan, Tiangan)
        assert_type(value.zhi, Dizhi)


assert_type(wuxing_of(Tiangan.Jia), Wuxing)
assert_type(wuxing_of(Dizhi.Zi), Wuxing)
assert_type(wuxing_of(Trigram.Qian), Wuxing)
assert_type(yinyang_of(Gender.Male), YinYang)

jiazi = SixtyJiazi.parse("甲子")
assert_type(jiazi, SixtyJiazi)
assert_type(stem_of(jiazi), Tiangan)
assert_type(jiazi.get_nayin(), Nayin)
assert_type(jiazi.get_kongwang(), tuple[Dizhi, Dizhi])
