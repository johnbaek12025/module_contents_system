import logging
from adm.jobs.workshop.commom_bjh import get_stock_name, get_cybos7210
from adm import to_int
from adm.jobs.html.buy12_html import get_table, get_html, get_org_info, get_for_info
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
        self.dealing_type = "sonmeme_amt"
        self.subject = None
        self.sort = None
        self.stock_name = None
        self.stock_code = None
        self.time_deal = None
        self.market = None

    def set_analysis_target(self):
        sort = lambda x: "desc" if "mesu" else "asc"
        org = lambda x: "orgr" if "org" else x
        columns = [
            "sonmeme_type",
            "customer_type",
            "hour_period",
            "stk_code",
            "stk_name",
            "market",
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.customer_type = row.get("customer_type").lower()
        self.subject = org(self.customer_type)
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.market = row.get("market")
        self.sonmeme_type = row.get("sonmeme_type").lower()
        self.time_deal = row.get("hour_period")[0:2]
        self.sort = sort(self.dealing_type)
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        temp = f"{get_size_str(self.dealing_type)}{get_size_symbol(self.dealing_type)}"
        news_title_list = [
            {
                "text": f"{self.stock_name},",
                "color": None
            },
            {
                "text": f"장중 {get2_kor_name(self.subject)} ",
                "color": "red"
            },
        ]
        return {"news_title": news_title_list}

    def custom_process_condition(self):
        # implement the details in the inherited class.
        """
        아래 쿼리의 결과 <= 10  : 콘텐츠 생성함 (insert)
        아래 쿼리의 결과 >10   :  콘텐츠 생성안함 (SKIP)
        select RK from BUY12
        where INFO_SEQ = '149'  --> 자기자신의 ALS_MAIN.SN
        """
        columns = ["rk"]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        rk = row.get("rk")
        if rk > 10 or not rk:
            return False, {}
        return True, {}

    def make_news_cnts(self):
        news_cnts = None
        rows = self.get_result()
        table = get_table(rows)
        dealing_type = get_dealing_str(self.sort)
        forg, org, time = self.get_arrange(self.get_info())
        a = [
            get_for_info(forg, self.deal_date_dd, time, dealing_type),
            get_org_info(org)
        ]
        subject = get2_kor_name(self.subject)
        news_cnts = get_html(subject, dealing_type, self.deal_date_dd, time,
                             table, a)
        return {"news_cnts": news_cnts}

    def get_arrange(self, info):
        a = dict()
        b = dict()
        c = dict()
        for r in info:
            if info[r] == 0:
                continue
            if r == "time":
                c[r] = f"{info[r][0:2]}:{info[r][2:4]}"
            elif r == "forr":
                a[r] = f"{get2_kor_name(r)} {abs(info[r])}백만원 {get_dealing_str(info[r])}"
            elif r == "orgr":
                a[r] = f"{get2_kor_name(r)} {abs(info[r])}백만원 {get_dealing_str(info[r])}"
            elif r == "org2":
                b[r] = f"{get2_kor_name(r)} {abs(info[r])}백만원 {get_dealing_str(info[r])}"
            elif r == "org4":
                b[r] = f"{get2_kor_name(r)} {abs(info[r])}백만원 {get_dealing_str(info[r])}"
        return a, b, c

    def get_result(self, a=[]):
        cols = self.get_data_1()
        for r in cols:
            if self.stock_code == r.get("stkcode"):
                a.append("p")
                break
        if a:
            return cols
        else:
            rows = self.get_data_2()
            return rows

    def get_data_1(self):
        sql = f"""
            SELECT  A.RANK,
                    B.NAME,
                    A.{self.subject}_AMT,
                    A.STKCODE
            FROM    (
                        {get_cybos7210(self.subject, self.sort, self.deal_date, self.time_deal)}
                        WHERE ROWNUM <= 10
                    )A,
                    (
                        {get_stock_name(self.deal_date)}
                    )B
            WHERE A.STKCODE = B.CODE      
            """
        rows = self.rc_db_mgr.get_all_rows(sql)
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

    def get_data_2(self):
        sql = f"""
                SELECT  A.RANK,
                        B.NAME,
                        A.{self.subject}_amt,
                        A.STKCODE
                FROM    (
                            {get_cybos7210(self.subject, self.sort, self.deal_date, self.time_deal)}
                            WHERE ROWNUM <= 9
                            UNION ALL
                            SELECT *
                            FROM   (
                                        {get_cybos7210(self.subject, self.sort, self.deal_date, self.time_deal)}
                                    )
                            WHERE STKCODE = '{self.stock_code}'                    
                        )A,
                        (
                            {get_stock_name(self.deal_date)}
                        )B
                WHERE A.STKCODE = B.CODE      
                ORDER BY RANK ASC
            """
        rows = self.rc_db_mgr.get_all_rows(sql)
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
        {get_cybos7210(self.subject, self.sort, self.deal_date, self.time_deal)}
        WHERE STKCODE = '{self.stock_code}'
        """
        rows = self.rc_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({
                "forr": r[3],
                "orgr": r[4],
                "org2": r[5],
                "org4": r[6],
                "time": r[2]
            })
        return x[0]
