import logging
from adm import to_int
from adm.ad_manager import ADManager
from dateutil.relativedelta import relativedelta
from datetime import datetime
from adm.jobs.workshop.commom_bjh import get_cybos7254
from .html.nws01_html import get_row_html, get_html
from adm.jobs import (
    get_dealing_str,
    get_kor_name,
    circle_symbol,
    get_size_str,
    get_size_symbol,
)

logger = logging.getLogger(__name__)


class Contents(ADManager):
    def __init__(self):
        super().__init__()
        self.dealing_type = None
        self.subject = None
        self.sort = None
        self.period_len = None

    def set_analysis_target(self):
        columns = ["stk_code", "stk_name", "period_len"]

        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        self.period_len = row["period_len"]
        self.stock_name = row["stk_name"]
        self.stock_code = row["stk_code"]

        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"

    def make_news_info(self):
        news_title_list = [
            {"text": f"{self.stock_name},", "color": None},
            {"text": f"오늘 시장 관심 집중", "color": "red"},
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        rows = self.get_news_issue()
        row_html = get_row_html(rows)

        news_cnts = get_html(row_html)
        return {"news_cnts": news_cnts}

    def get_news_issue(self):
        sql = f"""
                select stk_name,datedeal, title_part2 as title, cnt                                        
                from nws01
                where period_len ='{self.period_len}'
                and cnt >=5
                AND ROWNUM <= 6
                order by datedeal asc, cnt desc
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            row = {
                "stkcode": r[0],
                "datedeal": r[1],
                "title": r[2],
                "cnt": r[3],
            }
            x.append(row)
        return x
