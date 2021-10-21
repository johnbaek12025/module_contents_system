from datetime import datetime
import datetime as dt
import logging
from adm import to_int
from adm.jobs.html.rpt01_html import get_table, get_html, get_info, get_day_html
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


class Contents(ADManager):
    def __init__(self):
        super().__init__()
        self.rk = None
        self.stock_code = None
        self.stock_name = None
        self.start_date_period_len_5 = None
        self.start_date_period_len_1 = None

    def set_analysis_target(self):
        columns = [
            "rk",
            "stk_code",
            "stk_name",
            "start_date_period_len_5",
            "start_date_period_len_1",
        ]
        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        self.rk = row["rk"]
        self.stock_name = row["stk_name"]
        self.stock_code = row["stk_code"]

        self.start_date_period_len_5 = row["start_date_period_len_5"]
        self.start_date_period_len_1 = row["start_date_period_len_1"]
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"

    def make_news_info(self):
        news_title_list = [
            {"text": f"{self.deal_date_dd}일 {self.stock_name},", "color": None},
            {
                "text": f"증권사 리포트수 TOP{self.rk}",
                "color": "red",
            },
        ]
        return {"news_title": news_title_list}

    def custom_process_condition(self):
        # implement the details in the inherited class.
        """
        period_len = 5  : 콘텐츠 생성함 (insert)
        period_len IS NOT 5   :  콘텐츠 생성안함 (SKIP)
        select PERIOD_LEN from RPT01
        where INFO_SEQ = '149'--> 자기자신의 ALS_MAIN.SN
        """
        week = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        current = dt.datetime.strptime(self.deal_date, "%Y%m%d").weekday()

        columns = ["period_len"]
        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        period_len = row.get("period_len")

        if current == 4:
            return True, {}
        elif current != 4:
            return False, {}
        elif period_len < 5 or not period_len:
            return False, {}
        elif len(period_len) <= 3:
            return False, {}
        else:
            return True, {}

    def make_news_cnts(self):
        news_cnts = None
        rows = self.get_result()
        table = get_table(rows)
        if len(rows) < 10:
            for i in range(10 - len(rows)):
                rows.append({"rk": "-", "stock_name": "-", "report_cnt": "-"})
        table = get_table(rows)

        info = self.get_count()
        org_info = get_info(info)

        days = self.get_day_data()
        day_html = get_day_html(days)

        news_cnts = get_html(table, org_info, day_html)
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
                select rk,stk_code,stk_name,report_cnt from rpt01
                where period_len =5
                and datedeal = TO_NUMBER('{self.deal_date}')
                and rownum <=10
                order by rk asc, report_cnt desc
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
                    "report_cnt": r[3],
                }
            )
        return x

    def get_for_data_2(self):
        sql = f"""
                select rk,stk_code,stk_name,report_cnt from rpt01
                where period_len =5
                and datedeal = TO_NUMBER('{self.deal_date}')
                and rownum <=10
                order by rk asc, report_cnt desc
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
                    "report_cnt": r[3],
                }
            )

        return x

    def get_count(self):
        x = self.get_org_data()
        if len(x) < 4:
            4 - len(x)
            return x
        else:
            return x

    def get_org_data(self):
        sql = f"""
                    SELECT  A.DATEDEAL,                    
                            B.ORG_NAME,
                            A.CONT_A
                    FROM    TP_STOCK.STOCK_CHANGKU_CODE B
                    INNER JOIN    TP_STOCK.ORG_OPINION_MANUAL_MOD A
                    ON  B.ORG_NUM = A.ORG_CODE
                    INNER JOIN   RPT01 C
                    ON  A.DATEDEAL = C.START_DATE_PERIOD_LEN_1
                    and c.DATEDEAL BETWEEN  '{self.start_date_period_len_5}' AND '{self.deal_date}' 
                    and c.info_seq = '{self.info_seq}'                        
                    and rownum <=3
                    ORDER BY A.SN DESC
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "datedeal": r[0][4:6] + "/" + r[0][6:8],
                    "org_name": r[1],
                    "cont_a": r[2],
                }
            )
        return x

    def get_day_data(self):
        sql = f"""
                select start_date_period_len_5, datedeal from rpt01
                where datedeal = '{self.deal_date}'
                and rownum =1
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "start_date_period_len_5": r[0][4:6] + "/" + r[0][6:8],
                    "deal_date": r[1][4:6] + "/" + r[1][6:8],
                }
            )
        return x
