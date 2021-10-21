import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import (get_stock_name, get_cybos7254,
                                  get_before_day, get_before_hour,
                                  get_empty_hour, related_stock)
from .workshop.chart_jh import Chart, Bar
from adm.jobs import (get_kor_name, get_dealing_str, get_size_str,
                      get_size_symbol, get_value_color, get_unit_str,
                      circle_symbol, get_sort, get_time_period,
                      get_previous_day)

logger = logging.getLogger(__name__)


def set_bar(bar):
    if None in [bar.tick, bar.value]:
        return False
    month = bar.tick[4:6]
    day = bar.tick[6:8]
    bar.tick = f"{month}/{day}"
    return True


def get_bar_chart_data(rows: dict, func=None):
    set_bar_chart_data = []
    for tick in rows:
        bar = Bar()
        bar.tick = tick
        bar.value = rows[tick]
        if func(bar):
            set_bar_chart_data.append(bar)
    return set_bar_chart_data


def get_bar_chart(rows: dict, local_image_whole_path, customs):
    chart_dict = {
        "face_color": "whitesmoke",
        "grid_color": "silver",
        "tick_position": "right",
        "tick_interval": 4,
        "spine_top": False,
        "spine_bottom": False,
        "spine_left": False,
        "grid": 'both',
    }
    bc = Chart(**chart_dict)
    colors = ['red', 'green', 'black']    
    for i, r in enumerate(rows):
        bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
        bc.add_data(bar_chart_data, 'plot', colors[i],
                    get_kor_name(customs[i]))
    bc.finalize_chart(local_image_whole_path, ticks=False, leg=customs)


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.use_ftp = True
        self.ts_data_count = 20
        self.count = 20
        self.period_len = None
        self.stock_code = None
        self.stock_name = None
        self.subject = []
        self.sonmeme_cnt = None
        self.recent = '5'
        self.dealing_type = None
        self.sub_list = None
        self.ratio = None
        self.columns = []
        self.rank_type = None
        self.process_condition = ADManager.SC_ONCE

    def set_analysis_target(self):
        self.columns = [
            "stk_code", "stk_name", "customer_type", "period_len", "rank_type",
            "sonmeme_cnt", "period_posession_ratio", "RK"
        ]
        condition = (f"and period_len = {self.recent}")
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       self.columns,
                                                       self.deal_date,
                                                       self.info_seq)
        self.dealing_type = 'sonmeme'
        self.unit = 'cnt'
        self.subject = row.get("customer_type").lower()
        self.period_len = row.get("period_len")
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.sonmeme_cnt = row.get("sonmeme_cnt")
        self.sub_list = ['for', 'org', 'etc']
        self.ratio = row.get('period_posession_ratio')
        self.rank_type = row.get("rank_type")
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name}",
                "color": None
            },
            {
                "text":
                f"{get_kor_name(self.subject)} 보유비중 {get_size_str(self.sonmeme_cnt)}(5일 누적)",
                "color": (get_value_color(self.sonmeme_cnt)),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr()}
            """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        return f"""
            <div class="module-tbl-txt">
                <span>누적순매매량</span>
            </div>            
            """

    def get_middle_tr(self):
        rows = self.get_amt_info()
        get_bar_chart(rows, self.local_image_whole_path, self.sub_list)
        return f"""
        <div class="module-chart text-center bgcolor">
            <img style="height:auto; max-width:100%;" src="{self.image_url}">
        </div>
        """

    def get_bottom_tr(self):
        amt = self.get_acc_amt()
        rows = self.get_today_amt()
        names = self.get_related_stock()
        color = get_value_color(self.ratio)
        c = "up" if color == "red" else "dn"
        x = []
        for r in rows:
            ob = f"{get_kor_name(r)} {format(abs(rows[r]), ',')}주 {get_dealing_str(rows[r], True)}"
            x.append(ob)
        return f"""
                <div class="module-tbl-txt mt-20">
                    <div class="dot">{self.recent}일 누적 {amt[0]} 순매매량: {amt[1]} 주  <em class="{c}">(매매비중 {round(abs(self.ratio), 2)}%)</em></div>
                    <div class="dot">{self.deal_date_dd}일 순매매 동향: {' '.join(x)}</div>
                    <div class="dot c999">{get_kor_name(self.subject)} 보유비중 확대 종목: {', '.join(names)} 등</div>
                </div>
            """

    def get_amt_info(self):
        dates = self.rc_db_mgr.get_dates(self.deal_date, 20, order='asc')
        rows = {}
        for subject in self.sub_list:
            x = {}
            for i, d in enumerate(dates):
                i += 1
                value = self.rc_db_mgr.get_7254_accu_value(
                    d, self.stock_code, self.dealing_type, self.unit, i)
                x[d] = value[subject]
            rows[subject] = x
        return rows

    def get_today_amt(self):
        x = {}
        for subject in self.sub_list:
            row = self.rc_db_mgr.get_7254_accu_value(self.deal_date,
                                                     self.stock_code,
                                                     self.dealing_type,
                                                     self.unit)
            x[subject] = row[subject]
        return x

    def get_acc_amt(self):
        row = self.rc_db_mgr.get_7254_accu_value(self.deal_date,
                                                 self.stock_code,
                                                 self.dealing_type, self.unit,
                                                 int(self.recent))
        x = []
        for r in row:
            id = r
            if id == self.subject:
                x.append(get_kor_name(id))
                x.append(format(row.get(id), ","))
        return x

    def get_related_stock(self):
        column = ['stk_code', 'stk_name']
        condition = (f"and   customer_type = '{self.subject.upper()}' "
                     f"and   rank_type = '{self.rank_type}' "
                     f"order by  rk asc")
        sql = related_stock(column,
                            self.analysis_type,
                            self.deal_date,
                            condition=condition,
                            num=3)
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x

        for r in rows:
            x.append(
                f'<a href=" https://dev.thinkpool.com/item/{r[0]}/trend">{r[1]}</a>'
            )
        return x
