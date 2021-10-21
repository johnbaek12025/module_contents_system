import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from adm.jobs.workshop.chart_jh import Chart, Bar
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import (get_stock_name, get_cybos7254, selectionsort,
                                  get_sorting, get_trend_value,
                                  get_stock_related)
from adm.jobs import (get_kor_name, get_dealing_str, get_size_str,
                      get_size_symbol, get_size_color, get_unit_str,
                      circle_symbol, get_previous_day)

logger = logging.getLogger(__name__)


def set_bar(bar):
    if None in [bar.tick, bar.value]:
        return False

    month = bar.tick[4:6]
    day = bar.tick[6:8]
    bar.tick = f"{month}/{day}"
    if bar.value < 0:
        bar.color = "blue"
    else:
        bar.color = "orange"
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


def get_bar_chart(rows: dict, local_image_whole_path, days=None, l=[]):
    chart_dict = {
        "face_color": "whitesmoke",
        # "grid_color": "silver",
        "tick_position": "left",
        "tick_interval": 4,
        "spine_top": False,
        # "spine_right": False,
        "grid": False
    }
    bc = Chart(**chart_dict)
    exval = get_sorting(**rows)
    colors = ['orange', 'navy', 'slateblue', 'lightblue']
    for i, r in enumerate(rows):
        l.append(r)
        if r == '검색빈도':
            bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
            bc.add_data(bar_chart_data, chart_type="bar", label=r)
        else:
            bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
            bc.add_data(bar_chart_data,
                        colors=colors[i],
                        twinx=True,
                        label=r,
                        exval=exval)
        if i == 0 or len(l[i - 1]) < 6:
            bc.finalize_chart(local_image_whole_path,
                              ticks=False,
                              leg=r,
                              loc='lower left',
                              loc_position=(0.2 * i, -0.4))
        else:
            bc.finalize_chart(local_image_whole_path,
                              ticks=False,
                              leg=r,
                              loc='lower left',
                              loc_position=(0.2 * i + 0.03, -0.4))


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.dealing_type = None
        self.subject = None
        self.unit = None
        self.use_ftp = True
        self.continuous_days_count = None
        self.rk = None
        self.unit = 'amt'
        self.stock_code = None
        self.stock_name = None
        self.ts_date = 20 
        self.count = 3
        self.process_condition = ADManager.SC_ONCE

    def set_analysis_target(self):
        columns = [
            "issn",
            "is_str",
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.issn = row.get("issn")
        self.is_str = row.get('is_str')
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.is_str},",
                "color": None
            },
            {
                "text": f"{self.deal_date_dd}일 포탈 검색 급증 ↑",
                "colo": get_size_color(self.dealing_type),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = None
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr()}
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        return f"""
            <div class="module-tbl-txt">                
                <div style = "float:left">
                <span>검색트렌드</span>
                </div>
                <div style = "float:right">
                <span>주가 누적등락률(%)</span>
                </div>
            </div>            
        """

    def get_middle_tr(self):
        rows = {
            '검색빈도': self.get_trend_info(),
        }
        codes = self.get_stock()
        for c in codes:
            rows[c] = self.get_stock_ratio(codes[c])
        get_bar_chart(rows=rows,
                      local_image_whole_path=self.local_image_whole_path)
        return f"""
            <div class="module-chart text-center bgcolor">
                <img style="height:auto; max-width:100%;" src="{self.image_url}">               
            </div>     
        """

    def get_bottom_tr(self):
        return f"""
            <div class="module-tbl-txt mt-20">                
                <div class="c999 dot">※ 검색빈도 : 최근 1달간 MAX 검색횟수를 100으로한 상대적인 변화 값으로 표시됨
            </div>      
            </div>
        """

    def get_trend_info(self):
        yesterday = get_previous_day(self.deal_date, 1)
        sql = get_trend_value(self.issn, yesterday)
        rows = self.data_db_mgr.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0]
            x[id] = r[1]
        return x

    def get_stock(self):
        rows = self.rc_db_mgr.get_related_stock(self.issn, self.count,
                                                self.deal_date)
        x = {}
        if not rows:
            return x
        return rows

    def get_stock_ratio(self, code):
        yesterday = get_previous_day(self.deal_date, 1)
        x = self.rc_db_mgr.get_stock_info(yesterday,
                                          self.ts_date,
                                          code,
                                          ratio=True)
        return x
