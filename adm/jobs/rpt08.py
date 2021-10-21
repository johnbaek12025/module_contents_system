import logging
from .html.rpt08_html import get_row_html, get_html
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
        self.subject = None
        self.sort = None
        self.dir = None
        self.dir_str = None

    def set_analysis_target(self):
        columns = ["stk_code", "stk_name"]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)

        self.stock_name = row["stk_name"]
        self.stock_code = row["stk_code"]

        analysis_list = {
            "01": {
                "dir": "down",
                "dir": f"히향 {down_arrow_symbol}"
            },
            "02": {
                "dir": "down",
                "dir": f"하향 {down_arrow_symbol}"
            },
            "03": {
                "dir": "up",
                "dir_str": f"상향 {up_arrow_symbol}"
            },
            "04": {
                "dir": "up",
                "dir_str": f"상향 {up_arrow_symbol}"
            },
        }
        analysis_target = analysis_list[self.analysis_id]
        self.dir_str = analysis_target["dir_str"]
        self.dir = analysis_target["dir"]
        self.org_evaluation_result = self.get_report()
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"

    def make_news_info(self):
        count = self.get_count(self.org_evaluation_result, self.dir)
        news_title_list = [
            {
                "text": f"최근 한달 {self.stock_name},",
                "color": None
            },
            {
                "text": f"증권사 {count}곳 목표가 {self.dir_str}",
                "color": "red"
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        row_html = get_row_html(self.org_evaluation_result)
        news_cnts = get_html(row_html)
        return {"news_cnts": news_cnts}

    def get_count(self, rows, dir):
        count = 0
        for r in rows:
            goal_1 = r["goal_1"]
            goal_2 = r["goal_2"]

            if dir == "up":
                if goal_1 > goal_2:
                    count += 1
            else:
                if goal_1 < goal_2:
                    count += 1
        return count

    def get_report(self):
        sql = f"""
            WITH BASE AS (
                SELECT  DATEDEAL, CODE, ORG_CODE, GOAL_VALUE, CONT_A,                
                        ROW_NUMBER() OVER(PARTITION BY ORG_CODE, CODE ORDER BY DATEDEAL DESC, SN desc) AS RN
                FROM    TP_STOCK.ORG_OPINION_MANUAL_MOD
                WHERE   DATEDEAL BETWEEN DATA_ENG.FUNC_ADD_DAY('{self.deal_date}', -30)
                                 AND     DATA_ENG.FUNC_ADD_DAY('{self.deal_date}', 0)
                AND     CODE = '{self.stock_code}'                  
                AND     GOAL_VALUE IS NOT NULL
            )
            SELECT  A.DATEDEAL, C.ORG_NAME, CONT_A, 
                    A.GOAL_VALUE AS GOAL_1, B.GOAL_VALUE AS GOAL_2
            FROM    (
                        SELECT  DATEDEAL, CODE, ORG_CODE, GOAL_VALUE
                        FROM    (
                                    SELECT  DATEDEAL, CODE, ORG_CODE, GOAL_VALUE
                                    FROM    BASE A
                                    WHERE   A.RN = 1
                                    ORDER BY DATEDEAL DESC
                                ) A
                        WHERE   ROWNUM <= 5
                    ) A
                    , BASE B
                    , TP_STOCK.STOCK_CHANGKU_CODE C        
            WHERE   A.CODE     = B.CODE
            AND     A.ORG_CODE = B.ORG_CODE
            AND     A.ORG_CODE = C.ORG_NUM
            AND     B.RN = 2
            ORDER BY DATEDEAL DESC
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            row = {
                "deal_date": r[0],
                "stock_firm": r[1],
                "title": r[2],
                "goal_1": r[3],
                "goal_2": r[4],
            }
            x.append(row)
        return x
