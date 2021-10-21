from datetime import datetime
import datetime as dt

import logging
from adm import to_int
from adm.jobs.html.rpt02_html import (
    get_table,
    get_html,
    get_day_html,
    get_info_html,
)
from adm.ad_manager import ADManager
from adm.jobs import (
    get_dealing_str,
    get_kor_name,
    get2_kor_name,
    circle_symbol,
    get_size_str,
    get_size_symbol,
    get_week,
)

logger = logging.getLogger(__name__)


class Contents(ADManager):
    def __init__(self):
        super().__init__()
        self.rk = None
        self.stock_code = None
        self.stock_name = None
        self.goal_value = None
        self.gap_ratio = None
        self.process_condition = ADManager.SC_CUSTOM

    def set_analysis_target(self):
        columns = [
            "rk",
            "stk_code",
            "stk_name",
            "goal_value",
            "gap_ratio",
        ]
        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        self.rk = row["rk"]
        self.stock_name = row["stk_name"]
        self.stock_code = row["stk_code"]
        self.goal_value = row["goal_value"]
        self.gap_ratio = row["gap_ratio"]
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/report"

    def make_news_info(self):
        news_title_list = [
            {"text": f"{self.deal_date_dd}일 {self.stock_name},", "color": None},
            {
                "text": f"목표가 상위 종목 TOP{self.rk}",
                "color": "red",
            },
        ]
        return {"news_title": news_title_list}

    def custom_process_condition(self):
        """
        금요일인 정보만  true, 나머지는 false
        """
        week = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        current = dt.datetime.strptime(self.deal_date, "%Y%m%d").weekday()

        if current == 4:
            return True, {}
        else:
            return False, {}

    def make_news_cnts(self):
        news_cnts = None
        rows = self.get_result()

        if len(rows) < 10:
            for i in range(10 - len(rows)):
                rows.append(
                    {"rk": "-", "stock_name": "-", "goal_value": "-", "gap_ratio": "-"}
                )
        table = get_table(rows)

        info = self.get_count()
        info_html = get_info_html(info)
        table = get_table(rows)

        days = self.get_day_data()
        day_html = get_day_html(days)

        week = (
            self.deal_date_mm
            + "월 "
            + self.deal_date_dd
            + "일 "
            + get_week(self.deal_date)
        )

        news_cnts = get_html(table, day_html, info_html, week)
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
            select rk, stk_code, stk_name, goal_value, TRUNC(gap_ratio*100) ratio
            from rpt02
            where period_len =5
            AND (DATEDEAL = '{self.deal_date}'
            and rownum <= 5)
            order by rk asc
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
                    "datedeal": r[2][4:6] + "/" + r[2][6:8],
                    "stock_name": r[3],
                    "goal_value": r[4],
                    "gap_ratio": r[5],
                }
            )

        return x

    def get_for_data_2(self):
        sql = f"""
            select rk, stk_code, stk_name, goal_value, TRUNC(gap_ratio*100) ratio
            from rpt02
            where period_len =5
            AND (DATEDEAL = '{self.deal_date}'
            and rownum <= 10)
            order by rk asc
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
                    "datedeal": r[2][4:6] + "/" + r[2][6:8],
                    "stock_name": r[3],
                    "goal_value": r[4],
                    "gap_ratio": r[5],
                }
            )

        return x

    def get_day_data(self):
        sql = f"""
                select  a.start_date_period_len_5,a.datedeal
                from rpt01 a
                join rpt02 b
                on(a.start_date_period_len_1 = b.datedeal)
                where b.period_len =5
                AND a.datedeal= '{self.deal_date}'
                and rownum =1
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "datedeal_5": r[0][4:6] + "/" + r[0][6:8],
                    "datedeal_1": r[1][4:6] + "/" + r[1][6:8],
                }
            )

        return x

    def get_count(self):
        x = self.get_org_data()
        if len(x) < 4:
            2 - len(x)
            return x
        else:
            return x

    def get_org_data(self):
        sql = f"""
                  SELECT  A.DATEDEAL,                    
                          B.ORG_NAME,
                          A.CONT_A
                  FROM    TP_STOCK.STOCK_CHANGKU_CODE B
                  INNER JOIN   TP_STOCK.ORG_OPINION_MANUAL_MOD A
                  ON  B.ORG_NUM = A.ORG_CODE
                  INNER JOIN   RPT01 C
                  ON  A.DATEDEAL = c.datedeal
                  join rpt02 d
                  on c.stk_code = d.stk_code
                  where (c.stk_code = '{self.stock_code}' 
                  AND c.DATEDEAL BETWEEN '{self.deal_date}-5' AND '{self.deal_date}')
                  and rownum =1
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
