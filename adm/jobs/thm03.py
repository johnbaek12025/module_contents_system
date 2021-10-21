import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from .workshop.chart import Chart, get_bar_chart_data
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import get_stock_name, get_cybos7254, get_amt_theme
from adm.jobs import (get_kor_name, get_dealing_str, get_size_str,
                      get_size_symbol, get_size_color, get_unit_str,
                      circle_symbol, get_sort)

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
        bar.color = "blue"
    return True


def get_bar_chart(rows, local_image_whole_path):
    chart_dict = {
        "face_color": "whitesmoke",
        "grid_color": None,
        "spine_top": False,
        "spine_left": False,
        "spine_right": False,
        "xaxis_format": "%m/%d",
        "tick_position": "left",
        "tick_interval": 4,
    }
    bc = Chart(**chart_dict)
    bar_chart_data = get_bar_chart_data(rows=rows, func=set_bar)
    bc.add_data(bar_chart_data, chart_type="bar", xhline=0)
    bc.finalize_chart(local_image_whole_path, 4)


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.dealing_type = None
        self.subject = None
        self.unit = 'amt'
        self.use_ftp = True
        self.ts_data_count = 20
        self.accumulated_days = 3
        self.count = 3

    def set_analysis_target(self):
        columns = ['theme_code', 'customer_type', 'theme_name', 'sonmeme_type']
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.theme_code = row.get('theme_code')
        self.theme_name = row.get('theme_name')
        self.subject = row.get('customer_type').lower()
        self.dealing_type = row.get('sonmeme_type').lower()
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.theme_name} 테마,",
                "color": None
            },
            {
                "text":
                f"{get_kor_name(self.subject)}  {get_kor_name(self.dealing_type)}세 포착",
                "color": get_size_color(self.dealing_type),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr()}
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        kor_subject = get_kor_name(self.subject)
        return f"""
            <div class="module-tbl-txt">
                <strong class="title title-s">{get_kor_name(self.subject)} 순매매 동향</strong>
                <span>(단위: {get_unit_str(self.unit)})</span>
            </div>            
        """

    def get_middle_tr(self):
        rows = self.get_cybos_theme_data()
        get_bar_chart(rows, self.local_image_whole_path)
        return f"""
            <div class="module-chart text-center bgcolor">
                <img style="height:auto; max-width:100%;" src="{self.image_url}">               
            </div>     
        """

    def get_bottom_tr(self):
        amt = self.get_accu_amt()
        stkname = self.get_related_name()
        return f"""
            <div class="module-tbl-txt mt-20">
                <div class="dot"> {get_kor_name(self.subject)} {get_kor_name(self.dealing_type)}세 포착: 최근{self.accumulated_days}일 {get_dealing_str(amt[self.subject])} {abs(amt[self.subject]/100)}억원</div>
                <div class="c999 dot"> 최근 주도 종목: {stkname} 등</div>      
            </div>
        """

    def get_cybos_theme_data(self):
        sql = f"""
            {get_amt_theme(
                self.subject, 
                self.unit, 
                self.theme_code, 
                self.deal_date, 
                self.ts_data_count
                )}
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0]
            x[id] = r[1]
        return x

    def get_accu_amt(self):
        sql = f"""
            {get_amt_theme(self.subject, 
                           self.unit, 
                           self.theme_code, 
                           self.deal_date, 
                           self.accumulated_days
                           )}
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        if not rows:
            return None
        row = rows[0]
        return_dict = {}
        return_dict[self.subject] = row[1]
        return return_dict

    def get_related_name(self):
        codes = self.data_db_mgr.get_related_stock_theme(
            self.theme_code, self.deal_date, self.count)
        col = []
        for i, name in enumerate(codes):
            col.append(name)
            if i > 2:
                break
        return ', '.join(col)