import logging
from adm.jobs.workshop.commom_bjh import get_stock_name, get_cybos7210
from adm import to_int
from adm.jobs.html.rpt0304_html import get_html
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
        self.subject = None
        self.sort = None
        self.dealing_type = None
        self.accumulated_days = None
        self.sn = None

    def set_analysis_target(self):
        columns = ["sn"]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.sn = row['sn']
        self.sort = "cnt"
        self.dealing_type = "sonmeme"
        self.accumulated_days = 5
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text": f"신규 매수 리포트 발표",
                "color": "red"
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = None
        rows = self.get_report()
        info = self.rc_db_mgr.get_7254_accu_value(self.deal_date,
                                                  self.stock_code,
                                                  self.dealing_type, self.sort,
                                                  self.accumulated_days)
        a = [self.omit_null(rows), self.make_sent(info)]
        news_cnts = get_html(rows[0], a)

        return {"news_cnts": news_cnts}

    def omit_null(self, rows):
        rows = rows[0]
        col = []
        for r in rows:
            if r == 'org_name':
                if rows['org_name']:
                    col.append(rows['org_name'])
                else:
                    continue
            if r == 'opinion':
                if rows['opinion'] != "Not Rated":
                    col.append(f"투자의견 {rows['opinion']}")
                else:
                    continue
            if r == 'goal_value':
                if rows['goal_value']:
                    col.append(f"목표가 {format(rows['goal_value'], ',')}원")
                else:
                    continue
            else:
                continue
        return f'<div class="dot">{" / ".join(col)}</div>'

    def make_sent(self, info):
        col = []
        for i in info:
            if i == 'org':
                if info[i]:
                    col.append(f"기관 {format(info[i], ',')}주")
                else:
                    continue
            elif i == 'for':
                if info[i]:
                    col.append(f"외국인 {format(info[i], ',')}주")
                else:
                    continue
            elif i == 'etc':
                if info[i]:
                    col.append(f" 개인 {format(info[i], ',')}주")
                else:
                    continue
            else:
                continue
        return f'<div class="dot">최근 5일 누적 순매매: {", ".join(col)}</div>'

    def get_report(self):
        sql = f"""
            SELECT  B.org_NAME, 
                    A.opinion, 
                    A.goal_value, 
                    A.cont_a, 
                    A.cont_b2
            FROM    TP_STOCK.ORG_OPINION_MANUAL_MOD@DATA_ENG A,
                    TP_STOCK.STOCK_CHANGKU_CODE B
            WHERE   B.ORG_NUM = A.ORG_CODE  
                    AND A.SN = {self.sn}        
                    AND A.DATEDEAL = {self.deal_date}
                """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({
                'org_name': r[0],
                'opinion': r[1],
                'goal_value': r[2],
                'title': r[3],
                'description': r[4],
            })
        return x
