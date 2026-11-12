import datetime
from collections.abc import Sequence
from typing import Self

from tyme4py import eightchar, enums, lunar, solar
from tyme4py.eightchar.provider import EightCharProvider
from tyme4py.eightchar.provider.impl import DefaultEightCharProvider, LunarSect2EightCharProvider

from divicast.entities.pillars import FourPillars
from divicast.entities.trigram import Trigram  # type: ignore
from divicast.time_utils import check_naive_datetime, four_pillars_from_tyme

from ..entities.daemon import Daemon
from ..entities.ganzhi import Canggan, Dizhi, Nayin, Shishen, SixtyJiazi, Tiangan, TwelveZhangsheng
from ..entities.misc import Gender
from .analysis import analyze_chart
from .analysis_models import ChartAnalysis
from .daemon import build_pillar_shensha


class ZhuInfo:
    """单柱的完整信息；根据干支、日主和已计算的神煞一次构造。"""

    _sixty_jiazi: SixtyJiazi
    zhuxing: Shishen  # 主星
    canggan: list[Canggan]  # 藏干
    fuxing: list[Shishen]  # 副星
    xingyun: TwelveZhangsheng  # 星运
    zizuo: TwelveZhangsheng  # 自坐
    shensha: list[Daemon]  # 神煞

    def __init__(self, sixty_jiazi: SixtyJiazi, *, day_master: Tiangan, shensha: Sequence[Daemon]) -> None:
        if not isinstance(sixty_jiazi, SixtyJiazi):
            raise TypeError("sixty_jiazi must be a SixtyJiazi")
        if not isinstance(day_master, Tiangan):
            raise TypeError("day_master must be a Tiangan")
        if isinstance(shensha, (str, bytes, bytearray)) or not isinstance(shensha, Sequence):
            raise TypeError("shensha must be a sequence of Daemon values")
        shensha_values = list(shensha)
        if any(not isinstance(value, Daemon) for value in shensha_values):
            raise TypeError("shensha must contain only Daemon values")

        self._sixty_jiazi = sixty_jiazi
        self.canggan = self.zhi.canggan()
        self.zhuxing = day_master.get_shishen(self.gan)
        self.fuxing = [day_master.get_shishen(canggan.gan) for canggan in self.canggan]
        self.xingyun = day_master.get_twelve_zhangsheng(self.zhi)
        self.zizuo = self.gan.get_twelve_zhangsheng(self.zhi)
        self.shensha = shensha_values

    @property
    def sixty_jiazi(self) -> SixtyJiazi:
        return self._sixty_jiazi

    @property
    def gan(self) -> Tiangan:
        return self.sixty_jiazi.gan

    @property
    def zhi(self) -> Dizhi:
        return self.sixty_jiazi.zhi

    @property
    def nayin(self) -> Nayin:
        return self.sixty_jiazi.get_nayin()

    @property
    def kongwang(self) -> tuple[Dizhi, Dizhi]:
        return self.sixty_jiazi.get_kongwang()


class BirthChart:
    # 原始信息
    _birth_solar: datetime.datetime  # 调用方已归一化好的排盘时间，例如当地真太阳时
    _gender: Gender  # 性别

    # tyme4py库类型的辅助时间信息
    _bazi: eightchar.EightChar
    _solar_time: solar.SolarTime
    _child_limit: eightchar.ChildLimit  # 童限
    _calc_rules: dict[str, str]

    # 命盘里除了四柱之外的其他属性
    kongwang: tuple[Dizhi, Dizhi]  # 空亡
    chinese_zodiac: str  # 生肖
    sign: str  # 星座
    taiyuan: str  # 胎元
    shengong: str  # 身宫
    minggua: str  # 命卦
    minggong: str  # 命宫
    taixi: str  # 胎息
    term: solar.SolarTermDay  # 二十四节气

    # 四柱
    _pillars: FourPillars
    yearzhu: ZhuInfo
    monthzhu: ZhuInfo
    dayzhu: ZhuInfo
    bihourzhu: ZhuInfo

    # 客观属性外的一些启发式分析结果，供后续更复杂的分析与对照使用
    chart_analysis: ChartAnalysis

    @property
    def pillars(self) -> FourPillars:
        """命盘的基础四柱；各柱的命盘信息引用其中对应的干支值。"""
        return self._pillars

    @classmethod
    def get_eightchar_provider(cls, calc_rules: dict[str, str] | None = None) -> EightCharProvider:
        """
        返回本次调用的八字计算器，规则主要区分晚子时的日柱归属。
        可选规则：
        - "default_next_day": 23:00-23:59 的日柱算次日。
        - "lunar_sect2_day_same": 23:00-23:59 的日柱算当天（八字默认）。
        时柱沿用对应 Tyme 算法，不表示时柱与日柱的天干相同。
        """
        rules = calc_rules or {}
        rule = rules.get("zi_hour", "lunar_sect2_day_same")

        providers = {
            "default_next_day": DefaultEightCharProvider(),
            "lunar_sect2_day_same": LunarSect2EightCharProvider(),
        }
        return providers[rule]

    @classmethod
    def calc_eightchar(
        cls, lunar_hour: lunar.LunarHour, calc_rules: dict[str, str] | None = None
    ) -> eightchar.EightChar:
        """按本次调用指定口径计算八字，不依赖 tyme4py 的全局 provider。"""
        return cls.get_eightchar_provider(calc_rules).get_eight_char(lunar_hour)

    def __init__(
        self, birth_solar: datetime.datetime, gender: Gender, calc_rules: dict[str, str] | None = None
    ) -> None:
        """构造包含完整盘面和分析结果的命盘；时间须由调用方归一化。"""
        self._birth_solar = check_naive_datetime(birth_solar)
        if not isinstance(gender, Gender):
            raise TypeError("gender must be a Gender")
        self._gender = gender
        self._calc_rules = calc_rules or {}
        self._solar_time = solar.SolarTime.from_ymd_hms(
            self._birth_solar.year,
            self._birth_solar.month,
            self._birth_solar.day,
            self._birth_solar.hour,
            self._birth_solar.minute,
            self._birth_solar.second,
        )
        self._bazi = self.calc_eightchar(self._solar_time.get_lunar_hour(), self._calc_rules)
        self._pillars = four_pillars_from_tyme(self._bazi)
        previous_provider = lunar.LunarHour.provider
        lunar.LunarHour.provider = self.get_eightchar_provider(self._calc_rules)
        try:
            self._child_limit = eightchar.ChildLimit(self._solar_time, enums.Gender(gender.num))
        finally:
            lunar.LunarHour.provider = previous_provider

        self.assemble()
        self.analyze()

    @classmethod
    def create(cls, dt: datetime.datetime, gender: Gender, calc_rules: dict[str, str] | None = None) -> Self:
        """创建完整命盘，与直接调用构造函数等价。

        `dt` 必须是调用方已经归一化好的排盘时间，且必须是 naive datetime。
        """
        return cls(dt, gender, calc_rules=calc_rules)

    def assemble(self) -> None:
        """装配盘面和各柱信息；构造过程会自动调用。"""
        shensha_by_pillar = build_pillar_shensha(self.pillars, self._gender)
        pillar_infos = [
            ZhuInfo(pillar, day_master=self.pillars.day.gan, shensha=shensha)
            for pillar, shensha in zip(self.pillars, shensha_by_pillar, strict=True)
        ]
        self.yearzhu, self.monthzhu, self.dayzhu, self.bihourzhu = pillar_infos

        self.kongwang = self.dayzhu.sixty_jiazi.get_kongwang()
        self.chinese_zodiac = self.yearzhu.zhi.chinese_zodiac()
        self.sign = (
            solar.SolarDay.from_ymd(self._birth_solar.year, self._birth_solar.month, self._birth_solar.day)
            .get_constellation()
            .get_name()
        )
        self.term = self._solar_time.get_solar_day().get_term_day()

        self.taiyuan = self._bazi.get_fetal_origin().get_name()
        self.taixi = self._bazi.get_fetal_breath().get_name()
        self.shengong = self._bazi.get_body_sign().get_name()
        self.minggua = self._calc_minggua()
        self.minggong = self._calc_minggong()

    def analyze(self) -> None:
        """计算并填充统一分析结果；构造过程会自动调用。"""
        self.chart_analysis = analyze_chart(self)

    def _calc_minggua(self) -> str:
        """
        命卦（八宅）计算规则:
        - 使用农历年（无法获取时退化为公历年）
        - 1900-1999: 男 = 10 - (year % 9), 女 = (year % 9) + 5
        - 2000-2099: 男 = 9 - (year % 9), 女 = (year % 9) + 6
        - 结果为 5 时：男取 2（坤），女取 8（艮）
        """
        method = self._calc_rules.get("minggua", "bazhai")
        if method != "bazhai":
            return ""
        lunar_year = self._solar_time.get_solar_day().get_lunar_day().get_year()
        if lunar_year is None:
            lunar_year = self._birth_solar.year

        if 1900 <= lunar_year <= 1999:
            base_male = 10
            base_female = 5
        else:
            base_male = 9
            base_female = 6

        remainder = lunar_year % 9
        if self._gender == Gender.Male:
            num = base_male - remainder
        else:
            num = base_female + remainder
        while num > 9:
            num -= 9
        if num == 5:
            num = 2 if self._gender == Gender.Male else 8

        trigram_map = {
            1: Trigram.Kan,
            2: Trigram.Kun,
            3: Trigram.Zhen,
            4: Trigram.Xun,
            6: Trigram.Qian,
            7: Trigram.Dui,
            8: Trigram.Gen,
            9: Trigram.Li,
        }
        return str(trigram_map[num])

    def _calc_minggong(self) -> str:
        """
        命宫（简化规则）:
        - 使用农历月与时支推算
        - 月支以寅为一月起点，时支以子为一时起点
        - 命宫序号 = 月序号 + 时序号 - 1（超出12则循环）
        """
        method = self._calc_rules.get("minggong", "eightchar_own_sign")
        if method == "eightchar_own_sign":
            try:
                return self._bazi.get_own_sign().get_name()
            except Exception:
                return ""
        if method != "month_hour_simple":
            return ""
        lunar_month = self._solar_time.get_solar_day().get_lunar_day().get_month()
        if lunar_month is None:
            return ""

        hour_zhi = self.bihourzhu.zhi
        month_zhi = Dizhi.Yin.next(lunar_month - 1)

        month_index = (month_zhi.num - Dizhi.Yin.num + 12) % 12 + 1
        hour_index = hour_zhi.num + 1
        ming_index = (month_index + hour_index - 1) % 12
        if ming_index == 0:
            ming_index = 12
        ming_zhi = Dizhi.Yin.next(ming_index - 1)
        return str(ming_zhi)
