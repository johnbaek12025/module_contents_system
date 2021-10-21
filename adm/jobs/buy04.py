import logging
from .workshop.commom_bjh import get_stock_name, get_cybos7254
from adm.jobs.html.buy04_html import get_table, get_html
from adm import to_int
from adm.ad_manager import ADManager
from adm.jobs import (
    get_dealing_str,
    get_kor_name,
    circle_symbol,
    get_size_str,
    get_size_symbol,
)

logger = logging.getLogger(__name__)


def html_table(rows, dealing_type, subject, now_day, info):
    pass


class Contents(ADManager):
    def __init__(self):
        super().__init__()
        self.dealing_type = "sonmeme_amt"
        self.market = None
        self.stock_code = None
        self.stock_name = None
        self.subject = None
        self.sort = None
        self.process_condition = ADManager.SC_ONCE

    def set_analysis_target(self):
        sort = lambda x: "desc" if "mesu" else "asc"
        columns = [
            "sonmeme_type", "customer_type", "stk_code", "stk_name", "market"
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.market = row.get("market")
        self.sonmeme_type = row.get("sonmeme_type").lower()
        self.subject = row.get("customer_type").lower()
        self.sort = sort(self.sonmeme_type)
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text":
                f"{get_kor_name(self.subject)} {get_dealing_str(self.sonmeme_type)} 상위 신규등장",
                "color": "red",
            },
        ]
        return {"news_title": news_title_list}

    def custom_process_condition(self):
        # implement the details in the inherited class.
        """
        아래 쿼리의 결과 > 5  : 콘텐츠 생성함 (insert)
        아래 쿼리의 결과 <= 5   :  콘텐츠 생성안함 (SKIP)
        select NO_RANK_PERIOD_LEN from BUY04
        where INFO_SEQ = '149'  --> 자기자신의 ALS_MAIN.SN
        """
        columns = ["no_rank_period_len"]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        period_len = row.get("no_rank_period_len")
        if period_len <= 5 or not period_len:
            return False, {}
        return True, {}

    def make_news_cnts(self):
        news_cnts = None
        row = self.get_result()
        rows = get_table(row)
        subject = get_kor_name(self.subject)
        dealing_type = get_dealing_str(self.sort)
        info = self.get_info()
        info = self.get_net(info)
        news_cnts = get_html(subject, dealing_type, rows, info)
        return {"news_cnts": news_cnts}

    def get_result(self, a=[]):
        cols = self.get_for_data_1()
        for r in cols:
            if self.stock_code == r.get("stkcode"):
                a.append("p")
                break
        if a:
            return cols
        else:
            rows = self.get_for_data_2()
            return rows

    def get_net(self, info):
        sent = f"{self.deal_date_dd}일 매매 동향:"
        collect = []
        for i in info:
            if not info[i]:
                continue
            collect.append(
                f"{get_kor_name(i)} {format(abs(info[i]), ',')}백만원 {get_dealing_str(info[i])}"
            )
        return sent + ", ".join(collect)

    def get_for_data_1(self):
        sql = f"""
            SELECT  A.RANK,
                    B.NAME,
                    ABS(A.{self.subject}_{self.dealing_type}) AS AMOUNT,
                    A.STKCODE
            FROM    (
                        {get_cybos7254(self.subject, self.dealing_type, self.sort, self.deal_date)}
                        WHERE  ROWNUM <= 15
                    ) A
                    , (
                        {get_stock_name(self.deal_date)}
                    ) B                    
            WHERE   B.CODE = A.STKCODE
            ORDER BY A.RANK ASC
        """
        x = []
        rows = self.data_db_mgr.get_all_rows(sql)
        if not rows:
            return x
        for r in rows:
            x.append({
                "rank": r[0],
                "stkname": r[1],
                "amount": r[2],
                "stkcode": r[3],
            })
        return x

    def get_for_data_2(self):
        sql = f"""
            SELECT  A.RANK,
                    B.NAME,
                    ABS(A.{self.subject}_{self.dealing_type}) AS AMOUNT,
                    A.STKCODE
            FROM    (
                        {get_cybos7254(self.subject, self.dealing_type, self.sort, self.deal_date)}
                        WHERE  ROWNUM <= 14
                        UNION            
                        SELECT  * 
                        FROM    (
                                    {get_cybos7254(self.subject, self.dealing_type, self.sort, self.deal_date)}
                                )
                        WHERE STKCODE = '{self.stock_code}'
                    ) A
                    , (
                        {get_stock_name(self.deal_date)}
                    )B
            WHERE   A.STKCODE = B.CODE
            ORDER BY A.RANK ASC
        """

        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({
                "rank": r[0],
                "stkname": r[1],
                "amount": r[2],
                "stkcode": r[3],
            })
        return x

    def get_info(self):
        sql = f"""
        {get_cybos7254(self.subject, self.dealing_type, self.sort, self.deal_date)}
        WHERE X.STKCODE = '{self.stock_code}'
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({
                "for": r[1],
                "org": r[2],
                "etc": r[3],
            })
        return x[0]
