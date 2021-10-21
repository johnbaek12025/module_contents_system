import datetime
import logging
from adm import to_int
from adm.ad_manager import ADManager
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import (
    get_stock_name,
    get_cybos7254,
    get_before_day,
    get_before_hour,
)
from .workshop.chart_jh import Chart, Bar
from adm.jobs import (get_kor_name, get_dealing_str, get_size_str,
                      get_size_strong, get_size_symbol, get_size_color,
                      get_unit_str, circle_symbol, get_sort, get_time_period,
                      get_previous_day)

logger = logging.getLogger(__name__)


def set_bar(bar):
    if None in [bar.tick, bar.value]:
        return False
    month = bar.tick[4:6]
    day = bar.tick[6:8]
    bar.tick = f"{month}/{day}"
    return True


def get_bar_chart_data(rows: dict, func):
    set_bar_chart_data = []
    for tick in rows:
        bar = Bar()
        bar.tick = tick
        bar.value = rows[tick]
        if func(bar):
            set_bar_chart_data.append(bar)
    return set_bar_chart_data


def get_bar_chart(rows: list, local_image_whole_path):
    chart_dict = {
        "face_color": "whitesmoke",
        "grid_color": "silver",
        "spine_top": False,
        "tick_position": "left",
        "tick_interval": 2,
        "spine_top": False,
        "spine_bottom": False,
        "spine_left": False,
        "spine_right": False,
    }
    bc = Chart(**chart_dict)
    colors = ['red', 'navy', 'slateblue', 'lightblue', 'royalblue']
    x = []
    for i, r in enumerate(rows):
        bar_chart_data = get_bar_chart_data(rows=rows[r], func=set_bar)
        bc.add_data(bar_chart_data, colors=colors[i], label=r)
        x.append(r)
    bc.finalize_chart(local_image_whole_path, leg=x)


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.use_ftp = True
        self.ts_data_count = 20
        self.accumulated_days = 5
        self.count = 4
        self.theme_code = None
        self.same_dir_percent = None
        self.theme_avg_diff = None
        self.subject = 'org'
        self.dealing_type = 'sonmeme'
        self.unit = 'cnt'
        self.sort = 'desc'

    def set_analysis_target(self):
        columns = [
            'theme_code',
            'theme_name',
            'dir_type',
            'theme_avg_diff',
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.theme_name = row.get('theme_name')
        self.theme_code = row.get('theme_code')
        self.dir_type = row.get('dir_type')
        self.theme_avg_diff = row.get('theme_avg_diff')
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"",
                "color": None
            },
            {
                "text":
                (f"{self.theme_name} 테마 {get_size_strong(self.dir_type)} "
                 f"{get_size_symbol(self.dir_type)}{self.theme_avg_diff}%"),
                "color":
                get_size_color(self.dir_type),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr()}
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        return f"""
            <div class="module-tbl-txt">
            <span>누적등락률%</span>
            </div>
            <div class="module-tbl-guide mt-15">                
            </div>
        """

    def get_middle_tr(self):
        rows = {}
        rows['테마'] = self.get_theme_info()
        if self.dir_type == 1:
            names = self.get_stock_name()
            info = self.collect_data()
            for i, r in enumerate(info):
                id = names[i]
                rows[id] = r
        else:
            rows[self.stock_name] = self.get_stock_info(self.stock_code)

        get_bar_chart(rows, self.local_image_whole_path)
        return f"""
                <div class="module-chart text-center bgcolor">
                    <img style="height:auto; max-width:100%;" src="{self.image_url}">               
                </div>
            """

    def get_bottom_tr(self):
        return f"""
            <div class="module-tbl-txt mt-20">                
                <div class="c999 dot">주도 종목: {', '.join(self.get_stock_name())} 등</div>      
            </div>
        """

    def get_theme_related_stock(self):
        sql = f"""
                select  *
                from    ( 
                            select  a.stkcode,
                                    b.ratio
                            FROM    RC_TEAM.EBEST_T1532 a,
                                    stock_1_day b
                            where   a.themecode='{self.theme_code}' 
                            and     a.datedeal = '{self.deal_date}'
                            and     b.code = a.stkcode
                            and     a.datedeal = b.datedeal
                            order by b.ratio desc
                        )
                where rownum <= {self.count}
                """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({
                "stkcode": r[0],
            })
        return x

    def get_stock_name(self):
        codes = self.get_theme_related_stock()
        x = []
        for code in codes:
            name = self.data_db_mgr.get_master_info(self.deal_date,
                                                    code['stkcode'])
            x.append(name['name'])
        return x

    def get_stock_info(self, stkcode):
        sql = f"""
            SELECT  A.DATEDEAL,
                    A.RATIO 
            FROM    STOCK_1_DAY A,
                    (   
                        SELECT  DATEDEAL
                        FROM    (
                                    SELECT  DATEDEAL
                                    FROM    TRADE_DAY
                                    WHERE   DATEDEAL <= '{self.deal_date}'
                                    ORDER BY DATEDEAL DESC
                                ) A
                        WHERE   ROWNUM <= {self.ts_data_count}
                    )B
            WHERE   A.DATEDEAL = B.DATEDEAL
            AND     A.CODE = '{stkcode}'
            ORDER BY  A.DATEDEAL ASC
        """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0]
            x[id] = r[1]
        return x

    def collect_data(self):
        codes = self.get_theme_related_stock()
        x = []
        for c in codes:
            doc = self.get_stock_info(c['stkcode'])
            x.append(doc)
        return x

    def get_theme_info(self):
        sql = f"""
                SELECT  DATEDEAL,
                        SUM(AVG_DIFF)OVER(PARTITION BY THEMECODE ORDER BY DATEDEAL) AS AVG_DIFF
                FROM(
                        SELECT  A.DATEDEAL,                
                                DECODE(B.AVG_DIFF, NULL, 0, B.AVG_DIFF) AS AVG_DIFF,
                                A.THEMECODE
                        FROM   (
                                    SELECT  DATEDEAL,
                                            '{self.theme_code}' AS THEMECODE                                        
                                    FROM    (
                                                SELECT  DATEDEAL                                        
                                                FROM    TRADE_DAY
                                                WHERE   DATEDEAL <= '{self.deal_date}'
                                                ORDER BY DATEDEAL DESC
                                            ) A
                                    WHERE   ROWNUM <= {self.ts_data_count}
                                )A,
                                (   
                                    select  a.datedeal,
                                            MAX(a.avg_diff)AS AVG_DIFF,
                                            A.THEMECODE
                                    FROM    RC_TEAM.EBEST_T1532 A,
                                            (
                                                SELECT  DATEDEAL
                                                FROM    (
                                                            SELECT  DATEDEAL
                                                            FROM    TRADE_DAY
                                                            WHERE   DATEDEAL <= '{self.deal_date}'
                                                            ORDER BY DATEDEAL DESC
                                                        ) A
                                                WHERE   ROWNUM <= {self.ts_data_count}
                                            )B
                                    where    a.datedeal = b.datedeal
                                    and      a.themecode = '{self.theme_code}'
                                    group by  a.datedeal, A.THEMECODE    
                                ) B
                        WHERE   A.DATEDEAL = B.DATEDEAL (+)                      
                        ORDER BY DATEDEAL ASC
                    )       
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0]
            x[id] = r[1]
        return x