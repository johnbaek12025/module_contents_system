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
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        temp = f"{get_size_str(self.dealing_type)} {get_size_symbol(self.dealing_type)}"
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text": f"{get_kor_name(self.subject)} 보유비중 {temp}",
                "color": get_size_color(self.dealing_type),
            },
        ]
        return {"news_title": news_title_list}

    def custom_process_condition(self):
        """아래 쿼리의 결과 0 => 콘텐츠 생성함 (insert)
        아래 쿼리의 결과 1 => 콘텐츠 생성안함 (SKIP)
        select COUNT(*) from ALS_MAIN
        where DATEDEAL = '20201201'  -->오늘기준 전 거래일
        AND STK_CODE = '00910' --> 동일종목코드
        AND INFO_CODE = 'AL_BUY02_01';  --> 우측표참고
        """
        row = self.data_db_mgr.check_if_exist_in_als_main(
            self.deal_date, self.info_code.upper(), stock_code=self.stock_code)
        if not row:
            return True, {}
        return False, {}

    def make_news_cnts(self):

        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr()}
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
        rows = self.data_db_mgr.get_7254_ts_data(
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
            sort_by="RK",
            sort_order="desc",
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
                <div class="dot"> {r1["sub"]} {r1["dt"]}: {r1["abs_val"]} {r1["unit"]} (<span class={r1["size_style"]}>상장주식수대비 {r1["ratio"]}%</span>)</div>
                <div class="dot">  {r2["sub"]} {r2["dt"]}: {r2["abs_val"]} {r2["unit"]}</div>
                <div class="dot c999"> {r1["sub"]} 보유비중 {r1["size"]}종목: {stock_list}</div>
            </div>
        """
