from types import SimpleNamespace

from divicast.birth_chart.analysis import analyze_chart
from divicast.birth_chart.birth import ZhuInfo


def build_chart(year: str, month: str, day: str, hour: str):
    chart = SimpleNamespace()
    chart.yearzhu = ZhuInfo(year)
    chart.monthzhu = ZhuInfo(month)
    chart.dayzhu = ZhuInfo(day)
    chart.bihourzhu = ZhuInfo(hour)

    for zhu in [chart.yearzhu, chart.monthzhu, chart.dayzhu, chart.bihourzhu]:
        zhu.canggan = zhu.zhi.canggan()
        zhu.zhuxing = chart.dayzhu.gan.get_shishen(zhu.gan)
        zhu.fuxing = [chart.dayzhu.gan.get_shishen(canggan.gan) for canggan in zhu.canggan]
        zhu.xingyun = chart.dayzhu.gan.get_twelve_zhangsheng(zhu.zhi)
        zhu.zizuo = zhu.gan.get_twelve_zhangsheng(zhu.zhi)
        zhu.kongwang = zhu.sixty_jiazi.get_kongwang()
        zhu.nayin = zhu.sixty_jiazi.get_nayin()
        zhu.daemon = []

    chart.chart_analysis = analyze_chart(chart)
    return chart
