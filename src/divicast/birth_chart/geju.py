"""
八字命盘格局计算模块

包含各种格局的判断算法：
1. 特殊格局（魁罡、归禄等）
2. 专旺格（木火土金水专旺）
3. 化气格（天干合化）
4. 从格（从杀、从财、从儿、从印、从强）
5. 正格（十种：官杀、财、印、食伤、劫比）
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from ..entities.ganzhi import Canggan, Dizhi, Shishen, Tiangan
from ..entities.wuxing import Wuxing

if TYPE_CHECKING:
    from .birth import BirthChart


class Geju(str, Enum):
    """
    八字命盘格局枚举

    包含所有常见的八字格局分类：
    - 正格：官杀、财、印绶、食伤、劫比
    - 从格：从杀、从财、从儿、从印、从强
    - 化气格：十天干化气
    - 专旺格：曲直、炎上、稼穑、润下、从革
    - 特殊格局：各种名格局
    """

    # 正格 - 官杀类
    ZHENG_GUAN = "正官格"  # 正官格
    QI_SHA = "七杀格"      # 七杀格（偏官格）

    # 正格 - 财类
    ZHENG_CAI = "正财格"  # 正财格
    PIAN_CAI = "偏财格"  # 偏财格

    # 正格 - 印绶类
    ZHENG_YIN = "正印格"  # 正印格
    PIAN_YIN = "偏印格"  # 偏印格（枭神格）

    # 正格 - 食伤类
    SHI_SHEN = "食神格"  # 食神格
    SHANG_GUAN = "伤官格"  # 伤官格

    # 正格 - 劫比类
    BI_JIAN = "比肩格"   # 比肩格
    JIE_CAI = "劫财格"   # 劫财格

    # 从格
    CONG_SHA = "从杀格"   # 从杀格（满盘官杀无克制）
    CONG_CAI = "从财格"   # 从财格（满盘财星无克制）
    CONG_ER = "从儿格"    # 从儿格（满盘食伤）
    CONG_YIN = "从印格"   # 从印格（满盘印星）
    CONG_QIANG = "从强格"  # 从强格（满盘比劫）

    # 专旺格
    QU_ZHI = "曲直格"     # 曲直仁寿格（木专旺）
    YAN_SHANG = "炎上格"  # 炎上格（火专旺）
    JIA_SE = "稼穑格"     # 稼穑格（土专旺）
    RUN_XIA = "润下格"    # 润下格（水专旺）
    CONG_GE = "从革格"    # 从革格（金专旺）

    # 化气格（天干合化）
    HUA_JIA = "化甲格"    # 甲己合化土
    HUA_YI = "化乙格"     # 乙庚合化金
    HUA_BING = "化丙格"   # 丙辛合化水
    HUA_DING = "化丁格"   # 丁壬合化木
    HUA_WU = "化戊格"     # 戊癸合化火
    HUA_JI = "化己格"     # 己甲合化木
    HUA_GENG = "化庚格"   # 庚乙合化金
    HUA_XIN = "化辛格"    # 辛丙合化水
    HUA_REN = "化壬格"    # 壬丁合化木
    HUA_GUI = "化癸格"    # 癸戊合化火

    # 特殊格局
    KUIGANG = "魁罡格"           # 壬辰、庚辰、庚戌、戊戌
    QI_QIANG_BEI = "壬骑龙背格"  # 壬辰日
    JING_LAN_CHA = "井栏叉格"    # 庚子、庚申、庚辰
    GUI_LU = "归禄格"            # 日主临官位
    SHU_GUI = "鼠贵格"           # 乙日逢子
    LIU_JIA_QU_GAN = "六甲趋干格"   # 甲日亥时
    LIU_YI_SHU_GUI = "六乙鼠贵格"   # 乙日子时
    LIU_YIN_CHAO_YANG = "六阴朝阳格"  # 辛日丑时
    LIU_REN_QU_GEN = "六壬趋艮格"    # 壬寅日
    GOU_CHEN_DE_WEI = "勾陈得位格"   # 戊日丑未
    XUAN_WU_DANG_QUAN = "玄武当权格"  # 壬日寅午
    LIANG_SHEN_CHENG_XIANG = "两神成象格"  # 两种五行势均力敌
    BAN_BI_JIANG_SHAN = "半壁江山格"  # 两组干支相同

    # 普通格局/无特殊格局
    REGULAR = "普通格局"  # 无特殊格局
    NO_GEJU = "无格局"   # 无法确定格局


def analyze_geju(birth_chart: BirthChart) -> Geju:
    """
    分析命盘格局

    判断顺序：
    1. 特殊格局（魁罡、归禄等）
    2. 专旺格（木火土金水专旺）
    3. 化气格（天干合化）
    4. 从格（从杀、从财、从儿、从印、从强）
    5. 正格（十种：官杀、财、印、食伤、劫比）
    """
    # 1. 特殊格局
    geju = _check_special_geju(birth_chart)
    if geju:
        return geju

    # 2. 专旺格
    geju = _check_zhuanwang_geju(birth_chart)
    if geju:
        return geju

    # 3. 化气格
    geju = _check_huaqigeju(birth_chart)
    if geju:
        return geju

    # 4. 从格
    geju = _check_cong_geju(birth_chart)
    if geju:
        return geju

    # 5. 正格
    geju = _check_zhengge(birth_chart)
    if geju:
        return geju

    # 默认：无格局
    return Geju.NO_GEJU


def _check_special_geju(birth_chart: BirthChart) -> Geju | None:
    """
    检查特殊格局

    包含：
    - 魁罡格：日柱为壬辰、庚辰、庚戌、戊戌
    - 归禄格：日主临官位（帝旺）
    - 壬骑龙背格：壬辰日，多见辰
    - 井栏叉格：庚子、庚申、庚辰日
    - 六甲趋干格：甲日亥时
    - 六乙鼠贵格：乙日子时
    - 六阴朝阳格：辛日丑时
    - 六壬趋艮格：壬寅日
    - 勾陈得位格：戊日丑未
    - 玄武当权格：壬日寅午
    - 两神成象格：两种五行势均力敌
    - 半壁江山格：两组干支相同
    """
    # 魁罡格
    if _is_kuigang(birth_chart):
        return Geju.KUIGANG

    # 归禄格：日主临官位（帝旺）
    if _is_guilu(birth_chart):
        return Geju.GUI_LU

    # 壬骑龙背格：壬辰日，多见辰
    if _is_qiqiang_bei(birth_chart):
        return Geju.QI_QIANG_BEI

    # 井栏叉格：庚子、庚申、庚辰日
    if _is_jinglan_cha(birth_chart):
        return Geju.JING_LAN_CHA

    # 六甲趋干格：甲日亥时
    if _is_liu_jia_qu_gan(birth_chart):
        return Geju.LIU_JIA_QU_GAN

    # 六乙鼠贵格：乙日子时
    if _is_liu_yi_shu_gui(birth_chart):
        return Geju.LIU_YI_SHU_GUI

    # 六阴朝阳格：辛日丑时
    if _is_liu_yin_chao_yang(birth_chart):
        return Geju.LIU_YIN_CHAO_YANG

    # 六壬趋艮格：壬寅日
    if _is_liu_ren_qu_gen(birth_chart):
        return Geju.LIU_REN_QU_GEN

    # 勾陈得位格：戊日丑未
    if _is_gou_chen_de_wei(birth_chart):
        return Geju.GOU_CHEN_DE_WEI

    # 玄武当权格：壬日寅午
    if _is_xuan_wu_dang_quan(birth_chart):
        return Geju.XUAN_WU_DANG_QUAN

    # 两神成象格：两种五行势均力敌
    if _is_liang_shen_cheng_xiang(birth_chart):
        return Geju.LIANG_SHEN_CHENG_XIANG

    # 半壁江山格：两组干支相同
    if _is_ban_bi_jiang_shan(birth_chart):
        return Geju.BAN_BI_JIANG_SHAN

    return None


def _is_kuigang(birth_chart: BirthChart) -> bool:
    """
    判断是否为魁罡格

    魁罡格条件：日柱为壬辰、庚辰、庚戌、戊戌
    """
    day_gan = birth_chart.dayzhu.gan
    day_zhi = birth_chart.dayzhu.zhi

    # 魁罡格：壬辰、庚辰、庚戌、戊戌
    kuigang_combos = [
        (Tiangan.Ren, Dizhi.Chen),   # 壬辰
        (Tiangan.Geng, Dizhi.Chen),  # 庚辰
        (Tiangan.Geng, Dizhi.Xu),    # 庚戌
        (Tiangan.Wu, Dizhi.Xu),      # 戊戌
    ]

    return (day_gan, day_zhi) in kuigang_combos


def _is_guilu(birth_chart: BirthChart) -> bool:
    """
    判断是否为归禄格

    归禄格条件：日主临官位（帝旺）
    - 甲临官在卯
    - 乙临官在寅
    - 丙戊临官在巳
    - 丁己临官在午
    - 庚临官在申
    - 辛临官在酉
    - 壬临官在亥
    - 癸临官在子
    """
    day_gan = birth_chart.dayzhu.gan
    day_zhi = birth_chart.dayzhu.zhi

    # 临官位对应表
    guanzi = {
        Tiangan.Jia: Dizhi.Mou,   # 甲临官在卯
        Tiangan.Yi: Dizhi.Yin,    # 乙临官在寅
        Tiangan.Bing: Dizhi.Si,   # 丙临官在巳
        Tiangan.Wu: Dizhi.Si,     # 戊临官在巳
        Tiangan.Ding: Dizhi.Wu,   # 丁临官在午
        Tiangan.Ji: Dizhi.Wu,     # 己临官在午
        Tiangan.Geng: Dizhi.Shen, # 庚临官在申
        Tiangan.Xin: Dizhi.You,   # 辛临官在酉
        Tiangan.Ren: Dizhi.Hai,   # 壬临官在亥
        Tiangan.Gui: Dizhi.Zi,    # 癸临官在子
    }

    expected_zhi = guanzi.get(day_gan)
    return expected_zhi is not None and day_zhi == expected_zhi


def _is_qiqiang_bei(birth_chart: BirthChart) -> bool:
    """
    判断是否为壬骑龙背格

    条件：壬辰日，多见辰（地支多见辰）
    """
    day_gan = birth_chart.dayzhu.gan
    day_zhi = birth_chart.dayzhu.zhi

    # 必须是壬辰日
    if day_gan != Tiangan.Ren or day_zhi != Dizhi.Chen:
        return False

    # 计算地支中有多少个辰
    pillars = [birth_chart.yearzhu.zhi, birth_chart.monthzhu.zhi,
               birth_chart.dayzhu.zhi, birth_chart.bihourzhu.zhi]
    chen_count = sum(1 for zhi in pillars if zhi == Dizhi.Chen)

    # 多见辰（至少2个）
    return chen_count >= 2


def _is_jinglan_cha(birth_chart: BirthChart) -> bool:
    """
    判断是否为井栏叉格

    条件：庚子、庚申、庚辰日
    """
    day_gan = birth_chart.dayzhu.gan
    day_zhi = birth_chart.dayzhu.zhi

    # 庚日子、申、辰
    return day_gan == Tiangan.Geng and day_zhi in (Dizhi.Zi, Dizhi.Shen, Dizhi.Chen)


def _is_liu_jia_qu_gan(birth_chart: BirthChart) -> bool:
    """
    判断是否为六甲趋干格

    条件：甲日亥时
    """
    day_gan = birth_chart.dayzhu.gan
    hour_zhi = birth_chart.bihourzhu.zhi

    return day_gan == Tiangan.Jia and hour_zhi == Dizhi.Hai


def _is_liu_yi_shu_gui(birth_chart: BirthChart) -> bool:
    """
    判断是否为六乙鼠贵格

    条件：乙日子时
    """
    day_gan = birth_chart.dayzhu.gan
    hour_zhi = birth_chart.bihourzhu.zhi

    return day_gan == Tiangan.Yi and hour_zhi == Dizhi.Zi


def _is_liu_yin_chao_yang(birth_chart: BirthChart) -> bool:
    """
    判断是否为六阴朝阳格

    条件：辛日丑时
    """
    day_gan = birth_chart.dayzhu.gan
    hour_zhi = birth_chart.bihourzhu.zhi

    return day_gan == Tiangan.Xin and hour_zhi == Dizhi.Chou


def _is_liu_ren_qu_gen(birth_chart: BirthChart) -> bool:
    """
    判断是否为六壬趋艮格

    条件：壬寅日
    """
    day_gan = birth_chart.dayzhu.gan
    day_zhi = birth_chart.dayzhu.zhi

    return day_gan == Tiangan.Ren and day_zhi == Dizhi.Yin


def _is_gou_chen_de_wei(birth_chart: BirthChart) -> bool:
    """
    判断是否为勾陈得位格

    条件：戊日丑未
    """
    day_gan = birth_chart.dayzhu.gan
    day_zhi = birth_chart.dayzhu.zhi

    return day_gan == Tiangan.Wu and day_zhi in (Dizhi.Chou, Dizhi.Wei)


def _is_xuan_wu_dang_quan(birth_chart: BirthChart) -> bool:
    """
    判断是否为玄武当权格

    条件：壬日寅午
    """
    day_gan = birth_chart.dayzhu.gan
    day_zhi = birth_chart.dayzhu.zhi

    return day_gan == Tiangan.Ren and day_zhi in (Dizhi.Yin, Dizhi.Wu)


def _is_liang_shen_cheng_xiang(birth_chart: BirthChart) -> bool:
    """
    判断是否为两神成象格

    条件：两种五行势均力敌（各占40%左右）
    """
    analysis = birth_chart.chart_analysis

    wuxing_keys = ["木", "火", "土", "金", "水"]
    scores = {wx: analysis[wx]["score"] for wx in wuxing_keys}
    total = sum(scores.values())

    if total == 0:
        return False

    # 找出最强的两个五行
    sorted_wx = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_wx) < 2:
        return False

    first_wx, first_score = sorted_wx[0]
    second_wx, second_score = sorted_wx[1]

    # 两者都占30%以上，且相差不大
    first_ratio = first_score / total
    second_ratio = second_score / total

    return first_ratio >= 0.3 and second_ratio >= 0.3 and first_ratio - second_ratio < 0.2


def _is_ban_bi_jiang_shan(birth_chart: BirthChart) -> bool:
    """
    判断是否为半壁江山格

    条件：两组干支相同（如两壬寅、两丙午等）
    """
    pillars = [
        (birth_chart.yearzhu.gan, birth_chart.yearzhu.zhi),
        (birth_chart.monthzhu.gan, birth_chart.monthzhu.zhi),
        (birth_chart.dayzhu.gan, birth_chart.dayzhu.zhi),
        (birth_chart.bihourzhu.gan, birth_chart.bihourzhu.zhi),
    ]

    # 统计每种组合出现的次数
    from collections import Counter
    pillar_counts = Counter(pillars)

    # 找出出现2次及以上的组合
    for pillar, count in pillar_counts.items():
        if count >= 2:
            return True

    return False


def _check_zhuanwang_geju(birth_chart: BirthChart) -> Geju | None:
    """
    检查专旺格

    专旺格条件：某行特别强旺（占总分60%以上），日主无根且日主五行与最强五行一致

    - 曲直格：木专旺（木>60%，日主为甲乙木）
    - 炎上格：火专旺（火>60%，日主为丙丁火）
    - 稼穑格：土专旺（土>60%，日主为戊己土）
    - 润下格：水专旺（水>60%，日主为壬癸水）
    - 从革格：金专旺（金>60%，日主为庚辛金）
    """
    analysis = birth_chart.chart_analysis

    # 计算总分（只计算五行分数）
    wuxing_keys = ["木", "火", "土", "金", "水"]
    total_score = sum(analysis[key]["score"] for key in wuxing_keys)

    # 判断最强的五行占比
    strongest = analysis.get("strongest")
    if not strongest:
        return None

    strongest_score = analysis[strongest]["score"]
    ratio = strongest_score / total_score if total_score > 0 else 0

    # 专旺格需要最强的五行占60%以上
    if ratio < 0.6:
        return None

    # 日主必须无根
    day_master_has_root = analysis.get("day_master_has_root", False)
    if day_master_has_root:
        return None

    # 日主五行必须与最强五行一致
    day_master_wuxing = analysis.get("day_master_wuxing")
    if day_master_wuxing != strongest:
        return None

    # 判断是哪一行专旺
    if strongest == "木":
        return Geju.QU_ZHI
    elif strongest == "火":
        return Geju.YAN_SHANG
    elif strongest == "土":
        return Geju.JIA_SE
    elif strongest == "水":
        return Geju.RUN_XIA
    elif strongest == "金":
        return Geju.CONG_GE

    return None


def _check_huaqigeju(birth_chart: BirthChart) -> Geju | None:
    """
    检查化气格

    化气格条件：天干合化，且化神旺，日主弱

    合化规则：
    - 甲己合化土 -> 化土
    - 乙庚合化金 -> 化金
    - 丙辛合化水 -> 化水
    - 丁壬合化木 -> 化木
    - 戊癸合化火 -> 化火
    """
    # 获取天干列表
    heaven_stems = [
        birth_chart.yearzhu.gan,
        birth_chart.monthzhu.gan,
        birth_chart.dayzhu.gan,
        birth_chart.bihourzhu.gan,
    ]

    # 合化规则：(天干1, 天干2) -> 化神
    hua_rules = {
        (Tiangan.Jia, Tiangan.Ji): "土",   # 甲己合化土
        (Tiangan.Yi, Tiangan.Geng): "金",  # 乙庚合化金
        (Tiangan.Bing, Tiangan.Xin): "水", # 丙辛合化水
        (Tiangan.Ding, Tiangan.Ren): "木",  # 丁壬合化木
        (Tiangan.Wu, Tiangan.Gui): "火",   # 戊癸合化火
    }

    # 检查是否有合化
    hua_wuxing = None
    for (tg1, tg2), wx in hua_rules.items():
        if tg1 in heaven_stems and tg2 in heaven_stems:
            hua_wuxing = wx
            break

    if not hua_wuxing:
        return None

    # 化神要旺（占总分40%以上）
    analysis = birth_chart.chart_analysis
    wuxing_keys = ["木", "火", "土", "金", "水"]
    total_score = sum(analysis[key]["score"] for key in wuxing_keys)
    hua_score = analysis[hua_wuxing]["score"]
    ratio = hua_score / total_score if total_score > 0 else 0

    if ratio < 0.4:
        return None

    # 日主要弱（日主无根）
    if analysis.get("day_master_has_root", False):
        return None

    # 根据化神返回对应的格局
    # 化气格以合化后的天干命名
    if hua_wuxing == "土":
        # 甲己合化土 -> 化甲格或化己格
        return Geju.HUA_JIA
    elif hua_wuxing == "金":
        # 乙庚合化金 -> 化乙格或化庚格
        return Geju.HUA_YI
    elif hua_wuxing == "水":
        # 丙辛合化水 -> 化丙格或化辛格
        return Geju.HUA_BING
    elif hua_wuxing == "木":
        # 丁壬合化木 -> 化丁格或化壬格
        return Geju.HUA_DING
    elif hua_wuxing == "火":
        # 戊癸合化火 -> 化戊格或化癸格
        return Geju.HUA_WU

    return None


def _check_cong_geju(birth_chart: BirthChart) -> Geju | None:
    """
    检查从格

    从格条件：日主无根，且某一行特别强旺（占总分60%以上）

    - 从杀格：从官杀（金水） - 官杀占主导
    - 从财格：从财星（土金） - 财星占主导
    - 从儿格：从食伤（火木） - 食伤占主导
    - 从印格：从印星（水木） - 印星占主导
    - 从强格：从比劫（木火土金水） - 比劫占主导（日主同类）
    """
    analysis = birth_chart.chart_analysis

    # 从格必须日主无根
    day_master_has_root = analysis.get("day_master_has_root", False)
    if day_master_has_root:
        return None

    # 计算总分
    wuxing_keys = ["木", "火", "土", "金", "水"]
    total_score = sum(analysis[key]["score"] for key in wuxing_keys)

    # 判断最强的五行
    strongest = analysis.get("strongest")
    if not strongest:
        return None

    strongest_score = analysis[strongest]["score"]
    ratio = strongest_score / total_score if total_score > 0 else 0

    # 从格需要最强的五行占60%以上
    if ratio < 0.6:
        return None

    # 根据最强的五行判断从什么
    # 官杀：金（庚辛）、水（壬癸）
    # 财星：土（戊己）、金（庚辛）
    # 食伤：火（丙丁）、木（甲乙）
    # 印星：水（壬癸）、木（甲乙）
    # 比劫：与日主同类

    day_master_wuxing = analysis.get("day_master_wuxing")

    if strongest == "金":
        # 金可以是官杀（金）或财星（金）
        # 需要看日主，日主是丙丁火则从杀，日主是戊己土则从财
        if day_master_wuxing in ("火", "土"):
            return Geju.CONG_SHA
        elif day_master_wuxing in ("水", "木"):
            return Geju.CONG_CAI
    elif strongest == "水":
        # 水是官杀（水）或印星（水）
        if day_master_wuxing in ("火", "土", "金"):
            return Geju.CONG_SHA
        elif day_master_wuxing in ("木",):
            return Geju.CONG_YIN
    elif strongest == "土":
        # 土是财星
        return Geju.CONG_CAI
    elif strongest == "木":
        # 木是食伤（木）或印星（木）
        if day_master_wuxing in ("火", "土", "金", "水"):
            return Geju.CONG_ER
    elif strongest == "火":
        # 火是食伤
        return Geju.CONG_ER

    return None


def _check_zhengge(birth_chart: BirthChart) -> Geju | None:
    """
    检查正格

    正格条件：以月支藏干透出天干为准

    十种正格：
    - 正官格：月支透正官
    - 七杀格：月支透七杀（偏官）
    - 正财格：月支透正财
    - 偏财格：月支透偏财
    - 正印格：月支透正印
    - 偏印格：月支透偏印（枭神）
    - 食神格：月支透食神
    - 伤官格：月支透伤官
    - 比肩格：月支透比肩
    - 劫财格：月支透劫财
    """
    # 获取月支
    month_zhi = birth_chart.monthzhu.zhi

    # 获取月支藏干
    month_canggan = birth_chart.monthzhu.canggan

    # 获取天干列表（年、月、日、时）
    heaven_stems = [
        birth_chart.yearzhu.gan,
        birth_chart.monthzhu.gan,
        birth_chart.dayzhu.gan,
        birth_chart.bihourzhu.gan,
    ]

    # 检查月支藏干是否透出天干
    for canggan in month_canggan:
        cgan = canggan.gan
        # 检查此藏干是否出现在天干中
        if cgan in heaven_stems:
            # 根据藏干对应的十神确定格局
            shishen = birth_chart.dayzhu.gan.get_shishen(cgan)

            from ..entities.ganzhi import Shishen

            if shishen == Shishen.ZhengGuan:
                return Geju.ZHENG_GUAN
            elif shishen == Shishen.QiSha:
                return Geju.QI_SHA
            elif shishen == Shishen.ZhengCai:
                return Geju.ZHENG_CAI
            elif shishen == Shishen.PianCai:
                return Geju.PIAN_CAI
            elif shishen == Shishen.ZhengYin:
                return Geju.ZHENG_YIN
            elif shishen == Shishen.PianYin:
                return Geju.PIAN_YIN
            elif shishen == Shishen.ShiShen:
                return Geju.SHI_SHEN
            elif shishen == Shishen.ShangGuan:
                return Geju.SHANG_GUAN
            elif shishen == Shishen.BiJian:
                return Geju.BI_JIAN
            elif shishen == Shishen.JieCai:
                return Geju.JIE_CAI

    # 月支藏干未透出，返回普通格局
    return Geju.REGULAR
