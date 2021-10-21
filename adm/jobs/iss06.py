import logging
from .html.iss06_html import get_row_html, get_html
from adm import to_int
from adm.ad_manager import ADManager
from adm.jobs import (
    get_dealing_str,
    get_kor_name,
    up_arrow_symbol,
    down_arrow_symbol,
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
        self.dir = None
        self.dir_str = None
        self.issn = None
        self.is_str = None

    def set_analysis_target(self):
        columns = ["is_str", "issn"]

        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        self.is_str = row["is_str"]
        self.issn = row["issn"]

        analysis_list = {
            "01": {"dir": "up", "dir_str": f"상승"},
            "02": {"dir": "down", "dir_str": f"하락"},
        }
        analysis_target = analysis_list[self.analysis_id]
        self.dir_str = analysis_target["dir_str"]
        self.dir = analysis_target["dir"]
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"

    def make_news_info(self):
        news_title_list = [
            {"text": f"신규 이슈 포착", "color": None},
            {"text": f"{self.is_str}", "color": "red"},
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        rows = self.get_news_issue()
        if len(rows) < 5:
            for i in range(5 - len(rows)):
                rows.append({"stkname": "-", "ratio": "-", "header": "-"})
        print(rows)
        row_html = get_row_html(rows)
        news_cnts = get_html(row_html)
        return {"news_cnts": news_cnts}

    def get_news_issue(self):
        sql = f"""
                SELECT C.STK_NAME, B.RATIO, A.HEADER
                FROM TP_STOCK.FI_OUTLINE_CONT A
                JOIN ISS06 B
                ON (A.CODE = B.STK_CODE)
                JOIN TP_STOCK.a3_curprice C
                ON(B.STK_NAME =C.STK_NAME)
                WHERE B.ISSN = '{self.issn}'
                AND ROWNUM <= 5 
                ORDER BY B.RATIO DESC    
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            row = {
                "stkname": r[0],
                "ratio": r[1],
                "header": r[2],
            }
            x.append(row)
        return x
