import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import (get_stock_name, get_cybos7254,
                                  get_before_day, get_before_hour,
                                  get_empty_hour)
from .workshop.chart_jh import Chart, Bar
from adm.jobs import (get_kor_name, get_dealing_str, get_size_rising,
                      get_size_str, get_size_symbol, get_size_color,
                      get_unit_str, circle_symbol, get_sort, get_time_period,
                      get_previous_day)

logger = logging.getLogger(__name__)


def set_bar(bar):
    """
        차트 부분에서 날짜를 보여주기위해 
        20210104 -> 01/04로 포맷하는 함수
    """
    if None in [bar.tick, bar.value]:
        return False
    month = bar.tick[4:6]
    day = bar.tick[6:8]
    bar.tick = f"{month}/{day}"
    return True


def get_bar_chart_data(rows: dict, func):
    """
        차트를 만들기 위해 
        key와 value를 분리해서
        리스트로 만드는 함수
    """
    set_bar_chart_data = []
    for tick in rows:
        bar = Bar()
        bar.tick = tick
        bar.value = rows[tick]
        if func(bar):
            set_bar_chart_data.append(bar)
    return set_bar_chart_data


def get_bar_chart(rows: list, local_image_whole_path, line=None, days=None):
    """
        차트를 만드는 함수
    """
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
    for i, row in enumerate(rows):
        bar_chart_data = get_bar_chart_data(rows=row, func=set_bar)
        bc.add_data(bar_chart_data, 'plot', colors=colors[i])
    bc.finalize_chart(local_image_whole_path, leg=rows, grid='xgrid')


class Contents(ADManager):
    def __init__(self):
        """
            공통 변수 정의
        """
        ADManager.__init__(self)
        self.use_ftp = True
        self.ts_data_count = 20
        self.stock_list = 4
        self.count = 2
        self.issn = None
        self.is_str = None
        self.dir_type = None

    def set_analysis_target(self):
        """
            data_eng 테이블에서 해당 콘텐츠의 컬럼 가져오는 함수
        """
        columns = ["issn", "is_str", "dir_type"]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.issn = row.get('issn')
        self.is_str = row.get('is_str')
        self.dir_type = row.get('dir_type')
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        """
          해당 콘텐츠의 제목 부분
        """
        news_title_list = [
            {
                "text": f"",
                "color": None
            },
            {
                "text": (f"''{self.is_str}'' 관련 종목, "
                         f"최근 {get_size_rising(self.dir_type)} 포착"),
                "color":
                get_size_color(self.dir_type),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        """
            콘텐츠의 내용 부분에서 상 중 하로 나뉜 것을 합쳐서  return
        """
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr()}
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        """
            콘텐츠의 상단 부분으로 차트의 설명을 html로 만들어서 출력하는 함수
        """
        return f"""
            <div class="module-tbl-txt">
            <span>괸련 종목 평균 등락률 추이</span>
            </div>
            <div class="module-tbl-guide mt-15">                
            </div>
        """

    def get_middle_tr(self):
        """
            콘텐츠 내용부분에서 중간부분으로  차트를 만들어서 html로 출력 하는 함수
        """
        rows = self.get_ratio_info()
        get_bar_chart(rows=rows,
                      local_image_whole_path=self.local_image_whole_path,
                      line=self.count)
        return f"""
            <div class="module-chart text-center bgcolor">
                <img style="height:auto; max-width:100%;" src="{self.image_url}">               
            </div>     
        """

    def get_bottom_tr(self):
        """
            콘텐츠에서 하단 부분으로 등락률 상위 종목들을 html로 만들어서 출력하는 함수
        """
        a = self.get_stock_name()
        return f"""
            <div class="module-tbl-txt mt-20">                
                <div class="c999 dot">등락률 상위 종목: {', '.join(a)} 등</div>      
            </div>            
        """

    def get_stock_name(self):
        """
            콘텐츠 하단 부분에서 사용 할 등락률 상위 종목들의 코드를 수집한 후 
            코드에 해당하는 종목명을 리스트로 만들어서 출력하는 함수
        """
        row = self.get_stock_list()
        x = []
        for r in row:
            name = self.data_db_mgr.get_master_info(self.deal_date,
                                                    r['stkname'])
            x.append(name['name'])
        return x

    def get_ratio_info(self):
        """
            콘텐츠의 차트를 만드는데 사용할 데이터를 수집하는 함수
        """
        sql = f"""
               SELECT  a.DATEDEAL,
                       DECODE(a.avr, null, 0, a.avr) AS avr
               FROM   (
                                select  A.DATEDEAL,        
                                        nvl(ROUND(SUM(A.RATIO)/COUNT(C.CODE), 3), ROUND(SUM(B.FLUCT_RATIO)/COUNT(C.CODE), 3))avr
                                from    STOCK_1_DAY A,
                                        a3_curprice B,
                                        KTP.CT_ISSUE_CODE C
                                WHERE   C.ISSN = '{self.issn}'
                                AND     A.CODE = C.CODE
                                AND     B.STK_CODE = C.CODE                    
                                GROUP BY  A.DATEDEAL                
                        )A,
                        (
                                SELECT  DATEDEAL         
                                FROM    (
                                            SELECT  DATEDEAL                                        
                                            FROM    TRADE_DAY
                                            WHERE   DATEDEAL <= '{self.deal_date}'
                                            ORDER BY DATEDEAL DESC
                                        ) 
                                WHERE   ROWNUM <={self.ts_data_count}
                        )B
                WHERE   A.DATEDEAL = B.DATEDEAL
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0]
            x[id] = r[1]
        return [x]

    def get_stock_list(self):
        """
            등락률 상위 종목들의 코드를 수집하는 함수
        """
        sql = f"""
            select *
            from  (
                        select  code 
                        from    a3_curprice A,
                                KTP.CT_ISSUE_CODE B
                        where   b.issn = '{self.issn}'        
                        and     a.stk_code = b.code
                        and     a.d_cntr = '{self.deal_date}'
                        order by  A.fluct_ratio desc
                    )
            where rownum <= {self.stock_list}
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({'stkname': r[0]})
        return x
