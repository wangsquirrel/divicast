import datetime
from typing import Self

from tyme4py import eightchar, enums, lunar, solar
from tyme4py.eightchar.provider.impl import DefaultEightCharProvider, LunarSect2EightCharProvider

from divicast.entities.trigram import Trigram  # type: ignore
from divicast.time_utils import check_naive_datetime

from ..entities.daemon import Daemon
from ..entities.ganzhi import Canggan, Dizhi, Nayin, Shishen, SixtyJiazi, Tiangan, TwelveZhangsheng
from ..entities.misc import Gender
from .analysis import analyze_chart
from .analysis_models import ChartAnalysis
from .daemon import build_pillar_shensha


class ZhuInfo(object):
    """柱的命盘信息, 可以是年柱, 月柱, 日柱, 时柱"""

    gan: Tiangan
    zhi: Dizhi

    sixty_jiazi: SixtyJiazi  # 六十甲子
    zhuxing: Shishen  # 主星
    canggan: list[Canggan]  # 藏干
    fuxing: list[Shishen]  # 副星
    xingyun: TwelveZhangsheng  # 星运
    zizuo: TwelveZhangsheng  # 自坐
    kongwang: tuple[Dizhi, Dizhi]  # 空亡
    nayin: Nayin  # 纳音
    shensha: list[Daemon]  # 神煞

    def __init__(self, ganzhi: str) -> None:
        self.gan = Tiangan[ganzhi[0]]
        self.zhi = Dizhi[ganzhi[1]]
        self.sixty_jiazi = SixtyJiazi(self.gan, self.zhi)
        self.shensha = []


class BirthChart(object):
    # 原始信息
    _birth_solar: datetime.datetime  # 调用方已归一化好的排盘时间，例如当地真太阳时
    _gender: Gender  # 性别

    # tyme4py库类型的辅助时间信息
    _bazi: lunar.EightChar
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
    yearzhu: ZhuInfo
    monthzhu: ZhuInfo
    dayzhu: ZhuInfo
    bihourzhu: ZhuInfo

    # 客观属性外的一些启发式分析结果，供后续更复杂的分析与对照使用
    chart_analysis: ChartAnalysis

    @classmethod
    def get_eightchar_provider(cls, calc_rules: dict[str, str] | None = None):
        """
        八字计算规则选择，主要影响时柱的计算。默认使用 "lunar_sect2_day_same"，即以农历日期为基础，时柱与日柱天干相同。
        可选规则：
        - "default_next_day": 以公历日期为基础，时柱天干
        - "lunar_sect2_day_same": 以农历日期为基础，时柱天干与日柱相同（默认）
        """
        rules = calc_rules or {}
        rule = rules.get("zi_hour", "lunar_sect2_day_same")

        providers = {
            "default_next_day": DefaultEightCharProvider(),
            "lunar_sect2_day_same": LunarSect2EightCharProvider(),
        }
        return providers[rule]

    @classmethod
    def calc_eightchar(cls, lunar_hour: lunar.LunarHour, calc_rules: dict[str, str] | None = None):
        """按本次调用指定口径计算八字，不依赖 tyme4py 的全局 provider。"""
        return cls.get_eightchar_provider(calc_rules).get_eight_char(lunar_hour)

    def __init__(
        self, birth_solar: datetime.datetime, gender: Gender, calc_rules: dict[str, str] | None = None
    ) -> None:
        """命盘初始化，只包括八字，没有完整的盘面信息"""
        self._birth_solar = check_naive_datetime(birth_solar)
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
        previous_provider = lunar.LunarHour.provider
        lunar.LunarHour.provider = self.get_eightchar_provider(self._calc_rules)
        try:
            self._child_limit = eightchar.ChildLimit(self._solar_time, enums.Gender(gender.num))
        finally:
            lunar.LunarHour.provider = previous_provider

    @classmethod
    def create(cls, dt: datetime.datetime, gender: Gender, calc_rules: dict[str, str] | None = None) -> Self:
        """创建命盘。

        `dt` 必须是调用方已经归一化好的排盘时间，且必须是 naive datetime。
        """
        bc = cls(dt, gender, calc_rules=calc_rules)
        bc.assemble()
        bc.analyze()
        return bc

    def assemble(self) -> None:
        self.yearzhu = ZhuInfo(self._bazi.get_year().get_name())
        self.monthzhu = ZhuInfo(self._bazi.get_month().get_name())
        self.dayzhu = ZhuInfo(self._bazi.get_day().get_name())
        self.bihourzhu = ZhuInfo(self._bazi.get_hour().get_name())

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

        for zhu in [self.yearzhu, self.monthzhu, self.dayzhu, self.bihourzhu]:
            zhu.canggan = zhu.zhi.canggan()
            zhu.zhuxing = self.dayzhu.gan.get_shishen(zhu.gan)
            zhu.fuxing = [self.dayzhu.gan.get_shishen(canggan.gan) for canggan in zhu.canggan]

            zhu.xingyun = self.dayzhu.gan.get_twelve_zhangsheng(zhu.zhi)
            zhu.zizuo = zhu.gan.get_twelve_zhangsheng(zhu.zhi)
            zhu.kongwang = zhu.sixty_jiazi.get_kongwang()
            zhu.nayin = zhu.sixty_jiazi.get_nayin()
            zhu.shensha = []

        shensha_by_pillar = build_pillar_shensha(self._bazi, self._gender)
        for zhu, shensha in zip([self.yearzhu, self.monthzhu, self.dayzhu, self.bihourzhu], shensha_by_pillar):
            zhu.shensha = shensha

    def analyze(self) -> None:
        """计算并填充统一分析结果。当前分析层以启发式加权与规则匹配为主。"""
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
