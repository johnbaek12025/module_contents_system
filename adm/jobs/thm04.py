import logging
from .html.thm04_html import get_row_html, get_html
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
        self.signal = None

        self.theme_name = None
        self.avgdiff = None

    def set_analysis_target(self):
        columns = [
            "theme_name",
            "theme_code",
            "avgdiff",
        ]

        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        self.theme_name = row["theme_name"]
        self.theme_code = row["theme_code"]
        self.avgdiff = row["avgdiff"]

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
            {"text": f"{self.deal_date_dd}일 {self.theme_name},", "color": None},
            {"text": f"{self.avgdiff}", "color": "red"},
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        rows = self.get_theme()
        row_html = get_row_html(rows)
        news_cnts = get_html(row_html)
        return {"news_cnts": news_cnts}

    def get_theme(self):
        sql = f"""
          SELECT  A.STKNAME,
                    CASE WHEN A.YDAY = 0 THEN 0 
                        ELSE ROUND((A.TDAY - A.YDAY) / A.YDAY * 100, 2) 
                    END AS RATIO
                    ,B.HEADER
            FROM    (
                        SELECT  STKCODE,STKNAME,
                                SUM(DECODE( DATEDEAL, TO_CHAR(TO_DATE('{self.deal_date}', 'YYYYMMDD')-1,'YYYYMMDD') , CURPRICE, 0)) AS YDAY,
                                SUM(DECODE( DATEDEAL, '{self.deal_date}', CURPRICE, 0)) AS TDAY
                        FROM    (
                                    SELECT  DATEDEAL, STKCODE, CURPRICE, STKNAME,
                                            ROW_NUMBER() OVER ( PARTITION BY DATEDEAL, STKCODE, STKNAME ORDER BY TIMEDEAL DESC) AS RN
                                    FROM    RC_TEAM.CYBOS_CPSVR7210
                                    WHERE   DATEDEAL IN ( TO_CHAR(TO_DATE('{self.deal_date}', 'YYYYMMDD')-1,'YYYYMMDD'), '{self.deal_date}')
                                    AND     STKCODE IN (            
                                                SELECT  STKCODE
                                                FROM    RC_TEAM.EBEST_THEME_MAPPING
                                                WHERE   THEMECODE = '{self.theme_code}'
                                            ) 
                                    AND     CURPRICE IS NOT Null
                                ) A
                        WHERE   RN =1
                        GROUP BY STKCODE, STKNAME
                    ) A, (
                        SELECT CODE, HEADER
                        FROM TP_STOCK.FI_OUTLINE_CONT
                    ) B
            WHERE  A.STKCODE = B.CODE 
            AND ROWNUM <= 5
            ORDER BY RATIO DESC          
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
