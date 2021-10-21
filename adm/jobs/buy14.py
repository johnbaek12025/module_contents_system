import logging
from adm.jobs.workshop.commom_psh import get_stock_name, get_cybos7210
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
        self.dealing_type = "sonmeme_cnt"
        self.subject = None
        self.sort = None
        self.stock_name = None
        self.stock_code = None
        self.time_deal = None
        self.market = None

    def set_analysis_target(self):
        columns = [
            "sonmeme_type",
            "hour_period",
            "stk_code",
            "stk_name",
            "market",
        ]
        row = self.data_db_mgr.get_essential_info_data(
            self.analysis_type, columns, self.deal_date, self.info_seq
        )
        self.subject = row.get("subject")
        self.sort = row.get("sort")
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.sonmeme_type = row.get("sonmeme_type").lower()
        self.time_deal = row.get("hour_period")[0:2]
        self.rep_image = f"https://dev.thinkpool.com/item/{self.stock_code}/trend"

    def make_news_info(self):
        news_title_list = [
            {"text": f"{self.stock_name},", "color": None},
            {"text": f"장중 외국인,기관 동시 {self.sonmeme_type}", "color": "red"},
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = None
        rows = self.get_result()
        rows = get_table(rows)
        dealing_type = get_dealing_str(self.sort)
        forg, org, time = self.get_arrange(self.get_info())
        a = [
            get_for_info(forg, self.deal_date_dd, time, dealing_type),
            get_org_info(org),
        ]
        subject = get2_kor_name(self.subject)
        news_cnts = get_html(subject, dealing_type, self.deal_date_dd, time, table, a)
        return {"news_cnts": news_cnts}

    def get_arrange(self, info):
        a = dict()
        b = dict()
        c = dict()
        for r in info:
            print(r)
            if info[r] == 0:
                continue
            if r == "time":
                c[r] = f"{info[r][0:2]}:{info[r][2:4]}"
            elif r == "forr":
                a[r] = f"{get2_kor_name(r)} {info[r]}주 {get_dealing_str(info[r])}"
            elif r == "orgr":
                a[r] = f"{get2_kor_name(r)} {info[r]}주 {get_dealing_str(info[r])}"
            elif r == "org2":
                b[r] = f"{get2_kor_name(r)} {info[r]}주 {get_dealing_str(info[r])}"
            elif r == "org4":
                b[r] = f"{get2_kor_name(r)} {info[r]}주 {get_dealing_str(info[r])}"
        return a, b, c

    def get_info(self):
        sql = f"""
        {get_cybos7210(self.subject, self.sort, self.deal_date, self.time_deal,self.dodratio)}
        WHERE STKCODE = '{self.stock_code}'
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append(
                {
                    "forr": r[3],
                    "orgr": r[4],
                    "org2": r[5],
                    "org4": r[6],
                    "time": r[2],
                    "dodratio": [7],
                }
            )
        return x[0]
