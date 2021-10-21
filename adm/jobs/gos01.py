import logging
from .workshop.commom_bjh import get_stock_name, get_cybos7254
from adm.jobs.html.gos01_html import get_row_html, get_html
from adm import to_int
from adm.ad_manager import ADManager
from adm.jobs import (
    get_dealing_str,
    get_kor_name,
    circle_symbol,
    get_size_str,
    get_size_symbol,
    get_previous_years,
)

logger = logging.getLogger(__name__)
import replace


class Contents(ADManager):
    def __init__(self):
        super().__init__()
        self.stock_code = None
        self.stock_name = None
        self.rcpno = None
        self.sales_protion_type = None  #매출액 대비 계약금 비중 타입
        self.sales_protion = None  #매출액 대비 계약금 비중
        self.dt = None  #데이터 입력일
        self.process_condition = ADManager.SC_GONGSI

    def set_analysis_target(self):
        columns = [
            'stk_code', 'rcpno', 'sales_portion_type', 'sales_portion', 'dt'
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.stock_code = row.get('stk_code')
        stock_name = self.rc_db_mgr.get_master_info(self.deal_date,
                                                    self.stock_code)
        self.stock_name = stock_name['name']
        self.rcpno = row.get('rcpno')
        self.sales_protion_type = row.get('sales_protion_type')
        self.sales_protion = row.get('sales_protion')
        self.dt = row.get('dt')
        self.prvious_years = get_previous_years(self.deal_date, 3)

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.stock_name},",
                "color": 'black'
            },
            {
                "text": f"계약 체결 공시 발표",
                "color": "red",
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        first = self.get_arrange_1sent()
        second = self.get_arrange_2sent()
        down = get_row_html(second)
        news_cnts = get_html(first, down)
        return {"news_cnts": news_cnts}

    def get_contraction_info(self, columns, condition=''):
        if condition == 'up':
            x = f'where  rcpno = {self.rcpno}'
        elif condition == 'down':
            x = f"""
                    where   crp_code = '{self.stock_code}'      
                    and     contract_date  between  '{self.prvious_years}'  and  '{self.deal_date}'
                    order by  contract_date
                    """
        sql = f"""
            select  {', '.join(columns)}
            from    RC_TEAM.RBS_SUJU_PARSING
            {x}
            """
        rows = self.rc_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for i, r in enumerate(rows):
            if i > 2:
                break
            if len(rows) < 2:
                return r
            else:
                x.append(r)
        return x

    def get_arrange_1sent(self):
        columns = [
            'suju_cont', 'amount', 'sales_portion', 'start_dt', 'end_dt',
            'contract_date', 'partner_name'
        ]
        x = {}
        rows = self.get_contraction_info(columns, condition='up')
        for i, r in enumerate(rows):
            if columns[i] == 'amount':
                x[columns[i]] = round(int(r.replace(',', '')) / 10**8)
            else:
                x[columns[i]] = r
        return x

    def get_arrange_2sent(self):
        columns = [
            'suju_cont', 'sales_portion',
            "to_char(to_date(contract_date, 'yyyy/mm/dd'),'yyyy.mm.dd')"
        ]
        rows = self.get_contraction_info(columns, condition='down')
        x = []
        for r in rows:
            x.append(f"{r[2]}/매출액 대비 {r[1]}%/{r[0]}")
        return x
