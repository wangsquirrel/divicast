from __future__ import annotations

from ..entities.ganzhi import CangganType, Dizhi, Shishen, Tiangan
from ..entities.wuxing import Wuxing
from .analysis_enums import Geju, Strength
from .relation_models import RelationAnalysis


class WuxingScore:
    """五行分析主题: 单个五行的数量和分值。"""

    count: int
    score: float

    def __init__(self, count: int = 0, score: float = 0.0) -> None:
        self.count = count
        self.score = score


class RootInfo:
    """通根分析主题: 日主在各柱地支中的根气明细。"""

    pillar: str
    branch: Dizhi
    gan: Tiangan
    role: CangganType
    score: float

    def __init__(self, pillar: str, branch: Dizhi, gan: Tiangan, role: CangganType, score: float) -> None:
        self.pillar = pillar
        self.branch = branch
        self.gan = gan
        self.role = role
        self.score = score


class WuxingAnalysis:
    """五行分析主题: 五行数量、分值、月令五行和最旺五行。"""

    items: dict[Wuxing, WuxingScore]
    month_zhi_wuxing: Wuxing | None
    strongest: Wuxing | None
    total_score: float

    def __init__(self) -> None:
        self.items = {wx: WuxingScore() for wx in Wuxing.all()}
        self.month_zhi_wuxing = None
        self.strongest = None
        self.total_score = 0.0


class StrengthAnalysis:
    """旺衰分析主题: 基于加权扶抑与通根信息估计日主强弱。"""

    day_master_wuxing: Wuxing | None
    month_ling_shishen_family: str
    support_score: float
    opposition_score: float
    support_ratio: float
    day_master_has_root: bool
    day_master_root_count: int
    day_master_root_score: float
    day_master_roots: list[RootInfo]
    day_master_strength: Strength | None

    def __init__(self) -> None:
        self.day_master_wuxing = None
        self.month_ling_shishen_family = ""
        self.support_score = 0.0
        self.opposition_score = 0.0
        self.support_ratio = 0.0
        self.day_master_has_root = False
        self.day_master_root_count = 0
        self.day_master_root_score = 0.0
        self.day_master_roots = []
        self.day_master_strength = None


class TenGodAnalysis:
    """十神分析主题: 十神分布以及十神家族分布。"""

    scores: dict[Shishen, float]
    family_scores: dict[str, float]

    def __init__(self) -> None:
        self.scores = {shishen: 0.0 for shishen in Shishen.all()}
        self.family_scores = {
            "比劫": 0.0,
            "食伤": 0.0,
            "财星": 0.0,
            "官杀": 0.0,
            "印星": 0.0,
        }


class FavorabilityAnalysis:
    """喜忌分析主题: 基于旺衰与五行分布给出启发式补益倾向。"""

    favorable_elements: list[Wuxing]
    unfavorable_elements: list[Wuxing]
    useful_element: Wuxing | None
    taboo_element: Wuxing | None

    def __init__(self) -> None:
        self.favorable_elements = []
        self.unfavorable_elements = []
        self.useful_element = None
        self.taboo_element = None


class GejuAnalysis:
    """格局分析主题: 基于规则匹配给出候选格局及判断依据。"""

    geju: Geju | None
    basis: list[str]

    def __init__(self) -> None:
        self.geju = None
        self.basis = []


class ChartAnalysis:
    """命盘总分析结构: 汇总启发式分析结果，不直接代表术数定论。"""

    wuxing: WuxingAnalysis
    strength: StrengthAnalysis
    ten_god: TenGodAnalysis
    favorability: FavorabilityAnalysis
    geju: GejuAnalysis
    relations: RelationAnalysis

    def __init__(self) -> None:
        self.wuxing = WuxingAnalysis()
        self.strength = StrengthAnalysis()
        self.ten_god = TenGodAnalysis()
        self.favorability = FavorabilityAnalysis()
        self.geju = GejuAnalysis()
        self.relations = RelationAnalysis()

    def __bool__(self) -> bool:
        return self.wuxing.strongest is not None or self.strength.day_master_wuxing is not None
