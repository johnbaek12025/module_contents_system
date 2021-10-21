import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import (get_stock_name, get_cybos7254,
                                  get_before_day, get_before_hour,
                                  get_empty_hour)
from .workshop.chart_jh import Chart, Bar
from adm.jobs import (get_kor_name, get_dealing_str, get_size_str,
                      get_size_symbol, get_size_color, get_unit_str,
                      circle_symbol, get_sort, get_time_period,
                      get_previous_day)

logger = logging.getLogger(__name__)


def get_bar_chart_data(rows: dict):
    set_bar_chart_data = []
    for tick in rows:
        bar = Bar()
        bar.tick = tick
        bar.value = rows[tick]
        set_bar_chart_data.append(bar)
    return set_bar_chart_data


def get_bar_chart(rows: list, deal_date, local_image_whole_path, line):
    chart_dict = {
        "face_color": "whitesmoke",
        "grid_color": "silver",
        "tick_position": "left",
        "tick_interval": 2,
        "spine_top": False,
        "spine_bottom": False,
        "spine_left": False,
        "spine_right": False,
        "grid": True,
    }
    bc = Chart(**chart_dict)
    colors = ['red', 'navy', 'slateblue', 'lightblue', 'royalblue']
    days = [f'{get_previous_day(deal_date, i)[-2:]}일' for i in range(0, 5)]
    for i, row in enumerate(rows):
        bar_chart_data = get_bar_chart_data(rows=row)
        bc.add_data(bar_chart_data, 'plot', colors[i], days[i])
    bc.finalize_chart(local_image_whole_path,
                      line=line,
                      leg=days,
                      ticks=False,
                      grid='xgrid')


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.use_ftp = True
        self.ts_data_count = 23
        self.accumulated_days = 5
        self.count = 3
        self.hh = self.now_time[0:2]
        self.now = self.now_datetime[:-2]        
        self.hour_period = None
        self.period_len = None
        self.inc_ratio = None
        self.avg_cnt = None
        self.max_cnt = None
        self.stock_code = None
        self.stock_name = None

    def set_analysis_target(self):
        columns = [
            "stk_code",
            "stk_name",
            "hour_period",
            "period_len",
            "inc_ratio",
            "avg_cnt",
            "max_cnt",
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.hour_period = row.get("hour_period")
        self.period_len = row.get("period_len")
        self.inc_ratio = row.get("inc_ratio")
        self.avg_cnt = row.get("avg_cnt")
        self.max_cnt = row.get("max_cnt")
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.stock_name}",
                "color": None
            },
            {
                "text": f"{get_time_period(self.hour_period)} 관련글 급증 ",
                "color": get_size_color(self.hour_period),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}
            """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        return f"""
            <div class="module-tbl-txt">
                <strong class="title title-s">최근 {self.period_len}일 동시간대 대비 {round(self.inc_ratio)}% 수준</strong>                
            </div>            
            """

    def get_middle_tr(self):
        rows = []
        for i in range(0, 5):
            date = get_previous_day(self.deal_date, i)
            row = self.get_info_date(date)
            rows.append(row)
        get_bar_chart(rows, self.deal_date, self.local_image_whole_path,
                      self.ts_data_count)
        return f"""
            <div class="module-chart text-center bgcolor">
                <img style="height:auto; max-width:100%;" src="{self.image_url}">               
            </div>     
        """

    def get_info_date(self, deal_date):
        sql = f"""
            SELECT  A.YYYYMMDDHH, DECODE(B.CNT, NULL, 0, B.CNT) CNT
            FROM    {get_empty_hour(deal_date, self.hour_period, self.now, self.hh)}
                    , (
                        SELECT  YYYYMMDDHH, COUNT(*) AS CNT
                        FROM    (
                                    SELECT  TO_CHAR(COLDATE, 'yyyymmddhh24') AS YYYYMMDDHH
                                    FROM    TB_COMMUNITY_NAVER@USER_BARISTA
                                    WHERE   TO_CHAR(COLDATE, 'yyyymmddhh24')  BETWEEN '{deal_date}'-1 ||'{get_before_hour(self.now_datetime, 23)}' AND '{deal_date}' ||'{self.hh}'
                                    AND     CODE ='{self.stock_code}'
                                )
                        GROUP BY YYYYMMDDHH
                    ) B
            WHERE   A.YYYYMMDDHH = B.YYYYMMDDHH(+)
            ORDER BY YYYYMMDDHH ASC
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0][-2:]
            x[id] = r[1]
        return x
