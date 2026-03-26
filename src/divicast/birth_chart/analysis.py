from __future__ import annotations

from typing import TYPE_CHECKING

from ..entities.ganzhi import CangganType, Dizhi, Shishen, Tiangan, TwelveZhangsheng
from ..entities.wuxing import Wuxing
from .analysis_enums import GanZhi, Strength, Zhu
from .analysis_models import (
    ChartAnalysis,
    FavorabilityAnalysis,
    GejuAnalysis,
    RootInfo,
    StrengthAnalysis,
    TenGodAnalysis,
    WuxingAnalysis,
)
from .geju import analyze_geju
from .relation_models import (
    RelationAnalysis,
    RelationEvent,
    RelationOutcome,
    RelationOutcomeKind,
    RelationParticipant,
    RelationPattern,
    RelationQualifier,
)

if TYPE_CHECKING:
    from .birth import BirthChart


class BirthChartAnalyzer:
    """命盘分析器: 读取命盘并依次产出各分析主题结果。"""

    def analyze(self, birth_chart: BirthChart, analysis: ChartAnalysis | None = None) -> ChartAnalysis:
        """总分析入口: 按主题顺序填充统一分析结构。"""

        target = analysis if analysis is not None else ChartAnalysis()
        target.wuxing = self.analyze_wuxing(birth_chart)
        target.ten_god = self.analyze_tengod(birth_chart)
        target.strength = self.analyze_strength(birth_chart)
        target.favorability = self.analyze_favorability(
            birth_chart,
            target.wuxing,
            target.strength,
        )
        target.relations = self.analyze_relations(birth_chart)
        target.geju = self.analyze_geju(birth_chart, target)
        return target

    def analyze_wuxing(self, birth_chart: BirthChart) -> WuxingAnalysis:
        """五行分析主题: 读取命盘并填充五行数量、分值与月令信息。"""

        result = WuxingAnalysis()
        day_master = birth_chart.dayzhu.gan
        month_zhi_wuxing = birth_chart.monthzhu.zhi.belongs_to(Wuxing)

        pillars = [
            (Zhu.YEAR, birth_chart.yearzhu),
            (Zhu.MONTH, birth_chart.monthzhu),
            (Zhu.DAY, birth_chart.dayzhu),
            (Zhu.HOUR, birth_chart.bihourzhu),
        ]

        for pillar_name, zhu in pillars:
            stem_weight = PILLAR_STEM_WEIGHTS[pillar_name]
            stem_element = zhu.gan.belongs_to(Wuxing)
            result.items[stem_element].count += 1
            result.items[stem_element].score += stem_weight

            branch_weight = PILLAR_BRANCH_WEIGHTS[pillar_name]
            for canggan in zhu.canggan:
                canggan_weight = branch_weight * CANGGAN_WEIGHTS[canggan.canggan_type]
                canggan_element = canggan.gan.belongs_to(Wuxing)
                result.items[canggan_element].count += 1
                result.items[canggan_element].score += canggan_weight
        result.items[month_zhi_wuxing].score += abs(_month_ling_bonus(day_master.belongs_to(Wuxing), month_zhi_wuxing))

        result.month_zhi_wuxing = month_zhi_wuxing
        result.total_score = sum(item.score for item in result.items.values())
        result.strongest = max(result.items, key=lambda wx: result.items[wx].score)
        return result

    def analyze_tengod(self, birth_chart: BirthChart) -> TenGodAnalysis:
        """十神分析主题: 读取命盘并填充十神及十神家族分布。"""

        result = TenGodAnalysis()
        day_master = birth_chart.dayzhu.gan
        pillars = [
            (Zhu.YEAR, birth_chart.yearzhu),
            (Zhu.MONTH, birth_chart.monthzhu),
            (Zhu.DAY, birth_chart.dayzhu),
            (Zhu.HOUR, birth_chart.bihourzhu),
        ]

        for pillar_name, zhu in pillars:
            stem_weight = PILLAR_STEM_WEIGHTS[pillar_name]
            stem_shishen = day_master.get_shishen(zhu.gan)
            result.scores[stem_shishen] += stem_weight
            result.family_scores[TEN_GOD_FAMILIES[stem_shishen]] += stem_weight

            branch_weight = PILLAR_BRANCH_WEIGHTS[pillar_name]
            for canggan in zhu.canggan:
                canggan_weight = branch_weight * CANGGAN_WEIGHTS[canggan.canggan_type]
                canggan_shishen = day_master.get_shishen(canggan.gan)
                family = TEN_GOD_FAMILIES[canggan_shishen]
                result.scores[canggan_shishen] += canggan_weight
                result.family_scores[family] += canggan_weight

        return result

    def analyze_strength(self, birth_chart: BirthChart) -> StrengthAnalysis:
        """旺衰分析主题: 读取命盘并填充扶抑、通根和日主强弱。"""

        result = StrengthAnalysis()
        day_master = birth_chart.dayzhu.gan
        day_master_wuxing = day_master.belongs_to(Wuxing)
        month_zhi_wuxing = birth_chart.monthzhu.zhi.belongs_to(Wuxing)
        month_ling_family = _family_for_element(day_master_wuxing, month_zhi_wuxing)

        roots: list[RootInfo] = []
        root_score = 0.0
        support_score = 0.0
        opposition_score = 0.0

        pillars = [
            (Zhu.YEAR, birth_chart.yearzhu),
            (Zhu.MONTH, birth_chart.monthzhu),
            (Zhu.DAY, birth_chart.dayzhu),
            (Zhu.HOUR, birth_chart.bihourzhu),
        ]

        for pillar_name, zhu in pillars:
            stem_weight = PILLAR_STEM_WEIGHTS[pillar_name]
            stem_shishen = day_master.get_shishen(zhu.gan)
            if TEN_GOD_FAMILIES[stem_shishen] in ("比劫", "印星"):
                support_score += stem_weight
            else:
                opposition_score += stem_weight

            phase_weight = ZHANGSHENG_WEIGHTS.get(zhu.xingyun, 0.0)
            if phase_weight:
                if _is_supportive_element(day_master_wuxing, zhu.zhi.belongs_to(Wuxing)):
                    support_score += phase_weight * 0.6
                else:
                    opposition_score += phase_weight * 0.35

            branch_weight = PILLAR_BRANCH_WEIGHTS[pillar_name]
            for canggan in zhu.canggan:
                canggan_weight = branch_weight * CANGGAN_WEIGHTS[canggan.canggan_type]
                canggan_element = canggan.gan.belongs_to(Wuxing)
                canggan_shishen = day_master.get_shishen(canggan.gan)
                family = TEN_GOD_FAMILIES[canggan_shishen]

                if family in ("比劫", "印星"):
                    support_score += canggan_weight
                else:
                    opposition_score += canggan_weight

                if canggan_element == day_master_wuxing:
                    root_value = canggan_weight + phase_weight * 0.25
                    roots.append(
                        RootInfo(
                            pillar=pillar_name,
                            branch=zhu.zhi,
                            gan=canggan.gan,
                            role=canggan.canggan_type,
                            score=root_value,
                        )
                    )
                    root_score += root_value

        month_ling_bonus = _month_ling_bonus(day_master_wuxing, month_zhi_wuxing)
        if month_ling_bonus >= 0:
            support_score += month_ling_bonus
        else:
            opposition_score += abs(month_ling_bonus)

        support_ratio = (
            support_score / (support_score + opposition_score) if (support_score + opposition_score) else 0.5
        )
        strength = _resolve_strength(
            support_ratio=support_ratio,
            month_ling_family=month_ling_family,
            root_score=root_score,
            root_count=len(roots),
        )

        result.day_master_wuxing = day_master_wuxing
        result.month_ling_shishen_family = month_ling_family
        result.support_score = support_score
        result.opposition_score = opposition_score
        result.support_ratio = support_ratio
        result.day_master_has_root = len(roots) > 0
        result.day_master_root_count = len(roots)
        result.day_master_root_score = root_score
        result.day_master_roots = roots
        result.day_master_strength = strength
        return result

    def analyze_favorability(
        self,
        birth_chart: BirthChart,
        wuxing_analysis: WuxingAnalysis,
        strength_analysis: StrengthAnalysis,
    ) -> FavorabilityAnalysis:
        """喜忌分析主题: 根据旺衰和五行分布填充喜用忌神。"""

        result = FavorabilityAnalysis()
        day_master_wuxing = birth_chart.dayzhu.gan.belongs_to(Wuxing)
        strength = strength_analysis.day_master_strength
        if strength is None:
            return result

        favorable_elements, unfavorable_elements = _recommend_elements(
            day_master_wuxing,
            strength,
            {wx.chinese_name: item.score for wx, item in wuxing_analysis.items.items()},
        )

        result.favorable_elements = favorable_elements
        result.unfavorable_elements = unfavorable_elements
        result.useful_element = favorable_elements[0] if favorable_elements else None
        result.taboo_element = unfavorable_elements[0] if unfavorable_elements else None
        return result

    def analyze_relations(self, birth_chart: BirthChart) -> RelationAnalysis:
        """关系分析主题: 读取命盘并填充四柱之间的核心干支关系。"""

        pillars = {
            Zhu.YEAR: birth_chart.yearzhu,
            Zhu.MONTH: birth_chart.monthzhu,
            Zhu.DAY: birth_chart.dayzhu,
            Zhu.HOUR: birth_chart.bihourzhu,
        }
        result = RelationAnalysis()

        stem_values = {pillar: zhu.gan for pillar, zhu in pillars.items()}
        branch_values = {pillar: zhu.zhi for pillar, zhu in pillars.items()}

        _append_tiangan_relations(result, stem_values)
        _append_dizhi_pair_relations(result, branch_values)
        _append_dizhi_group_relations(result, branch_values)

        return result

    def analyze_geju(self, birth_chart: BirthChart, analysis: ChartAnalysis) -> GejuAnalysis:
        """格局分析主题: 读取命盘并填充格局结果。"""

        return analyze_geju(birth_chart, analysis)


PILLAR_STEM_WEIGHTS = {
    Zhu.YEAR: 1.0,
    Zhu.MONTH: 1.6,
    Zhu.DAY: 1.2,
    Zhu.HOUR: 1.0,
}

PILLAR_BRANCH_WEIGHTS = {
    Zhu.YEAR: 0.8,
    Zhu.MONTH: 1.8,
    Zhu.DAY: 1.1,
    Zhu.HOUR: 0.9,
}

CANGGAN_WEIGHTS = {
    CangganType.MAIN: 1.0,
    CangganType.MIDDLE: 0.6,
    CangganType.SECONDARY: 0.35,
}

ZHANGSHENG_WEIGHTS = {
    TwelveZhangsheng.ZhangSheng: 0.9,
    TwelveZhangsheng.MuYu: 0.25,
    TwelveZhangsheng.GuanDai: 0.45,
    TwelveZhangsheng.LinGuan: 1.2,
    TwelveZhangsheng.DiWang: 1.5,
    TwelveZhangsheng.Shuai: 0.35,
    TwelveZhangsheng.Bing: 0.1,
    TwelveZhangsheng.Si: 0.0,
    TwelveZhangsheng.Mu: 0.55,
    TwelveZhangsheng.Jue: 0.0,
    TwelveZhangsheng.Tai: 0.3,
    TwelveZhangsheng.Yang: 0.35,
}

TEN_GOD_FAMILIES = {
    Shishen.BiJian: "比劫",
    Shishen.JieCai: "比劫",
    Shishen.ShiShen: "食伤",
    Shishen.ShangGuan: "食伤",
    Shishen.PianCai: "财星",
    Shishen.ZhengCai: "财星",
    Shishen.QiSha: "官杀",
    Shishen.ZhengGuan: "官杀",
    Shishen.PianYin: "印星",
    Shishen.ZhengYin: "印星",
}


def analyze_chart(birth_chart: BirthChart, analysis: ChartAnalysis | None = None) -> ChartAnalysis:
    """总分析入口: 返回完整的统一分析结果。"""

    return BirthChartAnalyzer().analyze(birth_chart, analysis)


def analyze_wuxing(birth_chart: BirthChart, analysis: ChartAnalysis | None = None) -> WuxingAnalysis:
    """五行分析主题: 读取命盘并返回五行结果。"""

    result = BirthChartAnalyzer().analyze_wuxing(birth_chart)
    if analysis is not None:
        analysis.wuxing = result
    return result


def analyze_relations(
    birth_chart: BirthChart,
    analysis: ChartAnalysis | None = None,
) -> RelationAnalysis:
    """关系分析主题: 计算四柱之间的核心干支关系。"""

    result = BirthChartAnalyzer().analyze_relations(birth_chart)
    if analysis is not None:
        analysis.relations = result
    return result


def determine_strength(analysis: ChartAnalysis) -> Strength | None:
    return analysis.strength.day_master_strength


def _resolve_strength(
    support_ratio: float,
    month_ling_family: str,
    root_score: float,
    root_count: int,
) -> Strength:
    score = support_ratio
    if month_ling_family in ("比劫", "印星"):
        score += 0.08
    elif month_ling_family in ("财星", "官杀", "食伤"):
        score -= 0.08

    score += min(root_score, 2.4) * 0.08
    if root_count >= 3:
        score += 0.05
    elif root_count == 0:
        score -= 0.05

    if score >= 0.78:
        return Strength.VERY_STRONG
    if score >= 0.6:
        return Strength.STRONG
    if score >= 0.42:
        return Strength.NEUTRAL
    if score >= 0.26:
        return Strength.WEAK
    return Strength.VERY_WEAK


def _recommend_elements(
    day_master_element: Wuxing,
    strength: Strength,
    wuxing_scores: dict[str, float],
) -> tuple[list[Wuxing], list[Wuxing]]:
    same = day_master_element
    output = day_master_element.generate()
    wealth = day_master_element.restrain()
    officer = _element_that_restrains(day_master_element)
    resource = _element_that_generates(day_master_element)

    if strength in (Strength.STRONG, Strength.VERY_STRONG):
        favorable_pool = [output, wealth, officer]
        unfavorable_pool = [same, resource]
    elif strength in (Strength.WEAK, Strength.VERY_WEAK):
        favorable_pool = [same, resource]
        unfavorable_pool = [output, wealth, officer]
    else:
        strongest = max(wuxing_scores, key=wuxing_scores.get)
        if strongest in (same.chinese_name, resource.chinese_name):
            favorable_pool = [output, wealth]
            unfavorable_pool = [same, resource]
        else:
            favorable_pool = [resource, same]
            unfavorable_pool = [wealth, officer]

    favorable = _sort_elements_by_need(favorable_pool, wuxing_scores)
    unfavorable = _sort_elements_by_need(unfavorable_pool, wuxing_scores, reverse=True)
    return favorable, unfavorable


def _sort_elements_by_need(
    elements: list[Wuxing],
    scores: dict[str, float],
    reverse: bool = False,
) -> list[Wuxing]:
    unique = {element.chinese_name: element for element in elements}
    ordered = sorted(
        unique.values(),
        key=lambda element: scores.get(element.chinese_name, 0.0),
        reverse=reverse,
    )
    return ordered


def _family_for_element(day_master: Wuxing, other: Wuxing) -> str:
    if other == day_master:
        return "比劫"
    if other == day_master.generate():
        return "食伤"
    if other == day_master.restrain():
        return "财星"
    if other == _element_that_restrains(day_master):
        return "官杀"
    return "印星"


def _month_ling_bonus(day_master: Wuxing, month_element: Wuxing) -> float:
    family = _family_for_element(day_master, month_element)
    if family == "比劫":
        return 2.0
    if family == "印星":
        return 1.6
    if family == "食伤":
        return -1.0
    if family == "财星":
        return -1.4
    return -1.8


def _is_supportive_element(day_master: Wuxing, branch_element: Wuxing) -> bool:
    return branch_element in (day_master, _element_that_generates(day_master))


def _element_that_generates(target: Wuxing) -> Wuxing:
    return Wuxing((target.num - 1) % 5)


def _element_that_restrains(target: Wuxing) -> Wuxing:
    return Wuxing((target.num + 2) % 5)


def _append_tiangan_relations(result: RelationAnalysis, stems: dict[Zhu, Tiangan]) -> None:
    names = list(stems.keys())
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            pair = frozenset((stems[left], stems[right]))
            if pair in _TIANGAN_CHONG:
                result.add_event(
                    _build_relation_event(
                        pattern=RelationPattern.TIANGAN_CHONG,
                        participants=[
                            (left, GanZhi.TIANGAN, stems[left]),
                            (right, GanZhi.TIANGAN, stems[right]),
                        ],
                    )
                )
            he_result = _TIANGAN_HE.get(pair)
            if he_result:
                result.add_event(
                    _build_relation_event(
                        pattern=RelationPattern.TIANGAN_WU_HE,
                        participants=[
                            (left, GanZhi.TIANGAN, stems[left]),
                            (right, GanZhi.TIANGAN, stems[right]),
                        ],
                        outcome=RelationOutcome(RelationOutcomeKind.HUA, he_result),
                    )
                )


def _append_dizhi_pair_relations(result: RelationAnalysis, branches: dict[Zhu, Dizhi]) -> None:
    names = list(branches.keys())
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            pair = frozenset((branches[left], branches[right]))
            participants = [
                (left, GanZhi.DIZHI, branches[left]),
                (right, GanZhi.DIZHI, branches[right]),
            ]

            if pair in _DIZHI_PAIR_XING:
                result.add_event(
                    _build_relation_event(
                        pattern=RelationPattern.DIZHI_XIANG_XING,
                        participants=participants,
                        qualifier=_DIZHI_PAIR_XING[pair],
                    )
                )
            if branches[left].is_chong(branches[right]):
                result.add_event(_build_relation_event(RelationPattern.DIZHI_LIU_CHONG, participants))

            he_result = _DIZHI_LIUHE.get(pair)
            if he_result:
                result.add_event(
                    _build_relation_event(
                        pattern=RelationPattern.DIZHI_LIU_HE,
                        participants=participants,
                        outcome=RelationOutcome(RelationOutcomeKind.HUA, he_result),
                    )
                )

            if pair in _DIZHI_HAI:
                result.add_event(_build_relation_event(RelationPattern.DIZHI_LIU_HAI, participants))

            if pair in _DIZHI_PO:
                result.add_event(_build_relation_event(RelationPattern.DIZHI_LIU_PO, participants))


def _append_dizhi_group_relations(result: RelationAnalysis, branches: dict[Zhu, Dizhi]) -> None:
    pillar_names = list(branches.keys())
    seen_group_keys: set[tuple[str, tuple[Zhu, ...]]] = set()

    for combo in _combinations(pillar_names, 3):
        branch_set = frozenset(branches[pillar] for pillar in combo)
        participants = [(pillar, GanZhi.DIZHI, branches[pillar]) for pillar in combo]

        sanhe_result = _DIZHI_SANHE.get(branch_set)
        if sanhe_result:
            key = ("地支三合", tuple(combo))
            if key not in seen_group_keys:
                seen_group_keys.add(key)
                result.add_event(
                    _build_relation_event(
                        pattern=RelationPattern.DIZHI_SAN_HE,
                        participants=participants,
                        outcome=RelationOutcome(RelationOutcomeKind.JU, sanhe_result),
                    )
                )

        sanhui_result = _DIZHI_SANHUI.get(branch_set)
        if sanhui_result:
            key = ("地支三会", tuple(combo))
            if key not in seen_group_keys:
                seen_group_keys.add(key)
                result.add_event(
                    _build_relation_event(
                        pattern=RelationPattern.DIZHI_SAN_HUI,
                        participants=participants,
                        outcome=RelationOutcome(RelationOutcomeKind.JU, sanhui_result),
                    )
                )

        sanxing_qualifier = _DIZHI_SANXING.get(branch_set)
        if sanxing_qualifier:
            key = ("地支三刑", tuple(combo))
            if key not in seen_group_keys:
                seen_group_keys.add(key)
                result.add_event(
                    _build_relation_event(
                        pattern=RelationPattern.DIZHI_SAN_XING,
                        participants=participants,
                        qualifier=sanxing_qualifier,
                    )
                )

    for target in _DIZHI_SELF_XING:
        matched = [pillar for pillar, branch in branches.items() if branch == target]
        if len(matched) >= 2:
            result.add_event(
                _build_relation_event(
                    pattern=RelationPattern.DIZHI_ZI_XING,
                    participants=[(pillar, GanZhi.DIZHI, branches[pillar]) for pillar in matched],
                    qualifier=RelationQualifier.ZI_XING,
                )
            )


def _build_relation_event(
    pattern: RelationPattern,
    participants: list[tuple[Zhu, GanZhi, Tiangan | Dizhi]],
    outcome: RelationOutcome | None = None,
    qualifier: RelationQualifier | None = None,
) -> RelationEvent:
    return RelationEvent(
        pattern=pattern,
        participants=[
            RelationParticipant(
                pillar=pillar,
                position=position,
                value=value,
            )
            for pillar, position, value in participants
        ],
        outcome=outcome,
        qualifier=qualifier,
    )


def _combinations(items: list[Zhu], size: int) -> list[tuple[Zhu, ...]]:
    if size == 0:
        return [()]
    if len(items) < size:
        return []
    if len(items) == size:
        return [tuple(items)]

    head = items[0]
    include = [(head, *tail) for tail in _combinations(items[1:], size - 1)]
    exclude = _combinations(items[1:], size)
    return include + exclude


_TIANGAN_CHONG = {
    frozenset((Tiangan.Jia, Tiangan.Geng)),
    frozenset((Tiangan.Yi, Tiangan.Xin)),
    frozenset((Tiangan.Bing, Tiangan.Ren)),
    frozenset((Tiangan.Ding, Tiangan.Gui)),
    frozenset((Tiangan.Wu, Tiangan.Ji)),
}

_TIANGAN_HE = {
    frozenset((Tiangan.Jia, Tiangan.Ji)): Wuxing.Earth,
    frozenset((Tiangan.Yi, Tiangan.Geng)): Wuxing.Metal,
    frozenset((Tiangan.Bing, Tiangan.Xin)): Wuxing.Water,
    frozenset((Tiangan.Ding, Tiangan.Ren)): Wuxing.Wood,
    frozenset((Tiangan.Wu, Tiangan.Gui)): Wuxing.Fire,
}

_DIZHI_LIUHE = {
    frozenset((Dizhi.Zi, Dizhi.Chou)): Wuxing.Earth,
    frozenset((Dizhi.Yin, Dizhi.Hai)): Wuxing.Wood,
    frozenset((Dizhi.Mou, Dizhi.Xu)): Wuxing.Fire,
    frozenset((Dizhi.Chen, Dizhi.You)): Wuxing.Metal,
    frozenset((Dizhi.Si, Dizhi.Shen)): Wuxing.Water,
    frozenset((Dizhi.Wu, Dizhi.Wei)): Wuxing.Earth,
}

_DIZHI_HAI = {
    frozenset((Dizhi.Zi, Dizhi.Wei)),
    frozenset((Dizhi.Chou, Dizhi.Wu)),
    frozenset((Dizhi.Yin, Dizhi.Si)),
    frozenset((Dizhi.Mou, Dizhi.Chen)),
    frozenset((Dizhi.Shen, Dizhi.Hai)),
    frozenset((Dizhi.You, Dizhi.Xu)),
}

_DIZHI_PO = {
    frozenset((Dizhi.Zi, Dizhi.You)),
    frozenset((Dizhi.Mou, Dizhi.Wu)),
    frozenset((Dizhi.Chen, Dizhi.Chou)),
    frozenset((Dizhi.Wei, Dizhi.Xu)),
    frozenset((Dizhi.Yin, Dizhi.Hai)),
    frozenset((Dizhi.Si, Dizhi.Shen)),
}

_DIZHI_SANHE = {
    frozenset((Dizhi.Shen, Dizhi.Zi, Dizhi.Chen)): Wuxing.Water,
    frozenset((Dizhi.Hai, Dizhi.Mou, Dizhi.Wei)): Wuxing.Wood,
    frozenset((Dizhi.Yin, Dizhi.Wu, Dizhi.Xu)): Wuxing.Fire,
    frozenset((Dizhi.Si, Dizhi.You, Dizhi.Chou)): Wuxing.Metal,
}

_DIZHI_SANHUI = {
    frozenset((Dizhi.Hai, Dizhi.Zi, Dizhi.Chou)): Wuxing.Water,
    frozenset((Dizhi.Yin, Dizhi.Mou, Dizhi.Chen)): Wuxing.Wood,
    frozenset((Dizhi.Si, Dizhi.Wu, Dizhi.Wei)): Wuxing.Fire,
    frozenset((Dizhi.Shen, Dizhi.You, Dizhi.Xu)): Wuxing.Metal,
}

_DIZHI_SANXING = {
    frozenset((Dizhi.Yin, Dizhi.Si, Dizhi.Shen)): RelationQualifier.WU_EN_ZHI_XING,
    frozenset((Dizhi.Chou, Dizhi.Wei, Dizhi.Xu)): RelationQualifier.SHI_SHI_ZHI_XING,
}

_DIZHI_PAIR_XING = {
    frozenset((Dizhi.Zi, Dizhi.Mou)): RelationQualifier.WU_LI_ZHI_XING,
}

_DIZHI_SELF_XING = {
    Dizhi.Chen,
    Dizhi.Wu,
    Dizhi.You,
    Dizhi.Hai,
}
