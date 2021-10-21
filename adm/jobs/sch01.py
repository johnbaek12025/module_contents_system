import logging
from adm import to_int
from adm.jobs.html.sch01_html import get_html, get_table
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
        self.no_rank_period_len = None
        self.stock_code = None
        self.stock_name = None

    def set_analysis_target(self):
        # columns = ["market", "period_len", "stk_code"]
        columns = ["stk_code", "stk_name", "no_rank_period_len"]
        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        # self.period_len = row["period_len"]
        # self.market = row["market"]
        self.stock_name = row.get("stk_name")
        self.stock_code = row.get("stk_code")
        self.no_rank_period_len = row.get("no_rank_period_len")
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"

    def make_news_info(self):
        if self.no_rank_period_len == None or self.no_rank_period_len > 250:
            news_title_list = [
                {"text": f"{self.deal_date_dd}일 {self.stock_name},", "color": None},
                {"text": f"검색 상위에 신규 진입", "color": "red"},
            ]

        elif self.no_rank_period_len >= 5 and self.no_rank_period_len < 250:
            news_title_list = [
                {"text": f"{self.deal_date_dd}일 {self.stock_name},", "color": None},
                {"text": f"검색 상위에 재 진입", "color": "red"},
            ]
        return {"news_title": news_title_list}

    def custom_process_condition(self):
        # implement the details in the inherited class.
        """
        NO_RANK_PERIOD_LEN
        case 1   NO_RANK_PERIOD_LEN <5 : SKIP
        case 2   NO_RANK_PERIOD_LEN >=5 and NO_RANK_PERIOD_LEN < 250  : 생성함 (재진입!!)
        case 3   NO_RANK_PERIOD_LEN >=250 OR null   : 생성함 (신규 진입!!)
        select NO_RANK_PERIOD_LEN from SCH01
        where INFO_SEQ = '149'  --> 자기자신의 'ALS_MAIN.SN'

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
        select
         T3. rank, T3. stk_name,
        DATA_ENG.FUNC_CNT_TRADEDAY(LAST_RANK_PERIOD_START, DATEDEAL) as rank_period_len
                from
                    (
                        select
                            T_MAIN. *,
                            T_RANK_PERIOD_START.RANK_PERIOD_START as LAST_RANK_PERIOD_START,
                            row_number() over(
                                partition by T_MAIN.DATEDEAL,
                                T_MAIN.STK_CODE
                                order by
                                    RANK_PERIOD_START desc
                            ) as RN
                        from
                            RC_TEAM.NAVER_SEARCH_RANK T_MAIN,
                            (
                                select
                                    DATEDEAL as RANK_PERIOD_START,
                                    STK_CODE,
                                    STK_NAME
                                from
                                    (
                                        select
                                            T1. *
                                        from
                                            RC_TEAM.NAVER_SEARCH_RANK T1,
                                            RC_TEAM.NAVER_SEARCH_RANK T2
                                        where
                                            T1.STK_CODE = T2.STK_CODE(+)
                                            and DATA_ENG.FUNC_ADD_DAY(T1.DATEDEAL, -1) = T2.DATEDEAL(+)
                                            and T2.DATEDEAL is null
                                    )
                            ) T_RANK_PERIOD_START
                        where
                            T_RANK_PERIOD_START.STK_CODE = T_MAIN.STK_CODE
                            and T_RANK_PERIOD_START.RANK_PERIOD_START <= T_MAIN.DATEDEAL
                            and T_MAIN.DATEDEAL = DATA_ENG.FUNC_ADD_TRADEDAY('{self.deal_date}', 0)
                    ) T3
                where
                    RN = 1
                and rownum <= 15
                order by TO_NUMBER(RANK) ASC
        """
        x = []
        rows = self.data_db_mgr.get_all_rows(sql)

        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "rank": int(r[0]),
                    "stock_name": r[1],
                    "rank_period_len": int(r[2]),
                }
            )
        return x

    def get_for_data_2(self):
        sql = f"""
            select
                    T3.rank, T3.stk_name,
                    DATA_ENG.FUNC_CNT_TRADEDAY(LAST_RANK_PERIOD_START, DATEDEAL) as rank_period_len
                from
                    (
                        select
                            T_MAIN. *,
                            T_RANK_PERIOD_START.RANK_PERIOD_START as LAST_RANK_PERIOD_START,
                            row_number() over(
                                partition by T_MAIN.DATEDEAL,
                                T_MAIN.STK_CODE
                                order by
                                    RANK_PERIOD_START desc
                            ) as RN
                        from
                            RC_TEAM.NAVER_SEARCH_RANK T_MAIN,
                            (
                                select
                                    DATEDEAL as RANK_PERIOD_START,
                                    stk_code,
                                    stk_name
                                from
                                    (
                                        select
                                            T1. *
                                        from
                                            RC_TEAM.NAVER_SEARCH_RANK T1,
                                            RC_TEAM.NAVER_SEARCH_RANK T2
                                        where
                                            T1.STK_CODE = T2.STK_CODE(+)
                                            and DATA_ENG.FUNC_ADD_DAY(T1.DATEDEAL, -1) = T2.DATEDEAL(+)
                                            and T2.DATEDEAL is null
                                    )
                            ) T_RANK_PERIOD_START
                        where
                            T_RANK_PERIOD_START.STK_CODE = T_MAIN.STK_CODE
                            and T_RANK_PERIOD_START.RANK_PERIOD_START <= T_MAIN.DATEDEAL
                            and T_MAIN.DATEDEAL = DATA_ENG.FUNC_ADD_TRADEDAY('{self.deal_date}', 0)
                    ) T3
                where
                    RN = 1
                and rownum <= 20
                order by TO_NUMBER(rank) ASC
        """

        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "rank": int(r[0]),
                    "stock_name": r[1],
                    "rank_period_len": int(r[2]),
                }
            )
        return x
