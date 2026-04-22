from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, validator
from tyme4py import sixtycycle, solar

from divicast.birth_chart.analysis_models import ChartAnalysis as InternalChartAnalysis
from divicast.time_utils import check_naive_datetime

from ..entities.ganzhi import Tiangan
from ..entities.wuxing import Wuxing, YinYang
from .birth import BirthChart, ZhuInfo


class PersonalInfo(BaseModel):
    gregorian_birth: datetime = Field(..., description="公历出生时间")
    lunar_birth: Optional[str] = Field(None, description="农历出生日期")
    gender: str = Field(..., description="性别，男/女")
    zodiac: str = Field(..., description="生肖")
    constellation: str = Field(..., description="星座")
    birth_term: str = Field(..., description="出生节气")
    birth_term_time: Optional[str] = Field(None, description="节气交节时间")


class HiddenStem(BaseModel):
    name: str = Field(..., description="藏干名称")
    element: str = Field(..., description="藏干五行")
    yinYang: str = Field(..., description="阴阳")
    role: str = Field(..., description="本气/中气/余气")
    tengod: str = Field(..., description="十神(副星)")


class HeavenStem(BaseModel):
    name: str = Field(..., description="天干名称")
    element: str = Field(..., description="五行")
    yinYang: str = Field(..., description="阴阳")
    tengod: str = Field(..., description="十神(主星)")


class EarthBranch(BaseModel):
    name: str = Field(..., description="地支名称")
    element: str = Field(..., description="五行")
    yinYang: str = Field(..., description="阴阳")
    hiddenStems: List[HiddenStem] = Field(default_factory=list, description="地支藏干")


class Pillar(BaseModel):
    pillar: str = Field(..., description="柱的天干地支，如 甲子")
    heavenlyStem: HeavenStem = Field(..., description="天干信息")
    earthlyBranch: EarthBranch = Field(..., description="地支信息")
    nayin: str = Field(..., description="纳音")
    xun: Optional[str] = Field(None, description="旬")
    shensha: List[str] = Field(default_factory=list, description="神煞")
    forDayMastertwelveLifeStages: Optional[str] = Field(None, description="星运（日主十二长生）")
    forPillarStemtwelveLifeStages: Optional[str] = Field(None, description="自坐(本柱十二长生)")
    kongwang: str = Field(..., description="柱的空亡")


class FourPillars(BaseModel):
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar


class NatalChart(BaseModel):
    day_master: str = Field(..., description="日主")
    day_master_element: str = Field(..., description="日主五行")
    day_master_yinyang: str = Field(..., description="日主阴阳")
    conception_pillar: str = Field(..., description="胎元")
    fetal_breath: str = Field(..., description="胎息")
    body_pillar: str = Field(..., description="身宫")
    life_pillar: Optional[str] = Field(None, description="命宫")
    life_trigram: Optional[str] = Field(None, description="命卦")
    kongwang: str = Field(..., description="空亡")
    shensha: List[str] = Field(
        default_factory=list, description="全盘神煞，所有柱位中神煞的汇总。位置可以在具体柱位查看”"
    )
    calc_rules: dict[str, str] = Field(default_factory=dict, description="计算流派/口径")
    four_pillars: FourPillars = Field(..., description="四柱信息")


class AnnualDetail(BaseModel):
    age: int = Field(..., description="流年年龄")
    gregorian_year: Optional[int] = Field(None, description="对应公历年")
    annual_pillar: str = Field(..., description="流年干支")
    annual_tengod: Optional[str] = Field(None, description="流年十神（以日主为准）")
    annual_element: Optional[str] = Field(None, description="流年天干五行")
    annual_yinyang: Optional[str] = Field(None, description="流年天干阴阳")
    minor_pillar: str = Field(..., description="小运干支")


class MajorCycle(BaseModel):
    age_range: Tuple[int, int] = Field(..., description="大运年龄范围")
    pillar: str = Field(..., description="大运干支")
    year_range: Optional[Tuple[int, int]] = Field(None, description="大运公历年范围")
    tengod: Optional[str] = Field(None, description="大运十神（以日主为准）")
    element: Optional[str] = Field(None, description="大运天干五行")
    yinyang: Optional[str] = Field(None, description="大运天干阴阳")
    annual_details: List[AnnualDetail] = Field(default_factory=list, description="流年详情")


class LuckCycles(BaseModel):
    start_age: int = Field(..., description="大运起始年龄")
    start_date: Optional[str] = Field(None, description="起运公历日期")
    direction: Optional[str] = Field(None, description="顺逆行规则")
    major_cycles: List[MajorCycle] = Field(default_factory=list, description="大运列表")


class TargetFlow(BaseModel):
    target_datetime: datetime = Field(..., description="目标日期时间")
    lunar_date: Optional[str] = Field(None, description="目标日期农历")
    year_pillar: str = Field(..., description="流年干支")
    month_pillar: str = Field(..., description="流月干支")
    day_pillar: str = Field(..., description="流日干支")
    hour_pillar: str = Field(..., description="流时干支")
    year_tengod: Optional[str] = Field(None, description="流年十神")
    month_tengod: Optional[str] = Field(None, description="流月十神")
    day_tengod: Optional[str] = Field(None, description="流日十神")
    hour_tengod: Optional[str] = Field(None, description="流时十神")
    year_element: Optional[str] = Field(None, description="流年天干五行")
    month_element: Optional[str] = Field(None, description="流月天干五行")
    day_element: Optional[str] = Field(None, description="流日天干五行")
    hour_element: Optional[str] = Field(None, description="流时天干五行")
    year_yinyang: Optional[str] = Field(None, description="流年天干阴阳")
    month_yinyang: Optional[str] = Field(None, description="流月天干阴阳")
    day_yinyang: Optional[str] = Field(None, description="流日天干阴阳")
    hour_yinyang: Optional[str] = Field(None, description="流时天干阴阳")
    minor_pillar: Optional[str] = Field(None, description="目标年份小运干支")
    flow_months: List["FlowMonth"] = Field(default_factory=list, description="目标年份流月列表")


class FlowMonth(BaseModel):
    index: int = Field(..., description="流月序号")
    solar_term: str = Field(..., description="流月起点节气")
    start_date: str = Field(..., description="流月起始公历日期")
    month_pillar: str = Field(..., description="流月干支")
    month_tengod: Optional[str] = Field(None, description="流月十神")
    month_element: Optional[str] = Field(None, description="流月天干五行")
    month_yinyang: Optional[str] = Field(None, description="流月天干阴阳")


class RelationParticipant(BaseModel):
    pillar: str = Field(..., description="参与关系的柱位")
    position: str = Field(..., description="所在位置，天干或地支")
    value: str = Field(..., description="对应的天干或地支")


class RelationPeer(BaseModel):
    pillar: str = Field(..., description="其他参与柱位")
    value: str = Field(..., description="其他参与方的天干或地支")


class RelationEvent(BaseModel):
    name: str = Field(..., description="关系名称，如天干五合、地支三合")
    relation: str = Field(..., description="关系大类，如合、冲、刑、害、破、会")
    participants: List[RelationParticipant] = Field(default_factory=list, description="参与关系的柱位明细")
    result: Optional[str] = Field(None, description="关系结果，如化土、火局")
    qualifier: Optional[str] = Field(None, description="关系细分说明，如无恩之刑、自刑")


class RelationIndexItem(BaseModel):
    event_index: int = Field(..., description="对应 events 中的索引，从 0 开始")
    name: str = Field(..., description="关系名称")
    relation: str = Field(..., description="关系大类")
    peers: List[RelationPeer] = Field(default_factory=list, description="除当前柱位外的其他参与方")
    result: Optional[str] = Field(None, description="关系结果，如化土、火局")
    qualifier: Optional[str] = Field(None, description="关系细分说明，如无恩之刑、自刑")


class PillarRelations(BaseModel):
    stem: List[RelationIndexItem] = Field(default_factory=list, description="该柱天干参与的关系")
    branch: List[RelationIndexItem] = Field(default_factory=list, description="该柱地支参与的关系")


class RelationByPillar(BaseModel):
    year: PillarRelations = Field(..., description="年柱参与的关系索引")
    month: PillarRelations = Field(..., description="月柱参与的关系索引")
    day: PillarRelations = Field(..., description="日柱参与的关系索引")
    hour: PillarRelations = Field(..., description="时柱参与的关系索引")


class Relations(BaseModel):
    events: List[RelationEvent] = Field(default_factory=list, description="标准化关系事件列表")
    by_pillar: RelationByPillar = Field(..., description="按柱位回查的关系索引")


class WuxingScoreOutput(BaseModel):
    count: int = Field(..., description="五行出现次数")
    score: float = Field(..., description="五行加权分数")
    percentage: float = Field(..., description="五行加权占比百分数")
    balance_label: str = Field(..., description="五行相对分布标签")


class WuxingAnalysisOutput(BaseModel):
    items: dict[str, WuxingScoreOutput] = Field(..., description="五行数量和加权分数")
    month_zhi_wuxing: str = Field(..., description="月支五行")
    strongest: str = Field(..., description="当前加权最旺五行")
    total_score: float = Field(..., description="五行加权总分")


class RootInfoOutput(BaseModel):
    pillar: str = Field(..., description="通根所在柱位")
    branch: str = Field(..., description="通根地支")
    gan: str = Field(..., description="通根天干")
    role: str = Field(..., description="藏干角色")
    score: float = Field(..., description="根气加权分数")


class StrengthAnalysisOutput(BaseModel):
    day_master_wuxing: str = Field(..., description="日主五行")
    month_ling_shishen_family: str = Field(..., description="月令所属十神家族")
    support_score: float = Field(..., description="扶助加权分")
    opposition_score: float = Field(..., description="克泄耗加权分")
    support_ratio: float = Field(..., description="扶助加权占比")
    day_master_has_root: bool = Field(..., description="日主是否通根")
    day_master_root_count: int = Field(..., description="通根数量")
    day_master_root_score: float = Field(..., description="通根加权总分")
    day_master_roots: List[RootInfoOutput] = Field(default_factory=list, description="通根明细")
    day_master_strength: Optional[str] = Field(None, description="日主强弱估计")


class TenGodAnalysisOutput(BaseModel):
    ten_god_scores: dict[str, float] = Field(..., description="十神分布加权分数")
    ten_god_family_scores: dict[str, float] = Field(..., description="十神家族分布加权分数")


class FavorabilityAnalysisOutput(BaseModel):
    favorable_elements: List[str] = Field(default_factory=list, description="倾向补益五行（启发式）")
    unfavorable_elements: List[str] = Field(default_factory=list, description="倾向回避五行（启发式）")
    useful_element: Optional[str] = Field(None, description="首选补益五行（启发式）")
    taboo_element: Optional[str] = Field(None, description="首选回避五行（启发式）")


class GejuAnalysisOutput(BaseModel):
    geju: Optional[str] = Field(None, description="候选格局（启发式）")
    basis: List[str] = Field(default_factory=list, description="候选格局判断依据")


class ChartAnalysisOutput(BaseModel):
    wuxing: WuxingAnalysisOutput = Field(..., description="五行加权分析")
    strength: StrengthAnalysisOutput = Field(..., description="旺衰估计")
    ten_god: TenGodAnalysisOutput = Field(..., description="十神加权分析")
    favorability: FavorabilityAnalysisOutput = Field(..., description="喜忌倾向分析")
    geju: GejuAnalysisOutput = Field(..., description="格局候选分析")
    relations: Relations = Field(..., description="干支关系分析")


class StandardBirthChartOutput(BaseModel):
    personal_info: PersonalInfo = Field(..., description="个人基本信息")
    natal_chart: NatalChart = Field(..., description="八字命盘（静态信息）")
    luck_cycles: LuckCycles = Field(..., description="大运小运流年（动态信息）")
    target_flow: TargetFlow = Field(..., description="指定时间的流年月日时")
    heuristic_analysis: ChartAnalysisOutput = Field(..., description="盘面启发式分析结果，不作为最终结论，仅供参考")

    @validator("personal_info", pre=True)
    def parse_personal_birth(cls, v):
        # 如果传入的是 dict，pydantic 会自动处理 datetime 字段的解析
        return v


def to_standard_format(birth_chart: BirthChart, target_dt: datetime) -> StandardBirthChartOutput:
    """
    将 BirthChart 转换为标准化的输出格式
    """
    target_dt = check_naive_datetime(target_dt)

    def zhu_to_pillar(zhu: ZhuInfo) -> Pillar:

        pillar_str = f"{zhu.gan}{zhu.zhi}"
        xun = _get_sixty_cycle_ten(pillar_str)

        # heaven stem
        hs_name = str(zhu.gan)
        hs_element = str(zhu.gan.belongs_to(Wuxing))
        hs_yinyang = str(zhu.gan.belongs_to(YinYang))
        hs_ten = str(zhu.zhuxing)
        heavenly = HeavenStem(name=hs_name, element=hs_element, yinYang=hs_yinyang, tengod=hs_ten)

        # earthly branch and hidden stems
        eb_name = str(zhu.zhi)
        eb_element = str(zhu.zhi.belongs_to(Wuxing))
        eb_yinyang = str(zhu.zhi.belongs_to(YinYang))
        hidden: list[HiddenStem] = []

        for c in zhu.canggan:

            name = str(c.gan)
            element = str(c.gan.belongs_to(Wuxing))
            yinyang = str(c.gan.belongs_to(YinYang))
            role = str(c.canggan_type)

            ten = str(birth_chart.dayzhu.gan.get_shishen(c.gan))
            hidden.append(HiddenStem(name=name, element=element, yinYang=yinyang, role=role, tengod=ten))
        earthly = EarthBranch(name=eb_name, element=eb_element, yinYang=eb_yinyang, hiddenStems=hidden)

        return Pillar(
            pillar=pillar_str,
            heavenlyStem=heavenly,
            earthlyBranch=earthly,
            nayin=str(zhu.nayin),
            xun=xun,
            shensha=[str(s) for s in zhu.shensha],
            forDayMastertwelveLifeStages=str(zhu.xingyun),
            forPillarStemtwelveLifeStages=str(zhu.zizuo),
            kongwang=",".join([str(s) for s in zhu.kongwang]),
        )

    analysis_output = _build_chart_analysis_output(birth_chart.chart_analysis)

    # personal info
    personal = PersonalInfo(
        gregorian_birth=birth_chart._birth_solar,
        lunar_birth=_get_lunar_date_str(birth_chart),
        gender=str(birth_chart._gender),
        zodiac=birth_chart.chinese_zodiac,
        constellation=birth_chart.sign,
        birth_term=f"{birth_chart.term.get_name()}第{birth_chart.term.get_day_index()}天",
        birth_term_time=str(birth_chart.term.get_solar_term().get_julian_day().get_solar_time()),
    )

    # natal chart
    four = FourPillars(
        year=zhu_to_pillar(birth_chart.yearzhu),
        month=zhu_to_pillar(birth_chart.monthzhu),
        day=zhu_to_pillar(birth_chart.dayzhu),
        hour=zhu_to_pillar(birth_chart.bihourzhu),
    )

    natal = NatalChart(
        day_master=str(birth_chart.dayzhu.gan),
        day_master_element=str(birth_chart.dayzhu.gan.belongs_to(Wuxing)),
        day_master_yinyang=str(birth_chart.dayzhu.gan.belongs_to(YinYang)),
        conception_pillar=birth_chart.taiyuan,
        fetal_breath=birth_chart.taixi,
        body_pillar=birth_chart.shengong,
        life_pillar=birth_chart.minggong,
        life_trigram=birth_chart.minggua,
        kongwang=f"{birth_chart.kongwang[0]}{birth_chart.kongwang[1]}",
        four_pillars=four,
        shensha=_collect_chart_shensha(birth_chart),
        calc_rules=_resolved_calc_rules(birth_chart),
    )

    # luck cycles
    start_age = 0
    major_cycles_list: list[MajorCycle] = []
    child_limit = birth_chart._child_limit

    decade = child_limit.get_start_decade_fortune()
    start_age = decade.get_start_age()
    start_date_str = str(child_limit.get_end_time())
    direction = _get_luck_direction(child_limit)

    for _ in range(0, 10):

        pillar_name = decade.get_sixty_cycle().get_name()
        age_range = (decade.get_start_age(), decade.get_end_age())
        year_range = decade.get_start_sixty_cycle_year().get_year(), decade.get_end_sixty_cycle_year().get_year()
        tengod, element, yinyang = _pillar_tengod_element_yinyang(birth_chart, pillar_name)

        annual_details: list[AnnualDetail] = []

        fortune = decade.get_start_fortune()
        for j in range(0, 10):
            minor = fortune.get_sixty_cycle().get_name()
            annual = fortune.get_sixty_cycle_year().get_sixty_cycle().get_name()
            annual_year = fortune.get_sixty_cycle_year().get_year()
            annual_tg, annual_element, annual_yinyang = _pillar_tengod_element_yinyang(birth_chart, annual)
            annual_details.append(
                AnnualDetail(
                    age=fortune.get_age(),
                    gregorian_year=annual_year,
                    annual_pillar=annual,
                    annual_tengod=annual_tg,
                    annual_element=annual_element,
                    annual_yinyang=annual_yinyang,
                    minor_pillar=minor,
                )
            )
            fortune = fortune.next(1)

        major_cycles_list.append(
            MajorCycle(
                age_range=age_range,
                pillar=pillar_name,
                year_range=year_range,
                tengod=tengod,
                element=element,
                yinyang=yinyang,
                annual_details=annual_details,
            )
        )

        decade = decade.next(1)
    luck = LuckCycles(
        start_age=start_age,
        start_date=start_date_str,
        direction=direction,
        major_cycles=major_cycles_list,
    )

    target_flow = _build_target_flow(birth_chart, target_dt)

    return StandardBirthChartOutput(
        personal_info=personal,
        natal_chart=natal,
        luck_cycles=luck,
        target_flow=target_flow,
        heuristic_analysis=analysis_output,
    )


def plain_draw_chart(birth_chart: BirthChart, target_dt: datetime | None = None) -> None:
    """在终端中绘制适配当前标准输出结构的命盘与分析结果。"""
    render_target = target_dt if target_dt is not None else birth_chart._birth_solar
    output = to_standard_format(birth_chart, render_target)

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    C_HEADER = "\033[96m"
    C_SUBHEADER = "\033[93m"
    C_YEAR = "\033[91m"
    C_MONTH = "\033[92m"
    C_DAY = "\033[94m"
    C_HOUR = "\033[95m"
    C_INFO = "\033[97m"
    C_ACCENT = "\033[36m"
    C_SOFT = "\033[90m"
    WIDTH = 92

    def style(text: str, *codes: str) -> str:
        return "".join(codes) + text + RESET

    def header(title: str) -> None:
        inner = f" {title} "
        pad = max(WIDTH - len(inner), 0)
        left = pad // 2
        right = pad - left
        print()
        print(style("┏" + "━" * WIDTH + "┓", BOLD, C_HEADER))
        print(style("┃" + " " * left + inner + " " * right + "┃", BOLD, C_HEADER))
        print(style("┗" + "━" * WIDTH + "┛", BOLD, C_HEADER))

    def subheader(title: str) -> None:
        print(style(f"\n▶ {title}", BOLD, C_SUBHEADER))

    def line(label: str, value: str | None, color: str = C_INFO, indent: str = "  ") -> None:
        if value is None or value == "":
            value = "无"
        print(f"{indent}{style(label + ':', DIM)} {style(str(value), color)}")

    def wrapped_items(label: str, values: list[str], color: str = C_INFO, indent: str = "  ") -> None:
        if not values:
            line(label, "无", color=color, indent=indent)
            return
        rows: list[str] = []
        current = ""
        for value in values:
            candidate = value if not current else f"{current} / {value}"
            if len(candidate) > 72:
                rows.append(current)
                current = value
            else:
                current = candidate
        if current:
            rows.append(current)
        print(f"{indent}{style(label + ':', DIM)} {style(rows[0], color)}")
        for row in rows[1:]:
            print(f"{indent}{' ' * (len(label) + 2)} {style(row, color)}")

    def draw_bar(
        label: str,
        score: float,
        max_score: float,
        count: int | None = None,
        percentage: float | None = None,
        balance_label: str | None = None,
        color: str = C_INFO,
    ) -> None:
        width = 24
        ratio = 0.0 if max_score <= 0 else score / max_score
        filled = int(ratio * width)
        bar = "█" * filled + "░" * (width - filled)
        count_text = "" if count is None else f"  数量 {count}"
        percentage_text = "" if percentage is None else f"  {percentage:>5.1f}%"
        label_text = "" if balance_label is None else f"  {balance_label}"
        print(
            f"  {style(label, BOLD, color):<10} {style(bar, color)}  "
            f"{score:>5.2f}{percentage_text}{count_text}{label_text}"
        )

    def join_non_empty(values: list[str | None]) -> str:
        return " / ".join([value for value in values if value])

    personal = output.personal_info
    natal = output.natal_chart
    analysis = output.heuristic_analysis

    header("八字命盘")
    line("公历", personal.gregorian_birth.strftime("%Y-%m-%d %H:%M:%S"))
    line("农历", personal.lunar_birth)
    line("性别", personal.gender)
    line("生肖 / 星座", f"{personal.zodiac} / {personal.constellation}")
    line("出生节气", personal.birth_term)
    line("交节时刻", personal.birth_term_time)
    line("时区", getattr(personal, "timezone", None))

    header("四柱盘面")
    pillar_configs = [
        ("年柱", natal.four_pillars.year, C_YEAR),
        ("月柱", natal.four_pillars.month, C_MONTH),
        ("日柱", natal.four_pillars.day, C_DAY),
        ("时柱", natal.four_pillars.hour, C_HOUR),
    ]
    for name, pillar, color in pillar_configs:
        subheader(f"{name}  {pillar.pillar}")
        line(
            "天干",
            f"{pillar.heavenlyStem.name} {pillar.heavenlyStem.element}{pillar.heavenlyStem.yinYang}  主星 {pillar.heavenlyStem.tengod}",
            color=color,
            indent="    ",
        )
        line(
            "地支",
            f"{pillar.earthlyBranch.name} {pillar.earthlyBranch.element}{pillar.earthlyBranch.yinYang}",
            color=color,
            indent="    ",
        )
        hidden_stems = [
            f"{item.name}[{item.role}/{item.tengod}/{item.element}{item.yinYang}]"
            for item in pillar.earthlyBranch.hiddenStems
        ]
        wrapped_items("藏干", hidden_stems, color=color, indent="    ")
        line("纳音 / 旬", join_non_empty([pillar.nayin, pillar.xun]), color=color, indent="    ")
        line(
            "星运 / 自坐",
            join_non_empty([pillar.forDayMastertwelveLifeStages, pillar.forPillarStemtwelveLifeStages]),
            color=color,
            indent="    ",
        )
        line("空亡", pillar.kongwang, color=color, indent="    ")
        wrapped_items("神煞", pillar.shensha, color=color, indent="    ")

    header("命盘摘要")
    line("日主", f"{natal.day_master} {natal.day_master_element}{natal.day_master_yinyang}")
    line("胎元 / 胎息", f"{natal.conception_pillar} / {natal.fetal_breath}")
    line("身宫 / 命宫", f"{natal.body_pillar} / {natal.life_pillar}")
    line("命卦", natal.life_trigram)
    line("全盘空亡", natal.kongwang)
    wrapped_items("全盘神煞", natal.shensha)

    header("分析结果")
    subheader("五行")
    wuxing_items = analysis.wuxing.items
    max_wuxing_score = max((item.score for item in wuxing_items.values()), default=0.0)
    for wuxing in ["木", "火", "土", "金", "水"]:
        item = wuxing_items[wuxing]
        draw_bar(
            wuxing,
            item.score,
            max_wuxing_score,
            count=item.count,
            percentage=item.percentage,
            balance_label=item.balance_label,
            color=C_ACCENT,
        )
    line("月令五行 / 最旺五行", f"{analysis.wuxing.month_zhi_wuxing} / {analysis.wuxing.strongest}")

    subheader("旺衰")
    line("日主强弱", analysis.strength.day_master_strength)
    line(
        "扶助 / 克泄耗",
        f"{analysis.strength.support_score:.2f} / {analysis.strength.opposition_score:.2f}",
    )
    line("扶助占比", f"{analysis.strength.support_ratio:.1%}")
    line("月令家族", analysis.strength.month_ling_shishen_family)
    line(
        "通根",
        f"{'有' if analysis.strength.day_master_has_root else '无'}  共 {analysis.strength.day_master_root_count} 处  分数 {analysis.strength.day_master_root_score:.2f}",
    )
    roots = [
        f"{root.pillar}{root.branch}藏{root.gan}({root.role}, {root.score:.2f})"
        for root in analysis.strength.day_master_roots
    ]
    wrapped_items("根气明细", roots)

    subheader("十神与喜忌")
    family_scores = analysis.ten_god.ten_god_family_scores
    max_family_score = max(family_scores.values(), default=0.0)
    for family in ["比劫", "食伤", "财星", "官杀", "印星"]:
        draw_bar(family, family_scores[family], max_family_score, color=C_INFO)
    line(
        "喜用候选",
        join_non_empty([analysis.favorability.useful_element, "、".join(analysis.favorability.favorable_elements)]),
    )
    line(
        "忌神候选",
        join_non_empty([analysis.favorability.taboo_element, "、".join(analysis.favorability.unfavorable_elements)]),
    )

    subheader("格局与关系")
    line("格局候选", analysis.geju.geju)
    wrapped_items("判断依据", analysis.geju.basis)
    if analysis.relations.events:
        for index, event in enumerate(analysis.relations.events, start=1):
            participants = " + ".join([f"{item.pillar}{item.position}{item.value}" for item in event.participants])
            detail = participants
            if event.result:
                detail += f" => {event.result}"
            if event.qualifier:
                detail += f" ({event.qualifier})"
            print(f"  {style(f'{index:>2}.', DIM)} {style(event.name, BOLD, C_ACCENT)}  {detail}")
    else:
        line("关系事件", "无")

    header("运势")
    line("起运", f"{output.luck_cycles.start_age}岁")
    line("起运日期", output.luck_cycles.start_date)
    line("顺逆", output.luck_cycles.direction)
    subheader("前八步大运")
    for index, cycle in enumerate(output.luck_cycles.major_cycles[:8], start=1):
        age_text = f"{cycle.age_range[0]}-{cycle.age_range[1]}岁"
        year_text = f"{cycle.year_range[0]}-{cycle.year_range[1]}" if cycle.year_range is not None else "年份待补"
        detail = join_non_empty([cycle.tengod, cycle.element, cycle.yinyang])
        print(
            f"  {style(f'{index:>2}.', DIM)} {style(cycle.pillar, BOLD, C_INFO)}  {age_text:<12} {year_text:<12} {detail}"
        )

    if target_dt is not None:
        header("目标时刻流转")
        flow = output.target_flow
        line("目标时刻", flow.target_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        line("目标农历", flow.lunar_date)
        line(
            "流转四柱",
            f"{flow.year_pillar} / {flow.month_pillar} / {flow.day_pillar} / {flow.hour_pillar}",
        )
        line(
            "流转十神",
            f"年{flow.year_tengod} 月{flow.month_tengod} 日{flow.day_tengod} 时{flow.hour_tengod}",
        )
        line("目标年份小运", flow.minor_pillar)
        subheader("流月")
        for month in flow.flow_months:
            detail = join_non_empty([month.month_tengod, month.month_element, month.month_yinyang])
            print(
                f"  {style(f'{month.index:>2}.', DIM)} {style(month.solar_term, BOLD, C_INFO)}  "
                f"{month.start_date}  {month.month_pillar}  {detail}"
            )

    header("计算口径")
    for key, value in natal.calc_rules.items():
        line(key, value, color=C_SOFT)

    print()
    print(
        style("注：旺衰、喜忌、格局、关系结果属于程序化分析输出，适合对照与检索，不应直接替代人工断盘。", DIM, C_SOFT)
    )
    print()


def _safe_call(obj: object, method: str):
    if obj is None:
        return None
    func = getattr(obj, method, None)
    if callable(func):
        try:
            return func()
        except Exception:
            return None
    return None


def _get_lunar_date_str(birth_chart: BirthChart) -> Optional[str]:
    lunar_hour = birth_chart._solar_time.get_lunar_hour()
    if lunar_hour is None:
        return None
    return str(lunar_hour)


def _collect_chart_shensha(birth_chart: BirthChart) -> List[str]:
    result: list[str] = []
    for zhu in [birth_chart.yearzhu, birth_chart.monthzhu, birth_chart.dayzhu, birth_chart.bihourzhu]:
        for s in zhu.shensha:
            name = str(s)
            if name not in result:
                result.append(name)
    return result


def _pillar_tengod_element_yinyang(
    birth_chart: BirthChart, pillar: str
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    if not pillar or len(pillar) < 2:
        return None, None, None
    gan = Tiangan[pillar[0]]
    tengod = str(birth_chart.dayzhu.gan.get_shishen(gan))
    element = str(gan.belongs_to(Wuxing))
    yinyang = str(gan.belongs_to(YinYang))
    return tengod, element, yinyang


def _get_luck_direction(child_limit: object) -> Optional[str]:
    is_forward = _safe_call(child_limit, "is_forward")
    if isinstance(is_forward, bool):
        return "顺行" if is_forward else "逆行"
    return None


def _get_decade_year_range(decade: object) -> Optional[Tuple[int, int]]:
    start = decade.get_start_sixty_cycle_year().get_year()
    end = decade.get_end_sixty_cycle_year().get_year()
    return (start, end)


def _build_target_flow(birth_chart: BirthChart, target_dt: datetime) -> TargetFlow:
    # 使用 tyme4py 的 SolarTime/EightChar 计算流年月日时
    solar_time = birth_chart._solar_time.__class__.from_ymd_hms(
        target_dt.year, target_dt.month, target_dt.day, target_dt.hour, target_dt.minute, target_dt.second
    )
    lunar_hour = solar_time.get_lunar_hour()
    eight_char = BirthChart.calc_eightchar(lunar_hour, birth_chart._calc_rules)

    year_pillar = eight_char.get_year().get_name()
    month_pillar = eight_char.get_month().get_name()
    day_pillar = eight_char.get_day().get_name()
    hour_pillar = eight_char.get_hour().get_name()

    year_tg, year_element, year_yinyang = _pillar_tengod_element_yinyang(birth_chart, year_pillar)
    month_tg, month_element, month_yinyang = _pillar_tengod_element_yinyang(birth_chart, month_pillar)
    day_tg, day_element, day_yinyang = _pillar_tengod_element_yinyang(birth_chart, day_pillar)
    hour_tg, hour_element, hour_yinyang = _pillar_tengod_element_yinyang(birth_chart, hour_pillar)

    lunar_date = str(lunar_hour)
    flow_year_strategy = _get_flow_year_strategy(birth_chart)
    flow_year = _resolve_flow_year(target_dt, flow_year_strategy)
    flow_months = _build_flow_months(birth_chart, flow_year, flow_year_strategy)
    minor_pillar = _find_minor_pillar_for_year(birth_chart, flow_year)

    return TargetFlow(
        target_datetime=target_dt,
        lunar_date=lunar_date,
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        year_tengod=year_tg,
        month_tengod=month_tg,
        day_tengod=day_tg,
        hour_tengod=hour_tg,
        year_element=year_element,
        month_element=month_element,
        day_element=day_element,
        hour_element=hour_element,
        year_yinyang=year_yinyang,
        month_yinyang=month_yinyang,
        day_yinyang=day_yinyang,
        hour_yinyang=hour_yinyang,
        minor_pillar=minor_pillar,
        flow_months=flow_months,
    )


def _resolve_flow_year(target_dt: datetime, strategy: str) -> int:
    # 以立春为年界，确定流年所属的节气年（预留流派扩展入口）
    if strategy != "lichun_boundary":
        pass
    lichun = solar.SolarTerm.from_name(target_dt.year, "立春")
    lichun_time = lichun.get_julian_day().get_solar_time()
    lichun_dt = datetime(
        lichun_time.get_year(),
        lichun_time.get_month(),
        lichun_time.get_day(),
        lichun_time.get_hour(),
        lichun_time.get_minute(),
        lichun_time.get_second(),
    )
    return target_dt.year - 1 if target_dt < lichun_dt else target_dt.year


def _build_flow_months(birth_chart: BirthChart, flow_year: int, strategy: str) -> List[FlowMonth]:
    # 按节气月（十二节）生成流月列表，作为统一口径的实现（预留流派扩展入口）
    if strategy != "solar_term_month_start":
        pass
    term_names = [
        "立春",
        "惊蛰",
        "清明",
        "立夏",
        "芒种",
        "小暑",
        "立秋",
        "白露",
        "寒露",
        "立冬",
        "大雪",
        "小寒",
    ]
    flow_months: list[FlowMonth] = []
    for idx, name in enumerate(term_names, start=1):
        term_year = flow_year + 1 if name == "小寒" else flow_year
        term = solar.SolarTerm.from_name(term_year, name)
        term_time = term.get_julian_day().get_solar_time()
        term_dt = datetime(
            term_time.get_year(),
            term_time.get_month(),
            term_time.get_day(),
            term_time.get_hour(),
            term_time.get_minute(),
            term_time.get_second(),
        )
        solar_time = birth_chart._solar_time.__class__.from_ymd_hms(
            term_dt.year, term_dt.month, term_dt.day, term_dt.hour, term_dt.minute, term_dt.second
        )
        month_pillar = (
            BirthChart.calc_eightchar(solar_time.get_lunar_hour(), birth_chart._calc_rules).get_month().get_name()
        )
        month_tg, month_element, month_yinyang = _pillar_tengod_element_yinyang(birth_chart, month_pillar)
        start_date = term_dt.strftime("%Y-%m-%d")
        flow_months.append(
            FlowMonth(
                index=idx,
                solar_term=name,
                start_date=start_date,
                month_pillar=month_pillar,
                month_tengod=month_tg,
                month_element=month_element,
                month_yinyang=month_yinyang,
            )
        )
    return flow_months


def _find_minor_pillar_for_year(birth_chart: BirthChart, target_year: int) -> Optional[str]:
    child_limit = birth_chart._child_limit
    decade = child_limit.get_start_decade_fortune()
    if decade is None:
        return None
    fortune = decade.get_start_fortune()
    if fortune is None:
        return None

    current_year = fortune.get_sixty_cycle_year().get_year()
    if current_year is None:
        return None

    step = 1 if target_year >= current_year else -1
    for _ in range(0, 180):
        year = fortune.get_sixty_cycle_year().get_year()
        if year == target_year:
            return fortune.get_sixty_cycle().get_name()
        fortune = fortune.next(step)
    return None


def _resolved_calc_rules(birth_chart: BirthChart) -> dict[str, str]:
    return {
        "minggua": birth_chart._calc_rules.get("minggua", "bazhai"),
        "minggong": birth_chart._calc_rules.get("minggong", "eightchar_own_sign"),
        "zi_hour": birth_chart._calc_rules.get("zi_hour", "lunar_sect2_day_same"),
        "analysis_framework": birth_chart._calc_rules.get("analysis_framework", "heuristic_scoring_v1"),
        "day_master_strength": birth_chart._calc_rules.get("day_master_strength", "simple_score"),
        "favorability": birth_chart._calc_rules.get("favorability", "strength_balance_heuristic"),
        "geju": birth_chart._calc_rules.get("geju", "rule_based_candidate_match"),
        "relations": birth_chart._calc_rules.get("relations", "core_relations_v2"),
        "flow_months": birth_chart._calc_rules.get("flow_months", "solar_term_month_start"),
        "minor_fortune": birth_chart._calc_rules.get("minor_fortune", "child_limit"),
        "flow_year": birth_chart._calc_rules.get("flow_year", "lichun_boundary"),
    }


def _get_flow_year_strategy(birth_chart: BirthChart) -> str:
    return birth_chart._calc_rules.get("flow_year", "lichun_boundary")


def _get_sixty_cycle_ten(pillar: str) -> Optional[str]:
    try:
        sc = sixtycycle.SixtyCycle.from_name(pillar)
    except Exception:
        return None
    try:
        ten = sc.get_ten()
        return str(ten)
    except Exception:
        return None


def _build_relation_event_output(event) -> RelationEvent:
    return RelationEvent(
        name=event.name,
        relation=str(event.relation_type),
        participants=[
            RelationParticipant(
                pillar=participant.pillar.value,
                position=participant.position.value,
                value=str(participant.value),
            )
            for participant in event.participants
        ],
        result=str(event.outcome) if event.outcome else None,
        qualifier=str(event.qualifier) if event.qualifier else None,
    )


def _build_relation_index_item_output(item) -> RelationIndexItem:
    return RelationIndexItem(
        event_index=item.event_index,
        name=item.name,
        relation=str(item.relation_type),
        peers=[RelationPeer(pillar=peer.pillar.value, value=str(peer.value)) for peer in item.peers],
        result=str(item.outcome) if item.outcome else None,
        qualifier=str(item.qualifier) if item.qualifier else None,
    )


def _build_chart_analysis_output(analysis: InternalChartAnalysis) -> ChartAnalysisOutput:
    total_score = analysis.wuxing.total_score
    wuxing_items = {
        str(wuxing): WuxingScoreOutput(
            count=item.count,
            score=round(item.score, 3),
            percentage=round(_wuxing_percentage(item.score, total_score), 2),
            balance_label=_wuxing_balance_label(item.score, total_score),
        )
        for wuxing, item in analysis.wuxing.items.items()
    }
    strength = analysis.strength
    ten_god = analysis.ten_god
    favorability = analysis.favorability
    geju = analysis.geju

    return ChartAnalysisOutput(
        wuxing=WuxingAnalysisOutput(
            items=wuxing_items,
            month_zhi_wuxing=str(analysis.wuxing.month_zhi_wuxing) if analysis.wuxing.month_zhi_wuxing else "",
            strongest=str(analysis.wuxing.strongest) if analysis.wuxing.strongest else "",
            total_score=round(analysis.wuxing.total_score, 3),
        ),
        strength=StrengthAnalysisOutput(
            day_master_wuxing=str(strength.day_master_wuxing) if strength.day_master_wuxing else "",
            month_ling_shishen_family=strength.month_ling_shishen_family,
            support_score=round(strength.support_score, 3),
            opposition_score=round(strength.opposition_score, 3),
            support_ratio=round(strength.support_ratio, 4),
            day_master_has_root=strength.day_master_has_root,
            day_master_root_count=strength.day_master_root_count,
            day_master_root_score=round(strength.day_master_root_score, 3),
            day_master_roots=[
                RootInfoOutput(
                    pillar=item.pillar,
                    branch=str(item.branch),
                    gan=str(item.gan),
                    role=str(item.role),
                    score=round(item.score, 3),
                )
                for item in strength.day_master_roots
            ],
            day_master_strength=str(strength.day_master_strength) if strength.day_master_strength else None,
        ),
        ten_god=TenGodAnalysisOutput(
            ten_god_scores={str(key): round(value, 3) for key, value in ten_god.scores.items()},
            ten_god_family_scores={key: round(value, 3) for key, value in ten_god.family_scores.items()},
        ),
        favorability=FavorabilityAnalysisOutput(
            favorable_elements=[str(item) for item in favorability.favorable_elements],
            unfavorable_elements=[str(item) for item in favorability.unfavorable_elements],
            useful_element=str(favorability.useful_element) if favorability.useful_element else None,
            taboo_element=str(favorability.taboo_element) if favorability.taboo_element else None,
        ),
        geju=GejuAnalysisOutput(
            geju=geju.geju.value if geju.geju else None,
            basis=list(geju.basis),
        ),
        relations=Relations(
            events=[_build_relation_event_output(event) for event in analysis.relations.events],
            by_pillar=RelationByPillar(
                year=PillarRelations(
                    stem=[
                        _build_relation_index_item_output(item) for item in analysis.relations.pillar_index.year.tiangan
                    ],
                    branch=[
                        _build_relation_index_item_output(item) for item in analysis.relations.pillar_index.year.dizhi
                    ],
                ),
                month=PillarRelations(
                    stem=[
                        _build_relation_index_item_output(item)
                        for item in analysis.relations.pillar_index.month.tiangan
                    ],
                    branch=[
                        _build_relation_index_item_output(item) for item in analysis.relations.pillar_index.month.dizhi
                    ],
                ),
                day=PillarRelations(
                    stem=[
                        _build_relation_index_item_output(item) for item in analysis.relations.pillar_index.day.tiangan
                    ],
                    branch=[
                        _build_relation_index_item_output(item) for item in analysis.relations.pillar_index.day.dizhi
                    ],
                ),
                hour=PillarRelations(
                    stem=[
                        _build_relation_index_item_output(item) for item in analysis.relations.pillar_index.hour.tiangan
                    ],
                    branch=[
                        _build_relation_index_item_output(item) for item in analysis.relations.pillar_index.hour.dizhi
                    ],
                ),
            ),
        ),
    )


def _wuxing_percentage(score: float, total_score: float) -> float:
    if total_score <= 0:
        return 0.0
    return score / total_score * 100


def _wuxing_balance_label(score: float, total_score: float) -> str:
    percentage = _wuxing_percentage(score, total_score)
    if percentage < 12:
        return "明显偏弱"
    if percentage < 16:
        return "偏弱"
    if percentage <= 24:
        return "均衡"
    if percentage < 30:
        return "偏旺"
    return "明显偏旺"
