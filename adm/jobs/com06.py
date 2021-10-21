import datetime
import logging
from adm import to_int
from adm.ad_manager import ADManager
from .html.com06_html import get_table, get_html
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import (
    get_stock_name,
    get_cybos7254,
    get_before_day,
    get_before_hour,
    get_empty_hour,
    related_stock,
)
from .workshop.chart_jh import Chart, Bar
from adm.jobs import (
    get_kind_market,
    get_kor_name,
    get_dealing_str,
    get_size_str,
    get_size_symbol,
    get_size_color,
    get_unit_str,
    circle_symbol,
    get_sort,
    get_time_period,
    get_previous_day,
)

logger = logging.getLogger(__name__)


def set_bar(bar):
    if None in [bar.tick, bar.value]:
        return False
    month = bar.tick[4:6]
    day = bar.tick[6:8]
    bar.tick = f"{month}/{day}"
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


def get_bar_chart(rows: list, deal_date, local_image_whole_path):
    chart_dict = {
        "face_color": "whitesmoke",
        "grid_color": "silver",
        "tick_position": "left",
        "tick_interval": 4,
        "spine_top": False,
        "spine_bottom": False,
        # "spine_left": False,
        "grid": True,
        "spine_right": False,
    }
    bc = Chart(**chart_dict)
    colors = ["red", "green", "blue", "yellow", "orange"]
    for i, r in enumerate(rows):
        bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
        bc.add_data(bar_chart_data, "plot", colors[i], r)
    bc.finalize_chart(
        local_image_whole_path,
        ticks=False,
        leg=rows,
    )


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.use_ftp = True
        self.ts_data_count = 23
        self.accumulated_days = 5
        self.count = 3        
        self.now = "202101221150"
        self.hh = "11"
        self.market = None
        self.hour_period = None
        self.stock_code = None
        self.stock_name = None
        self.market = None
        self.cnt = None
        self.rk = None
        self.condition = None

    def set_analysis_target(self):
        columns = [
            "market",
            "hour_period",
            "stk_code",
            "stk_name",
            "cnt",
            "rk",
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.cnt = row.get("cnt")
        self.market = row.get("market")
        self.hour_period = row.get("hour_period")
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.rk = row.get("rk")
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.stock_name}",
                "color": None
            },
            {
                "text": f"{ (self.hour_period)} 관련글 수 상위 ",
                "color": get_size_color(self.hour_period),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = None
        if self.rk <= 5:
            self.get_top_tr()
            self.get_middle_tr()
            news_cnts = f"""
                {self.get_top_tr()}{self.get_middle_tr()}
                """
        else:
            rows = self.upper_f_rank()
            table = get_table(rows)
            market = get_kind_market(self.market)
            html = get_html(market=market, table=table)
            news_cnts = html
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        return f"""
            <div class="module-tbl-txt">
                <span>{get_kind_market(self.market)} 게시물 상위 랭킹</span>
            </div>            
            """

    def get_middle_tr(self):
        rows = self.get_info_stock()
        get_bar_chart(rows, self.deal_date, self.local_image_whole_path)
        return f"""
        <div class="module-chart text-center bgcolor">
            <img style="height:auto; max-width:100%;" src="{self.image_url}">               
        </div>     
        """

    def get_info_stock(self):
        codes = self.under_f_rank()
        x = {}
        for code in codes:
            info = self.get_info(code["stk_code"])
            row = self.data_db_mgr.get_master_info(self.deal_date,
                                                   code["stk_code"])
            id = row["name"]
            x[id] = info
        return x

    def under_f_rank(self):
        column = ["stk_code"]
        self.condition = (f" and   hour_period='{self.hour_period}'"
                          f" and   market = '{self.market}'"
                          f" order by rk asc")
        sql = related_stock(column,
                            self.analysis_type,
                            self.deal_date,
                            self.condition,
                            num=5)
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({
                "stk_code": r[0],
            })
        return x

    def upper_f_rank(self):
        column = ["rk", "stk_name", "cnt"]
        self.condition = (f" and   hour_period='{self.hour_period}'"
                          f" and   market = '{self.market}'"
                          f" order by rk asc")
        sql = f"""
                select  *
                from (
                        {related_stock(column = column, analysis_type=self.analysis_type, 
                         deal_date=self.deal_date, condition = self.condition, num=20)}
                    )                        
                where  rk between 6 and 20
                """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({
                "rk": r[0],
                "stk_name": r[1],
                "cnt": r[2],
            })
        return x

    def get_info(self, stock_code):
        sql = f"""
            SELECT  B.DATEDEAL,            
                    NVL(COUNT(A.CODE), 0) AS CNT
            FROM    (        
                        SELECT  TO_CHAR(COLDATE, 'YYYYMMDD')DATEDEAL, 
                                CODE        
                        FROM    TB_COMMUNITY_NAVER@USER_BARISTA A
                        WHERE   CODE = '{stock_code}'
                    )A,
                    (
                        SELECT  DATEDEAL,
                                0 AS CODE
                        FROM    (
                                    SELECT  DATEDEAL
                                    FROM    TRADE_DAY
                                    WHERE   DATEDEAL <= '{self.deal_date}'
                                    ORDER BY DATEDEAL DESC
                                ) A
                        WHERE   ROWNUM <= 20
                    )B
            WHERE   B.DATEDEAL = A.DATEDEAL(+)    
            GROUP BY B.DATEDEAL
            ORDER BY B.DATEDEAL
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0]
            x[id] = r[1]
        return x
