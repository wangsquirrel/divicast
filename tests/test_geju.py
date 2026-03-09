"""
格局计算模块单元测试
"""

import datetime
import unittest

from divicast.birth_chart.birth import BirthChart, Gender
from divicast.birth_chart.geju import Geju


class TestGeju(unittest.TestCase):
    """测试命盘格局计算"""

    # ==================== 特殊格局 ====================

    def test_kuigang_ren_chen(self):
        """测试魁罡格 - 壬辰"""
        # TODO: 填入具体日期
        bc = BirthChart.create(
            datetime.datetime(2024, 5, 28, 12, 0, 0), Gender.MAN
        )
        self.assertEqual(bc.dayzhu.gan.chinese_name + bc.dayzhu.zhi.chinese_name, "壬辰")
        self.assertEqual(bc.geju, Geju.KUIGANG)

    def test_kuigang_geng_chen(self):
        """测试魁罡格 - 庚辰"""
        # TODO: 填入具体日期
        bc = BirthChart.create(
            datetime.datetime(2024, 1, 17, 12, 0, 0), Gender.MAN
        )
        self.assertEqual(bc.dayzhu.gan.chinese_name + bc.dayzhu.zhi.chinese_name, "庚辰")
        self.assertEqual(bc.geju, Geju.KUIGANG)

    def test_kuigang_geng_xu(self):
        """测试魁罡格 - 庚戌"""
        # TODO: 填入具体日期
        bc = BirthChart.create(
            datetime.datetime(2024, 2, 16, 12, 0, 0), Gender.MAN
        )
        self.assertEqual(bc.dayzhu.gan.chinese_name + bc.dayzhu.zhi.chinese_name, "庚戌")
        self.assertEqual(bc.geju, Geju.KUIGANG)

    def test_kuigang_wu_xu(self):
        """测试魁罡格 - 戊戌"""
        # TODO: 填入具体日期
        bc = BirthChart.create(
            datetime.datetime(2024, 2, 4, 12, 0, 0), Gender.MAN
        )
        self.assertEqual(bc.dayzhu.gan.chinese_name + bc.dayzhu.zhi.chinese_name, "戊戌")
        self.assertEqual(bc.geju, Geju.KUIGANG)

    def test_guilu(self):
        """测试归禄格 - 日主临官位"""
        # TODO: 填入具体日期
        # 甲卯、乙寅、丙巳、丁午、戊巳、己午、庚申、辛酉、壬亥、癸子
        pass

    def test_qiqiang_bei(self):
        """测试壬骑龙背格 - 壬辰日多见辰"""
        # TODO: 填入具体日期
        pass

    def test_jinglan_cha(self):
        """测试井栏叉格 - 庚子庚申庚辰日"""
        # TODO: 填入具体日期
        pass

    def test_liu_jia_qu_gan(self):
        """测试六甲趋干格 - 甲日亥时"""
        # TODO: 填入具体日期
        pass

    def test_liu_yi_shu_gui(self):
        """测试六乙鼠贵格 - 乙日子时"""
        # TODO: 填入具体日期
        pass

    def test_liu_yin_chao_yang(self):
        """测试六阴朝阳格 - 辛日丑时"""
        # TODO: 填入具体日期
        pass

    def test_liu_ren_qu_gen(self):
        """测试六壬趋艮格 - 壬寅日"""
        # TODO: 填入具体日期
        pass

    def test_gou_chen_de_wei(self):
        """测试勾陈得位格 - 戊日丑未"""
        # TODO: 填入具体日期
        pass

    def test_xuan_wu_dang_quan(self):
        """测试玄武当权格 - 壬日寅午"""
        # TODO: 填入具体日期
        pass

    def test_liang_shen_cheng_xiang(self):
        """测试两神成象格 - 两种五行势均力敌"""
        # TODO: 填入具体日期
        pass

    def test_ban_bi_jiang_shan(self):
        """测试半壁江山格 - 两组干支相同"""
        # TODO: 填入具体日期
        pass

    # ==================== 专旺格 ====================

    def test_quzhi(self):
        """测试曲直格 - 木专旺"""
        # TODO: 填入具体日期
        # 条件：木占60%以上，日主为甲乙木，日支无根
        pass

    def test_yanshang(self):
        """测试炎上格 - 火专旺"""
        # TODO: 填入具体日期
        pass

    def test_jiase(self):
        """测试稼穑格 - 土专旺"""
        # TODO: 填入具体日期
        pass

    def test_runxia(self):
        """测试润下格 - 水专旺"""
        # TODO: 填入具体日期
        pass

    def test_congge(self):
        """测试从革格 - 金专旺"""
        # TODO: 填入具体日期
        pass

    # ==================== 从格 ====================

    def test_congsha(self):
        """测试从杀格"""
        # TODO: 填入具体日期
        pass

    def test_congcai(self):
        """测试从财格"""
        # TODO: 填入具体日期
        pass

    def test_conger(self):
        """测试从儿格"""
        # TODO: 填入具体日期
        pass

    def test_congyin(self):
        """测试从印格"""
        # TODO: 填入具体日期
        pass

    def test_congqiang(self):
        """测试从强格"""
        # TODO: 填入具体日期
        pass

    # ==================== 化气格 ====================

    def test_hua_jia(self):
        """测试化甲格 - 甲己合化土"""
        # TODO: 填入具体日期
        # 条件：天干有甲己，化神土旺，日主弱
        pass

    def test_hua_yi(self):
        """测试化乙格 - 乙庚合化金"""
        # TODO: 填入具体日期
        pass

    def test_hua_bing(self):
        """测试化丙格 - 丙辛合化水"""
        # TODO: 填入具体日期
        pass

    def test_hua_ding(self):
        """测试化丁格 - 丁壬合化木"""
        # TODO: 填入具体日期
        pass

    def test_hua_wu(self):
        """测试化戊格 - 戊癸合化火"""
        # TODO: 填入具体日期
        pass

    # ==================== 正格 ====================

    def test_zhengge_zhengyin(self):
        """测试正印格"""
        # TODO: 填入具体日期
        # 条件：月支藏干透正印
        pass

    def test_zhengge_pianyin(self):
        """测试偏印格"""
        # TODO: 填入具体日期
        pass

    def test_zhengge_zhenguan(self):
        """测试正官格"""
        # TODO: 填入具体日期
        pass

    def test_zhengge_qisha(self):
        """测试七杀格"""
        # TODO: 填入具体日期
        pass

    def test_zhengge_zhengcai(self):
        """测试正财格"""
        # TODO: 填入具体日期
        pass

    def test_zhengge_piancai(self):
        """测试偏财格"""
        # TODO: 填入具体日期
        pass

    def test_zhengge_shishen(self):
        """测试食神格"""
        # TODO: 填入具体日期
        pass

    def test_zhengge_shangguan(self):
        """测试伤官格"""
        # TODO: 填入具体日期
        pass

    def test_zhengge_bijian(self):
        """测试比肩格"""
        # TODO: 填入具体日期
        pass

    def test_zhengge_jiecai(self):
        """测试劫财格"""
        # TODO: 填入具体日期
        pass

    # ==================== 普通格局 ====================

    def test_regular_not_kuigang(self):
        """测试非魁罡格"""
        bc = BirthChart.create(
            datetime.datetime(2024, 1, 1, 12, 0, 0), Gender.MAN
        )
        self.assertNotEqual(bc.geju, Geju.KUIGANG)


if __name__ == "__main__":
    unittest.main()
