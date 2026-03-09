from __future__ import annotations  # 用于前向引用

from enum import Enum
from typing import ClassVar, Dict, List, Self

from divicast.base.symbol import ValuedMultiton
from divicast.entities.wuxing import Wuxing, YinYang


class Shishen(ValuedMultiton):
    """
    十神
    """

    BiJian = (0, "比肩")
    JieCai = (1, "劫财")
    ShiShen = (2, "食神")
    ShangGuan = (3, "伤官")
    PianCai = (4, "偏财")
    ZhengCai = (5, "正财")
    QiSha = (6, "七杀")  # 也叫偏官
    ZhengGuan = (7, "正官")
    PianYin = (8, "偏印")  # 也叫枭神
    ZhengYin = (9, "正印")


class Tiangan(ValuedMultiton):
    """
    天干
    """

    Jia = (0, "甲")
    Yi = (1, "乙")
    Bing = (2, "丙")
    Ding = (3, "丁")
    Wu = (4, "戊")
    Ji = (5, "己")
    Geng = (6, "庚")
    Xin = (7, "辛")
    Ren = (8, "壬")
    Gui = (9, "癸")

    def get_shishen(self, other: Self) -> Shishen:
        """
        获取对应的十神
        """
        if self.belongs_to(Wuxing) == other.belongs_to(Wuxing):
            # 同五行
            return (
                Shishen.BiJian
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.JieCai  # type: ignore
            )
        elif self.belongs_to(Wuxing).generate() == other.belongs_to(Wuxing):
            # 我生对方
            return (
                Shishen.ShiShen
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.ShangGuan  # type: ignore
            )
        elif self.belongs_to(Wuxing).restrain() == other.belongs_to(Wuxing):
            # 我克对方
            return (
                Shishen.PianCai
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.ZhengCai  # type: ignore
            )
        elif self.belongs_to(Wuxing) == other.belongs_to(Wuxing).restrain():
            # 对方克我
            return (
                Shishen.QiSha
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.ZhengGuan  # type: ignore
            )
        elif self.belongs_to(Wuxing) == other.belongs_to(Wuxing).generate():
            # 对方生我
            return (
                Shishen.PianYin
                if self.belongs_to(YinYang) == other.belongs_to(YinYang)
                else Shishen.ZhengYin  # type: ignore
            )
        else:
            raise ValueError("无法计算对应的十神关系")

    def get_twelve_zhangsheng(self, zhi: Dizhi) -> TwelveZhangsheng:
        """
        获取对应的十二长生
        """
        CHANGSHENG_START_BRANCH = {
            0: 11,  # 甲 in 亥
            1: 6,  # 乙 in 午
            2: 2,  # 丙 in 寅
            3: 9,  # 丁 in 酉
            4: 2,  # 戊 in 寅
            5: 9,  # 己 in 酉
            6: 5,  # 庚 in 巳
            7: 0,  # 辛 in 子
            8: 8,  # 壬 in 申
            9: 3,  # 癸 in 卯
        }
        start_branch_index = CHANGSHENG_START_BRANCH[self.num]
        if self.belongs_to(YinYang) == YinYang.Yang:
            # 阳干顺行
            changsheng_index = (zhi.num - start_branch_index + 12) % 12
        else:
            # 阴干逆行
            changsheng_index = (start_branch_index - zhi.num + 12) % 12

        return TwelveZhangsheng(changsheng_index)


Tiangan._BELONGS_TO = {
    Wuxing: {
        Tiangan.Jia: Wuxing.Wood,
        Tiangan.Yi: Wuxing.Wood,
        Tiangan.Bing: Wuxing.Fire,
        Tiangan.Ding: Wuxing.Fire,
        Tiangan.Wu: Wuxing.Earth,
        Tiangan.Ji: Wuxing.Earth,
        Tiangan.Geng: Wuxing.Metal,
        Tiangan.Xin: Wuxing.Metal,
        Tiangan.Ren: Wuxing.Water,
        Tiangan.Gui: Wuxing.Water,
    },
    YinYang: lambda x: YinYang((x.num + 1) % 2),
}


class CangganType(Enum):
    """地支藏干类型"""

    MAIN = "main"  # 本气
    SECONDARY = "secondary"  # 余气
    MIDDLE = "middle"  # 中气


class TwelveZhangsheng(ValuedMultiton):
    """
    十二长生
    """

    ZhangSheng = (0, "长生")
    MuYu = (1, "沐浴")
    GuanDai = (2, "冠带")
    LinGuan = (3, "临官")
    DiWang = (4, "帝旺")
    Shuai = (5, "衰")
    Bing = (6, "病")
    Si = (7, "死")
    Mu = (8, "墓")
    Jue = (9, "绝")
    Tai = (10, "胎")
    Yang = (11, "养")


class Canggan:
    """地支藏干"""

    gan: Tiangan  # 干
    canggan_type: CangganType  # 藏干类型

    def __init__(self, gan: Tiangan, canggan_type: CangganType):
        self.gan = gan
        self.canggan_type = canggan_type

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Canggan):
            return NotImplemented
        return self.gan == other.gan and self.canggan_type == other.canggan_type


class Dizhi(ValuedMultiton):
    """
    地支
    """

    Zi = (0, "子")
    Chou = (1, "丑")
    Yin = (2, "寅")
    Mou = (3, "卯")
    Chen = (4, "辰")
    Si = (5, "巳")
    Wu = (6, "午")
    Wei = (7, "未")
    Shen = (8, "申")
    You = (9, "酉")
    Xu = (10, "戌")
    Hai = (11, "亥")

    def is_chong(self, d: Dizhi) -> bool:
        """判断地支相冲"""
        return abs(self.num - d.num) == 6

    def chong(self) -> Dizhi:
        """返回相冲的地支"""
        return Dizhi((self.num + 6) % 12)

    def is_he(self, d: Dizhi) -> bool:
        """判断地支相合"""
        return (self.num + d.num) % 12 == 1

    def he(self) -> Dizhi:
        """返回相合的地支"""
        return Dizhi((13 - self.num) % 12)

    def generate(self) -> List[Dizhi]:
        r = []
        w = self.belongs_to(Wuxing).generate()
        for d in self.all():
            if d.belongs_to(Wuxing) == w:
                r.append(d)
        return r

    def restrain(self) -> List[Dizhi]:
        r = []
        w = self.belongs_to(Wuxing).restrain()
        for d in self.all():
            if d.belongs_to(Wuxing) == w:
                r.append(d)
        return r

    def chinese_zodiac(self) -> str:
        """返回地支对应的生肖"""
        zodiacs = [
            "鼠",  # 子
            "牛",  # 丑
            "虎",  # 寅
            "兔",  # 卯
            "龙",  # 辰
            "蛇",  # 巳
            "马",  # 午
            "羊",  # 未
            "猴",  # 申
            "鸡",  # 酉
            "狗",  # 戌
            "猪",  # 亥
        ]
        return zodiacs[self.num]

    def canggan(self) -> List[Canggan]:
        """地址藏干"""
        canggan_map: dict[Dizhi, List[Canggan]] = {
            Dizhi.Zi: [Canggan(Tiangan.Gui, CangganType.MAIN)],
            Dizhi.Chou: [
                Canggan(Tiangan.Ji, CangganType.MAIN),
                Canggan(Tiangan.Xin, CangganType.MIDDLE),
                Canggan(Tiangan.Gui, CangganType.SECONDARY),
            ],
            Dizhi.Yin: [
                Canggan(Tiangan.Jia, CangganType.MAIN),
                Canggan(Tiangan.Bing, CangganType.MIDDLE),
                Canggan(Tiangan.Wu, CangganType.SECONDARY),
            ],
            Dizhi.Mou: [Canggan(Tiangan.Yi, CangganType.MAIN)],
            Dizhi.Chen: [
                Canggan(Tiangan.Wu, CangganType.MAIN),
                Canggan(Tiangan.Gui, CangganType.MIDDLE),
                Canggan(Tiangan.Yi, CangganType.SECONDARY),
            ],
            Dizhi.Si: [
                Canggan(Tiangan.Bing, CangganType.MAIN),
                Canggan(Tiangan.Geng, CangganType.MIDDLE),
                Canggan(Tiangan.Wu, CangganType.SECONDARY),
            ],
            Dizhi.Wu: [Canggan(Tiangan.Ding, CangganType.MAIN), Canggan(Tiangan.Ji, CangganType.MIDDLE)],
            Dizhi.Wei: [
                Canggan(Tiangan.Ji, CangganType.MAIN),
                Canggan(Tiangan.Yi, CangganType.MIDDLE),
                Canggan(Tiangan.Ding, CangganType.SECONDARY),
            ],
            Dizhi.Shen: [
                Canggan(Tiangan.Geng, CangganType.MAIN),
                Canggan(Tiangan.Ren, CangganType.MIDDLE),
                Canggan(Tiangan.Wu, CangganType.SECONDARY),
            ],
            Dizhi.You: [Canggan(Tiangan.Xin, CangganType.MAIN)],
            Dizhi.Xu: [
                Canggan(Tiangan.Wu, CangganType.MAIN),
                Canggan(Tiangan.Ding, CangganType.MIDDLE),
                Canggan(Tiangan.Xin, CangganType.SECONDARY),
            ],
            Dizhi.Hai: [Canggan(Tiangan.Ren, CangganType.MAIN), Canggan(Tiangan.Jia, CangganType.MIDDLE)],
        }
        return canggan_map[self]


Dizhi._BELONGS_TO = {
    Wuxing: {
        Dizhi.Zi: Wuxing.Water,
        Dizhi.Chou: Wuxing.Earth,
        Dizhi.Yin: Wuxing.Wood,
        Dizhi.Mou: Wuxing.Wood,
        Dizhi.Chen: Wuxing.Earth,
        Dizhi.Si: Wuxing.Fire,
        Dizhi.Wu: Wuxing.Fire,
        Dizhi.Wei: Wuxing.Earth,
        Dizhi.Shen: Wuxing.Metal,
        Dizhi.You: Wuxing.Metal,
        Dizhi.Xu: Wuxing.Earth,
        Dizhi.Hai: Wuxing.Water,
    },
    YinYang: lambda x: YinYang((x.num + 1) % 2),
}


class SixtyJiazi:
    gan: Tiangan
    zhi: Dizhi

    def __init__(self, gan: Tiangan, zhi: Dizhi):
        self.gan = gan
        self.zhi = zhi

    def get_nayin(self) -> Nayin:
        index = ((6 - ((self.zhi.num - self.gan.num) % 12) // 2) * 10 + self.gan.num) % 60
        return Nayin(index // 2)

    def get_kongwang(self) -> tuple[Dizhi, Dizhi]:
        return (
            Dizhi((self.zhi.num - self.gan.num - 2) % 12),
            Dizhi((self.zhi.num - self.gan.num - 1) % 12),
        )


class Nayin(ValuedMultiton):
    """
    纳音
    """

    HaiZhongJin = (0, "海中金")
    LuZhongHuo = (1, "炉中火")
    DaLinMu = (2, "大林木")
    LuPangTu = (3, "路旁土")
    JianFengjin = (4, "剑锋金")
    ShanTouHuo = (5, "山头火")
    DongXiaShui = (6, "洞下水")
    ChengQiangTu = (7, "城墙土")
    BaiLajin = (8, "白蜡金")
    YangLiuMu = (9, "杨柳木")
    QuanZhongShui = (10, "泉中水")
    WuShangTu = (11, "屋上土")
    PiLiHuo = (12, "霹雳火")
    SongBaiMu = (13, "松柏木")
    ChangLiuShui = (14, "长流水")
    ShaZhongJin = (15, "沙中金")
    ShanXiaHuo = (16, "山下火")
    PingDiMu = (17, "平地木")
    BiShanTu = (18, "壁上土")
    JinBoJin = (19, "金箔金")
    FoDengHuo = (20, "佛灯火")
    TianHeShui = (21, "天河水")
    DaYiTu = (22, "大驿土")
    ChaiShanJin = (23, "钗钐金")
    SangSongMu = (24, "桑松木")
    DaXiShui = (25, "大溪水")
    ShaZhongTu = (26, "沙中土")
    TianShangHuo = (27, "天上火")
    ShiLiuMu = (28, "石榴木")
    DaHaiShui = (29, "大海水")


Nayin._BELONGS_TO = {
    Wuxing: {
        Nayin.HaiZhongJin: Wuxing.Metal,
        Nayin.LuZhongHuo: Wuxing.Fire,
        Nayin.DaLinMu: Wuxing.Wood,
        Nayin.LuPangTu: Wuxing.Earth,
        Nayin.JianFengjin: Wuxing.Metal,
        Nayin.ShanTouHuo: Wuxing.Fire,
        Nayin.DongXiaShui: Wuxing.Water,
        Nayin.ChengQiangTu: Wuxing.Earth,
        Nayin.BaiLajin: Wuxing.Metal,
        Nayin.YangLiuMu: Wuxing.Wood,
        Nayin.QuanZhongShui: Wuxing.Water,
        Nayin.WuShangTu: Wuxing.Earth,
        Nayin.PiLiHuo: Wuxing.Fire,
        Nayin.SongBaiMu: Wuxing.Wood,
        Nayin.ChangLiuShui: Wuxing.Water,
        Nayin.ShaZhongJin: Wuxing.Metal,
        Nayin.ShanXiaHuo: Wuxing.Fire,
        Nayin.PingDiMu: Wuxing.Wood,
        Nayin.BiShanTu: Wuxing.Earth,
        Nayin.JinBoJin: Wuxing.Metal,
        Nayin.FoDengHuo: Wuxing.Fire,
        Nayin.TianHeShui: Wuxing.Water,
        Nayin.DaYiTu: Wuxing.Earth,
        Nayin.ChaiShanJin: Wuxing.Metal,
        Nayin.SangSongMu: Wuxing.Wood,
        Nayin.DaXiShui: Wuxing.Water,
        Nayin.ShaZhongTu: Wuxing.Earth,
        Nayin.TianShangHuo: Wuxing.Fire,
        Nayin.ShiLiuMu: Wuxing.Wood,
        Nayin.DaHaiShui: Wuxing.Water,
    }
}
