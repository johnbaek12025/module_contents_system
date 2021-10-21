import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from .workshop.chart import get_bar_chart, get_bar_chart_data
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
        self.market = None
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
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.market = row.get("market")
        self.dealing_type = row.get("sonmeme_type").lower()
        self.subject = row.get("customer_type").lower()
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"


    def make_news_info(self):
        temp = f"{get_size_str(self.dealing_type)}"
        news_title_list = [
            {
                "text": f"{self.stock_name},",
                "color": None
            },
            {
                "text": f"장중{get_kor_name(self.subject)} 보유비중 {temp}",
                "color": get_size_color(self.dealing_type),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):

        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        stock_list = self.data_db_mgr.get_stock_list_from_analysis_table(
            self.analysis_type,
            self.deal_date,
            self.dealing_type,
            self.subject,
            self.market,
            sort_by="RK",
            sort_order="ASC",
        )
        stock_list = get_stock_list_str(stock_list)

        t1 = self.subject
        t2 = "for" if t1 == "org" else "org"

        r = get_bottom_values(
            self.data_db_mgr,
            self.analysis_type,
            self.deal_date,
            self.dealing_type,
            [t1, t2],
            self.stock_code,
            self.unit,
        )

        r1 = r[t1]

        return f"""
            <div class="module-tbl-txt">
                <strong class="title title-s">{r1["sub"]} {r1["dt"]} {r1["abs_val"]} {r1["unit"]} (상장주식수대비 {r1["ratio"]}%)</strong>
            </div>
        """

    def get_middle_tr(self):
        stock_list = self.data_db_mgr.get_stock_list_from_analysis_table(
            self.analysis_type,
            self.deal_date,
            self.dealing_type,
            self.subject,
            self.market,
            sort_by="RK",
            sort_order="asc",
        )
        stock_list = get_stock_list_str(stock_list)

        t1 = self.subject
        t2 = "for" if t1 == "org" else "org"

        r = get_bottom_values(
            self.data_db_mgr,
            self.analysis_type,
            self.deal_date,
            self.dealing_type,
            [t1, t2],
            self.stock_code,
            self.unit,
        )

        r1 = r[t1]
        r2 = r[t2]

        return f"""
            <div class="module-tbl-txt mt-20">
                <div class="dot">  {r2["sub"]} {r2["dt"]}: {r2["abs_val"]} {r2["unit"]}</div>
                <div class="dot c999"> {r1["sub"]} 보유비중 {r1["size"]}종목: {stock_list}</div>
            </div>
        """