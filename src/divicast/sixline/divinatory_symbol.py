from __future__ import annotations

import datetime
import random
from typing import List, NamedTuple, Optional, Self

from tyme4py import solar  # type: ignore

from divicast.entities.daemon import Daemon
from divicast.entities.dizhi import Dizhi
from divicast.entities.liushen import Liushen
from divicast.entities.relative import Relative
from divicast.entities.tiangan import Tiangan
from divicast.entities.trigram import *
from divicast.entities.trigram import Trigram
from divicast.entities.wuxing import Wuxing


class Bazi(NamedTuple):
    year: Ganzhi
    month: Ganzhi
    day: Ganzhi
    bihour: Ganzhi

    def __str__(self):
        return f"{self.year} {self.month} {self.day} {self.bihour}"


def create_bazi(dt: datetime.datetime) -> Bazi:
    bz = (
        solar.SolarTime.from_ymd_hms(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
        )
        .get_lunar_hour()
        .get_eight_char()
    )

    year = Ganzhi(
        Tiangan.from_chinese_name(bz.get_year().get_heaven_stem().get_name()),
        Dizhi.from_chinese_name(bz.get_year().get_earth_branch().get_name()),
    )
    month = Ganzhi(
        Tiangan.from_chinese_name(bz.get_month().get_heaven_stem().get_name()),
        Dizhi.from_chinese_name(bz.get_month().get_earth_branch().get_name()),
    )
    day = Ganzhi(
        Tiangan.from_chinese_name(bz.get_day().get_heaven_stem().get_name()),
        Dizhi.from_chinese_name(bz.get_day().get_earth_branch().get_name()),
    )
    bihour = Ganzhi(
        Tiangan.from_chinese_name(bz.get_hour().get_heaven_stem().get_name()),
        Dizhi.from_chinese_name(bz.get_hour().get_earth_branch().get_name()),
    )
    return Bazi(year, month, day, bihour)


class Ganzhi(NamedTuple):
    gan: Tiangan
    zhi: Dizhi

    def __str__(self):
        return f"{self.gan}{self.zhi}"


def create_relative(obj: Wuxing, sub: Wuxing) -> tuple | Relative:

    if sub == obj.generate():
        return Relative.Descendant
    elif sub == obj.restrain():
        return Relative.Wife
    elif sub.generate() == obj:
        return Relative.Parent
    elif sub.restrain() == obj:
        return Relative.Governer
    elif sub == obj:
        return Relative.Brother
    else:
        raise AssertionError("无法判断六亲关系")


class LineInHexagram:
    """
    卦爻：在卦中的爻
    """

    line: Line
    relative: Relative
    gan: Tiangan
    zhi: Dizhi
    wuxing: Wuxing
    is_subject: bool
    is_object: bool
    fushen: LineInHexagram

    def __init__(self, _01):
        self.line = Line(_01)  # 爻
        self.relative = None  # 六亲
        self.gan = None  # 干
        self.zhi = None  # 支
        self.wuxing = None  # 五行
        self.is_subject = None  # 世
        self.is_object = None  # 应
        self.fushen = None  # 伏神


def create_kongwang(ganzhi: Ganzhi) -> tuple[Dizhi, Dizhi]:
    return (
        Dizhi((ganzhi.zhi.num - ganzhi.gan.num - 2) % 12),
        Dizhi((ganzhi.zhi.num - ganzhi.gan.num - 1) % 12),
    )


def create_first_liushen(gan: Tiangan) -> Liushen:
    """
    根据天干排出第一个六神
    """
    start = 0

    if gan.num in [0, 1]:
        start = 0
    elif gan.num in [2, 3]:
        start = 1
    elif gan.num == 4:
        start = 2
    elif gan.num == 5:
        start = 3
    elif gan.num in [6, 7]:
        start = 4
    elif gan.num in [8, 9]:
        start = 5
    else:
        raise AssertionError("Unexpected Gan")
    return Liushen(start % 6)


class LinePosition:
    """
    爻位，在整个盘中的爻
    """

    liushen: Liushen
    origin: LineInHexagram
    variant: LineInHexagram
    is_changed: bool

    def __init__(self):
        self.liushen = None  # 六神
        self.origin = None  # 本卦爻
        self.variant = None  # 变卦爻
        self.is_changed = None  # 是否变爻


def create_line_position(n: int) -> LinePosition:
    """
    根据铜钱的结果创建一个爻位
    :param n: 铜钱中1的个数
    """

    if n == 0:  # 老阴，变爻，阴动
        origin_line = LineInHexagram(0)
        variant_line = LineInHexagram(1)
    elif n == 1:  # 少阳
        origin_line = LineInHexagram(1)
        variant_line = LineInHexagram(1)
    elif n == 2:  # 少阴
        origin_line = LineInHexagram(0)
        variant_line = LineInHexagram(0)
    elif n == 3:  # 老阳，变爻，阳动
        origin_line = LineInHexagram(1)
        variant_line = LineInHexagram(0)

    line_pos = LinePosition()
    line_pos.origin = origin_line
    line_pos.variant = variant_line
    line_pos.is_changed = origin_line.line != variant_line.line
    return line_pos


class DivinatorySymbol:
    """
    六爻卦象

    """

    """
    乾纳甲壬坎纳戊
    离纳己土震纳庚
    坤纳乙癸巽纳辛
    艮纳丙火兑纳丁
    """
    _inside_tiangan_dict = {
        Trigram.Qian: Tiangan.Jia,
        Trigram.Kan: Tiangan.Wu,
        Trigram.Li: Tiangan.Ji,
        Trigram.Zhen: Tiangan.Geng,
        Trigram.Kun: Tiangan.Yi,
        Trigram.Xun: Tiangan.Xin,
        Trigram.Gen: Tiangan.Bing,
        Trigram.Dui: Tiangan.Ding,
    }
    _outside_tiangan_dict = {
        Trigram.Qian: Tiangan.Ren,
        Trigram.Kan: Tiangan.Wu,
        Trigram.Li: Tiangan.Ji,
        Trigram.Zhen: Tiangan.Geng,
        Trigram.Kun: Tiangan.Gui,
        Trigram.Xun: Tiangan.Xin,
        Trigram.Gen: Tiangan.Bing,
        Trigram.Dui: Tiangan.Ding,
    }
    _dizhi_dict = {
        Trigram.Qian: [Dizhi(i * 2) for i in range(6)],
        Trigram.Dui: [Dizhi((5 - i * 2) % 12) for i in range(6)],
        Trigram.Li: [Dizhi((3 - i * 2) % 12) for i in range(6)],
        Trigram.Zhen: [Dizhi((i * 2) % 12) for i in range(6)],
        Trigram.Xun: [Dizhi((1 - i * 2) % 12) for i in range(6)],
        Trigram.Kan: [Dizhi((2 + i * 2) % 12) for i in range(6)],
        Trigram.Gen: [Dizhi((4 + i * 2) % 12) for i in range(6)],
        Trigram.Kun: [Dizhi((7 - i * 2) % 12) for i in range(6)],
    }

    # 以下和时间有关
    _time: datetime.datetime
    bazi: Bazi
    kongwang: tuple[Dizhi, Dizhi]  # 空亡
    daemons: dict[Daemon, List[Dizhi]]  # 神煞

    # 以下和时间无关,之和卦象有关，但是六神和时间有关
    _cnts: List[int]  # 阳面的个数
    lines: List[LinePosition]
    guashen: Dizhi  # 卦身
    chuangzhang: List[Dizhi]  # 床帐
    xianggui: List[Dizhi]  # 香闺

    def __init__(self):
        self._time = None
        self.bazi = None
        self.kongwang = None
        self.daemons = {}
        self.lines = []

    @classmethod
    def create(
        cls,
        cnts: Optional[List[int]] = None,  # 铜钱中1的个
        now: Optional[datetime.datetime] = None,
        bazi: Optional[Bazi] = None,
    ) -> Self:
        """
        创建一个六爻卦象实例。
        :param cnts: 铜钱中1的个数的列表,顺序由下到上, e.g. [3, 2, 1, 0, 1, 2]
        :param now: 当前时间，默认为当前时间
        :param bazi: 八字，默认为当前时间的八字
        """
        d = cls()
        d._time = now or (datetime.datetime.now() +
                          datetime.timedelta(hours=8))
        d._cnts = cnts or [bin(random.randrange(0, 8)).count("1")
                           for _ in range(6)]

        d.bazi = bazi or create_bazi(d._time)  # 0. 装八字
        d._roll(d._cnts)  # 1. 摇卦
        d._assemble_tiangan()  # 2. 装天干
        d._assemble_dizhi()  # 3. 装地支
        d._assenble_shiying()  # 4. 安世应
        d._assenble_relative()  # 5. 装六亲
        d._assemble_liushen(d.bazi)  # 6. 装六神, 和时间有关
        d.kongwang = create_kongwang(d.bazi.day)  # 7. 装空亡, 和时间有关
        d._assemble_daemon()  # 8. 装神煞, 和时间有关

        return d

    @property
    def origin_hexagram(self) -> Hexagram:
        """
        本卦
        """
        return Hexagram(sum(self.lines[i].origin.line.num * (2**i) for i in range(6)))

    @property
    def variant_hexagram(self) -> Hexagram:
        """
        变卦
        """
        return Hexagram(sum(self.lines[i].variant.line.num * (2**i) for i in range(6)))

    @property
    def origin_inside_trigram(self) -> Trigram:
        """
        本卦内卦
        """
        return self.origin_hexagram.inside_trigram()

    @property
    def origin_outside_trigram(self) -> Trigram:
        """
        本卦外卦
        """
        return self.origin_hexagram.outside_trigram()

    @property
    def variant_inside_trigram(self) -> Trigram:
        """
        变卦内卦
        """
        return self.variant_hexagram.inside_trigram()

    @property
    def variant_outside_trigram(self) -> Trigram:
        """
        变卦外卦
        """
        return self.variant_hexagram.outside_trigram()

    @property
    def six_denties(self) -> List[Liushen]:
        return [l.liushen for l in self.lines]

    def _roll(self, cnts: List[int]):
        """
        摇卦
        """
        for i in range(6):
            line_pos = create_line_position(cnts[i])
            self.lines.append(line_pos)

    def _assemble_tiangan(self):
        # 处理内卦的天干
        for i in range(0, 3):
            self.lines[i].origin.gan = self._inside_tiangan_dict[
                self.origin_inside_trigram
            ]
            self.lines[i].variant.gan = self._inside_tiangan_dict[
                self.variant_inside_trigram
            ]
        # 处理外卦的天干
        for i in range(3, 6):
            self.lines[i].origin.gan = self._outside_tiangan_dict[
                self.origin_outside_trigram
            ]
            self.lines[i].variant.gan = self._outside_tiangan_dict[
                self.variant_outside_trigram
            ]

    def _assemble_dizhi(self):
        for i in range(0, 3):
            self.lines[i].origin.zhi = self._dizhi_dict[self.origin_inside_trigram][i]
            self.lines[i].variant.zhi = self._dizhi_dict[self.variant_inside_trigram][i]
        for i in range(3, 6):
            self.lines[i].origin.zhi = self._dizhi_dict[self.origin_outside_trigram][i]
            self.lines[i].variant.zhi = self._dizhi_dict[self.variant_outside_trigram][
                i
            ]

        for i in range(0, 6):
            self.lines[i].origin.wuxing = self.lines[i].origin.zhi.belongs_to_wuxing()
            self.lines[i].variant.wuxing = self.lines[i].variant.zhi.belongs_to_wuxing()

    def _assenble_shiying(self):
        """
        安世应
        """
        seq = 0
        if self.origin_hexagram.belongs_to_trigram_seq() == 2:  # 天同二世
            seq = 1
        elif self.origin_hexagram.belongs_to_trigram_seq() == 5:  # 天变五
            seq = 4
        elif self.origin_hexagram.belongs_to_trigram_seq() == 4:  # 地同四世
            seq = 3
        elif self.origin_hexagram.belongs_to_trigram_seq() == 1:  # 地变初
            seq = 0
        elif self.origin_hexagram.belongs_to_trigram_seq() == 6:  # 本宫六世
            seq = 5
        elif self.origin_hexagram.belongs_to_trigram_seq() == 3:  # 三世异
            seq = 2
        elif self.origin_hexagram.belongs_to_trigram_seq() == 7:  # 人同游魂四世
            seq = 3  # 游魂
        elif self.origin_hexagram.belongs_to_trigram_seq() == 8:  # 人变归,归魂三
            seq = 2  # 归魂
        else:
            raise AssertionError("无法判断归宫的序号")

        for i in range(0, 6):
            self.lines[i].origin.is_subject = False
            self.lines[i].origin.is_object = False

        self.lines[seq].origin.is_subject = True
        self.lines[(seq + 3) % 6].origin.is_object = True

    def _assenble_relative(self):

        for i in range(0, 6):
            self.lines[i].origin.relative = create_relative(
                self.origin_hexagram.belongs_to_trigram().belongs_to_wuxing(),
                self.lines[i].origin.wuxing,
            )
            # 变卦的六亲要按照变卦各爻的地支和本卦所属卦宫的五行生克关系来装。
            self.lines[i].variant.relative = create_relative(
                self.origin_hexagram.belongs_to_trigram().belongs_to_wuxing(),
                self.lines[i].variant.wuxing,
            )

        diffs = set(Relative.all()) - \
            set(l.origin.relative for l in self.lines)
        if len(diffs) == 0:
            return

        # 伏神
        d = DivinatorySymbol.create(
            [
                2 - (self.origin_hexagram.belongs_to_trigram().num >> 0 & 0b001),
                2 - (self.origin_hexagram.belongs_to_trigram().num >> 1 & 0b001),
                2 - (self.origin_hexagram.belongs_to_trigram().num >> 2 & 0b001),
                2 - (self.origin_hexagram.belongs_to_trigram().num >> 0 & 0b001),
                2 - (self.origin_hexagram.belongs_to_trigram().num >> 1 & 0b001),
                2 - (self.origin_hexagram.belongs_to_trigram().num >> 2 & 0b001),
            ],
            None,  # 和时间无关
        )
        for r in diffs:
            for i, l in enumerate(d.lines):
                if l.origin.relative == r:
                    self.lines[i].origin.fushen = l.origin

    def _assemble_liushen(self, bazi: Bazi):
        """"""
        first = create_first_liushen(bazi.day.gan)
        for i in range(0, 6):
            # self.lines[i].liushen = Liushen((i + start.num) % 6)
            self.lines[i].liushen = first
            first = first.next()  # 下一个六神

    def _assemble_daemon(self):
        """
        和时间有关
        """
        # 天乙贵人
        tianyiguiren = None
        if self.bazi.day.gan.num in [0, 4]:
            tianyiguiren = [
                Dizhi.from_chinese_name("丑"),
                Dizhi.from_chinese_name("未"),
            ]
        elif self.bazi.day.gan.num in [1, 5]:
            tianyiguiren = [
                Dizhi.from_chinese_name("子"),
                Dizhi.from_chinese_name("申"),
            ]
        elif self.bazi.day.gan.num in [2, 3]:
            tianyiguiren = [
                Dizhi.from_chinese_name("亥"),
                Dizhi.from_chinese_name("酉"),
            ]
        elif self.bazi.day.gan.num in [6, 7]:
            tianyiguiren = [
                Dizhi.from_chinese_name("午"),
                Dizhi.from_chinese_name("寅"),
            ]
        elif self.bazi.day.gan.num in [8, 9]:
            tianyiguiren = [
                Dizhi.from_chinese_name("卯"),
                Dizhi.from_chinese_name("巳"),
            ]
        self.daemons[Daemon.Tianyiguiren] = tianyiguiren

        # 驿马
        if self.bazi.day.zhi in [Dizhi.Shen, Dizhi.Zi, Dizhi.Chen]:
            yima = [Dizhi.Yin]
        elif self.bazi.day.zhi in [Dizhi.Si, Dizhi.You, Dizhi.Chou]:
            yima = [Dizhi.Hai]
        elif self.bazi.day.zhi in [Dizhi.Hai, Dizhi.Mou, Dizhi.Wei]:
            yima = [Dizhi.Si]
        elif self.bazi.day.zhi in [Dizhi.Yin, Dizhi.Wu, Dizhi.Xu]:
            yima = [Dizhi.Shen]
        else:
            raise AssertionError("Unexpected Zhi")
        self.daemons[Daemon.Yima] = yima

        # 桃花
        if self.bazi.day.zhi in [Dizhi.Shen, Dizhi.Zi, Dizhi.Chen]:
            taohua = [Dizhi.You]
        elif self.bazi.day.zhi in [Dizhi.Si, Dizhi.You, Dizhi.Chou]:
            taohua = [Dizhi.Wu]
        elif self.bazi.day.zhi in [Dizhi.Hai, Dizhi.Mou, Dizhi.Wei]:
            taohua = [Dizhi.Zi]
        elif self.bazi.day.zhi in [Dizhi.Yin, Dizhi.Wu, Dizhi.Xu]:
            taohua = [Dizhi.Mou]
        else:
            raise AssertionError("Unexpected Zhi")
        self.daemons[Daemon.Taohua] = taohua

        # 文昌
        wenchang_dict = {
            Tiangan.Jia: Dizhi.Si,
            Tiangan.Yi: Dizhi.Wu,
            Tiangan.Bing: Dizhi.Shen,
            Tiangan.Wu: Dizhi.Shen,
            Tiangan.Geng: Dizhi.Hai,
            Tiangan.Xin: Dizhi.Zi,
            Tiangan.Ding: Dizhi.You,
            Tiangan.Ji: Dizhi.You,
            Tiangan.Ren: Dizhi.Yin,
            Tiangan.Gui: Dizhi.Mou,
        }
        self.daemons[Daemon.Wenchang] = [wenchang_dict[self.bazi.day.gan]]

        # 禄神
        lushen_dict = {
            Tiangan.Jia: Dizhi.Yin,
            Tiangan.Yi: Dizhi.Mou,
            Tiangan.Bing: Dizhi.Si,
            Tiangan.Wu: Dizhi.Si,
            Tiangan.Geng: Dizhi.Shen,
            Tiangan.Xin: Dizhi.You,
            Tiangan.Ding: Dizhi.Wu,
            Tiangan.Ji: Dizhi.Wu,
            Tiangan.Ren: Dizhi.Hai,
            Tiangan.Gui: Dizhi.Zi,
        }
        self.daemons[Daemon.Lushen] = [lushen_dict[self.bazi.day.gan]]

        # 劫煞：日支
        # 口诀：申子辰见巳，亥卯未见申，寅午戌见亥，巳酉丑见寅。《星平会海》诀：“寅午戌亥上不须说，亥卯未申上勿道情，申子辰巳上化灰尘，巳酉丑寅上休开口”
        jiesha_dict = {
            Dizhi.Shen: Dizhi.Si,
            Dizhi.Zi: Dizhi.Si,
            Dizhi.Chen: Dizhi.Si,
            Dizhi.Hai: Dizhi.Shen,
            Dizhi.Mou: Dizhi.Shen,
            Dizhi.Wei: Dizhi.Shen,
            Dizhi.Yin: Dizhi.Hai,
            Dizhi.Wu: Dizhi.Hai,
            Dizhi.Xu: Dizhi.Hai,
            Dizhi.Si: Dizhi.Yin,
            Dizhi.You: Dizhi.Yin,
            Dizhi.Chou: Dizhi.Yin,
        }
        self.daemons[Daemon.Jiesha] = [jiesha_dict[self.bazi.day.zhi]]

        # 华盖：日支
        # 口诀：寅午戌见戌，亥卯未见未，申子辰见辰，巳酉丑见丑
        huagai_dict = {
            Dizhi.Shen: Dizhi.Chen,
            Dizhi.Zi: Dizhi.Chen,
            Dizhi.Chen: Dizhi.Chen,
            Dizhi.Hai: Dizhi.Wei,
            Dizhi.Mou: Dizhi.Wei,
            Dizhi.Wei: Dizhi.Wei,
            Dizhi.Yin: Dizhi.Xu,
            Dizhi.Wu: Dizhi.Xu,
            Dizhi.Xu: Dizhi.Xu,
            Dizhi.Si: Dizhi.You,
            Dizhi.You: Dizhi.You,
            Dizhi.Chou: Dizhi.You,
        }
        self.daemons[Daemon.Huagai] = [huagai_dict[self.bazi.day.zhi]]

        # 将星：
        # 申子辰在子，巳酉丑在酉，寅午戌在午，亥卯未在卯。
        jiangxing_dict = {
            Dizhi.Shen: Dizhi.Zi,
            Dizhi.Zi: Dizhi.Zi,
            Dizhi.Chen: Dizhi.Zi,
            Dizhi.Si: Dizhi.You,
            Dizhi.You: Dizhi.You,
            Dizhi.Chou: Dizhi.You,
            Dizhi.Yin: Dizhi.Wu,
            Dizhi.Wu: Dizhi.Wu,
            Dizhi.Xu: Dizhi.Wu,
            Dizhi.Hai: Dizhi.Mou,
            Dizhi.Mou: Dizhi.Mou,
            Dizhi.Wei: Dizhi.Mou,
        }
        self.daemons[Daemon.Jiangxing] = [jiangxing_dict[self.bazi.day.zhi]]

        # 天喜
        # 春天占卜天喜在戌，夏天占卜天喜在丑，秋天占卜天喜在辰，冬天占卜天喜在未。
        tianxi_dict = {
            Dizhi.Yin: Dizhi.Xu,
            Dizhi.Mou: Dizhi.Xu,
            Dizhi.Chen: Dizhi.Xu,
            Dizhi.Si: Dizhi.Chou,
            Dizhi.Wu: Dizhi.Chou,
            Dizhi.Wei: Dizhi.Chou,
            Dizhi.Shen: Dizhi.Chen,
            Dizhi.You: Dizhi.Chen,
            Dizhi.Xu: Dizhi.Chen,
            Dizhi.Hai: Dizhi.Wei,
            Dizhi.Zi: Dizhi.Wei,
            Dizhi.Chou: Dizhi.Wei,
        }
        self.daemons[Daemon.Tianxi] = [tianxi_dict[self.bazi.month.zhi]]

        # 天医
        self.daemons[Daemon.Tianyi] = [self.bazi.month.zhi.next(-1)]

        # 阳刃
        # 甲卯，乙寅，丙戊午，庚酉，辛申，丁己巳，壬子，癸亥。
        yangren_dict = {
            Tiangan.Jia: Dizhi.Mou,
            Tiangan.Yi: Dizhi.Yin,
            Tiangan.Bing: Dizhi.Wu,
            Tiangan.Wu: Dizhi.Wu,
            Tiangan.Geng: Dizhi.You,
            Tiangan.Xin: Dizhi.Shen,
            Tiangan.Ding: Dizhi.Si,
            Tiangan.Ji: Dizhi.Si,
            Tiangan.Ren: Dizhi.Zi,
            Tiangan.Gui: Dizhi.Hai,
        }

        self.daemons[Daemon.Yangren] = [yangren_dict[self.bazi.day.gan]]

        # 灾煞
        # 申子辰日灾煞在午，逢巳酉丑日灾. 煞在卯，逢寅午戌日灾煞在子，逢亥卯未日灾煞在酉。
        zashang_dict = {
            Dizhi.Shen: Dizhi.Wu,
            Dizhi.Zi: Dizhi.Wu,
            Dizhi.Chen: Dizhi.Wu,
            Dizhi.Si: Dizhi.Mou,
            Dizhi.You: Dizhi.Mou,
            Dizhi.Chou: Dizhi.Mou,
            Dizhi.Yin: Dizhi.Zi,
            Dizhi.Wu: Dizhi.Zi,
            Dizhi.Xu: Dizhi.Zi,
            Dizhi.Hai: Dizhi.You,
            Dizhi.Mou: Dizhi.You,
            Dizhi.Wei: Dizhi.You,
        }
        self.daemons[Daemon.Zaisha] = [zashang_dict[self.bazi.day.zhi]]

        # 谋星
        # 口诀：逢申子辰日谋星在戌，逢巳酉丑日谋星在未，逢寅午戌日谋星在辰，逢亥卯未日谋星在丑。
        mouxing_dict = {
            Dizhi.Shen: Dizhi.Xu,
            Dizhi.Zi: Dizhi.Xu,
            Dizhi.Chen: Dizhi.Xu,
            Dizhi.Si: Dizhi.Wei,
            Dizhi.You: Dizhi.Wei,
            Dizhi.Chou: Dizhi.Wei,
            Dizhi.Yin: Dizhi.Chen,
            Dizhi.Wu: Dizhi.Chen,
            Dizhi.Xu: Dizhi.Chen,
            Dizhi.Hai: Dizhi.Chou,
            Dizhi.Mou: Dizhi.Chou,
            Dizhi.Wei: Dizhi.Chou,
        }
        self.daemons[Daemon.Mouxing] = [mouxing_dict[self.bazi.day.zhi]]

        # 卦身
        for i, l in enumerate(self.lines):
            if l.origin.is_subject:
                if l.origin.line == Line.YinYao:
                    self.guashen = Dizhi.Wu.next(i)
                else:
                    self.guashen = Dizhi.Zi.next(i)
                break

        # 床帐
        self.chuangzhang = self.guashen.generate()

        # 香闺
        self.xianggui = self.guashen.restrain()
