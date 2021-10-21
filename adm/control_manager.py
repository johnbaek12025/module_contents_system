import logging
import time

from adm import to_int, to_bool
from adm.db_manager_ad import DBManager
from adm.ftp_manager import FTPManager
from adm.smtp_manager import SMTPManager
from adm.kafka_manager import KafkaManager
from adm.exceptions import ConfigError, ContentsError
from adm.jobs import get_sort

logger = logging.getLogger(__name__)


class ControlManager(object):
    def __init__(self):
        # config info
        self.oracle_info = None
        self.rc_db_info = None
        self.data_db_info = None
        self.target_db_info = None
        self.kafka_info = None
        self.ftp1_info = None
        self.ftp2_info = None
        self.smtp_info = None
        self.lib_path = None

        self.rc_db_mgr = None
        self.nu_db_mgr = None
        self.data_db_mgr = None
        self.t_db_mgr = None

        self.kafka_mgr = None
        self.ftp1_mgr = None
        self.ftp2_mgr = None

        self.sleep_interval = None
        self.local_image_path = None
        self.image_base_url = None
        self.use_kafka = None

        self.news_code_initial = "ta"

    def check_config(self, config_dict):
        self.oracle_info = config_dict.get("oracle")
        if not self.oracle_info:
            ConfigError("check config file: [oracle]")

        self.rc_db_info = config_dict.get("rc_database")
        if not self.rc_db_info:
            ConfigError("check config file: [rc_database]")

        self.nu_db_info = config_dict.get("news_user_database")
        if not self.nu_db_info:
            ConfigError("check config file: [news_user_database]")

        self.data_db_info = config_dict.get("data_database")
        if not self.data_db_info:
            ConfigError("check config file: [data_database]")

        self.target_db_info = config_dict.get("target_database")
        if not self.target_db_info:
            ConfigError("check config file: [target_database]")

        self.kafka_info = config_dict.get("kafka")
        if not self.kafka_info:
            ConfigError("check config file: [kafka]")

        self.ftp1_info = config_dict.get("ftp_1")
        if not self.ftp1_info:
            ConfigError("check config file: [ftp_1]")

        self.ftp2_info = config_dict.get("ftp_2")
        if not self.ftp2_info:
            ConfigError("check config file: [ftp_2]")

        self.smtp_info = config_dict.get("smtp")
        if not self.smtp_info:
            ConfigError("check config file: [smtp]")

        self.lib_path = self.oracle_info.get("lib_path")
        if not self.lib_path:
            ConfigError("check config file: [oracle][lib_path]")
            return

        self.adm_info = config_dict.get("adm")
        if not self.adm_info:
            ConfigError("check config file: [adm]")
            return

        self.sleep_interval = float(self.adm_info.get("sleep_interval", 10))
        self.local_image_path = self.adm_info.get("local_image_path")
        self.image_base_url = self.adm_info.get("image_base_url")
        self.test_mode = to_bool(self.adm_info.get("test_mode", False))
        self.use_kafka = to_bool(self.adm_info.get("use_kafka", False))

    def initialize_oracle_lib_path(self):
        logger.info("initialize orcle lib_path")
        DBManager().set_lib_path(self.lib_path)

    def connect_to_db(self):
        logger.info("connect to databases")
        self.rc_db_mgr = DBManager()
        self.rc_db_mgr.connect(**self.rc_db_info)

        self.data_db_mgr = DBManager()
        self.data_db_mgr.connect(**self.data_db_info)

        self.nu_db_mgr = DBManager()
        self.nu_db_mgr.connect(**self.nu_db_info)

        self.t_db_mgr = DBManager()
        self.t_db_mgr.connect(**self.target_db_info)

    def connect_to_ftp(self):
        logger.info("connect to ftp")
        self.ftp1_info["ftp_port"] = to_int(self.ftp1_info["ftp_port"])
        self.ftp1_mgr = FTPManager()
        self.ftp1_mgr.connect(**self.ftp1_info)

        self.ftp2_info["ftp_port"] = to_int(self.ftp2_info["ftp_port"])
        self.ftp2_mgr = FTPManager()
        self.ftp2_mgr.connect(**self.ftp2_info)

    def connect_to_kafka(self):
        logger.info("connect to kafka")
        self.kafka_mgr = KafkaManager()
        self.kafka_mgr.connect(**self.kafka_info)

    def disconnect_from_db(self):
        logger.info("disconnect from databases")
        if self.rc_db_mgr:
            self.rc_db_mgr.disconnect()

        if self.t_db_mgr:
            self.t_db_mgr.disconnect()

    def disconnect_from_ftp(self):
        if self.ftp1_mgr:
            self.ftp1_mgr.disconnect()

    def disconnect_from_kafka(self):
        if self.kafka_mgr:
            self.kafka_mgr.disconnect()

    def send_email(self, message):
        smtp_manager = SMTPManager(**self.smtp_info)
        smtp_manager.send_email(message)

    def initialize(self, config):
        self.check_config(config)

    def run(self, test_data=None):
        self.initialize_oracle_lib_path()
        cur_request = None
        while True:
            try:
                self.connect_to_db()
                self.connect_to_ftp()
                if self.use_kafka:
                    self.connect_to_kafka()

                if test_data is not None:
                    self.create_contents([test_data])
                    break

                requests = self.data_db_mgr.get_requests(count=10)
                self.create_contents(requests)
                time.sleep(self.sleep_interval)
            except KeyboardInterrupt as err:
                logger.info(f"key interruption : {cur_request}")
            except ConfigError as err:
                logger.info(err)                
            finally:
                self.disconnect_from_db()
                self.disconnect_from_ftp()
                self.disconnect_from_kafka()

    def validate_target_list(self, t):
        info_seq = t.get("info_seq")
        request_type = t.get("request_type")
        info_code = t.get("info_code")
        deal_date = t.get("deal_date")
        is_manual = t.get("is_manual")

        messages = []
        if info_seq is None:
            messages.append("info_seq is None")
        if request_type is None:
            messages.append("request_type is None")
        if info_code is None:
            messages.append("info_code is None")
        if deal_date is None:
            messages.append("deal_date is None")
        if is_manual is None:
            messages.append("is_manual is None")

        if messages:
            return messages

        if request_type not in ["I", "U", "D"]:
            messages.append(
                f"'request_type' should be 'I', 'U' or 'D', current value: {request_type}"
            )
        if len(info_code.split("_")) != 3:
            messages.append(f"wrong news code type : {info_code}")
        if len(deal_date) != 8:
            messages.append("the length of deal_date should be 8")
        if is_manual not in ["0", "1"]:
            messages.append(
                f"'is_manual' should be '0' or '1', current value: {is_manual}"
            )
        return messages

    def get_analysis_object(self, analysis_type):
        content, message = None, None
        try:
            exec(f"from .jobs.{analysis_type} import Contents")
        except ModuleNotFoundError as err:
            message = f"news code '{analysis_type}' does not exist : {err}"
            return content, message
        try:
            content = eval("Contents()")
        except Exception as err:
            message = f"{err}"
            return content, message

        return content, message

    def get_request_dict(self, request):
        info_seq = request["info_seq"]
        info_code = request["info_code"]
        deal_date = request["deal_date"]
        request_type = request["request_type"]
        is_manual = request["is_manual"]
        stock_code = request.get("stock_code")

        analysis_type = info_code.split("_")[1]
        analysis_id = info_code.split("_")[2]

        if self.test_mode:
            news_code = f"test_{self.news_code_initial}_{analysis_type}_{analysis_id}"
        else:
            news_code = f"{self.news_code_initial}_{analysis_type}_{analysis_id}"

        return {
            "deal_date": deal_date,
            "info_seq": info_seq,
            "info_code": info_code,
            "news_code": news_code.upper(),
            "analysis_type": analysis_type,
            "analysis_id": analysis_id,
            "stock_code": stock_code,
            "request_type": request_type,
            "is_manual": is_manual,
            "local_image_path": self.local_image_path,
            "image_base_url": self.image_base_url,
        }

    def comparing_info_code(self, r: dict):
        def make_dict(r, codes):
            x = []
            for name in codes:
                x.append({
                    'deal_date': r.get('deal_date'),
                    'info_seq': r.get('info_seq'),
                    'info_code': r.get('info_code'),
                    'request_type': r.get('request_type'),
                    'is_manual': r.get('is_manual'),
                    "stock_code": codes[name],
                })
            return x

        r_dict = self.get_request_dict(r)
        analysis_type = r_dict['analysis_type']
        deal_date = r_dict['deal_date']
        info_seq = r_dict['info_seq']
        column2 = ["theme_code"]
        if analysis_type in {'iss01', 'iss02'}:
            info = self.data_db_mgr.get_essential_info_data(
                analysis_type, ["issn"], deal_date, info_seq)
            codes = self.rc_db_mgr.get_pre_related_stock(
                info["issn"], 20, deal_date)
            x = make_dict(r, codes)
            return x

        elif analysis_type in {'iss03', 'iss04', 'iss05'}:
            info = self.data_db_mgr.get_essential_info_data(
                analysis_type, ["issn", "dir_type"], deal_date, info_seq)
            codes = self.rc_db_mgr.get_related_stock(
                info["issn"],
                20,
                deal_date,
                order=get_sort(info.get('dir_type')))
            x = make_dict(r, codes)
            return x

        else:
            kind = lambda x: 'dir_type' if x in ['thm02', 'thm04'
                                                 ] else 'sonmeme_type'
            order = kind(analysis_type)
            info = self.data_db_mgr.get_essential_info_data(
                analysis_type,
                ["theme_code", kind(analysis_type)], deal_date, info_seq)
            a = [str(info[x]).lower() for x in info]
            theme_code = a[0]
            sort = get_sort(a[1])
            codes = self.rc_db_mgr.get_related_stock_theme(
                theme_code, deal_date, 5)
            x = make_dict(r, codes)
            return x

    def inflate_requests(self, requests: list):
        inflated_requests = []
        contents = {
            'thm02', 'thm03', 'thm04', 'iss01', 'iss02', 'iss03', 'iss04',
            'iss05'
        }
        for r in requests:
            r_dict = self.get_request_dict(r)
            module_code = r_dict['analysis_type']
            if module_code not in contents:
                inflated_requests.append(r)
                continue
            extention = self.comparing_info_code(r)
            inflated_requests.extend(extention)
        return inflated_requests

    def create_contents(self, requests):
        requests = self.inflate_requests(requests)
        for r in requests:
            logger.info(
                "[start] ############################################################################"
            )
            logger.info(f"start handling: {r}")
            try:
                # '컨텐츠 생성요청' 유효성 체크
                validation_results = self.validate_target_list(r)
                if validation_results:
                    raise ContentsError(
                        f"validation filed: {validation_results}")

                r_dict = self.get_request_dict(r)
                # 컨텐츠 생성 대상 '객체' 불러오기
                c, m = self.get_analysis_object(r_dict["analysis_type"])
                if c is None:
                    raise ContentsError(f"object creation error: {m}")

                c.set_db_conn(self.data_db_mgr, self.rc_db_mgr, self.t_db_mgr)

                # 컨텐츠 생성
                c.initialize(**r_dict)
                if c.create_news():
                    # Image 있는 컨텐츠는 Image를 FTP전송
                    ftp_upload_info = c.get_ftp_upload_info()
                    if bool(ftp_upload_info):
                        self.send_image_to_ftp(ftp_upload_info)

                self.data_db_mgr.handle_processed_requests(r_dict["info_seq"])
                # Broker(Kafka Server)에 메세지 전송
                # 전송실패시, 특별한 조치 없음. 관리자 화면에서 처리함
                self.send_message_to_broker(c, r_dict["news_code"])
            except ContentsError as err:
                logger.error(f"ContentsError : {err}")
                self.data_db_mgr.change_requests_status(r.get("info_seq"),
                                                        status="F")
            finally:
                logger.info(
                    "[end] ##############################################################################"
                )

    def send_image_to_ftp(self, upload_info):
        target_dir = upload_info.get("target_dir")
        from_file_path = upload_info.get("from_file_path")
        to_file_path = upload_info.get("to_file_path")

        if None in [target_dir, from_file_path, to_file_path]:
            raise ContentsError(
                f"Please check ftp upload info: {target_dir, from_file_path, to_file_path}"
            )

        for m in [self.ftp1_mgr, self.ftp2_mgr]:
            m.check_path(target_dir)
            m.send(from_file_path, to_file_path)

    def send_message_to_broker(self, module, news_code):
        if not self.use_kafka:
            logger.error("[error] use_kafka is false")
            return
        topics = self.nu_db_mgr.get_topics(news_code)
        if not topics:
            logger.error(f"[error] news_code {news_code} dose not have topics")
            return
        message = module.get_data_to_publish()
        for topic in topics:
            self.kafka_mgr.send_messages([(topic, message, 0.01)])
