import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta

circle_symbol = "&bull;"
up_arrow_symbol = "&#8593;"
down_arrow_symbol = "&#8595;"
right_arrow_symbol = "&#8594;"
left_arrow_symbol = "&#8592;"
single_quatation_mark = "&#39;"
plus_sign = "&#43;"
minus_sign = "&#8722;"

subject_7254 = [
    "etc",
    "for",
    "org",
    "org1",
    "org2",
    "org3",
    "org4",
    "org5",
    "org6",
    "org7",
    "org8",
    "org9",
    "org10",
]


def get_file_name(path):
    import ntpath

    file_name = ntpath.basename(path)
    return file_name.split(".")[0]


word_dict = {
    "etc": "개인",
    "for": "외국인",
    "org": "기관",
    "org1": "금융투자",
    "org2": "보험",
    "org3": "투신",
    "org4": "은행",
    "org5": "기타금융",
    "org6": "연기금",
    "org7": "국가지자체",
    "org8": "기타외인",
    "org9": "사모펀드",
    "org10": "기타법인",
    "cnt": "수량",
    "amt": "금액",
    "medo": "매도",
    "mesu": "매수",
    "sonmeme": "순매수",
}


def get_kor_name(eng_name):
    kor_name = word_dict.get(eng_name)
    if kor_name is None:
        return eng_name
    return kor_name


# cybos_7210 테이블의 column이 7254와 다름
word2_dict = {"forr": "외국인", "orgr": "기관", "org2": "투신", "org4": "연기금"}


def get2_kor_name(eng_name):
    kor_name = word2_dict.get(eng_name)
    if kor_name is None:
        return eng_name
    return kor_name


def get_dealing_str(value, with_son=True):
    retrun_value = ""
    if with_son:
        retrun_value += "순"

    if isinstance(value, str):
        if value in ["desc", "mesu"]:
            retrun_value += "매수"
        else:
            retrun_value += "매도"
    else:
        if value >= 0:
            retrun_value += "매수"
        else:
            retrun_value += "매도"

    return retrun_value


def get_size_str(value):
    if isinstance(value, str):
        if value == "mesu":
            return "확대"
        return "축소"
    else:
        if value > 0:
            return "확대"
        return "축소"


def get_size_strong(value):
    if isinstance(value, str):
        if value in ["mesu", '1']:
            return "강세"
        return "약세"
    else:
        if value > 0:
            return "강세"
        return "약세"


def get_size_rising(value):
    if value in ["mesu", '1']:
        return "상승세"
    return "하락세"


def get_size_symbol(value):
    if isinstance(value, str):
        if value in ["mesu", '1']:
            return "+"
        return "-"
    else:
        if value > 0:
            return "+"
        return "-"


def get_size_color(value):
    if value in ["mesu", 1]:
        return "red"
    return "blue"


def get_value_color(value):
    if value > 0:
        return "red"
    return "blue"

def get_value_style(value):
    if value > 0:
        return "up"
    return "dn"


def get_value_style(value):
    if value > 0:
        return "up"
    return "dn"


def get_kind_market(value):
    if value in [1]:
        return "코스피"
    return "코스닥"


def get_size_style(value):
    if value == "mesu":
        return "up"
    return "dn"


def get_unit_str(value):
    if value == "cnt":
        return "주"
    return "백만원"


def make_list(rows):
    x = []
    for id in range(0, 5):
        a = rows[id]
        b = rows[id + 5]
        c = rows[id + 10]
        row_data = {
            "rank_1": a["rank"],
            "stkname_1": a["stkname"],
            "amount_1": a["amount"],
            "rank_2": b["rank"],
            "stkname_2": b["stkname"],
            "amount_2": b["amount"],
            "rank_3": c["rank"],
            "stkname_3": c["stkname"],
            "amount_3": c["amount"],
        }
        x.append(row_data)
    return x


def separate_yyyymmdd(yyyymmdd):
    if len(yyyymmdd) != 8:
        return None, None, None
    return yyyymmdd[0:4], yyyymmdd[4:6], yyyymmdd[6:8]


def get_sort(dealing_type):
    if dealing_type in ["medo", -1, '-1']:
        return "asc"
    elif dealing_type in ["mesu", 1, '1']:
        return "desc"


time_word = {
    "1_BEFORE_TRADE": "개장전",
    "2_TRADE_AM": "오전장",
    "3_TRADE_PM": "오후장",
    "4_AFTER_TRADE": "장마감 후",
}


def get_time_period(period):
    kor_period = time_word.get(period)
    if kor_period is None:
        return period
    return kor_period


def get_previous_day(day, i):
    current = dt.datetime.strptime(day, "%Y%m%d")
    before_day = current - dt.timedelta(days=i)
    return before_day.strftime("%Y%m%d")


def get_previous_years(date, i):
    current = dt.datetime.strptime(date, "%Y%m%d")
    before_year = current - relativedelta(years=i)
    return before_year.strftime('%Y%m%d')


def get_previous_month(date, i):
    current = dt.datetime.strptime(date, "%Y%m%d")
    before_year = current - relativedelta(months=i)
    return before_year.strftime('%Y%m%d')


def get_week(day):
    week = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    current = dt.datetime.strptime(day, "%Y%m%d").weekday()
    return week[current]
