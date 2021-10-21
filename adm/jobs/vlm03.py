import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from adm.jobs.workshop.chart_jh import Chart, Bar
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import get_stock_name, get_cybos7254
from adm.jobs import (
    get_kor_name,
    get_dealing_str,
    get_size_str,
    get_size_symbol,
    get_size_color,
    get_unit_str,
    circle_symbol,
    get_week,
)

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
        bar.color = "red"
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


def get_bar_chart(rows: dict, local_image_whole_path):
    chart_dict = {
        "face_color": "whitesmoke",
        "grid_color": "silver",
        "tick_interval": 1,
        "spine_left": False,
        "spine_top": False,
        "spine_right": False,
        "spine_bottom": False,
        "grid": 'y',
        "rotation": 45
    }
    bc = Chart(**chart_dict)
    for r in rows:
        if r == '거래량':
            bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
            bc.add_data(bar_chart_data, chart_type="bar")
        elif r == '주가':
            bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
            bc.add_data(bar_chart_data, colors='green', twinx=True)
        bc.finalize_chart(local_image_whole_path, ticks=False, leg=r)


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.use_ftp = True
        self.continuous_days_count = None
        self.rk = None
        self.stock_code = None
        self.stock_name = None
        self.count = 20

    def set_analysis_target(self):
        columns = [
            "stk_code",
            "stk_name",
            "jang_type",
            "rk",
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.stock_name = row.get('stk_name')
        self.stock_code = row.get('stk_code')
        self.jang_type = row.get('jang_type')
        self.rk = row.get('rk')
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text": f"거래량 급등",
                "colo": 'red',
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        return f"""
            <div class="module-tbl-txt">                
                <div style = "float:left">                
                </div>
                <div style = "float:right">
                <span>주가 (원)</span>
                </div>
            </div>            
        """

    def get_middle_tr(self):
        x = self.get_today(vol=True)
        row = self.rc_db_mgr.get_stock_info(self.deal_date,
                                            self.count - 1,
                                            self.stock_code,
                                            vol=True,
                                            order='desc')
        for r in row:
            x[r] = row[r]

        y = self.get_today(price=True)
        col = self.rc_db_mgr.get_stock_info(self.deal_date,
                                            self.count - 1,
                                            self.stock_code,
                                            price=True,
                                            order='desc')
        for c in col:
            y[c] = col[c]

        rows = {
            '거래량': x,
            '주가': y,
        }
        get_bar_chart(rows, self.local_image_whole_path)
        return f"""
            <div class="module-chart text-center bgcolor">
                <img style="height:auto; max-width:100%;" src="{self.image_url}">               
            </div>     
        """

    def get_today(self, vol=False, price=False):
        if vol:
            col = ['acc_trade_vol']
        elif price:
            col = ['close']
        sql = f"""
            select  d_cntr,
                    {', '.join(col)}
            from    a3_curprice
            where   stk_code = '{self.stock_code}'
            """
        row = self.rc_db_mgr.get_all_rows(sql)
        x = {}
        if not row:
            return x
        for r in row:
            id = r[0]
            x[id] = r[1]
        return x
