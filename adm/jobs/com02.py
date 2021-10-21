import logging
from adm import to_int
from adm.jobs.html.com02_html import get_html, get_table
from adm.ad_manager import ADManager
from adm.jobs import (
    get_dealing_str,
    get_kor_name,
    get2_kor_name,
    circle_symbol,
    get_size_str,
    get_size_symbol,
)

logger = logging.getLogger(__name__)


def html_table(rows):
    pass


class Contents(ADManager):
    def __init__(self):
        super().__init__()
        self.market = None
        self.period_len = None
        self.stock_code = None

    def set_analysis_target(self):
        columns = ["market", "period_len", "stk_code"]

        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        self.period_len = row.get("period_len")
        self.market = row.get("market")
        self.stock_code = row.get("stk_code")
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"

    def make_news_info(self):
        news_title_list = [
            {"text": f"{self.deal_date_dd}일 {self.stock_name},", "color": None},
            {
                "text": f"관련글 수 상위 TOP15 ",
                "color": "red",
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = None
        row = self.get_result()
        rows = get_table(row)
        news_cnts = get_html(rows)
        return {"news_cnts": news_cnts}

    def get_result(self, a=[]):
        cols = self.get_for_data()
        for r in cols:
            if self.stock_code == r.get("stkcode"):
                a.append("p")
                break
        if a:
            return cols
        else:
            rows = self.get_for_data_2()
            return rows

    def get_for_data(self):
        sql = f"""
            select rk,stk_code, stk_name, cnt
            from com02
            where market ='{self.market}' 
            and datedeal='{self.deal_date}'
            and period_len ='{self.period_len}'
            and rownum <= 15
            ORDER BY RK ASC
        """
        x = []
        rows = self.data_db_mgr.get_all_rows(sql)

        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "rk": r[0],
                    "stock_code": r[1],
                    "stock_name": r[2],
                    "cnt": r[3],
                }
            )
        return x

    def get_for_data_2(self):
        sql = f"""
            select rk,stk_code, stk_name, cnt
            from com02
            where market ='{self.market}' 
            and datedeal='{self.deal_date}'
            and period_len ='{self.period_len}'
            and rownum <= 20
            ORDER BY RK ASC
        """

        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "rk": r[0],
                    "stock_code": r[1],
                    "stock_name": r[2],
                    "cnt": r[3],
                }
            )
        return x
