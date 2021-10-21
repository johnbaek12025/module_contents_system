import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import (get_stock_name, get_cybos7254,
                                  get_before_day, get_before_hour,
                                  get_empty_hour, related_stock)
from .workshop.chart_jh import Chart, Bar
from adm.jobs import (get_kor_name, get_dealing_str, get_size_str,
                      get_size_symbol, get_size_color, get_unit_str,
                      circle_symbol, get_sort, get_time_period,
                      get_previous_day)

logger = logging.getLogger(__name__)


def set_bar(bar):
    if None in [bar.tick, bar.value]:
        return False

    month = bar.tick[4:6]
    day = bar.tick[6:8]
    bar.tick = f"{month}/{day}"

    if bar.value < 0:
        bar.color = "blue"
    else:
        bar.color = "skyblue"
    return True


def get_bar_chart_data(rows: dict, func=None):
    set_bar_chart_data = []
    for tick in rows:
        bar = Bar()
        bar.tick = tick
        bar.value = rows[tick]
        if func(bar):
            set_bar_chart_data.append(bar)
    return set_bar_chart_data


def get_bar_chart(rows: dict, local_image_whole_path, days=None, period_len=5):
    rotation = None
    if period_len == 20:
        rotation = 90
    chart_dict = {
        "face_color": "whitesmoke",
        "tick_interval": 1,
        "spine_top": False,
        "spine_right": False,
        "grid": False,
        "rotation": rotation,
    }
    bc = Chart(**chart_dict)
    colors = ['orange', 'grey']
    for i, r in enumerate(rows):
        if r == '관련글':
            if period_len == 5:
                bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
                bc.add_data(bar_chart_data, chart_type="bar", label=r)
            else:
                bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
                bc.add_data(bar_chart_data, colors=colors[i], label=r)
        elif r == '주가':
            bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
            bc.add_data(bar_chart_data, colors=colors[i], twinx=True, label=r)
        bc.finalize_chart(local_image_whole_path,
                          ticks=False,
                          leg=rows,
                          loc='lower left',
                          loc_position=(0 + i * 0.15, -0.52))


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.subject = None
        self.use_ftp = True
        self.stock_code = None
        self.stock_name = None
        self.tr_date = 20
        self.period_len = None
        self.process_condition = ADManager.SC_ONCE

    def set_analysis_target(self):
        columns = [
            'period_len',
            'stk_code',
            'stk_name',
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.period_len = row.get('period_len')
        self.stock_name = row.get('stk_name')
        self.stock_code = row.get('stk_code')
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text": f"{self.select_str()}",
                "colo": 'red',
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        self.get_stock_rank()
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr()}
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        return f"""
            <div class="module-tbl-txt">                
                <div style = "float:left">
                <span>수량(건)</span>
                </div>
                <div style = "float:right">
                <span>주가(원)</span>
                </div>
            </div>            
        """

    def get_middle_tr(self):
        cnt = self.get_info()
        price = self.get_stock_ratio()
        rows = {'관련글': cnt, '주가': price}
        get_bar_chart(rows,
                      local_image_whole_path=self.local_image_whole_path,
                      period_len=self.period_len)
        return f"""
            <div class="module-chart text-center bgcolor">
                <img style="height:auto; max-width:100%;" src="{self.image_url}">               
            </div>     
            """

    def get_bottom_tr(self):
        names = self.get_stock_rank()
        return f"""
            <div class="module-tbl-txt mt-20">                
                <div class="c999 dot">관련글 급증 종목 : {', '.join(names)} 등</div>      
            </div>
        """

    def get_info(self):
        sql = f"""
            select  B.DATEDEAL, 
                    COUNT(CODE)CNT
            from    (  
                        SELECT TO_CHAR(REGDATE, 'YYYYMMDD')DATEDEAL,
                                CODE
                        FROM    TB_COMMUNITY_NAVER@USER_BARISTA
                        WHERE   CODE = '{self.stock_code}'
                    )A,
                    (            
                        SELECT  DATEDEAL
                        FROM    (
                                    SELECT  DATEDEAL
                                    FROM    TRADE_DAY
                                    WHERE   DATEDEAL <= '{self.deal_date}'
                                    ORDER BY DATEDEAL DESC
                                ) A
                        WHERE   ROWNUM <= {int(self.period_len)}
                    )B
            where   B.DATEDEAL = A.DATEDEAL(+)
            GROUP BY  B.DATEDEAL
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0]
            x[id] = r[1]
        return x

    def get_stock_ratio(self):
        yesterday = get_previous_day(self.deal_date, 1)
        x = self.data_db_mgr.get_stock_info(yesterday,
                                            int(self.period_len),
                                            self.stock_code,
                                            price=True)
        return x

    def get_stock_rank(self):
        column = ['stk_name']
        condition = f"""
            and  period_len = {self.period_len}
            order by  max_cnt desc
            """
        sql = related_stock(column, self.analysis_type, self.deal_date,
                            condition, 3)
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append(r[0])
        return x

    def select_str(self):
        if self.period_len == '5':
            return '관련글 증가'
        else:
            return '최근 1달 관련글 급증'