from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional, Tuple

from pydantic import BaseModel, Field, validator

from ..entities.wuxing import Wuxing
from .birth import BirthChart, Gender, ZhuInfo


class PersonalInfo(BaseModel):
    gregorian_birth: datetime = Field(..., description="公历出生时间")
    gender: str = Field(..., description="性别，男/女")
    zodiac: str = Field(..., description="生肖")
    constellation: str = Field(..., description="星座")
    birth_term: str = Field(..., description="出生节气")


class HiddenStem(BaseModel):
    name: str = Field(..., description="藏干名称")
    element: str = Field(..., description="藏干五行")
    role: str = Field(..., description="本气/中气/余气")
    tenGod: str = Field(..., description="十神(副星)")


class HeavenStem(BaseModel):
    name: str = Field(..., description="天干名称")
    element: str = Field(..., description="五行")
    tenGod: str = Field(..., description="十神(主星)")


class EarthBranch(BaseModel):
    name: str = Field(..., description="地支名称")
    element: str = Field(..., description="五行")
    hiddenStems: List[HiddenStem] = Field(
        default_factory=list, description="地支藏干")


class Pillar(BaseModel):
    pillar: str = Field(..., description="柱的天干地支，如 甲子")
    heavenlyStem: HeavenStem = Field(..., description="天干信息")
    earthlyBranch: EarthBranch = Field(..., description="地支信息")
    nayin: str = Field(..., description="纳音")
    shensha: List[str] = Field(default_factory=list, description="神煞")
    forDayMastertwelveLifeStages: Optional[str] = Field(
        None, description="星运（日主十二长生）")
    forPillarStemtwelveLifeStages: Optional[str] = Field(
        None, description="自坐(本柱十二长生)")
    kongwang: str = Field(..., description="柱的空亡")


class FourPillars(BaseModel):
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar


class NatalChart(BaseModel):
    day_master: str = Field(..., description="日主")
    conception_pillar: str = Field(..., description="胎元")
    body_pillar: str = Field(..., description="身宫")
    kongwang: str = Field(..., description="空亡")
    element_scores: dict[str, float] = Field(..., description="五行分数")
    four_pillars: FourPillars = Field(..., description="四柱信息")


class AnnualDetail(BaseModel):
    age: int = Field(..., description="流年年龄")
    annual_pillar: str = Field(..., description="流年干支")
    minor_pillar: str = Field(..., description="小运干支")


class MajorCycle(BaseModel):
    age_range: Tuple[int, int] = Field(..., description="大运年龄范围")
    pillar: str = Field(..., description="大运干支")
    annual_details: List[AnnualDetail] = Field(
        default_factory=list, description="流年详情")


class LuckCycles(BaseModel):
    start_age: int = Field(..., description="大运起始年龄")
    major_cycles: List[MajorCycle] = Field(
        default_factory=list, description="大运列表")


class StandardBirthChartOutput(BaseModel):
    personal_info: PersonalInfo = Field(..., description="个人基本信息")
    natal_chart: NatalChart = Field(..., description="八字命盘（静态信息）")
    luck_cycles: LuckCycles = Field(..., description="大运小运流年（动态信息）")
    chart_analysis: dict[str, Any] = Field(..., description="五行分析结果")

    @validator("personal_info", pre=True)
    def parse_personal_birth(cls, v):
        # 如果传入的是 dict，pydantic 会自动处理 datetime 字段的解析
        return v


def to_standard_format(birth_chart: BirthChart) -> StandardBirthChartOutput:
    """
    将 BirthChart 转换为标准化的输出格式
    """
    def _get_chinese_name(obj, default=""):
        try:
            return obj.chinese_name
        except Exception:
            try:
                return str(obj)
            except Exception:
                return default

    role_map = {
        # CangganType values: MAIN -> 本气, MIDDLE -> 中气, SECONDARY -> 余气
        "MAIN": "本气",
        "MIDDLE": "中气",
        "SECONDARY": "余气",
    }

    def zhu_to_pillar(zhu: ZhuInfo) -> Pillar:

        pillar_str = zhu.gan.chinese_name + zhu.zhi.chinese_name

        # heaven stem
        hs_name = zhu.gan.chinese_name
        hs_element = zhu.gan.belongs_to_wuxing().chinese_name
        hs_ten = zhu.zhuxing.chinese_name
        heavenly = HeavenStem(name=hs_name, element=hs_element, tenGod=hs_ten)

        # earthly branch and hidden stems
        eb_name = zhu.zhi.chinese_name
        eb_element = zhu.zhi.belongs_to_wuxing().chinese_name
        hidden: list[HiddenStem] = []

        for c in zhu.canggan:

            name = c.gan.chinese_name
            element = c.gan.belongs_to_wuxing().chinese_name
            ctype_name = c.canggan_type.name
            role = role_map[ctype_name]

            ten = birth_chart.dayzhu.gan.get_shishen(c.gan).chinese_name
            hidden.append(HiddenStem(
                name=name, element=element, role=role, tenGod=ten))
        earthly = EarthBranch(name=eb_name, element=eb_element,
                              hiddenStems=hidden)

        return Pillar(
            pillar=pillar_str,
            heavenlyStem=heavenly,
            earthlyBranch=earthly,
            nayin=zhu.nayin.chinese_name,
            shensha=[str(s) for s in zhu.shensha],
            forDayMastertwelveLifeStages=zhu.xingyun.chinese_name,
            forPillarStemtwelveLifeStages=zhu.zizuo.chinese_name,
            kongwang=",".join([str(s) for s in zhu.kongwang]),
        )

    # personal info
    personal = PersonalInfo(
        gregorian_birth=birth_chart._birth_solar,
        gender='男' if birth_chart._gender == Gender.MAN else '女',
        zodiac=birth_chart.chinese_zodiac,
        constellation=birth_chart.sign,
        birth_term=f"{birth_chart.term.get_name()}第{birth_chart.term.get_day_index()}天"
    )

    # natal chart
    four = FourPillars(
        year=zhu_to_pillar(birth_chart.yearzhu),
        month=zhu_to_pillar(birth_chart.monthzhu),
        day=zhu_to_pillar(birth_chart.dayzhu),
        hour=zhu_to_pillar(birth_chart.bihourzhu),
    )

    natal = NatalChart(
        day_master=birth_chart.dayzhu.gan.chinese_name,
        conception_pillar=birth_chart.taiyuan,
        body_pillar=birth_chart.shengong,
        kongwang=birth_chart.kongwang[0].chinese_name +
        birth_chart.kongwang[1].chinese_name,
        four_pillars=four,
        element_scores={}
    )

    # luck cycles
    start_age = 0
    major_cycles_list: list[MajorCycle] = []
    child_limit = birth_chart._child_limit

    decade = child_limit.get_start_decade_fortune()
    start_age = decade.get_start_age()

    for _ in range(0, 9):

        pillar_name = decade.get_sixty_cycle().get_name()
        age_range = (decade.get_start_age(), decade.get_end_age())

        annual_details: list[AnnualDetail] = []

        fortune = decade.get_start_fortune()
        for j in range(0, 10):
            minor = fortune.get_sixty_cycle().get_name()
            annual = fortune.get_sixty_cycle_year().get_sixty_cycle().get_name()
            annual_details.append(AnnualDetail(
                age=fortune.get_age(), annual_pillar=annual, minor_pillar=minor))
            fortune = fortune.next(1)

        major_cycles_list.append(MajorCycle(
            age_range=age_range, pillar=pillar_name, annual_details=annual_details))

        decade = decade.next(1)
    luck = LuckCycles(start_age=start_age, major_cycles=major_cycles_list)

    return StandardBirthChartOutput(personal_info=personal, natal_chart=natal, luck_cycles=luck, chart_analysis=birth_chart.chart_analysis)


def plain_draw_chart(birth_chart: BirthChart) -> None:
    """绘制命盘的函数示例"""
    print(f"出生日期：{birth_chart._birth_solar.strftime('%Y-%m-%d %H:%M:%S')}")
    print(
        f"出生节气：{birth_chart.term.get_name()}第{birth_chart.term.get_day_index()}天")
    print(f"节气时间: {birth_chart.term.get_solar_term().get_name()}-{birth_chart.term.get_solar_term().get_julian_day().get_solar_time()}")

    print(f"性别：{birth_chart._gender}")
    print("四柱八字:")
    print(
        f"年柱: {birth_chart.yearzhu.gan.chinese_name}{birth_chart.yearzhu.zhi.chinese_name}")
    print(
        f"月柱: {birth_chart.monthzhu.gan.chinese_name}{birth_chart.monthzhu.zhi.chinese_name}")
    print(
        f"日柱: {birth_chart.dayzhu.gan.chinese_name}{birth_chart.dayzhu.zhi.chinese_name}")
    print(
        f"时柱: {birth_chart.bihourzhu.gan.chinese_name}{birth_chart.bihourzhu.zhi.chinese_name}")
    print(f"生肖: {birth_chart.chinese_zodiac}")
    print(f"星座: {birth_chart.sign}")
    print(f"胎元: {birth_chart.taiyuan}")
    print(f"身宫: {birth_chart.shengong}")
    print(
        f"空亡: {birth_chart.kongwang[0].chinese_name}, {birth_chart.kongwang[1].chinese_name}")
    print("\n详细信息:")
    for zhu, name in zip([birth_chart.yearzhu, birth_chart.monthzhu, birth_chart.dayzhu, birth_chart.bihourzhu],
                         ["年柱", "月柱", "日柱", "时柱"]):
        print(f"{name}:")
        print(
            f"  藏干: {', '.join([canggan.gan.chinese_name for canggan in zhu.canggan])}")
        print(f"  主星: {zhu.zhuxing.chinese_name}")
        print(
            f"  副星: {', '.join([fuxing.chinese_name for fuxing in zhu.fuxing])}")
        print(f"  纳音: {zhu.nayin.chinese_name}")
        print(
            f"  神煞: {', '.join([shensha.chinese_name for shensha in zhu.shensha])}")
        print(f"  星运(日主十二长生): {zhu.xingyun.chinese_name}")
        print(f"  自坐(本柱十二长生): {zhu.zizuo.chinese_name}")
        print(
            f"  空亡: {zhu.kongwang[0].chinese_name}, {zhu.kongwang[1].chinese_name}")
        print()
    decade_fortune = birth_chart._child_limit.get_start_decade_fortune()
    for i in range(0, 9):
        print(
            f"大运{i} - {decade_fortune.get_sixty_cycle().get_name()}, 年龄: {decade_fortune.get_start_age()} - {decade_fortune.get_end_age()}"
        )
        fortune = decade_fortune.get_start_fortune()
        for j in range(0, 10):
            print(
                f"{fortune.get_age()}岁: 小运: {fortune.get_sixty_cycle().get_name()} - 流年: {fortune.get_sixty_cycle_year().get_sixty_cycle().get_name()}"
            )
            fortune = fortune.next(1)
        print("\n")
        decade_fortune = decade_fortune.next(1)
