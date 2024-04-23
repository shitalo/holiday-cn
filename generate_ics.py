import datetime
from typing import Any, Iterator, Sequence, Text, Tuple
from icalendar import Event, Calendar, Timezone, TimezoneStandard
from zhdate import ZhDate
import uuid
import requests


def _create_timezone():
    tz = Timezone()
    tz.add("TZID", "Asia/Shanghai")

    tz_standard = TimezoneStandard()
    tz_standard.add("DTSTART", datetime.datetime(1970, 1, 1))
    tz_standard.add("TZOFFSETFROM", datetime.timedelta(hours=8))
    tz_standard.add("TZOFFSETTO", datetime.timedelta(hours=8))

    tz.add_component(tz_standard)
    return tz


def _create_event(event_name, start, end, descrip=None, work=None):
    # 创建事件/日程
    event = Event()
    event.add("SUMMARY", event_name)

    event.add("DTSTART", start)
    event.add("DTEND", end)
    # 创建时间
    event.add("DTSTAMP", start)
    if (descrip):
        event.add("DESCRIPTION", descrip)
    # UID保证唯一
    if (work):
        event.add("X-APPLE-SPECIAL-DAY", "WORK-HOLIDAY")
    event["UID"] = str(uuid.uuid4())
    return event


def _cast_date(v: Any) -> datetime.date:
    if isinstance(v, datetime.date):
        return v
    if isinstance(v, str):
        return datetime.date.fromisoformat(v)
    raise NotImplementedError("can not convert to date: %s" % v)


def _iter_date_ranges(days: Sequence[dict]) -> Iterator[Tuple[dict, dict]]:
    if len(days) == 0:
        return

    if len(days) == 1:
        yield days[0], days[0]
        return

    fr, to = days[0], days[0]
    for cur in days[1:]:
        if (_cast_date(cur["date"]) - _cast_date(to["date"])).days == 1 and cur[
            "isOffDay"
        ] == to["isOffDay"]:
            to = cur
        else:
            yield fr, to
            fr, to = cur, cur
    yield fr, to


def generate_ics(days: Sequence[dict], filename: Text) -> None:
    """Generate ics from days."""
    cal = Calendar()
    cal.add("X-WR-CALNAME", "中国法定节假日")
    cal.add("X-WR-CALDESC", "中国法定节假日数据，自动每日抓取国务院公告。")
    cal.add("VERSION", "2.0")
    cal.add("METHOD", "PUBLISH")
    cal.add("CLASS", "PUBLIC")

    cal.add_component(_create_timezone())
    days = sorted(days, key=lambda x: x["date"])

    for fr, to in _iter_date_ranges(days):
        start = _cast_date(fr["date"])
        end = _cast_date(to["date"]) + datetime.timedelta(days=1)

        name = fr["name"] + "(休)"
        if not fr["isOffDay"]:
            name = fr["name"] + "(班)"
        cal.add_component(_create_event(name, start, end, work=True))

    with open(filename, "wb") as f:
        f.write(cal.to_ical())


def generate_main_ics(days: Sequence[dict], filename: Text, nowyear) -> None:
    """Generate ics from days."""
    # url = 'https://calendars.icloud.com/holidays/cn_zh.ics'
    # cal = Calendar.from_ical(requests.get(url).text)
    cal = Calendar()
    cal.add("X-WR-CALNAME", "节日补充")
    cal.add("X-WR-CALDESC", "补充节日数据")
    cal.add("VERSION", "2.0")
    cal.add("METHOD", "PUBLISH")
    cal.add("CLASS", "PUBLIC")
    cal.add_component(_create_timezone())
    for year in range(nowyear-3, nowyear + 2):
        # name = "元旦"
        # start = _cast_date("%d-01-01" % year)
        # end = start
        # cal.add_component(_create_event(name, start, end))

        name = "情人节"
        start = _cast_date("%d-02-14" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "妇女节"
        start = _cast_date("%d-03-08" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "植树节"
        start = _cast_date("%d-03-12" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "愚人节"
        start = _cast_date("%d-04-01" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        # name = "世界地球日"
        # start = _cast_date("%d-04-22" % year)
        # end = start
        # cal.add_component(_create_event(name, start, end))

        # name = "劳动节"
        # start = _cast_date("%d-05-01" % year)
        # end = start
        # cal.add_component(_create_event(name, start, end))

        name = "青年节"
        start = _cast_date("%d-05-04" % year)
        end = start
        descrip = "五四运动%d周年纪念日" % (year - 1919)
        cal.add_component(_create_event(name, start, end, descrip))

        name = "母亲节"
        start = _cast_date("%d-05-01" % year)+datetime.timedelta(days=13 -
                                                                 _cast_date("%d-05-01" % year).weekday())
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "儿童节"
        start = _cast_date("%d-06-01" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "父亲节"
        start = _cast_date("%d-06-01" % year)+datetime.timedelta(days=20 -
                                                                 _cast_date("%d-06-01" % year).weekday())
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "建党节"
        start = _cast_date("%d-07-01" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "建军节"
        start = _cast_date("%d-08-01" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "抗日战争胜利纪念日"
        start = _cast_date("%d-09-03" % year)
        end = start
        descrip = "抗日战争胜利%d周年" % (year - 1945)
        cal.add_component(_create_event(name, start, end, descrip))

        name = "教师节"
        start = _cast_date("%d-09-10" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "国耻日"
        start = _cast_date("%d-09-18" % year)
        end = start
        descrip = "九·一八事变 1931年9月18日"
        cal.add_component(_create_event(name, start, end, descrip))

        # name = "国庆节"
        # start = _cast_date("%d-10-01" % year)
        # end = start
        # descrip = "建国%d周年" % (year - 1949)
        # cal.add_component(_create_event(name, start, end, descrip))

        name = "辛亥革命纪念日"
        start = _cast_date("%d-10-10" % year)
        end = start
        descrip = "辛亥革命%d周年" % (year-1911)
        cal.add_component(_create_event(name, start, end, descrip))

        name = "万圣夜"
        start = _cast_date("%d-10-31" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "万圣节"
        start = _cast_date("%d-11-01" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "感恩节"
        start = _cast_date("%d-11-25" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "一二·九运动纪念日"
        start = _cast_date("%d-12-09" % year)
        end = start
        descrip = "一二·九运动%d周年" % (year-1935)
        cal.add_component(_create_event(name, start, end, descrip))

        name = "南京大屠杀纪念日"
        start = _cast_date("%d-12-13" % year)
        end = start
        descrip = "南京大屠杀%d周年" % (year-1937)
        cal.add_component(_create_event(name, start, end, descrip))

        name = "平安夜"
        start = _cast_date("%d-12-24" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "圣诞节"
        start = _cast_date("%d-12-25" % year)
        end = start
        cal.add_component(_create_event(name, start, end))

        # name = "春节"
        # start = _cast_date(ZhDate(year, 1, 1).to_datetime().date())
        # end = start
        # cal.add_component(_create_event(name, start, end))

        name = "元宵节"
        start = _cast_date(ZhDate(year, 1, 15).to_datetime().date())
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "登高节"
        start = _cast_date(ZhDate(year, 1, 16).to_datetime().date())
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "龙抬头"
        start = _cast_date(ZhDate(year, 2, 2).to_datetime().date())
        end = start
        cal.add_component(_create_event(name, start, end))

        # name = "上巳节"
        # start = _cast_date(ZhDate(year, 3, 3).to_datetime().date())
        # end = start
        # cal.add_component(_create_event(name, start, end))

        # name = "端午节"
        # start = _cast_date(ZhDate(year, 5, 5).to_datetime().date())
        # end = start
        # cal.add_component(_create_event(name, start, end))

        name = "七夕节"
        start = _cast_date(ZhDate(year, 7, 7).to_datetime().date())
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "中元节"
        start = _cast_date(ZhDate(year, 7, 15).to_datetime().date())
        end = start
        cal.add_component(_create_event(name, start, end))

        # name = "中秋节"
        # start = _cast_date(ZhDate(year, 8, 15).to_datetime().date())
        # end = start
        # cal.add_component(_create_event(name, start, end))

        name = "重阳节"
        start = _cast_date(ZhDate(year, 9, 9).to_datetime().date())
        end = start
        cal.add_component(_create_event(name, start, end))

        # name = "下元节"
        # start = _cast_date(ZhDate(year, 10, 15).to_datetime().date())
        # end = start
        # cal.add_component(_create_event(name, start, end))

        name = "腊八节"
        start = _cast_date(ZhDate(year, 12, 8).to_datetime().date())
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "北方小年"
        start = _cast_date(ZhDate(year, 12, 23).to_datetime().date())
        end = start
        cal.add_component(_create_event(name, start, end))

        name = "南方小年"
        start = _cast_date(ZhDate(year, 12, 24).to_datetime().date())
        end = start
        cal.add_component(_create_event(name, start, end))

        # name = "除夕"
        # start = _cast_date(
        #     ZhDate(year, 1, 1).to_datetime().date()-datetime.timedelta(days=1))
        # end = start
        # cal.add_component(_create_event(name, start, end))

    days = sorted(days, key=lambda x: x["date"])

    # for fr, to in _iter_date_ranges(days):
    #     start = _cast_date(fr["date"])
    #     end = _cast_date(to["date"]) + datetime.timedelta(days=1)

    #     name = fr["name"] + "(休)"
    #     if not fr["isOffDay"]:
    #         name = fr["name"] + "(班)"
    #     cal.add_component(_create_event(name, start, end, work=True))

    with open(filename, "wb") as f:
        f.write(cal.to_ical())
