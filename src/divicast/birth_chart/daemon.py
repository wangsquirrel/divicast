"""
命盘神煞体系的实现
"""

from tyme4py import enums, lunar  # type: ignore

from ..entities.daemon import Daemon
from ..entities.ganzhi import Tiangan
from ..entities.misc import Gender
from ..entities.wuxing import YinYang


def build_pillar_shensha(bazi: lunar.EightChar, gender: Gender) -> list[list[Daemon]]:
    """
    神煞体系：
    - 规则参考 cantian-tymext 的 getShen 实现
    - 输出为年/月/日/时四柱的神煞列表
    """
    ganzhi_list = [
        bazi.get_year().get_name(),
        bazi.get_month().get_name(),
        bazi.get_day().get_name(),
        bazi.get_hour().get_name(),
    ]
    year_gz, month_gz, day_gz, hour_gz = ganzhi_list
    year_gan, year_zhi = year_gz[0], year_gz[1]
    month_zhi = month_gz[1]
    day_gan, day_zhi = day_gz[0], day_gz[1]
    hour_zhi = hour_gz[1]

    year_xun = XUN[year_gz]
    day_xun = XUN[day_gz]
    year_nayin_wuxing = NAYIN_WUXING[year_gz]
    year_yinyang = Tiangan[year_gan].belongs_to(YinYang)
    gender_yinyang = gender.belongs_to(YinYang)

    gods = [set() for _ in range(4)]

    def add(idx: int, name: str | None):
        if name:
            gods[idx].add(name)

    for i in range(4):
        gz = ganzhi_list[i]
        gan = gz[0]
        zhi = gz[1]
        add(i, grab_tianyiguiren(day_gan, year_gan, zhi))
        add(i, grab_tiandeguiren(month_zhi, gz))
        add(i, grab_yuedeguiren(month_zhi, gz))
        add(i, grab_tiandehe(month_zhi, gz))
        add(i, grab_yuedehe(month_zhi, gan))
        add(i, grab_lushen(day_gan, zhi))
        add(i, grab_taijiguiren(day_gan, year_gan, zhi))
        add(i, grab_guoyinguiren(day_gan, year_gan, zhi))
        add(i, grab_wenchangguiren(day_gan, year_gan, zhi))
        add(i, grab_jinyu(year_gan, day_gan, zhi))
        add(i, grab_yangren(day_gan, zhi))
        add(i, grab_feiren(day_gan, zhi))
        add(i, grab_xueren(month_zhi, zhi))
        add(i, grab_liuxia(day_gan, zhi))
        add(i, grab_hongyan(day_gan, zhi))
        add(i, grab_fuxingguiren(year_gan, day_gan, zhi))
        add(i, grab_dexiuguiren(month_zhi, gan))
        add(i, grab_tianchuguiren(year_gan, day_gan, zhi))
        add(i, grab_tianguanguiren(day_gan, year_gan, zhi))

    for i in range(1, 4):
        gz = ganzhi_list[i]
        zhi = gz[1]
        add(i, grab_xuetang(year_nayin_wuxing, day_gan, gz))
        add(i, grab_ciguan(year_nayin_wuxing, day_gan, gz))
        add(i, grab_zaisha(year_zhi, zhi))
        add(i, grab_guchen(year_zhi, zhi))
        add(i, grab_guasu(year_zhi, zhi))
        add(i, grab_hongluan(year_zhi, zhi))
        add(i, grab_tianxi(year_zhi, zhi))
        add(i, grab_goujiaosha(year_zhi, zhi))
        add(i, grab_yuanchen(year_yinyang, year_zhi, gender_yinyang, zhi))
        add(i, grab_sangmen(year_zhi, zhi))
        add(i, grab_diaoke(year_zhi, zhi))
        add(i, grab_pima(year_zhi, zhi))
        add(i, grab_pitou(year_zhi, zhi))
        add(i, grab_liuer(year_zhi, zhi))

    for i in range(4):
        if i != 1:
            add(i, grab_tianyi(month_zhi, ganzhi_list[i][1]))

    for i in range(4):
        if i != 0:
            add(i, grab_jiangxing(year_zhi, ganzhi_list[i][1]))
            add(i, grab_yima(year_zhi, ganzhi_list[i][1]))
            add(i, grab_huagai(year_zhi, ganzhi_list[i][1]))
            add(i, grab_wangshen(year_zhi, ganzhi_list[i][1]))
            add(i, grab_jiesha(year_zhi, ganzhi_list[i][1]))
            add(i, grab_kongwang(year_xun, ganzhi_list[i][1]))
            add(i, grab_taohua(year_zhi, ganzhi_list[i][1]))
            add(i, grab_tianluodiwang1(year_zhi, ganzhi_list[i][1]))
        if i != 2:
            add(i, grab_jiangxing(day_zhi, ganzhi_list[i][1]))
            add(i, grab_yima(day_zhi, ganzhi_list[i][1]))
            add(i, grab_huagai(day_zhi, ganzhi_list[i][1]))
            add(i, grab_wangshen(day_zhi, ganzhi_list[i][1]))
            add(i, grab_jiesha(day_zhi, ganzhi_list[i][1]))
            add(i, grab_kongwang(day_xun, ganzhi_list[i][1]))
            add(i, grab_taohua(day_zhi, ganzhi_list[i][1]))
            add(i, grab_tianluodiwang1(day_zhi, ganzhi_list[i][1]))

    add(2, grab_tiansheri(month_zhi, day_gz))
    add(2, grab_sanqiguiren("".join(ganzhi_list)))
    add(2, grab_sifeiri(month_zhi, day_gz))
    add(2, grab_tianluodiwang2(year_nayin_wuxing, day_zhi))
    add(2, grab_yinchayangcuo(day_gz))
    add(2, grab_kuigang(day_gz))
    add(2, grab_guluan(day_gz))
    add(2, grab_shiedabai(day_gz))
    add(2, grab_jinshen(day_gz))
    add(3, grab_jinshen(hour_gz))
    add(2, grab_tianzhuan(month_zhi, day_gz))
    add(2, grab_dizhuan(month_zhi, day_gz))
    add(2, grab_shiling(day_gz))
    add(2, grab_liuxiu(day_gz))
    add(2, grab_bazhuan(day_gz))
    add(2, grab_jiuchou(day_gz))
    add(2, grab_tongzisha(month_zhi, year_nayin_wuxing, day_zhi))
    add(3, grab_tongzisha(month_zhi, year_nayin_wuxing, hour_zhi))
    add(2, grab_gonglu(day_gz, hour_gz))
    add(2, grab_jinshenx(day_gz))
    add(3, grab_gejiaosha(day_zhi, hour_zhi))

    result: list[list[Daemon]] = []
    for item in gods:
        daemons: list[Daemon] = []
        for name in item:
            try:
                daemons.append(Daemon[name])
            except Exception:
                continue
        result.append(daemons)
    return result


NAYIN_WUXING = {
    "甲子": "金",
    "甲午": "金",
    "丙寅": "火",
    "丙申": "火",
    "戊辰": "木",
    "戊戌": "木",
    "庚午": "土",
    "庚子": "土",
    "壬申": "金",
    "壬寅": "金",
    "甲戌": "火",
    "甲辰": "火",
    "丙子": "水",
    "丙午": "水",
    "戊寅": "土",
    "戊申": "土",
    "庚辰": "金",
    "庚戌": "金",
    "壬午": "木",
    "壬子": "木",
    "甲申": "水",
    "甲寅": "水",
    "丙戌": "土",
    "丙辰": "土",
    "戊子": "火",
    "戊午": "火",
    "庚寅": "木",
    "庚申": "木",
    "壬辰": "水",
    "壬戌": "水",
    "乙丑": "金",
    "乙未": "金",
    "丁卯": "火",
    "丁酉": "火",
    "己巳": "木",
    "己亥": "木",
    "辛未": "土",
    "辛丑": "土",
    "癸酉": "金",
    "癸卯": "金",
    "乙亥": "火",
    "乙巳": "火",
    "丁丑": "水",
    "丁未": "水",
    "己卯": "土",
    "己酉": "土",
    "辛巳": "金",
    "辛亥": "金",
    "癸未": "木",
    "癸丑": "木",
    "乙酉": "水",
    "乙卯": "水",
    "丁亥": "土",
    "丁巳": "土",
    "己丑": "火",
    "己未": "火",
    "辛卯": "木",
    "辛酉": "木",
    "癸巳": "水",
    "癸亥": "水",
}

XUN = {
    "甲子": "甲子",
    "乙丑": "甲子",
    "丙寅": "甲子",
    "丁卯": "甲子",
    "戊辰": "甲子",
    "己巳": "甲子",
    "庚午": "甲子",
    "辛未": "甲子",
    "壬申": "甲子",
    "癸酉": "甲子",
    "甲戌": "甲戌",
    "乙亥": "甲戌",
    "丙子": "甲戌",
    "丁丑": "甲戌",
    "戊寅": "甲戌",
    "己卯": "甲戌",
    "庚辰": "甲戌",
    "辛巳": "甲戌",
    "壬午": "甲戌",
    "癸未": "甲戌",
    "甲申": "甲申",
    "乙酉": "甲申",
    "丙戌": "甲申",
    "丁亥": "甲申",
    "戊子": "甲申",
    "己丑": "甲申",
    "庚寅": "甲申",
    "辛卯": "甲申",
    "壬辰": "甲申",
    "癸巳": "甲申",
    "甲午": "甲午",
    "乙未": "甲午",
    "丙申": "甲午",
    "丁酉": "甲午",
    "戊戌": "甲午",
    "己亥": "甲午",
    "庚子": "甲午",
    "辛丑": "甲午",
    "壬寅": "甲午",
    "癸卯": "甲午",
    "甲辰": "甲辰",
    "乙巳": "甲辰",
    "丙午": "甲辰",
    "丁未": "甲辰",
    "戊申": "甲辰",
    "己酉": "甲辰",
    "庚戌": "甲辰",
    "辛亥": "甲辰",
    "壬子": "甲辰",
    "癸丑": "甲辰",
    "甲寅": "甲寅",
    "乙卯": "甲寅",
    "丙辰": "甲寅",
    "丁巳": "甲寅",
    "戊午": "甲寅",
    "己未": "甲寅",
    "庚申": "甲寅",
    "辛酉": "甲寅",
    "壬戌": "甲寅",
    "癸亥": "甲寅",
}

TIANYIGUIREN_MAP = {
    "甲": "丑未",
    "乙": "子申",
    "丙": "亥酉",
    "丁": "亥酉",
    "戊": "丑未",
    "己": "子申",
    "庚": "丑未",
    "辛": "午寅",
    "壬": "卯巳",
    "癸": "卯巳",
}

TIANDEGUIREN_MAP = {
    "寅": "丁",
    "卯": "申",
    "辰": "壬",
    "巳": "辛",
    "午": "亥",
    "未": "甲",
    "申": "癸",
    "酉": "寅",
    "戌": "丙",
    "亥": "乙",
    "子": "巳",
    "丑": "庚",
}

YUEDEGUIREN_MAP = {
    "寅": "丙",
    "午": "丙",
    "戌": "丙",
    "申": "壬",
    "子": "壬",
    "辰": "壬",
    "亥": "甲",
    "卯": "甲",
    "未": "甲",
    "巳": "庚",
    "酉": "庚",
    "丑": "庚",
}

TIANDEHE_MAP = {
    "寅": "壬",
    "卯": "巳",
    "辰": "丁",
    "巳": "丙",
    "午": "寅",
    "未": "己",
    "申": "戊",
    "酉": "亥",
    "戌": "辛",
    "亥": "庚",
    "子": "申",
    "丑": "乙",
}

YUEDEHE_MAP = {
    "寅": "辛",
    "午": "辛",
    "戌": "辛",
    "申": "丁",
    "子": "丁",
    "辰": "丁",
    "巳": "乙",
    "酉": "乙",
    "丑": "乙",
    "亥": "己",
    "卯": "己",
    "未": "己",
}

TIANSHERI_MAP = {
    "寅": "戊寅",
    "卯": "戊寅",
    "辰": "戊寅",
    "巳": "甲午",
    "午": "甲午",
    "未": "甲午",
    "申": "戊申",
    "酉": "戊申",
    "戌": "戊申",
    "亥": "甲子",
    "子": "甲子",
    "丑": "甲子",
}

LUSHEN_MAP = {
    "甲": "寅",
    "乙": "卯",
    "丙": "巳",
    "丁": "午",
    "戊": "巳",
    "己": "午",
    "庚": "申",
    "辛": "酉",
    "壬": "亥",
    "癸": "子",
}

YIMA_MAP = {
    "申": "寅",
    "子": "寅",
    "辰": "寅",
    "寅": "申",
    "午": "申",
    "戌": "申",
    "巳": "亥",
    "酉": "亥",
    "丑": "亥",
    "亥": "巳",
    "卯": "巳",
    "未": "巳",
}

TAIJIGUIREN_MAP = {
    "甲": "子午",
    "乙": "子午",
    "丙": "酉卯",
    "丁": "酉卯",
    "戊": "辰戌丑未",
    "己": "辰戌丑未",
    "庚": "寅亥",
    "辛": "寅亥",
    "壬": "巳申",
    "癸": "巳申",
}

JIANGXING_MAP = {
    "子": "子",
    "丑": "酉",
    "寅": "午",
    "卯": "卯",
    "辰": "子",
    "巳": "酉",
    "午": "午",
    "未": "卯",
    "申": "子",
    "酉": "酉",
    "戌": "午",
    "亥": "卯",
}

XUETANG_MAP = {
    "金": "巳",
    "木": "亥",
    "水": "申",
    "土": "申",
    "火": "寅",
    "甲": "己亥",
    "乙": "壬午",
    "丙": "丙寅",
    "丁": "丁酉",
    "戊": "戊寅",
    "己": "己酉",
    "庚": "辛巳",
    "辛": "甲子",
    "壬": "甲申",
    "癸": "乙卯",
}

CIGUAN_MAP = {
    "金": "申",
    "木": "寅",
    "水": "亥",
    "土": "亥",
    "火": "巳",
    "甲": "庚寅",
    "乙": "辛卯",
    "丙": "乙巳",
    "丁": "戊午",
    "戊": "丁巳",
    "己": "庚午",
    "庚": "壬申",
    "辛": "癸酉",
    "壬": "癸亥",
    "癸": "壬戌",
}

GUOYINGUIREN_MAP = {
    "甲": "戌",
    "乙": "亥",
    "丙": "丑",
    "丁": "寅",
    "戊": "丑",
    "己": "寅",
    "庚": "辰",
    "辛": "巳",
    "壬": "未",
    "癸": "申",
}

SANQIGUIREN_MAP = [r"甲.*戊.*庚|庚.*戊.*甲", r"乙.*丙.*丁|丁.*丙.*乙", r"壬.*癸.*辛|辛.*癸.*壬"]

WENCHANGGUIREN_MAP = {
    "甲": "巳",
    "乙": "午",
    "丙": "申",
    "丁": "酉",
    "戊": "申",
    "己": "酉",
    "庚": "亥",
    "辛": "子",
    "壬": "寅",
    "癸": "卯",
}

HUAGAI_MAP = {
    "寅": "戌",
    "午": "戌",
    "戌": "戌",
    "亥": "未",
    "卯": "未",
    "未": "未",
    "申": "辰",
    "子": "辰",
    "辰": "辰",
    "巳": "丑",
    "酉": "丑",
    "丑": "丑",
}

TIANYI_MAP = {
    "寅": "丑",
    "卯": "寅",
    "辰": "卯",
    "巳": "辰",
    "午": "巳",
    "未": "午",
    "申": "未",
    "酉": "申",
    "戌": "酉",
    "亥": "戌",
    "子": "亥",
    "丑": "子",
}

JINYU_MAP = {
    "甲": "辰",
    "乙": "巳",
    "丙": "未",
    "丁": "申",
    "戊": "未",
    "己": "申",
    "庚": "戌",
    "辛": "亥",
    "壬": "丑",
    "癸": "寅",
}

KONGWANG_MAP = {
    "甲子": "戌亥",
    "甲戌": "申酉",
    "甲申": "午未",
    "甲午": "辰巳",
    "甲辰": "寅卯",
    "甲寅": "子丑",
}

ZAISHA_MAP = {
    "申": "午",
    "子": "午",
    "辰": "午",
    "亥": "酉",
    "卯": "酉",
    "未": "酉",
    "寅": "子",
    "午": "子",
    "戌": "子",
    "巳": "卯",
    "酉": "卯",
    "丑": "卯",
}

JIESHA_MAP = {
    "寅": "亥",
    "午": "亥",
    "戌": "亥",
    "申": "巳",
    "子": "巳",
    "辰": "巳",
    "巳": "寅",
    "酉": "寅",
    "丑": "寅",
    "亥": "申",
    "卯": "申",
    "未": "申",
}

WANGSHEN_MAP = {
    "寅": "巳",
    "午": "巳",
    "戌": "巳",
    "申": "亥",
    "子": "亥",
    "辰": "亥",
    "亥": "寅",
    "卯": "寅",
    "未": "寅",
    "巳": "申",
    "酉": "申",
    "丑": "申",
}

YANGREN_MAP = {
    "甲": "卯",
    "乙": "寅",
    "丙": "午",
    "丁": "巳",
    "戊": "午",
    "己": "巳",
    "庚": "酉",
    "辛": "申",
    "壬": "子",
    "癸": "亥",
}

FEIREN_MAP = {
    "甲": "酉",
    "乙": "申",
    "丙": "子",
    "丁": "亥",
    "戊": "子",
    "己": "亥",
    "庚": "卯",
    "辛": "寅",
    "壬": "午",
    "癸": "巳",
}

XUEREN_MAP = {
    "寅": "丑",
    "卯": "未",
    "辰": "寅",
    "巳": "申",
    "午": "卯",
    "未": "酉",
    "申": "辰",
    "酉": "戌",
    "戌": "巳",
    "亥": "亥",
    "子": "午",
    "丑": "子",
}

LIUXIA_MAP = {
    "甲": "酉",
    "乙": "戌",
    "丙": "未",
    "丁": "申",
    "戊": "巳",
    "己": "午",
    "庚": "辰",
    "辛": "卯",
    "壬": "亥",
    "癸": "寅",
}

SIFEIRI_MAP = {
    "寅": ["庚申", "辛酉"],
    "卯": ["庚申", "辛酉"],
    "辰": ["庚申", "辛酉"],
    "巳": ["壬子", "癸亥"],
    "午": ["壬子", "癸亥"],
    "未": ["壬子", "癸亥"],
    "申": ["甲寅", "乙卯"],
    "酉": ["甲寅", "乙卯"],
    "戌": ["甲寅", "乙卯"],
    "亥": ["丙午", "丁巳"],
    "子": ["丙午", "丁巳"],
    "丑": ["丙午", "丁巳"],
}

TIANLUODIWANG_MAP = ["戌亥", "辰巳", "亥戌", "巳辰"]

TAOHUA_MAP = {
    "申": "酉",
    "子": "酉",
    "辰": "酉",
    "寅": "卯",
    "午": "卯",
    "戌": "卯",
    "巳": "午",
    "酉": "午",
    "丑": "午",
    "亥": "子",
    "卯": "子",
    "未": "子",
}

GUCHEN_MAP = {
    "亥": "寅",
    "子": "寅",
    "丑": "寅",
    "寅": "巳",
    "卯": "巳",
    "辰": "巳",
    "巳": "申",
    "午": "申",
    "未": "申",
    "申": "亥",
    "酉": "亥",
    "戌": "亥",
}

GUASU_MAP = {
    "亥": "戌",
    "子": "戌",
    "丑": "戌",
    "寅": "丑",
    "卯": "丑",
    "辰": "丑",
    "巳": "辰",
    "午": "辰",
    "未": "辰",
    "申": "未",
    "酉": "未",
    "戌": "未",
}

YINCHAYANGCUO_MAP = ["丙子", "丙午", "丁丑", "丁未", "戊寅", "戊申", "辛卯", "辛酉", "壬辰", "壬戌", "癸巳", "癸亥"]
KUIGANG_MAP = ["戊戌", "壬辰", "庚戌", "庚辰"]
GULUAN_MAP = ["甲寅", "乙巳", "丙午", "丁巳", "戊午", "戊申", "辛亥", "壬子"]
HONGLUAN_MAP = {
    "子": "卯",
    "丑": "寅",
    "寅": "丑",
    "卯": "子",
    "辰": "亥",
    "巳": "戌",
    "午": "酉",
    "未": "申",
    "申": "未",
    "酉": "午",
    "戌": "巳",
    "亥": "辰",
}

TIANXI_MAP = {
    "子": "酉",
    "丑": "申",
    "寅": "未",
    "卯": "午",
    "辰": "巳",
    "巳": "辰",
    "午": "卯",
    "未": "寅",
    "申": "丑",
    "酉": "子",
    "戌": "亥",
    "亥": "戌",
}

GOUJIAOSHA_MAP = {
    "子": "卯",
    "丑": "辰",
    "寅": "巳",
    "卯": "午",
    "辰": "未",
    "巳": "申",
    "午": "酉",
    "未": "戌",
    "申": "亥",
    "酉": "子",
    "戌": "丑",
    "亥": "寅",
}

HONGYAN_MAP = {
    "甲": "午",
    "乙": "午",
    "丙": "寅",
    "丁": "未",
    "戊": "辰",
    "己": "辰",
    "庚": "戌",
    "辛": "酉",
    "壬": "子",
    "癸": "申",
}

SHIEDABAI_MAP = ["甲辰", "乙巳", "壬申", "丙申", "丁亥", "庚辰", "戊戌", "癸亥", "辛巳", "己丑"]

YUANCHEN_MAP = {
    "同": {
        "子": "未",
        "丑": "申",
        "寅": "酉",
        "卯": "戌",
        "辰": "亥",
        "巳": "子",
        "午": "丑",
        "未": "寅",
        "申": "卯",
        "酉": "辰",
        "戌": "巳",
        "亥": "午",
    },
    "异": {
        "子": "巳",
        "丑": "午",
        "寅": "未",
        "卯": "申",
        "辰": "酉",
        "巳": "戌",
        "午": "亥",
        "未": "子",
        "申": "丑",
        "酉": "寅",
        "戌": "卯",
        "亥": "辰",
    },
}

JINSHEN_MAP = ["乙丑", "己巳", "癸酉"]

TIANZHUAN_MAP = {
    "寅": "乙卯",
    "卯": "乙卯",
    "辰": "乙卯",
    "巳": "丙午",
    "午": "丙午",
    "未": "丙午",
    "申": "辛酉",
    "酉": "辛酉",
    "戌": "辛酉",
    "亥": "壬子",
    "子": "壬子",
    "丑": "壬子",
}

DIZHUAN_MAP = {
    "寅": "辛卯",
    "卯": "辛卯",
    "辰": "辛卯",
    "巳": "戊午",
    "午": "戊午",
    "未": "戊午",
    "申": "癸酉",
    "酉": "癸酉",
    "戌": "癸酉",
    "亥": "丙子",
    "子": "丙子",
    "丑": "丙子",
}

SANGMEN_MAP = {
    "子": "寅",
    "丑": "卯",
    "寅": "辰",
    "卯": "巳",
    "辰": "午",
    "巳": "未",
    "午": "申",
    "未": "酉",
    "申": "戌",
    "酉": "亥",
    "戌": "子",
    "亥": "丑",
}

DIAOKE_MAP = {
    "子": "戌",
    "丑": "亥",
    "寅": "子",
    "卯": "丑",
    "辰": "寅",
    "巳": "卯",
    "午": "辰",
    "未": "巳",
    "申": "午",
    "酉": "未",
    "戌": "申",
    "亥": "酉",
}

PIMA_MAP = {
    "子": "酉",
    "丑": "戌",
    "寅": "亥",
    "卯": "子",
    "辰": "丑",
    "巳": "寅",
    "午": "卯",
    "未": "辰",
    "申": "巳",
    "酉": "午",
    "戌": "未",
    "亥": "申",
}

SHILING_MAP = ["甲辰", "乙亥", "丙辰", "丁酉", "戊午", "庚戌", "庚寅", "辛亥", "壬寅", "癸未"]
LIUXIU_MAP = ["丙午", "丁未", "戊子", "戊午", "己丑", "己未"]
BAZHUAN_MAP = ["甲寅", "乙卯", "丁未", "戊戌", "己未", "庚申", "辛酉", "癸丑"]
JIUCHOU_MAP = ["丁酉", "戊子", "戊午", "己卯", "己酉", "辛卯", "辛酉", "壬子", "壬午"]

TIANCHUGUIREN_MAP = {
    "甲": "巳",
    "乙": "午",
    "丙": "巳",
    "丁": "午",
    "戊": "申",
    "己": "酉",
    "庚": "亥",
    "辛": "子",
    "壬": "寅",
    "癸": "卯",
}

FUXINGGUIREN_MAP = {
    "甲": "寅子",
    "乙": "卯丑",
    "丙": "寅子",
    "丁": "亥",
    "戊": "申",
    "己": "未",
    "庚": "午",
    "辛": "巳",
    "壬": "辰",
    "癸": "卯丑",
}

DEXIUGUIREN_MAP = {
    "寅午戌": "丙丁戊癸",
    "申子辰": "壬癸戊丙辛甲己",
    "巳酉丑": "庚辛乙",
    "亥卯未": "甲乙丁壬",
}

GONGLU_MAP = {
    "癸亥": "癸丑",
    "癸丑": "癸亥",
    "丁巳": "丁未",
    "己未": "己巳",
    "戊辰": "戊午",
}

TIANGUANGUIREN_MAP = {
    "甲": "未",
    "乙": "辰",
    "丙": "巳",
    "丁": "酉",
    "戊": "戌",
    "己": "卯",
    "庚": "丑",
    "辛": "申",
    "壬": "寅",
    "癸": "午",
}

PITOU_MAP = {
    "子": "辰",
    "丑": "卯",
    "寅": "寅",
    "卯": "丑",
    "辰": "子",
    "巳": "亥",
    "午": "戌",
    "未": "酉",
    "申": "申",
    "酉": "未",
    "戌": "午",
    "亥": "巳",
}

LIUER_MAP = {
    "寅": "酉",
    "午": "酉",
    "戌": "酉",
    "申": "卯",
    "子": "卯",
    "辰": "卯",
    "亥": "午",
    "卯": "午",
    "未": "午",
    "巳": "子",
    "酉": "子",
    "丑": "子",
}

JINSHENX_MAP = ["甲子", "甲午", "己卯", "己酉"]

GEJIAOSHA_MAP = {
    "子": "寅",
    "丑": "卯",
    "寅": "辰",
    "卯": "巳",
    "辰": "午",
    "巳": "未",
    "午": "申",
    "未": "酉",
    "申": "戌",
    "酉": "亥",
    "戌": "子",
    "亥": "丑",
}


def grab_tianyiguiren(day_gan: str, year_gan: str, zhi: str) -> str | None:
    if zhi in TIANYIGUIREN_MAP[day_gan] or zhi in TIANYIGUIREN_MAP[year_gan]:
        return "天乙贵人"
    return None


def grab_tiandeguiren(month_zhi: str, ganzhi: str) -> str | None:
    if TIANDEGUIREN_MAP[month_zhi] in ganzhi:
        return "天德贵人"
    return None


def grab_yuedeguiren(month_zhi: str, ganzhi: str) -> str | None:
    if YUEDEGUIREN_MAP[month_zhi] in ganzhi:
        return "月德贵人"
    return None


def grab_tiandehe(month_zhi: str, ganzhi: str) -> str | None:
    if TIANDEHE_MAP[month_zhi] in ganzhi:
        return "天德合"
    return None


def grab_yuedehe(month_zhi: str, gan: str) -> str | None:
    if YUEDEHE_MAP[month_zhi] == gan:
        return "月德合"
    return None


def grab_tiansheri(month_zhi: str, day_ganzhi: str) -> str | None:
    if TIANSHERI_MAP[month_zhi] == day_ganzhi:
        return "天赦星"
    return None


def grab_lushen(day_gan: str, zhi: str) -> str | None:
    if LUSHEN_MAP[day_gan] == zhi:
        return "禄神"
    return None


def grab_yima(year_or_day_zhi: str, rest_zhi: str) -> str | None:
    if YIMA_MAP[year_or_day_zhi] == rest_zhi:
        return "驿马"
    return None


def grab_taijiguiren(day_gan: str, year_gan: str, zhi: str) -> str | None:
    if zhi in TAIJIGUIREN_MAP[day_gan] or zhi in TAIJIGUIREN_MAP[year_gan]:
        return "太极贵人"
    return None


def grab_jiangxing(year_or_day_zhi: str, rest_zhi: str) -> str | None:
    if JIANGXING_MAP[year_or_day_zhi] == rest_zhi:
        return "将星"
    return None


def grab_xuetang(year_nayin: str, day_gan: str, ganzhi: str) -> str | None:
    if XUETANG_MAP[year_nayin] == ganzhi[1] or XUETANG_MAP[day_gan] == ganzhi:
        return "学堂"
    return None


def grab_ciguan(year_nayin: str, day_gan: str, ganzhi: str) -> str | None:
    if CIGUAN_MAP[year_nayin] == ganzhi[1] or CIGUAN_MAP[day_gan] == ganzhi:
        return "词馆"
    return None


def grab_guoyinguiren(day_gan: str, year_gan: str, zhi: str) -> str | None:
    if GUOYINGUIREN_MAP[day_gan] == zhi or GUOYINGUIREN_MAP[year_gan] == zhi:
        return "国印"
    return None


def grab_sanqiguiren(bazi: str) -> str | None:
    import re

    for combo in SANQIGUIREN_MAP:
        if re.search(combo, bazi):
            return "三奇贵人"
    return None


def grab_wenchangguiren(day_gan: str, year_gan: str, zhi: str) -> str | None:
    if WENCHANGGUIREN_MAP[day_gan] == zhi or WENCHANGGUIREN_MAP[year_gan] == zhi:
        return "文昌贵人"
    return None


def grab_huagai(year_or_day_zhi: str, rest_zhi: str) -> str | None:
    if HUAGAI_MAP[year_or_day_zhi] == rest_zhi:
        return "华盖"
    return None


def grab_tianyi(month_zhi: str, rest_zhi: str) -> str | None:
    if TIANYI_MAP[month_zhi] == rest_zhi:
        return "天医星"
    return None


def grab_jinyu(year_gan: str, day_gan: str, zhi: str) -> str | None:
    if JINYU_MAP[year_gan] == zhi or JINYU_MAP[day_gan] == zhi:
        return "金舆"
    return None


def grab_kongwang(year_or_day_xun: str, rest_zhi: str) -> str | None:
    if rest_zhi in KONGWANG_MAP[year_or_day_xun]:
        return "空亡"
    return None


def grab_zaisha(year_zhi: str, rest_zhi: str) -> str | None:
    if ZAISHA_MAP[year_zhi] == rest_zhi:
        return "灾煞"
    return None


def grab_jiesha(year_or_day_zhi: str, rest_zhi: str) -> str | None:
    if JIESHA_MAP[year_or_day_zhi] == rest_zhi:
        return "劫煞"
    return None


def grab_wangshen(year_or_day_zhi: str, rest_zhi: str) -> str | None:
    if WANGSHEN_MAP[year_or_day_zhi] == rest_zhi:
        return "亡神"
    return None


def grab_yangren(day_gan: str, zhi: str) -> str | None:
    if YANGREN_MAP[day_gan] == zhi:
        return "羊刃"
    return None


def grab_feiren(day_gan: str, zhi: str) -> str | None:
    if FEIREN_MAP[day_gan] == zhi:
        return "飞刃"
    return None


def grab_xueren(month_zhi: str, zhi: str) -> str | None:
    if XUEREN_MAP[month_zhi] == zhi:
        return "血刃"
    return None


def grab_liuxia(day_gan: str, zhi: str) -> str | None:
    if LIUXIA_MAP[day_gan] == zhi:
        return "流霞"
    return None


def grab_sifeiri(month_zhi: str, day_ganzhi: str) -> str | None:
    if day_ganzhi in SIFEIRI_MAP[month_zhi]:
        return "四废"
    return None


def grab_tianluodiwang2(year_nayin: str, day_zhi: str) -> str | None:
    if year_nayin == "火":
        if day_zhi in ("戌", "亥"):
            return "天罗地网"
    elif year_nayin in ("水", "土"):
        if day_zhi in ("辰", "巳"):
            return "天罗地网"
    return None


def grab_tianluodiwang1(year_or_day_zhi: str, rest_zhi: str) -> str | None:
    if year_or_day_zhi + rest_zhi in TIANLUODIWANG_MAP:
        return "天罗地网"
    return None


def grab_taohua(year_or_day_zhi: str, rest_zhi: str) -> str | None:
    if TAOHUA_MAP[year_or_day_zhi] == rest_zhi:
        return "桃花"
    return None


def grab_guchen(year_zhi: str, rest_zhi: str) -> str | None:
    if GUCHEN_MAP[year_zhi] == rest_zhi:
        return "孤辰"
    return None


def grab_guasu(year_zhi: str, rest_zhi: str) -> str | None:
    if GUASU_MAP[year_zhi] == rest_zhi:
        return "寡宿"
    return None


def grab_yinchayangcuo(day_ganzhi: str) -> str | None:
    if day_ganzhi in YINCHAYANGCUO_MAP:
        return "阴差阳错"
    return None


def grab_kuigang(day_ganzhi: str) -> str | None:
    if day_ganzhi in KUIGANG_MAP:
        return "魁罡"
    return None


def grab_guluan(day_ganzhi: str) -> str | None:
    if day_ganzhi in GULUAN_MAP:
        return "孤鸾"
    return None


def grab_hongluan(year_zhi: str, rest_zhi: str) -> str | None:
    if HONGLUAN_MAP[year_zhi] == rest_zhi:
        return "红鸾"
    return None


def grab_tianxi(year_zhi: str, rest_zhi: str) -> str | None:
    if TIANXI_MAP[year_zhi] == rest_zhi:
        return "天喜"
    return None


def grab_goujiaosha(year_zhi: str, rest_zhi: str) -> str | None:
    if GOUJIAOSHA_MAP[year_zhi] == rest_zhi:
        return "勾绞煞"
    return None


def grab_hongyan(day_gan: str, zhi: str) -> str | None:
    if HONGYAN_MAP[day_gan] == zhi:
        return "红艳"
    return None


def grab_shiedabai(day_ganzhi: str) -> str | None:
    if day_ganzhi in SHIEDABAI_MAP:
        return "十恶大败"
    return None


def grab_yuanchen(year_yinyang: YinYang, year_zhi: str, gender_yinyang: YinYang, rest_zhi: str) -> str | None:
    key = "同" if year_yinyang == gender_yinyang else "异"
    if YUANCHEN_MAP[key][year_zhi] == rest_zhi:
        return "元辰"
    return None


def grab_jinshen(day_or_hour_ganzhi: str) -> str | None:
    if day_or_hour_ganzhi in JINSHEN_MAP:
        return "金神"
    return None


def grab_tianzhuan(month_zhi: str, day_ganzhi: str) -> str | None:
    if TIANZHUAN_MAP[month_zhi] == day_ganzhi:
        return "天转"
    return None


def grab_dizhuan(month_zhi: str, day_ganzhi: str) -> str | None:
    if DIZHUAN_MAP[month_zhi] == day_ganzhi:
        return "地转"
    return None


def grab_sangmen(year_zhi: str, rest_zhi: str) -> str | None:
    if SANGMEN_MAP[year_zhi] == rest_zhi:
        return "丧门"
    return None


def grab_diaoke(year_zhi: str, rest_zhi: str) -> str | None:
    if DIAOKE_MAP[year_zhi] == rest_zhi:
        return "吊客"
    return None


def grab_pima(year_zhi: str, rest_zhi: str) -> str | None:
    if PIMA_MAP[year_zhi] == rest_zhi:
        return "披麻"
    return None


def grab_pitou(year_zhi: str, rest_zhi: str) -> str | None:
    if PITOU_MAP[year_zhi] == rest_zhi:
        return "披头"
    return None


def grab_liuer(year_zhi: str, rest_zhi: str) -> str | None:
    if LIUER_MAP[year_zhi] == rest_zhi:
        return "六厄"
    return None


def grab_shiling(day_ganzhi: str) -> str | None:
    if day_ganzhi in SHILING_MAP:
        return "十灵"
    return None


def grab_liuxiu(day_ganzhi: str) -> str | None:
    if day_ganzhi in LIUXIU_MAP:
        return "六秀"
    return None


def grab_bazhuan(day_ganzhi: str) -> str | None:
    if day_ganzhi in BAZHUAN_MAP:
        return "八专"
    return None


def grab_jiuchou(day_ganzhi: str) -> str | None:
    if day_ganzhi in JIUCHOU_MAP:
        return "九丑"
    return None


def grab_tongzisha(month_zhi: str, year_nayin: str, rest_zhi: str) -> str | None:
    if month_zhi in "寅卯辰申酉戌":
        if rest_zhi in ("寅", "子"):
            return "童子煞"
    elif month_zhi in "巳午未亥子丑":
        if rest_zhi in ("卯", "未", "辰"):
            return "童子煞"
    if year_nayin in ("金", "木"):
        if rest_zhi in ("午", "卯"):
            return "童子煞"
    elif year_nayin in ("水", "火"):
        if rest_zhi in ("酉", "戌"):
            return "童子煞"
    elif year_nayin == "土":
        if rest_zhi in ("辰", "巳"):
            return "童子煞"
    return None


def grab_tianchuguiren(year_gan: str, day_gan: str, rest_zhi: str) -> str | None:
    if TIANCHUGUIREN_MAP[year_gan] == rest_zhi or TIANCHUGUIREN_MAP[day_gan] == rest_zhi:
        return "天厨贵人"
    return None


def grab_fuxingguiren(year_gan: str, day_gan: str, zhi: str) -> str | None:
    if zhi in FUXINGGUIREN_MAP[year_gan] or zhi in FUXINGGUIREN_MAP[day_gan]:
        return "福星贵人"
    return None


def grab_dexiuguiren(month_zhi: str, gan: str) -> str | None:
    for key, value in DEXIUGUIREN_MAP.items():
        if month_zhi in key and gan in value:
            return "德秀贵人"
    return None


def grab_gonglu(day_ganzhi: str, hour_ganzhi: str) -> str | None:
    if GONGLU_MAP.get(day_ganzhi) == hour_ganzhi:
        return "拱禄"
    return None


def grab_tianguanguiren(day_gan: str, year_gan: str, zhi: str) -> str | None:
    if TIANGUANGUIREN_MAP[year_gan] == zhi or TIANGUANGUIREN_MAP[day_gan] == zhi:
        return "天官贵人"
    return None


def grab_jinshenx(day_ganzhi: str) -> str | None:
    if day_ganzhi in JINSHENX_MAP:
        return "进神"
    return None


def grab_gejiaosha(day_zhi: str, hour_zhi: str) -> str | None:
    if GEJIAOSHA_MAP[day_zhi] == hour_zhi:
        return "隔角煞"
    return None
