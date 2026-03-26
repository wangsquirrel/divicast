from __future__ import annotations

from enum import Enum

from divicast.base.symbol import ValuedMultiton


class Strength(ValuedMultiton):
    """表示实体强弱的枚举"""

    VERY_WEAK = (0, "极弱")
    WEAK = (1, "弱")
    NEUTRAL = (2, "中和")
    STRONG = (3, "强")
    VERY_STRONG = (4, "极强")


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

    ZHENG_GUAN = "正官格"
    QI_SHA = "七杀格"
    ZHENG_CAI = "正财格"
    PIAN_CAI = "偏财格"
    ZHENG_YIN = "正印格"
    PIAN_YIN = "偏印格"
    SHI_SHEN = "食神格"
    SHANG_GUAN = "伤官格"
    BI_JIAN = "比肩格"
    JIE_CAI = "劫财格"

    CONG_SHA = "从杀格"
    CONG_CAI = "从财格"
    CONG_ER = "从儿格"
    CONG_YIN = "从印格"
    CONG_QIANG = "从强格"

    QU_ZHI = "曲直格"
    YAN_SHANG = "炎上格"
    JIA_SE = "稼穑格"
    RUN_XIA = "润下格"
    CONG_GE = "从革格"

    HUA_JIA = "化甲格"
    HUA_YI = "化乙格"
    HUA_BING = "化丙格"
    HUA_DING = "化丁格"
    HUA_WU = "化戊格"
    HUA_JI = "化己格"
    HUA_GENG = "化庚格"
    HUA_XIN = "化辛格"
    HUA_REN = "化壬格"
    HUA_GUI = "化癸格"

    KUIGANG = "魁罡格"
    QI_QIANG_BEI = "壬骑龙背格"
    JING_LAN_CHA = "井栏叉格"
    GUI_LU = "归禄格"
    SHU_GUI = "鼠贵格"
    LIU_JIA_QU_GAN = "六甲趋干格"
    LIU_YI_SHU_GUI = "六乙鼠贵格"
    LIU_YIN_CHAO_YANG = "六阴朝阳格"
    LIU_REN_QU_GEN = "六壬趋艮格"
    GOU_CHEN_DE_WEI = "勾陈得位格"
    XUAN_WU_DANG_QUAN = "玄武当权格"
    LIANG_SHEN_CHENG_XIANG = "两神成象格"
    BAN_BI_JIANG_SHAN = "半壁江山格"

    REGULAR = "普通格局"
    NO_GEJU = "无格局"


class Zhu(str, Enum):
    YEAR = "年"
    MONTH = "月"
    DAY = "日"
    HOUR = "时"


class GanZhi(str, Enum):
    TIANGAN = "天干"
    DIZHI = "地支"
