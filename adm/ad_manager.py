import logging
from abc import ABCMeta, abstractmethod
from datetime import datetime

from adm import create_dir
from adm.data_manager import NewsInfo, NewsContent, NewsCom
from adm.exceptions import ContentsError
from adm.jobs import get_file_name, separate_yyyymmdd
from adm.jobs.workshop.html_test import save_to_file

logger = logging.getLogger(__name__)

# 각 모듈을 관리하는 부모class
class ADManager(metaclass=ABCMeta):

    # sending condition
    SC_CUSTOM = 1
    SC_UPDATE = 2
    SC_ONCE = 3
    SC_GONGSI = 4

    def __init__(self):
        self.process_condition = ADManager.SC_CUSTOM # default 상태

        # 현재날짜 가져오기
        self.now_datetime = datetime.today().strftime("%Y%m%d%H%M%S")
        self.now_date = self.now_datetime[:8]
        self.now_time = self.now_datetime[8:]
        self.now_month = str(int(self.now_datetime[4:6]))
        self.now_day = str(int(self.now_datetime[6:8]))

        self.news_seq = None
        self.deal_date = None
        self.deal_date_yyyy = None
        self.deal_date_mm = None
        self.deal_date_dd = None
        self.info_code = None
        self.news_code = None

        self.stock_code = None
        self.theme_code = None
        self.issn = None

        self.analysis_id = None
        self.deal_day = None

        self.info_seq = None

        self.news_info = None
        self.news_cnts = None
        self.news_com = None

        self.local_image_path = None
        self.local_image_name = None
        self.local_image_whole_path = None
        self.image_sub_url = None
        self.image_url = None

        self.data_db_mgr = None
        self.rc_db_mgr = None
        self.t_db_mgr = None
        self.use_ftp = False
        self.rep_image = None

    def set_db_conn(self, data_db_mgr, rc_db_mgr, t_db_mgr):
        self.data_db_mgr = data_db_mgr
        self.rc_db_mgr = rc_db_mgr
        self.t_db_mgr = t_db_mgr

    def initialize(self, **kwargs):
        self.news_seq = self.t_db_mgr.get_news_seq()
        # news_seq 가 없을리가 없지만 혹시 몰라서 추가함
        if self.news_seq is None:
            raise Exception(f"news_seq 값이 없습니다: {self.news_seq}")

        self.deal_date = kwargs.get("deal_date")
        # fixme: deal_date_dd 와 deal_day 가 같다. 전체 파일 변경을 통해 deal_date_dd로 통일하자
        self.deal_date_yyyy, self.deal_date_mm, self.deal_date_dd = separate_yyyymmdd(
            self.deal_date)
        self.deal_day = int(self.deal_date[6:8])

        self.info_seq = kwargs.get("info_seq")
        self.info_code = kwargs.get("info_code")
        self.news_code = kwargs.get("news_code")

        self.analysis_type = kwargs.get("analysis_type")
        self.analysis_id = kwargs.get("analysis_id")

        self.request_type = kwargs.get("request_type")
        self.is_manual = kwargs.get("is_manual")
        self.stock_code = kwargs.get("stock_code")
        local_image_path = kwargs.get("local_image_path")
        self.local_image_path = f"{local_image_path}/{self.deal_date}"
        stock_code = lambda x: f'_{x}' if x else ''
        self.local_image_name = (
            f"{self.deal_date}_{self.news_code}{stock_code(self.stock_code)}.jpg"
        )
        self.local_image_whole_path = f"{self.local_image_path}/{self.local_image_name}"
        self.image_sub_url = f"{self.deal_date}/{self.local_image_name}"

        image_base_url = kwargs.get("image_base_url")
        self.image_url = f"{image_base_url}/{self.image_sub_url}"
        create_dir(self.local_image_path)
        # row = self.rc_db_mgr.get_master_info(self.deal_date, self.stock_code)
        # if self.stock_code:
        #     self.stock_name = row.get("name", self.stock_code)

        logger.info(f"news_seq: {self.news_seq}, "
                    f"info_code: {self.info_code}, "
                    f"news_code: {self.news_code}, "
                    f"deal_date: {self.deal_date}, "
                    f"stock_code: {self.stock_code}, "
                    f"theme_code: {self.theme_code}, "
                    f"analysis_type: {self.analysis_type}, "
                    f"analysis_id: {self.analysis_id}, "
                    f"request_type: {self.request_type}, "
                    f"deal_day: {self.deal_day}, "
                    f"local_image_whole_path: {self.local_image_whole_path}, ")

    @abstractmethod
    def set_analysis_target(self):
        pass

    def set_news_info(self, org_data=dict()):
        news_info_dict = dict()
        if self.request_type == "I":
            news_info_data = self.make_news_info()
            news_info_data["news_title"] = self.set_news_title_style(
                news_info_data["news_title"])
            news_info_dict = {
                "news_seq": self.news_seq,
                "now_date": self.now_date,
                "now_time": self.now_time,
                "news_code": self.news_code,
                "stock_code": self.stock_code,
                "news_title": news_info_data["news_title"],
                "request_type": self.request_type,
                "is_manual": self.is_manual,
                "is_reserved": "N",
                "org_news_seq": None,
                "org_now_date": None,
            }

        elif self.request_type == "D":
            news_info_dict = {
                "news_seq": self.news_seq,
                "now_date": self.now_date,
                "now_time": self.now_time,
                "news_code": org_data.get("news_code"),
                "stock_code": org_data.get("stock_code"),
                "news_title": org_data.get("news_title"),
                "request_type": self.request_type,
                "is_manual": self.is_manual,
                "is_reserved": "N",
                "org_news_seq": org_data.get("news_seq"),
                "org_now_date": org_data.get("news_date"),
            }

        elif self.request_type == "U":
            news_info_data = self.make_news_info()
            news_info_data["news_title"] = self.set_news_title_style(
                news_info_data["news_title"])
            news_info_dict = {
                "news_seq": self.news_seq,
                "now_date": self.now_date,
                "now_time": self.now_time,
                "news_code": self.news_code,
                "stock_code": self.stock_code,
                "news_title": news_info_data["news_title"],
                "request_type": self.request_type,
                "is_manual": self.is_manual,
                "is_reserved": "N",
                "org_news_seq": org_data.get("news_seq"),
                "org_now_date": org_data.get("news_date"),
            }

        self.news_info = NewsInfo(**news_info_dict)

    def set_news_cnts(self):
        # child_Class make_news_cnts method 실행
        news_cnts_data = self.make_news_cnts()
        news_cnts_dict = {
            "news_seq": self.news_seq,
            "now_date": self.now_date,
            "now_time": self.now_time,
            "contents_type": "T",
            "news_cnts": news_cnts_data["news_cnts"],
            "news_code": self.news_code,
            "rep_image": self.rep_image,
        }
        # 생성된 내용을 print 하기위해 constructor로 보냄
        self.news_cnts = NewsContent(**news_cnts_dict)

    def set_news_com(self):
        news_com_dict = {
            "news_seq": self.news_seq,
            "now_date": self.now_date,
            "info_seq": self.info_seq,
            "info_code": self.info_code,
        }
        # 생성된 내용을 print 하기위해 constructor로 보냄
        self.news_com = NewsCom(**news_com_dict)

    def custom_process_condition(self):
        # implement the details in the inherited class.
        return True, {}

    def check_process_condition(self):        
        if self.request_type in ["U", "D"]:
            org_data = self.t_db_mgr.get_original_data(self.info_seq)
            return True, org_data

        if self.process_condition == ADManager.SC_CUSTOM:
            return self.custom_process_condition()

        if self.process_condition == ADManager.SC_UPDATE:
            count = self.data_db_mgr.check_if_exist_in_als_main(
                self.deal_date,
                self.info_code,
                self.stock_code,
                self.theme_code,
                self.issn,
            )
            if count == 0:
                logger.info(
                    f"content is not created by the process condition: process_condition {self.process_condition}, count {count}"
                )
                return False, {}
            elif count == 1:
                return True, {}
            else:
                self.request_type = "U"
                org_data = self.data_db_mgr.get_lastest_infosn(
                    self.deal_date,
                    self.info_code,
                    self.stock_code,
                    self.theme_code,
                    self.issn,
                )
                return True, org_data

        if self.process_condition == ADManager.SC_ONCE:
            return self.sending_once()

        if self.process_condition == ADManager.SC_GONGSI:
            x = {
                'gos01': ['ORIG_RCPNO'],
                'gos02': ['ORIRCPNO'],
                'gos03': ['ORIRCPNO'],
                'gos04': ['ORIRCPNO', 'CHICOMTP'],
                'gos05': ['ORIRCPNO', 'CHICOMTP'],
                'gos06': ['ORIRCPNO'],
                'gos07': ['ORIRCPNO'],
            }
            f = [a for a in x]
            if self.analysis_type in f:
                result, org_data = self.data_db_mgr.check_gongsi_condition(
                    self.analysis_type, self.info_seq, x[self.analysis_type])
                return result, org_data

    def sending_once(self):
        count = self.data_db_mgr.check_if_exist_in_als_main(
            self.deal_date,
            self.info_code,
            self.stock_code,
            self.theme_code,
            self.issn,
        )
        if count == 0:
            return True, {}
        else:
            logger.info(
                f"content is not created by the process condition: process_condition {self.process_condition}, count {count}"
            )
            return False, {}

    def create_news(self):
        # child method 실행
        self.set_analysis_target()
        # 모듈별 process_condition 할당
        process_condition, org_data = self.check_process_condition()

        if not process_condition:
            return False

        self.set_news_info(org_data)
        self.news_info.print()

        if self.request_type != "D":
            news_info_data = self.make_news_info()
            news_info_data["news_title"] = self.set_news_title_style(
                news_info_data["news_title"])
            # 콘텐츠 module 내용 생성
            self.set_news_cnts()
            self.news_cnts.print()
            save_to_file(f"{self.deal_date}_{self.news_code}_{self.news_seq}",
                         self.news_cnts.news_cnts,
                         news_info_data["news_title"])

        self.set_news_com()
        self.news_com.print()

        self.save_news()

        return True

    def set_news_title_style(self, news_title_dict):
        data = ""
        for n, r in enumerate(news_title_dict):
            color = r.get("color")
            text = r.get("text")
            if color is None:
                data += f"<strong>{text}</strong>"
            else:
                c = "up" if color == "red" else "dn"
                data += f'<strong class="{c}">{text}</strong>'
        return data

    def add_news_link(self, link):
        return f"""
            <a href="{link}" class="pull-right">&#8594; 더보기</a>
        """

    def get_socket_data(self):
        return (
            f'<?xml version="1.0" encoding="euc-kr"?> '
            f'<news_info sn="{str(self.news_seq)}" news_code="{str(self.news_code)}" '
            f'date="{self.now_date}" />').encode()

    @abstractmethod
    def make_news_info(self):
        return {}

    @abstractmethod
    def make_news_cnts(self):
        return {}

    def save_news(self):
        self.t_db_mgr.save_news_info(self.news_info, commit=False)
        if self.request_type != "D":
            self.t_db_mgr.save_news_cnts(self.news_cnts, commit=False)
        self.t_db_mgr.save_news_com(self.news_com, commit=False)
        self.t_db_mgr.commit()

    def get_ftp_upload_info(self):
        ftp_upload_dict = {}
        if self.use_ftp:
            ftp_upload_dict["target_dir"] = self.deal_date
            ftp_upload_dict["from_file_path"] = self.local_image_whole_path
            ftp_upload_dict["to_file_path"] = self.image_sub_url
        return ftp_upload_dict

    def get_data_to_publish(self):
        return {
            "news_code": self.news_code,
            "news_sn": self.news_seq,
            "d_news_crt": self.now_date,
        }
