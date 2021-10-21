import logging
from adm import to_int
from adm.jobs.html.com03_html import get_html, get_table
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
        self.no_rank_period_len = None
        self.dir = None
        self.dir_str = None

    def set_analysis_target(self):
        columns = [
            "market",
            "no_rank_period_len",
            "stk_code",
            "stk_name",
        ]
        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        self.market = row.get("market")
        self.stock_name = row.get("stk_name")
        self.stock_code = row.get("stk_code")
        self.no_rank_period_len = row.get("no_rank_period_len")
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"

    def make_news_info(self):
        if self.no_rank_period_len == None or self.no_rank_period_len > 250:
            news_title_list = [
                {"text": f"{self.deal_date_dd}일 {self.stock_name},", "color": None},
                {"text": f"관련글 상위에 최초 등장!!", "color": "red"},
            ]
        elif self.no_rank_period_len >= 5 and self.no_rank_period_len < 250:
            news_title_list = [
                {"text": f"{self.deal_date_dd}일 {self.stock_name},", "color": None},
                {"text": f"관련글 상위에 진입!!", "color": "red"},
            ]
        return {"news_title": news_title_list}

    def custom_process_condition(self):
        # implement the details in the inherited class.
        """
        NO_RANK_PERIOD_LEN
        case 1   NO_RANK_PERIOD_LEN <5 : SKIP
        case 2   NO_RANK_PERIOD_LEN >=5 and NO_RANK_PERIOD_LEN < 250  : 생성함 (관련글 상위에 진입!!)
        case 3   NO_RANK_PERIOD_LEN >=250 OR null   : 생성함 (관련글 상위에 최초 등장!!)
        select NO_RANK_PERIOD_LEN from COM03
        where INFO_SEQ = '149'  --> 자기자신의 ALS_MAIN.SN

        """
        columns = ["no_rank_period_len"]
        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        period_len = row.get("no_rank_period_len")
        if period_len and period_len < 5:
            return False, {}
        return True, {}

    def make_news_cnts(self):
        print(self.no_rank_period_len)
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
                select a.rk,a.stk_name,a.cnt
                    , CASE WHEN NO_RANK_PERIOD_LEN >= 5 THEN 5 
                            WHEN NO_RANK_PERIOD_LEN IS NULL THEN 0
                        ELSE -1 END AS DDD
                from com02 a
                join com03 b
                on (a.datedeal = b.datedeal)
                and a.market ='{self.market}'
                and b.info_seq = '{self.info_seq}'
                and a.info_code = 'AL_COM02_01'
                ORDER BY A.RK ASC, A.CNT DESC
                 """
        x = []
        rows = self.data_db_mgr.get_all_rows(sql)

        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "rk": r[0],
                    "stock_name": r[1],
                    "cnt": r[2],
                }
            )
        return x

    def get_for_data_2(self):
        sql = f"""
                select a.rk,a.stk_name,a.cnt
                    , CASE WHEN NO_RANK_PERIOD_LEN >= 5 THEN 5 
                            WHEN NO_RANK_PERIOD_LEN IS NULL THEN 0
                        ELSE -1 END AS DDD
                from com02 a
                join com03 b
                on (a.datedeal = b.datedeal)
                and a.market ='{self.market}'
                and b.info_seq = '{self.info_seq}'
                and a.info_code = 'AL_COM02_01'
                ORDER BY A.RK ASC, A.CNT DESC
        """

        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "rk": r[0],
                    "stock_name": r[1],
                    "cnt": r[2],
                }
            )
        return x