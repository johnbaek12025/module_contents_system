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
        if func:
            if func(bar):
                set_bar_chart_data.append(bar)
        else:
            set_bar_chart_data.append(bar)
    return set_bar_chart_data


def get_bar_chart(rows: dict, local_image_whole_path, days=None):
    chart_dict = {
        "face_color": "whitesmoke",
        "tick_interval": 2,
        "spine_top": False,
        "grid": False
    }
    bc = Chart(**chart_dict)
    for r in rows.keys():
        if r == 'bar':
            bar_chart_data = get_bar_chart_data(rows=rows['bar'], func=set_bar)
            bc.add_data(bar_chart_data, chart_type="bar")
        elif r == 'plot':
            bar_chart_data = get_bar_chart_data(rows=rows['plot'])
            bc.add_data(bar_chart_data, colors='green', twinx=True, label='주가')
        bc.finalize_chart(local_image_whole_path, ticks=False, leg=['주가'])


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.dealing_type = None
        self.subject = None
        self.use_ftp = True
        self.continuous_days_count = None
        self.rk = None
        self.unit = 'amt'
        self.stock_code = None
        self.stock_name = None
        self.count = 3
        self.tr_acc_count = 20
        self.process_condition = ADManager.SC_CUSTOM

    def set_analysis_target(self):
        columns = [
            "customer_type", "sonmeme_type", "stk_code", "stk_name",
            "continuous_days_count", "rk"
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.subject = row.get('customer_type').lower()
        self.dealing_type = row.get('sonmeme_type').lower()
        self.stock_name = row.get('stk_name')
        self.stock_code = row.get('stk_code')
        self.continuous_days_count = row.get('continuous_days_count')
        self.rk = row.get('rk')
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text":
                f"{get_kor_name(self.subject)} {get_dealing_str(self.dealing_type, True)} {self.continuous_days_count}일 연속",
                "color": get_size_color(self.dealing_type),
            },
        ]
        return {"news_title": news_title_list}

    def custom_process_condition(self):
        # implement the details in the inherited class.
        """
           아래 쿼리의 결과 in (3,5,10,20) : 콘텐츠 생성함 (insert)
           아래 쿼리의 결과 not in (3,5,10,20)  :  콘텐츠 생성안함 (SKIP)
           select CONTINUOUS_DAYS_COUNT from BUY07
           where INFO_SEQ = '149'  --> 자기자신의 ALS_MAIN.SN
        """
        columns = ["continuous_days_count"]

        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        days_count = row.get("continuous_days_count")
        if days_count in {3, 5, 10, 20}:
            return True, {}

        return False, {}

    def make_news_cnts(self):
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}
        """
        print(news_cnts)
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        return f"""
            <div class="module-tbl-txt">
                <strong class="title title-s">{get_kor_name(self.subject)} 순매매 동향</strong>                
                <div style = "float:left">
                <span>(단위: {get_unit_str(self.unit)})</span>
                </div>
                <div style = "float:right">
                <span>(단위: 원)</span>
                </div>
            </div>            
        """

    def get_middle_tr(self):
        price = self.get_continuous_price()
        amt = self.get_continuous_amt()
        rows = {
            'plot': price,
            'bar': amt,
        }
        get_bar_chart(rows=rows,
                      local_image_whole_path=self.local_image_whole_path)
        return f"""
            <div class="module-chart text-center bgcolor">
                <img style="height:auto; max-width:100%;" src="{self.image_url}">               
            </div>     
        """

    def get_continuous_amt(self):
        rows = self.data_db_mgr.get_7254_ts_data(self.stock_code,
                                                 subject=self.subject,
                                                 dealing_type='sonmeme',
                                                 unit=self.unit,
                                                 deal_date=self.deal_date,
                                                 count=self.tr_acc_count)
        return rows

    def get_continuous_price(self):
        rows = self.rc_db_mgr.get_stock_info(self.deal_date,
                                             self.tr_acc_count,
                                             self.stock_code,
                                             price=True)
        return rows
