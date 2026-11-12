from types import SimpleNamespace

from divicast.birth_chart.analysis import analyze_chart
from divicast.birth_chart.birth import ZhuInfo
from divicast.entities.ganzhi import SixtyJiazi
from divicast.entities.pillars import FourPillars


def build_chart(year: str, month: str, day: str, hour: str):
    chart = SimpleNamespace(
        pillars=FourPillars(
            year=SixtyJiazi.parse(year),
            month=SixtyJiazi.parse(month),
            day=SixtyJiazi.parse(day),
            hour=SixtyJiazi.parse(hour),
        )
    )
    day_master = chart.pillars.day.gan
    chart.yearzhu = ZhuInfo(chart.pillars.year, day_master=day_master, shensha=())
    chart.monthzhu = ZhuInfo(chart.pillars.month, day_master=day_master, shensha=())
    chart.dayzhu = ZhuInfo(chart.pillars.day, day_master=day_master, shensha=())
    chart.bihourzhu = ZhuInfo(chart.pillars.hour, day_master=day_master, shensha=())

    chart.chart_analysis = analyze_chart(chart)
    return chart
