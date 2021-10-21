import datetime
import logging
from adm import to_int
from adm.jobs import separate_yyyymmdd
from adm.ad_manager import ADManager
from adm.jobs.workshop.chart import Chart, get_bar_chart, get_bar_chart_data
from adm.jobs.workshop.common_cyg import get_bottom_values, get_stock_list_str
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

    def set_analysis_target(self):
        columns = [
            'customer_type', 'sonmeme_type', 'stk_code', 'sn', 'stk_name'
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.subject = row.get('customer_type')
        self.dealing_type = row.get('sonmeme_type')
        self.stock_code = row.get('stk_code')
        self.sn = row.get('sn')
        self.stock_name = row.get('stk_name')
        period = lambda x: "before" if x >= 8 else "after"
        self.timing = period(int(self.analysis_id))
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text":
                f"신규 {get_dealing_str(self.dealing_type, with_son=False)} 리포트 발표",
                "color": get_size_color(self.dealing_type),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        print(self.analysis_id)
        news_cnts = f"""
            <table style="height:auto; width:650px;">
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr()}
            </table>
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        rows = self.data_db_mgr.get_report(self.deal_date, self.stock_code, 2)

        html = '<div class="module-tbl-txt mt-20">'
        for r in rows:
            deal_date = r["deal_date"]
            _, mm, dd = separate_yyyymmdd(deal_date)
            stock_firm = r["stock_firm"]
            title = r["title"]

            html += f"<div> {mm}/{dd} ({stock_firm}) {title} </div>"

        html += "</div>"
        return html

    def get_middle_tr(self):
        kor_subject = get_kor_name(self.subject)
        return f"""
            <div class="module-tbl-txt mt-20">
                {kor_subject} 순매매 동향
            </div>
        """

    def get_bottom_tr(self):
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