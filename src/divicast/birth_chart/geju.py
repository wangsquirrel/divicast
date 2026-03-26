"""
八字命盘格局计算模块

判断顺序保持现有架构：
1. 特殊格局
2. 专旺格
3. 化气格
4. 从格
5. 正格
6. 软特殊格
7. 普通格局（兜底）
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from ..entities.ganzhi import Canggan, Dizhi, Shishen, Tiangan
from ..entities.wuxing import Wuxing
from .analysis_enums import Geju, Strength
from .analysis_models import ChartAnalysis, GejuAnalysis

if TYPE_CHECKING:
    from .birth import BirthChart


ZHENGGE_MAP = {
    Shishen.ZhengGuan: Geju.ZHENG_GUAN,
    Shishen.QiSha: Geju.QI_SHA,
    Shishen.ZhengCai: Geju.ZHENG_CAI,
    Shishen.PianCai: Geju.PIAN_CAI,
    Shishen.ZhengYin: Geju.ZHENG_YIN,
    Shishen.PianYin: Geju.PIAN_YIN,
    Shishen.ShiShen: Geju.SHI_SHEN,
    Shishen.ShangGuan: Geju.SHANG_GUAN,
    Shishen.BiJian: Geju.BI_JIAN,
    Shishen.JieCai: Geju.JIE_CAI,
}

SPECIAL_LINGGUAN = {
    Tiangan.Jia: Dizhi.Mou,
    Tiangan.Yi: Dizhi.Yin,
    Tiangan.Bing: Dizhi.Si,
    Tiangan.Wu: Dizhi.Si,
    Tiangan.Ding: Dizhi.Wu,
    Tiangan.Ji: Dizhi.Wu,
    Tiangan.Geng: Dizhi.Shen,
    Tiangan.Xin: Dizhi.You,
    Tiangan.Ren: Dizhi.Hai,
    Tiangan.Gui: Dizhi.Zi,
}

HUA_RULES = {
    (Tiangan.Jia, Tiangan.Ji): (Wuxing.Earth, Geju.HUA_JIA, Geju.HUA_JI),
    (Tiangan.Yi, Tiangan.Geng): (Wuxing.Metal, Geju.HUA_YI, Geju.HUA_GENG),
    (Tiangan.Bing, Tiangan.Xin): (Wuxing.Water, Geju.HUA_BING, Geju.HUA_XIN),
    (Tiangan.Ding, Tiangan.Ren): (Wuxing.Wood, Geju.HUA_DING, Geju.HUA_REN),
    (Tiangan.Wu, Tiangan.Gui): (Wuxing.Fire, Geju.HUA_WU, Geju.HUA_GUI),
}


def analyze_geju(birth_chart: BirthChart, analysis: ChartAnalysis) -> GejuAnalysis:
    """格局分析主题: 读取命盘与分析上下文并返回格局结果。"""
    result = GejuAnalysis()

    geju = _check_hard_special_geju(birth_chart, analysis)
    if geju:
        result.geju = geju
        return result

    geju = _check_zhuanwang_geju(birth_chart, analysis)
    if geju:
        result.geju = geju
        return result

    geju = _check_huaqigeju(birth_chart, analysis)
    if geju:
        result.geju = geju
        return result

    geju = _check_cong_geju(birth_chart, analysis)
    if geju:
        result.geju = geju
        return result

    geju = _check_zhengge(birth_chart)
    if geju:
        result.geju = geju
        return result

    geju = _check_soft_special_geju(birth_chart, analysis)
    if geju:
        result.geju = geju
        return result

    result.geju = Geju.REGULAR
    return result


def _check_hard_special_geju(birth_chart: BirthChart, analysis: ChartAnalysis) -> Geju | None:
    if _is_qiqiang_bei(birth_chart, analysis):
        return Geju.QI_QIANG_BEI
    if _is_kuigang(birth_chart):
        return Geju.KUIGANG
    if _is_guilu(birth_chart, analysis):
        return Geju.GUI_LU
    if _is_jinglan_cha(birth_chart):
        return Geju.JING_LAN_CHA
    if _is_liu_jia_qu_gan(birth_chart):
        return Geju.LIU_JIA_QU_GAN
    if _is_liu_yi_shu_gui(birth_chart):
        return Geju.LIU_YI_SHU_GUI
    if _is_liu_yin_chao_yang(birth_chart):
        return Geju.LIU_YIN_CHAO_YANG
    if _is_liu_ren_qu_gen(birth_chart):
        return Geju.LIU_REN_QU_GEN
    if _is_gou_chen_de_wei(birth_chart):
        return Geju.GOU_CHEN_DE_WEI
    if _is_xuan_wu_dang_quan(birth_chart, analysis):
        return Geju.XUAN_WU_DANG_QUAN
    return None


def _check_soft_special_geju(birth_chart: BirthChart, analysis: ChartAnalysis) -> Geju | None:
    if _is_liang_shen_cheng_xiang(analysis):
        return Geju.LIANG_SHEN_CHENG_XIANG
    if _is_ban_bi_jiang_shan(birth_chart):
        return Geju.BAN_BI_JIANG_SHAN
    return None


def _is_kuigang(birth_chart: BirthChart) -> bool:
    return (birth_chart.dayzhu.gan, birth_chart.dayzhu.zhi) in {
        (Tiangan.Ren, Dizhi.Chen),
        (Tiangan.Geng, Dizhi.Chen),
        (Tiangan.Geng, Dizhi.Xu),
        (Tiangan.Wu, Dizhi.Xu),
    }


def _is_guilu(birth_chart: BirthChart, analysis: ChartAnalysis) -> bool:
    expected_zhi = SPECIAL_LINGGUAN.get(birth_chart.dayzhu.gan)
    if expected_zhi is None or birth_chart.dayzhu.zhi != expected_zhi:
        return False

    strength = analysis.strength.day_master_strength
    support = analysis.strength.support_score
    oppose = analysis.strength.opposition_score
    return strength in (Strength.STRONG, Strength.VERY_STRONG) and support >= oppose


def _is_qiqiang_bei(birth_chart: BirthChart, analysis: ChartAnalysis) -> bool:
    if birth_chart.dayzhu.gan != Tiangan.Ren or birth_chart.dayzhu.zhi != Dizhi.Chen:
        return False
    chen_count = sum(
        1
        for zhi in [birth_chart.yearzhu.zhi, birth_chart.monthzhu.zhi, birth_chart.dayzhu.zhi, birth_chart.bihourzhu.zhi]
        if zhi == Dizhi.Chen
    )
    strength = analysis.strength.day_master_strength
    return chen_count >= 2 and strength in (Strength.STRONG, Strength.VERY_STRONG)


def _is_jinglan_cha(birth_chart: BirthChart) -> bool:
    return birth_chart.dayzhu.gan == Tiangan.Geng and birth_chart.dayzhu.zhi in (Dizhi.Zi, Dizhi.Shen, Dizhi.Chen)


def _is_liu_jia_qu_gan(birth_chart: BirthChart) -> bool:
    return birth_chart.dayzhu.gan == Tiangan.Jia and birth_chart.bihourzhu.zhi == Dizhi.Hai


def _is_liu_yi_shu_gui(birth_chart: BirthChart) -> bool:
    return birth_chart.dayzhu.gan == Tiangan.Yi and birth_chart.bihourzhu.zhi == Dizhi.Zi


def _is_liu_yin_chao_yang(birth_chart: BirthChart) -> bool:
    return birth_chart.dayzhu.gan == Tiangan.Xin and birth_chart.bihourzhu.zhi == Dizhi.Chou


def _is_liu_ren_qu_gen(birth_chart: BirthChart) -> bool:
    return birth_chart.dayzhu.gan == Tiangan.Ren and birth_chart.dayzhu.zhi == Dizhi.Yin


def _is_gou_chen_de_wei(birth_chart: BirthChart) -> bool:
    return birth_chart.dayzhu.gan == Tiangan.Wu and birth_chart.dayzhu.zhi in (Dizhi.Chou, Dizhi.Wei)


def _is_xuan_wu_dang_quan(birth_chart: BirthChart, analysis: ChartAnalysis) -> bool:
    if birth_chart.dayzhu.gan != Tiangan.Ren or birth_chart.dayzhu.zhi not in (Dizhi.Yin, Dizhi.Wu):
        return False
    strength = analysis.strength.day_master_strength
    return strength in (Strength.STRONG, Strength.VERY_STRONG)


def _is_liang_shen_cheng_xiang(analysis: ChartAnalysis) -> bool:
    scores = _element_scores(analysis)
    total = sum(scores.values())
    if total <= 0:
        return False

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    (_, first_score), (_, second_score) = ordered[:2]
    remaining = ordered[2:]

    first_ratio = first_score / total
    second_ratio = second_score / total
    return (
        first_ratio >= 0.28
        and second_ratio >= 0.28
        and abs(first_ratio - second_ratio) <= 0.08
        and all(score / total <= 0.14 for _, score in remaining)
    )


def _is_ban_bi_jiang_shan(birth_chart: BirthChart) -> bool:
    pillars = [
        (birth_chart.yearzhu.gan, birth_chart.yearzhu.zhi),
        (birth_chart.monthzhu.gan, birth_chart.monthzhu.zhi),
        (birth_chart.dayzhu.gan, birth_chart.dayzhu.zhi),
        (birth_chart.bihourzhu.gan, birth_chart.bihourzhu.zhi),
    ]
    return any(count >= 2 for count in Counter(pillars).values())


def _check_zhuanwang_geju(birth_chart: BirthChart, analysis: ChartAnalysis) -> Geju | None:
    strength = analysis.strength.day_master_strength
    if strength != Strength.VERY_STRONG:
        return None

    scores = _element_scores(analysis)
    total = sum(scores.values())
    if total <= 0:
        return None

    strongest = analysis.wuxing.strongest
    day_master_wuxing = analysis.strength.day_master_wuxing
    support_ratio = analysis.strength.support_ratio
    root_score = analysis.strength.day_master_root_score
    month_family = analysis.strength.month_ling_shishen_family
    strongest_ratio = scores.get(strongest, 0.0) / total if strongest else 0.0

    if strongest != day_master_wuxing:
        return None
    if strongest_ratio < 0.45:
        return None
    required_support_ratio = 0.72
    if strongest == Wuxing.Earth:
        # 土旺盘在四库支与火印并见时容易被高估，适当收紧稼穑格门槛。
        required_support_ratio = 0.78
    elif strongest == Wuxing.Metal:
        # 从革格常见金旺而带少量水泄，支持比率略低于其他专旺盘。
        required_support_ratio = 0.70

    if support_ratio < required_support_ratio or root_score < 1.2:
        return None
    if month_family not in ("比劫", "印星"):
        return None

    mapping = {
        Wuxing.Wood: Geju.QU_ZHI,
        Wuxing.Fire: Geju.YAN_SHANG,
        Wuxing.Earth: Geju.JIA_SE,
        Wuxing.Water: Geju.RUN_XIA,
        Wuxing.Metal: Geju.CONG_GE,
    }
    return mapping.get(strongest)


def _check_huaqigeju(birth_chart: BirthChart, analysis: ChartAnalysis) -> Geju | None:
    strength = analysis.strength.day_master_strength
    if strength in (Strength.STRONG, Strength.VERY_STRONG):
        return None

    pair = _find_day_adjacent_hua_pair(birth_chart)
    if pair is None:
        return None

    left, right = pair
    rule_key = None
    rule = None
    for candidate_key, candidate_rule in HUA_RULES.items():
        if {left, right} == {candidate_key[0], candidate_key[1]}:
            rule_key = candidate_key
            rule = candidate_rule
            break
    if rule is None or rule_key is None:
        return None

    target_element, left_geju, right_geju = rule
    scores = _element_scores(analysis)
    total = sum(scores.values())
    if total <= 0:
        return None

    target_ratio = scores[target_element] / total
    month_element = birth_chart.monthzhu.zhi.belongs_to(Wuxing)
    root_score = analysis.strength.day_master_root_score

    if target_ratio < 0.33:
        return None
    if month_element not in (target_element, _generator_of(target_element)):
        return None
    if root_score > 0.9:
        return None

    return left_geju if birth_chart.dayzhu.gan == rule_key[0] else right_geju


def _check_cong_geju(birth_chart: BirthChart, analysis: ChartAnalysis) -> Geju | None:
    strength = analysis.strength.day_master_strength
    family_scores = analysis.ten_god.family_scores
    total_family = sum(family_scores.values())
    if total_family <= 0:
        return None

    support_ratio = analysis.strength.support_ratio
    root_score = analysis.strength.day_master_root_score
    root_count = analysis.strength.day_master_root_count

    support_family_ratio = (family_scores.get("比劫", 0.0) + family_scores.get("印星", 0.0)) / total_family
    if strength == Strength.VERY_STRONG and support_family_ratio >= 0.8 and root_count >= 2:
        return Geju.CONG_QIANG

    if strength not in (Strength.VERY_WEAK, Strength.WEAK):
        return None
    if support_ratio > 0.35 or root_score > 0.45 or root_count > 0:
        return None

    dominant_family, dominant_score = max(family_scores.items(), key=lambda item: item[1])
    ordered = sorted(family_scores.values(), reverse=True)
    dominant_ratio = dominant_score / total_family
    second_ratio = ordered[1] / total_family if len(ordered) > 1 else 0.0

    if dominant_ratio < 0.42 or (dominant_ratio - second_ratio) < 0.08:
        return None

    mapping = {
        "官杀": Geju.CONG_SHA,
        "财星": Geju.CONG_CAI,
        "食伤": Geju.CONG_ER,
        "印星": Geju.CONG_YIN,
        "比劫": Geju.CONG_QIANG,
    }
    return mapping.get(dominant_family)


def _check_zhengge(birth_chart: BirthChart) -> Geju | None:
    month_canggan = birth_chart.monthzhu.canggan
    exposed_stems = {
        birth_chart.yearzhu.gan,
        birth_chart.monthzhu.gan,
        birth_chart.bihourzhu.gan,
    }

    commander: Canggan | None = None
    for canggan in month_canggan:
        if canggan.gan in exposed_stems:
            commander = canggan
            break

    if commander is None:
        return None

    shishen = birth_chart.dayzhu.gan.get_shishen(commander.gan)
    return ZHENGGE_MAP.get(shishen)


def _find_day_adjacent_hua_pair(birth_chart: BirthChart) -> tuple[Tiangan, Tiangan] | None:
    candidates = [
        (birth_chart.monthzhu.gan, birth_chart.dayzhu.gan),
        (birth_chart.dayzhu.gan, birth_chart.bihourzhu.gan),
    ]
    for left, right in candidates:
        if (left, right) in HUA_RULES or (right, left) in HUA_RULES:
            return left, right
    return None


def _element_scores(analysis: ChartAnalysis) -> dict[Wuxing, float]:
    return {
        Wuxing.Wood: analysis.wuxing.items[Wuxing.Wood].score,
        Wuxing.Fire: analysis.wuxing.items[Wuxing.Fire].score,
        Wuxing.Earth: analysis.wuxing.items[Wuxing.Earth].score,
        Wuxing.Metal: analysis.wuxing.items[Wuxing.Metal].score,
        Wuxing.Water: analysis.wuxing.items[Wuxing.Water].score,
    }


def _generator_of(target: Wuxing) -> Wuxing:
    return Wuxing((target.num - 1) % 5)
