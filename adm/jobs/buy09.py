import logging
from adm import to_int
from adm.ad_manager import ADManager
from dateutil.relativedelta import relativedelta
from datetime import datetime
from adm.jobs.workshop.commom_bjh import get_cybos7254
from adm.jobs.html.buy09_html import get_html, get_info
from adm.jobs import (get_dealing_str, get_kor_name, circle_symbol,
                      get_size_str, get_dealing_str, get_size_symbol,
                      get_previous_month)
import replace

logger = logging.getLogger(__name__)


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.dealing_type = "SONMEME_AMT"
        self.subject = None
        self.sort = "DESC"
        self.process_condition = ADManager.SC_ONCE

    def set_analysis_target(self):
        columns = ["customer_type", "stk_code", "stk_name", "market"]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.subject = row.get("customer_type").lower()
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.market = row.get("market")
        self.onemonth_ago = get_previous_month(self.deal_date, 1)
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        temp = f"{get_size_str(self.dealing_type)}{get_size_symbol(self.dealing_type)}"
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text": f"{get_kor_name(self.subject)} 첫 매수 포착",
                "color": "red"
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = None
        row = self.get_cybos_data()
        info = self.get_count()
        org_info = get_info(info)
        news_cnts = get_html(self.deal_date_dd, row[0], org_info)
        return {"news_cnts": news_cnts}

    def get_count(self):
        x = []
        x.append(self.get_total_cnt())
        x.extend(self.get_org_data())
        if len(x) < 4:
            r = 4 - len(x)
            b = self.get_news_data(r)
            x.extend(b)
            return x
        else:
            return x

    def get_org_data(self):
        sql = f"""
            SELECT DATEDEAL,
                   ORG_NAME,
                   CONT_A
            FROM(                   
                    SELECT  A.DATEDEAL,                    
                            B.ORG_NAME,
                            A.CONT_A                     
                    FROM    TP_STOCK.ORG_OPINION_MANUAL@DATA_ENG A,
                            TP_STOCK.STOCK_CHANGKU_CODE@DATA_ENG B
                    WHERE   A.ORG_CODE = B.ORG_NUM AND
                            A.CODE = '{self.stock_code}' AND
                            A.DATEDEAL BETWEEN 
                            '{self.deal_date}' AND '{self.onemonth_ago}'
                    ORDER BY A.DATEDEAL DESC                            
                )
            WHERE  ROWNUM <= 4                
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            title = r[2].replace("'", "")
            x.append({
                "conts": f"{r[0][4:6]}/{r[0][6:8]} ({r[1]}) {title}",
                "stock_code": self.stock_code,
            })
        return x

    def get_news_data(self, count):
        sql = f"""
            SELECT  DATEDEAL,
                    TITLE       
            FROM(
                    SELECT  SUBSTR(PUBDATE, 1,8) DATEDEAL,
                            TITLE_PART2 AS  TITLE                    
                    FROM    NAVER_NEWS_STOCKISSUE
                    WHERE   TITLE_PART2 IS NOT NULL
                            AND SUBSTR(PUBDATE, 1,8) BETWEEN '{self.onemonth_ago}' AND '{self.deal_date}'
                            AND STKCODE = '{self.stock_code}'
                    ORDER BY DATEDEAL DESC
                )
            WHERE ROWNUM <={count}                                            
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            title = r[1].replace("'", "")
            x.append({"conts": f'{r[0][4:6]}/{r[0][6:8]} (뉴스) {title}'})
        return x

    def get_cybos_data(self):
        sql = f"""
            {get_cybos7254(self.subject, self.dealing_type, self.sort, self.deal_date)}
            WHERE     X.STKCODE='{self.stock_code}'            
                """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({
                "org_net": format(r[4], ','),
                "org_mesu": format(r[5], ','),
                "org_medo": format(r[6], ','),
                "org3_net": format(r[7], ','),
                "org3_mesu": format(r[8], ','),
                "org3_medo": format(r[9], ','),
                "org6_net": format(r[10], ','),
                "org6_mesu": format(r[11], ','),
                "org6_medo": format(r[12], ','),
                "org9_net": format(r[13], ','),
                "org9_mesu": format(r[14], ','),
                "org9_medo": format(r[15], ','),
            })
        return x

    def get_total_cnt(self):
        subject = ['for', 'org', 'etc']
        dealing_type = 'sonmeme'
        unit = 'cnt'
        x = []
        for s in subject:
            rows = self.rc_db_mgr.get_7254_value(self.deal_date,
                                                 self.stock_code, s,
                                                 dealing_type, unit)
            x.append(f"{get_kor_name(s)} {abs(rows)}주 {get_dealing_str(rows)}")

        return {'conts': f"{self.deal_date_dd}일 순매매동향: {', '.join(x)}"}