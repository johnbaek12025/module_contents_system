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
)

logger = logging.getLogger(__name__)


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.dealing_type = None
        self.subject = None
        self.unit = "cnt"
        self.use_ftp = True
        self.ts_data_count = 20

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
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.stock_name},",
                "color": None
            },
            {
                "text": f"장중 {get_kor_name(self.subject)} 대량 순매수",
                "color": get_size_color(self.dealing_type),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = f"""
            <table style="height:auto; width:650px;">
            {self.get_bottom_tr()}
            </table>
        """
        return {"news_cnts": news_cnts}

    def get_bottom_tr(self):

        stock_list = self.data_db_mgr.get_stock_list_from_analysis_table(
            self.analysis_type,
            self.deal_date,
            self.dealing_type,
            self.subject,
            self.market,
            sort_by="AVG_SONMEME_ABSCNT",
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

        r = get_bottom_values(
            self.data_db_mgr,
            self.analysis_type,
            self.deal_date,
            self.dealing_type,
            [t1, t2, t4, t5],
            self.stock_code,
            self.unit,
        )

        r1 = r[t1]
        r2 = r[t2]

        r4 = r[t4]
        r5 = r[t5]

        temp1 = (f'{r2["sub"]} {r2["abs_val"]} {r2["unit"]} {r2["dt"]}, '
                 f'{r1["sub"]} {r1["abs_val"]} {r1["unit"]} {r1["dt"]}, ')

        temp2 = (f'{r4["sub"]} {r4["abs_val"]} {r4["unit"]} {r4["dt"]}, '
                 f'{r5["sub"]} {r5["abs_val"]} {r5["unit"]} {r5["dt"]}, ')
        return f"""
            <div class="module-tbl-txt mt-20">
                <div class="dot"> 25일 14:20 매매 동향 : {temp1} </div>
                <div class="dot"> 기관 상세 동향 : {temp2} </div>
            </div>
        """