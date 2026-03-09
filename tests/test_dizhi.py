import unittest

from divicast.entities.ganzhi import (Canggan, CangganType, Dizhi, Nayin,
                                      Shishen, SixtyJiazi, Tiangan,
                                      TwelveZhangsheng)
from divicast.entities.wuxing import YinYang


class TestDizhi(unittest.TestCase):
    def test_chong(self):
        self.assertEqual(True, Dizhi.Zi.is_chong(Dizhi.Wu))
        self.assertEqual(True, Dizhi.Wu.is_chong(Dizhi.Zi))
        self.assertEqual(True, Dizhi.Mou.is_chong(Dizhi.You))
        self.assertEqual(True, Dizhi.You.is_chong(Dizhi.Mou))
        self.assertEqual(False, Dizhi.Zi.is_chong(Dizhi.Zi))
        self.assertEqual(Dizhi.Zi, Dizhi.Wu.chong())

    def test_he(self):
        self.assertEqual(True, Dizhi.Zi.is_he(Dizhi.Chou))
        self.assertEqual(True, Dizhi.Chou.is_he(Dizhi.Zi))
        self.assertEqual(True, Dizhi.Yin.is_he(Dizhi.Hai))
        self.assertEqual(True, Dizhi.Hai.is_he(Dizhi.Yin))
        self.assertEqual(False, Dizhi.Zi.is_he(Dizhi.Zi))
        self.assertEqual(Dizhi.Chou, Dizhi.Zi.he())

    def test_canggan(self):
        self.assertEqual(
            [Canggan(Tiangan.Gui, CangganType.MAIN)], Dizhi.Zi.canggan())
        self.assertEqual([Canggan(Tiangan.Ji, CangganType.MAIN), Canggan(Tiangan.Xin, CangganType.MIDDLE), Canggan(Tiangan.Gui, CangganType.SECONDARY)],
                         Dizhi.Chou.canggan())
        self.assertEqual([Canggan(Tiangan.Bing, CangganType.MAIN), Canggan(Tiangan.Geng, CangganType.MIDDLE), Canggan(Tiangan.Wu, CangganType.SECONDARY)],
                         Dizhi.Si.canggan())
        self.assertEqual([Canggan(Tiangan.Ji, CangganType.MAIN), Canggan(Tiangan.Yi, CangganType.MIDDLE), Canggan(Tiangan.Ding, CangganType.SECONDARY)],
                         Dizhi.Wei.canggan())
        self.assertEqual([Canggan(Tiangan.Geng, CangganType.MAIN), Canggan(Tiangan.Ren, CangganType.MIDDLE), Canggan(Tiangan.Wu, CangganType.SECONDARY)],
                         Dizhi.Shen.canggan())
        self.assertEqual(
            [Canggan(Tiangan.Xin, CangganType.MAIN)], Dizhi.You.canggan())
        self.assertEqual([Canggan(Tiangan.Wu, CangganType.MAIN), Canggan(Tiangan.Ding, CangganType.MIDDLE), Canggan(Tiangan.Xin, CangganType.SECONDARY)],
                         Dizhi.Xu.canggan())
        self.assertEqual([Canggan(Tiangan.Ren, CangganType.MAIN), Canggan(
            Tiangan.Jia, CangganType.MIDDLE)], Dizhi.Hai.canggan())


class TestTiangan(unittest.TestCase):
    def test_shishen(self):
        self.assertEqual(Shishen.BiJian, Tiangan.Jia.get_shishen(Tiangan.Jia))
        self.assertEqual(Shishen.JieCai, Tiangan.Jia.get_shishen(Tiangan.Yi))
        self.assertEqual(
            Shishen.ShiShen, Tiangan.Jia.get_shishen(Tiangan.Bing))
        self.assertEqual(Shishen.ShangGuan,
                         Tiangan.Jia.get_shishen(Tiangan.Ding))
        self.assertEqual(Shishen.PianCai, Tiangan.Jia.get_shishen(Tiangan.Wu))
        self.assertEqual(Shishen.ZhengCai, Tiangan.Jia.get_shishen(Tiangan.Ji))
        self.assertEqual(Shishen.QiSha, Tiangan.Jia.get_shishen(Tiangan.Geng))
        self.assertEqual(Shishen.ZhengGuan,
                         Tiangan.Jia.get_shishen(Tiangan.Xin))
        self.assertEqual(Shishen.PianYin, Tiangan.Jia.get_shishen(Tiangan.Ren))
        self.assertEqual(Shishen.ZhengYin,
                         Tiangan.Jia.get_shishen(Tiangan.Gui))
        self.assertEqual(Shishen.ZhengGuan,
                         Tiangan.Ren.get_shishen(Tiangan.Ji))
        tg1 = Tiangan.Ji
        tg2 = Tiangan.Jia
        for i in range(10):
            print(tg1, tg2, "(" + str(tg1.get_shishen(tg2)) + ")")
            tg2 = tg2.next()

    def test_yinyang(self):
        self.assertEqual(YinYang.Yang, Tiangan.Jia.belongs_to(YinYang))
        self.assertEqual(YinYang.Yin, Tiangan.Yi.belongs_to(YinYang))
        self.assertEqual(YinYang.Yang, Tiangan.Bing.belongs_to(YinYang))
        self.assertEqual(YinYang.Yin, Tiangan.Ding.belongs_to(YinYang))
        self.assertEqual(YinYang.Yang, Tiangan.Wu.belongs_to(YinYang))
        self.assertEqual(YinYang.Yin, Tiangan.Ji.belongs_to(YinYang))
        self.assertEqual(YinYang.Yang, Tiangan.Geng.belongs_to(YinYang))
        self.assertEqual(YinYang.Yin, Tiangan.Xin.belongs_to(YinYang))
        self.assertEqual(YinYang.Yang, Tiangan.Ren.belongs_to(YinYang))
        self.assertEqual(YinYang.Yin, Tiangan.Gui.belongs_to(YinYang))

    def test_zhangsheng(self):
        self.assertEqual(TwelveZhangsheng.MuYu,
                         Tiangan.Jia.get_twelve_zhangsheng(Dizhi.Zi))
        self.assertEqual(TwelveZhangsheng.GuanDai,
                         Tiangan.Jia.get_twelve_zhangsheng(Dizhi.Chou))

        self.assertEqual(TwelveZhangsheng.Bing,
                         Tiangan.Yi.get_twelve_zhangsheng(Dizhi.Zi))
        self.assertEqual(TwelveZhangsheng.Shuai,
                         Tiangan.Yi.get_twelve_zhangsheng(Dizhi.Chou))

    def test_nayin(self):
        self.assertEqual(Nayin.HaiZhongJin, SixtyJiazi(
            Tiangan.Jia, Dizhi.Zi).get_nayin())
        self.assertEqual(Nayin.HaiZhongJin, SixtyJiazi(
            Tiangan.Yi, Dizhi.Chou).get_nayin())
        self.assertEqual(Nayin.LuZhongHuo, SixtyJiazi(
            Tiangan.Bing, Dizhi.Yin).get_nayin())
        self.assertEqual(Nayin.LuZhongHuo, SixtyJiazi(
            Tiangan.Ding, Dizhi.Mou).get_nayin())
        self.assertEqual(Nayin.DongXiaShui, SixtyJiazi(
            Tiangan.Bing, Dizhi.Zi).get_nayin())
        self.assertEqual(Nayin.ChaiShanJin, SixtyJiazi(
            Tiangan.Xin, Dizhi.Hai).get_nayin())
        self.assertEqual(Nayin.ShiLiuMu, SixtyJiazi(
            Tiangan.Xin, Dizhi.You).get_nayin())
        self.assertEqual(Nayin.DaHaiShui, SixtyJiazi(
            Tiangan.Gui, Dizhi.Hai).get_nayin())
        self.assertEqual(Nayin.DaHaiShui, SixtyJiazi(
            Tiangan.Ren, Dizhi.Xu).get_nayin())
