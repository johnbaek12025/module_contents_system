import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from .workshop.chart import Chart, get_bar_chart, get_bar_chart_data
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
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


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.dealing_type = None
        self.subject = None
        self.unit = 'amt'
        self.use_ftp = True
        self.ts_data_count = 20
        self.process_condition = ADManager.SC_ONCE

    def set_analysis_target(self):
        columns = [
            "sonmeme_type", "customer_type", "stk_code", "stk_name", "market"
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.dealing_type = row.get("sonmeme_type").lower()
        self.subject = row.get("customer_type").lower()
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.market = row.get("market")
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text": f"{get_kor_name(self.subject)} 대량 순매수",
                "color": get_size_color(self.dealing_type),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = f"""
            <table style="height:auto; width:650px;">
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr()}
            </table>
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        kor_subject = get_kor_name(self.subject)
        return f"""
            <div class="module-tbl-txt">
                <strong class="title title-s">{kor_subject} 순매매 동향</strong>
            </div>
            <div class="module-tbl-guide mt-15">
                <span>(단위 {get_unit_str(self.unit)})</span>
            </div>
        """

    def get_middle_tr(self):
        rows = self.rc_db_mgr.get_7254_ts_data(
            self.stock_code,
            self.subject,
            "sonmeme",
            self.unit,
            self.deal_date,
            self.ts_data_count,
        )
        get_bar_chart(rows, self.local_image_whole_path)
        return f"""
            <div class="module-chart text-center bgcolor">
                <img style="height:auto; max-width:100%;" src="{self.image_url}">               
            </div>     
        """

    def get_bottom_tr(self):

        stock_list = self.data_db_mgr.get_stock_list_from_analysis_table(
            self.analysis_type,
            self.deal_date,
            self.dealing_type,
            self.subject,
            self.market,
            sort_by="AVG_SONMEME_ABSCNT_20DAY",
            sort_order="DESC",
        )
        stock_list = get_stock_list_str(stock_list)

        if self.subject == "org":
            t1 = "org"
            t2 = "for"
            t3 = "etc"
        elif self.subject == "for":
            t1 = "for"
            t2 = "org"
            t3 = "etc"
        elif self.subject == "etc":
            t1 = "etc"
            t2 = "for"
            t3 = "org"
        elif self.subject == "org3":
            t1 = "org3"
            t2 = "org"
            t3 = "for"
        elif self.subject == "org6":
            t1 = "org6"
            t2 = "org"
            t3 = "for"
        elif self.subject == "org9":
            t1 = "org9"
            t2 = "org"
            t3 = "for"
        t4 = "org3"
        t5 = "org6"
        t6 = "org9"

        r = get_bottom_values(
            self.data_db_mgr,
            self.analysis_type,
            self.deal_date,
            self.dealing_type,
            [t1, t2, t3, t4, t5, t6],
            self.stock_code,
            self.unit,
        )

        r1 = r[t1]
        r2 = r[t2]
        r3 = r[t3]
        r4 = r[t4]
        r5 = r[t5]
        r6 = r[t6]

        temp1 = (f'{r1["sub"]} {r1["abs_val"]} {r1["unit"]} {r1["dt"]}, '
                 f'{r2["sub"]} {r2["abs_val"]} {r2["unit"]} {r2["dt"]}, '
                 f'{r3["sub"]} {r3["abs_val"]} {r3["unit"]} {r3["dt"]}')

        temp2 = (f'{r4["sub"]} {r4["abs_val"]} {r4["unit"]} {r4["dt"]}, '
                 f'{r5["sub"]} {r5["abs_val"]} {r5["unit"]} {r5["dt"]}, '
                 f'{r6["sub"]} {r6["abs_val"]} {r6["unit"]} {r6["dt"]}')
        return f"""
            <div class="module-tbl-txt mt-20">
                <div class="dot"> 25일 순매매 동향 : {temp1} </div>
                <div class="dot"> 기관 상세 동향 : {temp2} </div>
                <div class="dot c999"> {r1["sub"]} 대량 {r1["dt"]}종목: {stock_list}</div>
            </div>
        """