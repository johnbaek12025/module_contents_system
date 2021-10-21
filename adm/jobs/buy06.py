import datetime
import logging

from adm import to_int
from adm.ad_manager import ADManager
from .workshop.chart import Chart, get_bar_chart_data
from .workshop.common_cyg import get_bottom_values, get_stock_list_str
from .workshop.commom_bjh import get_stock_name, get_cybos7254
from adm.jobs import (
    get_kor_name,
    get_dealing_str,
    get_size_str,
    get_size_symbol,
    get_size_color,
    get_unit_str,
    circle_symbol,
)

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
        bar.color = "blue"
    return True


def get_bar_chart(rows, local_image_whole_path):
    chart_dict = {
        "face_color": "whitesmoke",
        "grid_color": None,
        "spine_top": False,
        "spine_left": False,
        "spine_right": False,
        "xaxis_format": "%m/%d",
        "tick_position": "left",
        "tick_interval": 4,
    }
    bc = Chart(**chart_dict)
    bar_chart_data = get_bar_chart_data(rows=rows, func=set_bar)
    bc.add_data(bar_chart_data, chart_type="bar", xhline=0)
    bc.finalize_chart(local_image_whole_path, 4)


class Contents(ADManager):
    def __init__(self):
        ADManager.__init__(self)
        self.dealing_type = None
        self.subject = None
        self.unit = 'amt'
        self.use_ftp = True
        self.ts_data_count = 20
        self.accumulated_days = 3
        self.process_condition = ADManager.SC_ONCE

    def set_analysis_target(self):
        sort = lambda x: 'desc' if 'mesu' else 'asc'
        columns = [
            "sonmeme_type", "customer_type", "stk_code", 'stk_name', "market"
        ]
        row = self.data_db_mgr.get_essential_info_data(self.analysis_type,
                                                       columns, self.deal_date,
                                                       self.info_seq)
        self.stock_code = row.get("stk_code")
        self.stock_name = row.get("stk_name")
        self.market = row.get("market")
        self.dealing_type = row.get("sonmeme_type").lower()
        self.subject = row.get("customer_type").lower()
        self.rep_image = f'https://dev.thinkpool.com/item/{self.stock_code}/trend'

    def make_news_info(self):
        news_title_list = [
            {
                "text": f"{self.deal_date_dd}일 {self.stock_name},",
                "color": None
            },
            {
                "text":
                f"{get_kor_name(self.subject)}  {get_kor_name(self.dealing_type)}세 포착",
                "colo": get_size_color(self.dealing_type),
            },
        ]
        return {"news_title": news_title_list}

    def make_news_cnts(self):
        amt = self.get_volume_trading()
        info = self.get_data_arrange(amt)
        news_cnts = f"""
            {self.get_top_tr()}{self.get_middle_tr()}{self.get_bottom_tr(info)}
        """
        return {"news_cnts": news_cnts}

    def get_top_tr(self):
        kor_subject = get_kor_name(self.subject)
        return f"""
            <div class="module-tbl-txt">
                <strong class="title title-s">{kor_subject} 순매매 동향</strong>
                <span>(단위: {get_unit_str(self.unit)})</span>
            </div>            
        """

    def get_middle_tr(self):
        rows = self.rc_db_mgr.get_7254_ts_data(
            self.stock_code,
            self.subject,
            "sonmeme",
            self.unit,
            self.deal_date,
            self.ts_data_count,
        )
        get_bar_chart(rows, self.local_image_whole_path)
        return f"""
            <div class="module-chart text-center bgcolor">
                <img style="height:auto; max-width:100%;" src="{self.image_url}">               
            </div>     
        """

    def get_bottom_tr(self, info):
        rows = self.rc_db_mgr.get_7254_accu_value(self.deal_date,
                                                  self.stock_code, 'sonmeme',
                                                  'amt', self.accumulated_days)
        print()

        return f"""
            <div class="module-tbl-txt mt-20">
                <div class="dot"> {get_kor_name(self.subject)} {get_dealing_str(self.dealing_type)}세 포착: 최근{self.accumulated_days}일 누적 {get_dealing_str(rows[self.subject])} {rows[self.subject]}백만원</div>                
                <div class="up dot"> {info}</div>
            </div>
        """

    def get_volume_trading(self):
        sql = f"""
            {get_cybos7254(self.subject, 'sonmeme_amt', 'desc', self.deal_date)}
            where x.stkcode = '{self.stock_code}'
            """
        rows = self.data_db_mgr.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append({
                'org': r[2],
                'for': r[1],
                'etc': r[3],
            })
        return x[0]

    def get_data_arrange(self, amt):
        col = []
        for r in amt:
            if r == 'org':
                if amt[r]:
                    col.append(
                        f'{get_kor_name(r)} {abs(amt[r])}백만원 {get_dealing_str(amt[r])}'
                    )
                else:
                    continue
            elif r == 'for':
                if amt[r]:
                    col.append(
                        f'{get_kor_name(r)} {abs(amt[r])}백만원 {get_dealing_str(amt[r])}'
                    )
                else:
                    continue
            else:
                if amt[r]:
                    col.append(
                        f'{get_kor_name(r)} {abs(amt[r])}백만원 {get_dealing_str(amt[r])}'
                    )
                else:
                    continue
        return f'{self.deal_date_dd}일 매매 동향: {", ".join(col)}'