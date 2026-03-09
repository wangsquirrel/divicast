from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional, Tuple

from pydantic import BaseModel, Field, validator
from tyme4py import sixtycycle, solar

from ..entities.ganzhi import Tiangan
from ..entities.wuxing import Wuxing, YinYang
from .analysis import Strength
from .birth import BirthChart, Gender, ZhuInfo
from .geju import Geju


class PersonalInfo(BaseModel):
    gregorian_birth: datetime = Field(..., description="公历出生时间")
    lunar_birth: Optional[str] = Field(None, description="农历出生日期")
    true_solar_birth: Optional[str] = Field(None, description="真太阳时（若可得）")
    gender: str = Field(..., description="性别，男/女")
    zodiac: str = Field(..., description="生肖")
    constellation: str = Field(..., description="星座")
    birth_term: str = Field(..., description="出生节气")
    birth_term_time: Optional[str] = Field(None, description="节气交节时间")
    timezone: Optional[str] = Field(None, description="时区信息")


class HiddenStem(BaseModel):
    name: str = Field(..., description="藏干名称")
    element: str = Field(..., description="藏干五行")
    yinYang: str = Field(..., description="阴阳")
    role: str = Field(..., description="本气/中气/余气")
    tenGod: str = Field(..., description="十神(副星)")


class HeavenStem(BaseModel):
    name: str = Field(..., description="天干名称")
    element: str = Field(..., description="五行")
    yinYang: str = Field(..., description="阴阳")
    tenGod: str = Field(..., description="十神(主星)")


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
    tiangan_relations: Optional[str] = Field(None, description="天干关系")
    dizhi_relations: Optional[str] = Field(None, description="地支关系")


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
    shensha: List[str] = Field(default_factory=list, description="全盘神煞")
    element_scores: dict = Field(..., description="五行分数")
    day_master_strength: Optional[Strength] = Field(None, description="身强/身弱")
    favorable_elements: List[str] = Field(default_factory=list, description="喜用神对应五行")
    unfavorable_elements: List[str] = Field(default_factory=list, description="忌神对应五行")
    useful_element: Optional[str] = Field(None, description="用神")
    taboo_element: Optional[str] = Field(None, description="忌神")
    geju: Optional[Geju] = Field(None, description="命盘格局")
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


class RelationItem(BaseModel):
    target: str = Field(..., description="对应柱位")
    relation: str = Field(..., description="关系类型")


class PillarRelations(BaseModel):
    stem: List[RelationItem] = Field(default_factory=list, description="天干关系")
    branch: List[RelationItem] = Field(default_factory=list, description="地支关系")


class Relations(BaseModel):
    year: PillarRelations
    month: PillarRelations
    day: PillarRelations
    hour: PillarRelations


class StandardBirthChartOutput(BaseModel):
    personal_info: PersonalInfo = Field(..., description="个人基本信息")
    natal_chart: NatalChart = Field(..., description="八字命盘（静态信息）")
    luck_cycles: LuckCycles = Field(..., description="大运小运流年（动态信息）")
    target_flow: TargetFlow = Field(..., description="指定时间的流年月日时")
    relations: Relations = Field(..., description="刑冲合会（简化）")
    chart_analysis: dict[str, Any] = Field(..., description="五行分析结果")

    @validator("personal_info", pre=True)
    def parse_personal_birth(cls, v):
        # 如果传入的是 dict，pydantic 会自动处理 datetime 字段的解析
        return v


def to_standard_format(birth_chart: BirthChart, target_dt: datetime) -> StandardBirthChartOutput:
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
        xun = _get_sixty_cycle_ten(pillar_str)

        # heaven stem
        hs_name = zhu.gan.chinese_name
        hs_element = zhu.gan.belongs_to(Wuxing).chinese_name
        hs_yinyang = zhu.gan.belongs_to(YinYang).chinese_name
        hs_ten = zhu.zhuxing.chinese_name
        heavenly = HeavenStem(name=hs_name, element=hs_element, yinYang=hs_yinyang, tenGod=hs_ten)

        # earthly branch and hidden stems
        eb_name = zhu.zhi.chinese_name
        eb_element = zhu.zhi.belongs_to(Wuxing).chinese_name
        eb_yinyang = zhu.zhi.belongs_to(YinYang).chinese_name
        hidden: list[HiddenStem] = []

        for c in zhu.canggan:

            name = c.gan.chinese_name
            element = c.gan.belongs_to(Wuxing).chinese_name
            yinyang = c.gan.belongs_to(YinYang).chinese_name
            ctype_name = c.canggan_type.name
            role = role_map[ctype_name]

            ten = birth_chart.dayzhu.gan.get_shishen(c.gan).chinese_name
            hidden.append(HiddenStem(name=name, element=element, yinYang=yinyang, role=role, tenGod=ten))
        earthly = EarthBranch(name=eb_name, element=eb_element, yinYang=eb_yinyang, hiddenStems=hidden)

        return Pillar(
            pillar=pillar_str,
            heavenlyStem=heavenly,
            earthlyBranch=earthly,
            nayin=zhu.nayin.chinese_name,
            xun=xun,
            shensha=[str(s) for s in zhu.shensha],
            forDayMastertwelveLifeStages=zhu.xingyun.chinese_name,
            forPillarStemtwelveLifeStages=zhu.zizuo.chinese_name,
            kongwang=",".join([str(s) for s in zhu.kongwang]),
            tiangan_relations=zhu.tiangan_relations,
            dizhi_relations=zhu.dizhi_relations,
        )

    # personal info
    personal = PersonalInfo(
        gregorian_birth=birth_chart._birth_solar,
        lunar_birth=_get_lunar_date_str(birth_chart),
        true_solar_birth=_get_true_solar_time_str(birth_chart),
        gender="男" if birth_chart._gender == Gender.MAN else "女",
        zodiac=birth_chart.chinese_zodiac,
        constellation=birth_chart.sign,
        birth_term=f"{birth_chart.term.get_name()}第{birth_chart.term.get_day_index()}天",
        birth_term_time=_get_birth_term_time_str(birth_chart),
        timezone=str(birth_chart._birth_solar.tzinfo) if birth_chart._birth_solar.tzinfo else None,
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
        day_master_element=birth_chart.dayzhu.gan.belongs_to(Wuxing).chinese_name,
        day_master_yinyang=birth_chart.dayzhu.gan.belongs_to(YinYang).chinese_name,
        conception_pillar=birth_chart.taiyuan,
        fetal_breath=birth_chart.taixi,
        body_pillar=birth_chart.shengong,
        life_pillar=birth_chart.minggong,
        life_trigram=birth_chart.minggua,
        kongwang=birth_chart.kongwang[0].chinese_name + birth_chart.kongwang[1].chinese_name,
        four_pillars=four,
        shensha=_collect_chart_shensha(birth_chart),
        element_scores=birth_chart.chart_analysis,
        day_master_strength=_calc_day_master_strength(birth_chart),
        favorable_elements=_calc_favorable_elements(birth_chart),
        unfavorable_elements=_calc_unfavorable_elements(birth_chart),
        useful_element=_calc_useful_element(birth_chart),
        taboo_element=_calc_taboo_element(birth_chart),
        geju=birth_chart.geju,
        calc_rules=_resolved_calc_rules(birth_chart),
    )

    # luck cycles
    start_age = 0
    major_cycles_list: list[MajorCycle] = []
    child_limit = birth_chart._child_limit

    decade = child_limit.get_start_decade_fortune()
    start_age = decade.get_start_age()
    start_date_str = _safe_time_str(_safe_call(child_limit, "get_end_time"))
    direction = _get_luck_direction(child_limit)

    for _ in range(0, 10):

        pillar_name = decade.get_sixty_cycle().get_name()
        age_range = (decade.get_start_age(), decade.get_end_age())
        year_range = _get_decade_year_range(decade)
        tengod, element, yinyang = _pillar_tengod_element_yinyang(birth_chart, pillar_name)

        annual_details: list[AnnualDetail] = []

        fortune = decade.get_start_fortune()
        for j in range(0, 10):
            minor = fortune.get_sixty_cycle().get_name()
            annual = fortune.get_sixty_cycle_year().get_sixty_cycle().get_name()
            annual_year = _safe_year_value(_safe_call(fortune.get_sixty_cycle_year(), "get_year"))
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
    relations = _build_relations(birth_chart)

    return StandardBirthChartOutput(
        personal_info=personal,
        natal_chart=natal,
        luck_cycles=luck,
        target_flow=target_flow,
        relations=relations,
        chart_analysis=birth_chart.chart_analysis,
    )


def plain_draw_chart(birth_chart: BirthChart, target_dt: datetime | None = None) -> None:
    """绘制命盘的函数示例"""
    # ANSI 颜色代码
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # 颜色
    C_HEADER = "\033[96m"  # 青色 - 标题
    C_SUBHEADER = "\033[93m"  # 黄色 - 副标题
    C_YEAR = "\033[91m"  # 红色 - 年柱
    C_MONTH = "\033[92m"  # 绿色 - 月柱
    C_DAY = "\033[94m"  # 蓝色 - 日柱
    C_HOUR = "\033[95m"  # 紫色 - 时柱
    C_INFO = "\033[97m"  # 白色 - 信息
    C_ACCENT = "\033[96m"  # 青色 - 强调

    def print_header(title: str):
        print(f"\n{BOLD}{C_HEADER}{'=' * 50}{RESET}")
        print(f"{BOLD}{C_HEADER}{title:^50}{RESET}")
        print(f"{BOLD}{C_HEADER}{'=' * 50}{RESET}")

    def print_subheader(title: str):
        print(f"\n{BOLD}{C_SUBHEADER}■ {title}{RESET}")

    def p(key: str, value: str, color: str = C_INFO):
        print(f"  {color}{key}: {value}{RESET}")

    # ========== 基本信息 ==========
    print_header("基 本 信 息")
    gender_str = "男" if birth_chart._gender == Gender.MAN else "女"
    p("公历生日", birth_chart._birth_solar.strftime("%Y-%m-%d %H:%M:%S"))
    p("性别", gender_str)
    p("生肖", birth_chart.chinese_zodiac)
    p("星座", birth_chart.sign)
    p("出生节气", f"{birth_chart.term.get_name()}第{birth_chart.term.get_day_index()}天")

    # ========== 四柱八字 ==========
    print_header("四 柱 八 字")

    # 构建八字表格
    pillars = [
        ("年柱", birth_chart.yearzhu, C_YEAR),
        ("月柱", birth_chart.monthzhu, C_MONTH),
        ("日柱", birth_chart.dayzhu, C_DAY),
        ("时柱", birth_chart.bihourzhu, C_HOUR),
    ]

    # 打印表头
    print(f"\n{BOLD}{'柱位':<8}{'天干':<6}{'地支':<6}{'纳音':<8}{'主星':<8}{'副星':<12}{'空亡':<8}{RESET}")
    print("-" * 70)

    for name, zhu, color in pillars:
        pillar_str = zhu.gan.chinese_name + zhu.zhi.chinese_name
        nayin = zhu.nayin.chinese_name
        zhuxing = zhu.zhuxing.chinese_name
        fuxing_str = "/".join([f.chinese_name for f in zhu.fuxing])
        kongwang_str = zhu.kongwang[0].chinese_name + zhu.kongwang[1].chinese_name
        print(
            f"{color}{name:<8}{pillar_str[0]:<6}{pillar_str[1]:<6}{nayin:<8}{zhuxing:<8}{fuxing_str:<12}{kongwang_str:<8}{RESET}"
        )

    # ========== 日主信息 ==========
    print_subheader("日主信息")
    day_master = birth_chart.dayzhu.gan
    day_element = day_master.belongs_to(Wuxing)
    day_yinyang = day_master.belongs_to(YinYang)
    p("日主", f"{day_master.chinese_name} ({day_element.chinese_name}·{day_yinyang.chinese_name})")

    # 五行分析
    if birth_chart.chart_analysis:
        print_subheader("五行分数")
        scores = birth_chart.chart_analysis
        wuxing_list = ["木", "火", "土", "金", "水"]
        max_score = max((scores.get(w, {}).get("score", 0) for w in wuxing_list), default=1)

        bar_chars = "▏▎▍▌▋▊█"
        for w in wuxing_list:
            score = scores.get(w, {}).get("score", 0)
            count = scores.get(w, {}).get("count", 0)
            # 归一化并绘制条形图
            ratio = score / max_score if max_score > 0 else 0
            bar_len = int(ratio * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"  {w}: {bar} ({score:.1f}) [数量: {count}]")

        p("月令", scores.get("month_zhi_wuxing", ""))
        p("最强五行", scores.get("strongest", ""))

        # 身强身弱判断
        total = sum(v["score"] for v in scores.values() if isinstance(v, dict))
        if total > 0:
            avg = total / 5
            day_master_score = scores.get(day_element.chinese_name, {}).get("score", 0)
            strength = "身强" if day_master_score >= avg else "身弱"
            p("日主强弱", strength)

    # ========== 宫位信息 ==========
    print_subheader("宫位信息")
    p("胎元", birth_chart.taiyuan)
    p("胎息", birth_chart.taixi)
    p("身宫", birth_chart.shengong)
    p("命宫", birth_chart.minggong)
    p("命卦", birth_chart.minggua if birth_chart.minggua else "")
    p("空亡", birth_chart.kongwang[0].chinese_name + birth_chart.kongwang[1].chinese_name)

    # ========== 格局信息 ==========
    if birth_chart.geju:
        print_subheader("格局分析")
        geju = birth_chart.geju
        p("格局类型", geju.value)

    # ========== 神煞汇总 ==========
    print_subheader("神煞汇总")

    # 收集每个柱的神煞
    pillar_names = ["年柱", "月柱", "日柱", "时柱"]
    pillars = [birth_chart.yearzhu, birth_chart.monthzhu, birth_chart.dayzhu, birth_chart.bihourzhu]

    # 按柱分类收集神煞
    shensha_by_pillar: dict[str, list[str]] = {name: [] for name in pillar_names}

    for zhu, name in zip(pillars, pillar_names):
        for s in zhu.shensha:
            shensha_str = str(s)
            if shensha_str not in shensha_by_pillar[name]:
                shensha_by_pillar[name].append(shensha_str)

    # 打印每个柱的神煞
    has_shensha = False
    for name in pillar_names:
        shensha_list = shensha_by_pillar[name]
        if shensha_list:
            has_shensha = True
            print(f"  {C_ACCENT}{name}:{RESET} ", end="")
            # 每行显示4个
            for i, s in enumerate(shensha_list):
                if i > 0 and i % 4 == 0:
                    print(f"\n  {'':12}", end="")
                if i > 0:
                    print(" / ", end="")
                print(f"{C_ACCENT}{s}{RESET}", end="")
            print()

    if not has_shensha:
        print("  无")

    # ========== 大运 ==========
    print_header("大 运 走 向")
    decade_fortune = birth_chart._child_limit.get_start_decade_fortune()
    start_age = decade_fortune.get_start_age()
    p("起运年龄", f"{start_age}岁")

    # 判断顺逆
    child_limit = birth_chart._child_limit
    is_forward = getattr(child_limit, "is_forward", lambda: True)()
    direction = "顺行" if is_forward else "逆行"
    p("运程方向", direction)

    # 打印前8步大运
    print_subheader("大运干支")
    print(f"\n{BOLD}{'序号':<6}{'年龄':<12}{'干支':<8}{'天干':<6}{'五行':<6}{'阴阳':<6}{RESET}")
    print("-" * 60)

    for i in range(0, 8):
        pillar_name = decade_fortune.get_sixty_cycle().get_name()
        gan = Tiangan.from_chinese_name(pillar_name[0])
        tengod = birth_chart.dayzhu.gan.get_shishen(gan).chinese_name
        element = gan.belongs_to(Wuxing).chinese_name
        yinyang = gan.belongs_to(YinYang).chinese_name

        age_start = decade_fortune.get_start_age()
        age_end = decade_fortune.get_end_age()

        print(f"{i+1:<6}{age_start}-{age_end}岁{pillar_name:<8}{tengod:<6}{element:<6}{yinyang:<6}")
        decade_fortune = decade_fortune.next(1)

    # ========== 流年 (80岁以前，按大运分组) ==========
    print_subheader("流年预览 (80岁以前)")

    decade_fortune = birth_chart._child_limit.get_start_decade_fortune()
    decade_idx = 0

    # 遍历所有大运，直到80岁
    while decade_fortune:
        age_start = decade_fortune.get_start_age()
        age_end = decade_fortune.get_end_age()

        # 如果大运起始年龄超过80岁，停止
        if age_start >= 80:
            break

        decade_pillar = decade_fortune.get_sixty_cycle().get_name()
        decade_gan = Tiangan.from_chinese_name(decade_pillar[0])
        decade_tengod = birth_chart.dayzhu.gan.get_shishen(decade_gan).chinese_name

        # 打印大运分组标题
        # 显示实际年龄段
        end_display = min(age_end, 79)
        print(
            f"\n{C_ACCENT}┌─ 第{decade_idx + 1}大运: {decade_pillar} ({decade_tengod}) - {age_start}~{end_display}岁 ─┐{RESET}"
        )

        # 表头
        print(f"{BOLD}{'年龄':<6}{'小运':<6}{'流年':<6}{'十神':<6}{'五行':<4}{'阴阳':<4}{RESET}")
        print("-" * 40)

        # 打印该大运下的10个流年
        fortune = decade_fortune.get_start_fortune()
        for j in range(0, 10):
            age = fortune.get_age()

            # 只显示80岁以内的
            if age > 80:
                break

            minor = fortune.get_sixty_cycle().get_name()
            annual = fortune.get_sixty_cycle_year().get_sixty_cycle().get_name()

            gan = Tiangan.from_chinese_name(annual[0])
            tengod = birth_chart.dayzhu.gan.get_shishen(gan).chinese_name
            element = gan.belongs_to(Wuxing).chinese_name
            yinyang = gan.belongs_to(YinYang).chinese_name

            print(f"{age:<6}{minor:<6}{annual:<6}{tengod:<6}{element:<4}{yinyang:<4}")
            fortune = fortune.next(1)

        decade_fortune = decade_fortune.next(1)
        decade_idx += 1

    # 结束
    print(f"\n{BOLD}{C_HEADER}{'=' * 50}{RESET}")
    print(f"{DIM}注：八字信息仅供参考，具体分析请咨询专业人士{RESET}")
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


def _safe_year_value(obj: object) -> Optional[int]:
    for method in ("get_year", "get_value", "get_year_value"):
        value = _safe_call(obj, method)
        if isinstance(value, int):
            return value
    if isinstance(obj, int):
        return obj
    return None


def _safe_time_str(obj: object) -> Optional[str]:
    if obj is None:
        return None
    try:
        return str(obj)
    except Exception:
        return None


def _get_lunar_date_str(birth_chart: BirthChart) -> Optional[str]:
    lunar_hour = _safe_call(birth_chart._solar_time, "get_lunar_hour")
    if lunar_hour is None:
        return None
    return str(lunar_hour)


def _get_true_solar_time_str(birth_chart: BirthChart) -> Optional[str]:
    true_time = _safe_call(birth_chart._solar_time, "get_true_solar_time")
    if true_time is None:
        return None
    return str(true_time)


def _get_birth_term_time_str(birth_chart: BirthChart) -> Optional[str]:
    term = birth_chart.term
    solar_term = _safe_call(term, "get_solar_term")
    if solar_term is None:
        return None
    julian = _safe_call(solar_term, "get_julian_day")
    if julian is None:
        return None
    solar_time = _safe_call(julian, "get_solar_time")
    return str(solar_time) if solar_time is not None else None


def _collect_chart_shensha(birth_chart: BirthChart) -> List[str]:
    result: list[str] = []
    for zhu in [birth_chart.yearzhu, birth_chart.monthzhu, birth_chart.dayzhu, birth_chart.bihourzhu]:
        for s in zhu.shensha:
            name = str(s)
            if name not in result:
                result.append(name)
    return result


def _calc_day_master_strength(birth_chart: BirthChart) -> Optional[Strength]:
    method = birth_chart._calc_rules.get("day_master_strength", "simple_score")
    if method != "simple_score":
        return None
    scores = birth_chart.chart_analysis
    if not scores:
        return None
    day_element = birth_chart.dayzhu.gan.belongs_to(Wuxing).chinese_name

    total = sum(v["score"] for v in scores.values() if isinstance(v, dict))
    if total <= 0:
        return None
    avg = total / 5
    return Strength.STRONG if scores[day_element]["score"] >= avg else Strength.WEAK


def _calc_favorable_elements(birth_chart: BirthChart) -> List[str]:
    strength = _calc_day_master_strength(birth_chart)
    if strength is None:
        return []
    day_element = birth_chart.dayzhu.gan.belongs_to(Wuxing)
    if strength == Strength.STRONG:
        # 身强取泄耗与克制为喜用
        return [
            day_element.generate().chinese_name,
            _wuxing_controller(day_element).chinese_name,
        ]
    # 身弱取比助与生扶为喜用
    return [
        day_element.chinese_name,
        _wuxing_generator(day_element).chinese_name,
    ]


def _calc_unfavorable_elements(birth_chart: BirthChart) -> List[str]:
    strength = _calc_day_master_strength(birth_chart)
    if strength is None:
        return []
    day_element = birth_chart.dayzhu.gan.belongs_to(Wuxing)
    if strength == Strength.STRONG:
        return [
            day_element.chinese_name,
            _wuxing_generator(day_element).chinese_name,
        ]
    return [
        day_element.generate().chinese_name,
        _wuxing_controller(day_element).chinese_name,
    ]


def _calc_useful_element(birth_chart: BirthChart) -> Optional[str]:
    elements = _calc_favorable_elements(birth_chart)
    return elements[0] if elements else None


def _calc_taboo_element(birth_chart: BirthChart) -> Optional[str]:
    elements = _calc_unfavorable_elements(birth_chart)
    return elements[0] if elements else None


def _wuxing_generator(element: Wuxing) -> Wuxing:
    # 取生我者（母气）
    return Wuxing((element.num - 1) % 5)


def _wuxing_controller(element: Wuxing) -> Wuxing:
    # 取克我者
    return Wuxing((element.num - 2) % 5)


def _pillar_tengod_element_yinyang(
    birth_chart: BirthChart, pillar: str
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    if not pillar or len(pillar) < 2:
        return None, None, None
    gan = Tiangan.from_chinese_name(pillar[0])
    tengod = birth_chart.dayzhu.gan.get_shishen(gan).chinese_name
    element = gan.belongs_to(Wuxing).chinese_name
    yinyang = gan.belongs_to(YinYang).chinese_name
    return tengod, element, yinyang


def _get_luck_direction(child_limit: object) -> Optional[str]:
    is_forward = _safe_call(child_limit, "is_forward")
    if isinstance(is_forward, bool):
        return "顺行" if is_forward else "逆行"
    return None


def _get_decade_year_range(decade: object) -> Optional[Tuple[int, int]]:
    start = _safe_year_value(_safe_call(decade, "get_start_year"))
    end = _safe_year_value(_safe_call(decade, "get_end_year"))
    if start is None or end is None:
        return None
    return (start, end)


def _build_target_flow(birth_chart: BirthChart, target_dt: datetime) -> TargetFlow:
    # 使用 tyme4py 的 SolarTime/EightChar 计算流年月日时
    solar_time = birth_chart._solar_time.__class__.from_ymd_hms(
        target_dt.year, target_dt.month, target_dt.day, target_dt.hour, target_dt.minute, target_dt.second
    )
    lunar_hour = solar_time.get_lunar_hour()
    eight_char = lunar_hour.get_eight_char()

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
        month_pillar = solar_time.get_lunar_hour().get_eight_char().get_month().get_name()
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
    decade = _safe_call(child_limit, "get_start_decade_fortune")
    if decade is None:
        return None
    fortune = _safe_call(decade, "get_start_fortune")
    for _ in range(0, 150):
        if fortune is None:
            return None
        year = _safe_year_value(_safe_call(fortune.get_sixty_cycle_year(), "get_year"))
        if year == target_year:
            return fortune.get_sixty_cycle().get_name()
        fortune = fortune.next(1)
    return None


def _resolved_calc_rules(birth_chart: BirthChart) -> dict[str, str]:
    return {
        "minggua": birth_chart._calc_rules.get("minggua", "bazhai"),
        "minggong": birth_chart._calc_rules.get("minggong", "eightchar_own_sign"),
        "day_master_strength": birth_chart._calc_rules.get("day_master_strength", "simple_score"),
        "relations": birth_chart._calc_rules.get("relations", "simple_he_chong"),
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


def _build_relations(birth_chart: BirthChart) -> Relations:
    pillars = {
        "year": birth_chart.yearzhu,
        "month": birth_chart.monthzhu,
        "day": birth_chart.dayzhu,
        "hour": birth_chart.bihourzhu,
    }
    items = {}
    for name in pillars:
        items[name] = PillarRelations()

    names = list(pillars.keys())
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            left_zhu = pillars[left]
            right_zhu = pillars[right]

            stem_rel = _tiangan_relation(left_zhu.gan, right_zhu.gan)
            if stem_rel:
                items[left].stem.append(RelationItem(target=right, relation=stem_rel))
                items[right].stem.append(RelationItem(target=left, relation=stem_rel))

            branch_rel = _dizhi_relation(left_zhu.zhi, right_zhu.zhi)
            if branch_rel:
                items[left].branch.append(RelationItem(target=right, relation=branch_rel))
                items[right].branch.append(RelationItem(target=left, relation=branch_rel))

    return Relations(
        year=items["year"],
        month=items["month"],
        day=items["day"],
        hour=items["hour"],
    )


def _tiangan_relation(left: Tiangan, right: Tiangan) -> Optional[str]:
    if (left, right) in _TIANGAN_CHONG or (right, left) in _TIANGAN_CHONG:
        return "冲"
    if (left, right) in _TIANGAN_HE or (right, left) in _TIANGAN_HE:
        return "合"
    return None


def _dizhi_relation(left, right) -> Optional[str]:
    if left.is_chong(right):
        return "冲"
    if left.is_he(right):
        return "合"
    return None


_TIANGAN_CHONG = {
    (Tiangan.Jia, Tiangan.Geng),
    (Tiangan.Yi, Tiangan.Xin),
    (Tiangan.Bing, Tiangan.Ren),
    (Tiangan.Ding, Tiangan.Gui),
    (Tiangan.Wu, Tiangan.Ji),
}

_TIANGAN_HE = {
    (Tiangan.Jia, Tiangan.Ji),
    (Tiangan.Yi, Tiangan.Geng),
    (Tiangan.Bing, Tiangan.Xin),
    (Tiangan.Ding, Tiangan.Ren),
    (Tiangan.Wu, Tiangan.Gui),
}
