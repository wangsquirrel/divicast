import datetime
from typing import Self, Type, TypeVar

from tyme4py import (AbstractTyme, eightchar, enums, lunar,  # type: ignore
                     sixtycycle, solar)

from ..base.symbol import ValuedMultiton
from ..entities.daemon import Daemon
from ..entities.ganzhi import (Canggan, Dizhi, Nayin, Shishen, SixtyJiazi,
                               Tiangan, TwelveZhangsheng)

Gender = enums.Gender


class ZhuInfo(object):
    '''柱的命盘信息, 可以是年柱, 月柱, 日柱, 时柱'''
    gan: Tiangan
    zhi: Dizhi

    sixty_jiazi: SixtyJiazi  # 六十甲子
    zhuxing: Shishen  # 主星
    canggan: list[Canggan]  # 藏干
    fuxing: list[Shishen]  # 副星
    xingyun: TwelveZhangsheng  # 星运
    zizuo: TwelveZhangsheng  # 自坐
    kongwang: tuple[Dizhi, Dizhi]  # 空亡
    nayin: Nayin  # 纳音
    shensha: list[Daemon]  # 神煞

    tiangan_relations: str  # 天干关系
    dizhi_relations: str  # 地支关系

    def __init__(self, ganzhi: str) -> None:
        self.gan = Tiangan.from_chinese_name(ganzhi[0])
        self.zhi = Dizhi.from_chinese_name(ganzhi[1])
        self.sixty_jiazi = SixtyJiazi(self.gan, self.zhi)


class BirthChart(object):

    _bazi: lunar.EightChar
    _solar_time: solar.SolarTime
    _child_limit: eightchar.ChildLimit
    _birth_solar: datetime.datetime
    _gender: Gender

    # Additional attributes for a complete birth chart can be added here
    kongwang: tuple[Dizhi, Dizhi]
    chinese_zodiac: str  # 生肖
    sign: str  # 星座
    taiyuan: str  # 胎元
    shengong: str  # 身宫
    minggua: str  # 命卦
    term: solar.SolarTermDay

    # 四柱
    yearzhu: ZhuInfo
    monthzhu: ZhuInfo
    dayzhu: ZhuInfo
    bihourzhu: ZhuInfo

    def __init__(self, birth_solar: datetime.datetime, gender: Gender) -> None:
        '''命盘初始化，只包括八字，没有完整的盘面信息'''
        self._birth_solar = birth_solar
        self._gender = gender
        self._solar_time = solar.SolarTime.from_ymd_hms(
            birth_solar.year, birth_solar.month, birth_solar.day, birth_solar.hour, birth_solar.minute, birth_solar.second
        )
        self._bazi = self._solar_time.get_lunar_hour().get_eight_char()
        self._child_limit = eightchar.ChildLimit(
            self._solar_time,
            gender
        )

    @classmethod
    def create(cls, dt: datetime.datetime, gender: Gender) -> Self:
        """创建命盘"""
        bc = cls(dt, gender)
        bc.assemble()
        return bc

    def assemble(self) -> None:
        self.yearzhu = ZhuInfo(self._bazi.get_year().get_name())
        self.monthzhu = ZhuInfo(self._bazi.get_month().get_name())
        self.dayzhu = ZhuInfo(self._bazi.get_day().get_name())
        self.bihourzhu = ZhuInfo(self._bazi.get_hour().get_name())

        self.kongwang = self.dayzhu.sixty_jiazi.get_kongwang()
        self.chinese_zodiac = self.yearzhu.zhi.chinese_zodiac()
        self.sign = solar.SolarDay.from_ymd(
            self._birth_solar.year, self._birth_solar.month, self._birth_solar.day
        ).get_constellation().get_name()
        self.term = self._solar_time.get_solar_day().get_term_day()

        self.taiyuan = self._bazi.get_fetal_origin().get_name()
        self.shengong = self._bazi.get_body_sign().get_name()

        for zhu in [self.yearzhu, self.monthzhu, self.dayzhu, self.bihourzhu]:
            zhu.canggan = zhu.zhi.canggan()
            zhu.zhuxing = self.dayzhu.gan.get_shishen(zhu.gan)
            zhu.fuxing = [self.dayzhu.gan.get_shishen(
                canggan.gan) for canggan in zhu.canggan]

            zhu.xingyun = self.dayzhu.gan.get_twelve_zhangsheng(zhu.zhi)
            zhu.zizuo = zhu.gan.get_twelve_zhangsheng(zhu.zhi)
            zhu.kongwang = zhu.sixty_jiazi.get_kongwang()
            zhu.nayin = zhu.sixty_jiazi.get_nayin()
            # 计算神煞
            # 基于日干日支与当前柱的干支关系来计算常见神煞
            zhu.shensha = get_daemon(
                self.dayzhu.gan, self.dayzhu.zhi, zhu.gan, zhu.zhi)
            zhu.canggan = zhu.zhi.canggan()

            zhu.tiangan_relations = ''  # TODO: implement tiangan relations calculation
            zhu.dizhi_relations = ''  # TODO: implement dizhi relations calculation


def get_daemon(self_gan: Tiangan, self_zhi: Dizhi, other_gan: Tiangan, other_zhi: Dizhi) -> list[Daemon]:
    """
    获取神煞 TODO: 有问题
    """
    res: list[Daemon] = []

    # 参考 src/divicast/sixline/divinatory_symbol.py 中的规则
    # 天乙贵人（按日干）
    tianyiguiren_map = {
        0: (Dizhi.Chou, Dizhi.Wei),
        1: (Dizhi.Zi, Dizhi.Shen),
        2: (Dizhi.Hai, Dizhi.You),
        3: (Dizhi.Hai, Dizhi.You),
        4: (Dizhi.Chou, Dizhi.Wei),
        5: (Dizhi.Zi, Dizhi.Shen),
        6: (Dizhi.Wu, Dizhi.Yin),
        7: (Dizhi.Wu, Dizhi.Yin),
        8: (Dizhi.Mou, Dizhi.Si),
        9: (Dizhi.Mou, Dizhi.Si),
    }
    day_gan_num = self_gan.num
    tianyis = tianyiguiren_map.get(day_gan_num, ())
    if other_zhi in tianyis:
        res.append(Daemon.Tianyiguiren)

    # 桃花（按日支）
    if self_zhi in [Dizhi.Shen, Dizhi.Zi, Dizhi.Chen] and other_zhi == Dizhi.You:
        res.append(Daemon.Taohua)
    if self_zhi in [Dizhi.Si, Dizhi.You, Dizhi.Chou] and other_zhi == Dizhi.Wu:
        res.append(Daemon.Taohua)
    if self_zhi in [Dizhi.Hai, Dizhi.Mou, Dizhi.Wei] and other_zhi == Dizhi.Zi:
        res.append(Daemon.Taohua)
    if self_zhi in [Dizhi.Yin, Dizhi.Wu, Dizhi.Xu] and other_zhi == Dizhi.Mou:
        res.append(Daemon.Taohua)

    # 文昌（按日干对应地支）
    wenchang_map = {
        Tiangan.Jia: Dizhi.Si,
        Tiangan.Yi: Dizhi.Wu,
        Tiangan.Bing: Dizhi.Shen,
        Tiangan.Wu: Dizhi.Shen,
        Tiangan.Geng: Dizhi.Hai,
        Tiangan.Xin: Dizhi.Zi,
        Tiangan.Ding: Dizhi.You,
        Tiangan.Ji: Dizhi.You,
        Tiangan.Ren: Dizhi.Yin,
        Tiangan.Gui: Dizhi.Mou,
    }
    if other_zhi == wenchang_map.get(self_gan):
        res.append(Daemon.Wenchang)

    # 禄神
    lushen_map = {
        Tiangan.Jia: Dizhi.Yin,
        Tiangan.Yi: Dizhi.Mou,
        Tiangan.Bing: Dizhi.Si,
        Tiangan.Wu: Dizhi.Si,
        Tiangan.Geng: Dizhi.Shen,
        Tiangan.Xin: Dizhi.You,
        Tiangan.Ding: Dizhi.Wu,
        Tiangan.Ji: Dizhi.Wu,
        Tiangan.Ren: Dizhi.Hai,
        Tiangan.Gui: Dizhi.Zi,
    }
    if other_zhi == lushen_map.get(self_gan):
        res.append(Daemon.Lushen)

    # 劫煞（按日支） - 使用六爻实现中的表
    jiesha_map = {
        Dizhi.Shen: Dizhi.Si,
        Dizhi.Zi: Dizhi.Si,
        Dizhi.Chen: Dizhi.Si,
        Dizhi.Hai: Dizhi.Shen,
        Dizhi.Mou: Dizhi.Shen,
        Dizhi.Wei: Dizhi.Shen,
        Dizhi.Yin: Dizhi.Hai,
        Dizhi.Wu: Dizhi.Hai,
        Dizhi.Xu: Dizhi.Hai,
        Dizhi.Si: Dizhi.Yin,
        Dizhi.You: Dizhi.Yin,
        Dizhi.Chou: Dizhi.Yin,
    }
    if other_zhi == jiesha_map.get(self_zhi):
        res.append(Daemon.Jiesha)

    # 将星
    jiang_map = {
        Dizhi.Shen: Dizhi.Zi,
        Dizhi.Zi: Dizhi.Zi,
        Dizhi.Chen: Dizhi.Zi,
        Dizhi.Si: Dizhi.You,
        Dizhi.You: Dizhi.You,
        Dizhi.Chou: Dizhi.You,
        Dizhi.Yin: Dizhi.Wu,
        Dizhi.Wu: Dizhi.Wu,
        Dizhi.Xu: Dizhi.Wu,
        Dizhi.Hai: Dizhi.Mou,
        Dizhi.Mou: Dizhi.Mou,
        Dizhi.Wei: Dizhi.Mou,
    }
    if other_zhi == jiang_map.get(self_zhi):
        res.append(Daemon.Jiangxing)

    # 阳刃（按日干）
    yangren_map = {
        Tiangan.Jia: Dizhi.Mou,
        Tiangan.Yi: Dizhi.Yin,
        Tiangan.Bing: Dizhi.Wu,
        Tiangan.Wu: Dizhi.Wu,
        Tiangan.Geng: Dizhi.You,
        Tiangan.Xin: Dizhi.Shen,
        Tiangan.Ding: Dizhi.Si,
        Tiangan.Ji: Dizhi.Si,
        Tiangan.Ren: Dizhi.Zi,
        Tiangan.Gui: Dizhi.Hai,
    }
    if other_zhi == yangren_map.get(self_gan):
        res.append(Daemon.Yangren)

    # 灾煞（按日支） - 使用六爻表
    zaisha_map = {
        Dizhi.Shen: Dizhi.Wu,
        Dizhi.Zi: Dizhi.Wu,
        Dizhi.Chen: Dizhi.Wu,
        Dizhi.Si: Dizhi.Mou,
        Dizhi.You: Dizhi.Mou,
        Dizhi.Chou: Dizhi.Mou,
        Dizhi.Yin: Dizhi.Zi,
        Dizhi.Wu: Dizhi.Zi,
        Dizhi.Xu: Dizhi.Zi,
        Dizhi.Hai: Dizhi.You,
        Dizhi.Mou: Dizhi.You,
        Dizhi.Wei: Dizhi.You,
    }
    if other_zhi == zaisha_map.get(self_zhi):
        res.append(Daemon.Zaisha)

    # 谋星
    mou_map = {
        Dizhi.Shen: Dizhi.Xu,
        Dizhi.Zi: Dizhi.Xu,
        Dizhi.Chen: Dizhi.Xu,
        Dizhi.Si: Dizhi.Wei,
        Dizhi.You: Dizhi.Wei,
        Dizhi.Chou: Dizhi.Wei,
        Dizhi.Yin: Dizhi.Chen,
        Dizhi.Wu: Dizhi.Chen,
        Dizhi.Xu: Dizhi.Chen,
        Dizhi.Hai: Dizhi.Chou,
        Dizhi.Mou: Dizhi.Chou,
        Dizhi.Wei: Dizhi.Chou,
    }
    if other_zhi == mou_map.get(self_zhi):
        res.append(Daemon.Mouxing)

    # 孤辰寡宿（简化）：当 other_zhi 与 日支 相冲 或 相害 时标记孤辰寡宿
    # 这里使用相冲（差6）作为简化的触发条件
    if other_zhi.is_chong(self_zhi):
        res.append(Daemon.GuchenGuasu)

    # 天罗地网、亡神：这两个神煞的计算比较复杂且多版本。
    # 作为合理的默认实现，我们把天罗地网定义为：other_zhi 在 self_zhi.generate()/restrain() 中
    if other_zhi in self_zhi.generate() or other_zhi in self_zhi.restrain():
        res.append(Daemon.Tianluodiwang)

    # 亡神：当 other_zhi 等于 self_zhi.next(6)（相冲）或空亡时，标记为亡神
    kong1, kong2 = (self_zhi.next(i) for i in (0, 0))
    # 更可靠地使用 SixtyJiazi 计算空亡需要六十甲子对象，这里使用简化：若相冲则认为可能为亡神
    if other_zhi.is_chong(self_zhi):
        res.append(Daemon.Wangshen)

    # 去重并返回
    unique_res: list[Daemon] = []
    for d in res:
        if d not in unique_res:
            unique_res.append(d)
    return unique_res
