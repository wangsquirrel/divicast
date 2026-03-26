import unittest
from types import SimpleNamespace

from divicast.birth_chart.analysis import BirthChartAnalyzer
from divicast.birth_chart.analysis_enums import Zhu
from divicast.entities.ganzhi import Dizhi, Tiangan


def _build_chart(
    year: tuple[Tiangan, Dizhi],
    month: tuple[Tiangan, Dizhi],
    day: tuple[Tiangan, Dizhi],
    hour: tuple[Tiangan, Dizhi],
):
    return SimpleNamespace(
        yearzhu=SimpleNamespace(gan=year[0], zhi=year[1]),
        monthzhu=SimpleNamespace(gan=month[0], zhi=month[1]),
        dayzhu=SimpleNamespace(gan=day[0], zhi=day[1]),
        bihourzhu=SimpleNamespace(gan=hour[0], zhi=hour[1]),
    )


class TestBirthChartRelations(unittest.TestCase):
    def test_relation_events_support_multi_party_relations(self):
        chart = _build_chart(
            year=(Tiangan.Jia, Dizhi.Yin),
            month=(Tiangan.Ji, Dizhi.Wu),
            day=(Tiangan.Bing, Dizhi.Xu),
            hour=(Tiangan.Geng, Dizhi.Hai),
        )

        relations = BirthChartAnalyzer().analyze_relations(chart)

        sanhe = next(event for event in relations.events if event.name == "地支三合")
        self.assertEqual("合", str(sanhe.relation_type))
        self.assertEqual("火局", str(sanhe.outcome))
        self.assertEqual([Zhu.YEAR, Zhu.MONTH, Zhu.DAY], [item.pillar for item in sanhe.participants])

        tiangan_he = next(event for event in relations.events if event.name == "天干五合")
        self.assertEqual("化土", str(tiangan_he.outcome))
        self.assertEqual([Zhu.YEAR, Zhu.MONTH], [item.pillar for item in tiangan_he.participants])

        self.assertTrue(
            any(
                item.name == "地支三合" and str(item.outcome) == "火局"
                for item in relations.pillar_index.for_pillar(Zhu.YEAR).dizhi
            )
        )

    def test_relation_events_support_pair_branch_relations(self):
        chart = _build_chart(
            year=(Tiangan.Jia, Dizhi.Zi),
            month=(Tiangan.Yi, Dizhi.Mou),
            day=(Tiangan.Bing, Dizhi.Wu),
            hour=(Tiangan.Ding, Dizhi.You),
        )

        relations = BirthChartAnalyzer().analyze_relations(chart)
        indexed = {
            (event.name, str(event.qualifier) if event.qualifier else None, tuple(item.pillar for item in event.participants))
            for event in relations.events
        }

        self.assertIn(("地支相刑", "无礼之刑", (Zhu.YEAR, Zhu.MONTH)), indexed)
        self.assertIn(("地支六冲", None, (Zhu.YEAR, Zhu.DAY)), indexed)
        self.assertIn(("地支六破", None, (Zhu.YEAR, Zhu.HOUR)), indexed)

    def test_relation_events_support_three_punishments_and_self_punishment(self):
        sanxing_chart = _build_chart(
            year=(Tiangan.Jia, Dizhi.Yin),
            month=(Tiangan.Yi, Dizhi.Si),
            day=(Tiangan.Bing, Dizhi.Shen),
            hour=(Tiangan.Ding, Dizhi.Hai),
        )
        sanxing_relations = BirthChartAnalyzer().analyze_relations(sanxing_chart)
        sanxing = next(event for event in sanxing_relations.events if event.name == "地支三刑")
        self.assertEqual("无恩之刑", str(sanxing.qualifier))
        self.assertEqual([Zhu.YEAR, Zhu.MONTH, Zhu.DAY], [item.pillar for item in sanxing.participants])

        zixing_chart = _build_chart(
            year=(Tiangan.Jia, Dizhi.Chen),
            month=(Tiangan.Yi, Dizhi.Chen),
            day=(Tiangan.Bing, Dizhi.Zi),
            hour=(Tiangan.Ding, Dizhi.Wu),
        )
        zixing_relations = BirthChartAnalyzer().analyze_relations(zixing_chart)
        zixing = next(event for event in zixing_relations.events if event.name == "地支自刑")
        self.assertEqual("自刑", str(zixing.qualifier))
        self.assertEqual([Zhu.YEAR, Zhu.MONTH], [item.pillar for item in zixing.participants])
