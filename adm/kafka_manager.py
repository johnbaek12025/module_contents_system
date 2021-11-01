import logging
import time

from kafka import KafkaProducer
from json import dumps


logger = logging.getLogger(__name__)


class KafkaManager(object):
    def __init__(self):
        self.uri = None
        self.topic = None
        self.conn = None

    def connect(self, host, port, auto_offset_reset="latest"):
        # TODO: partition 설정 해줘야 함
        # acks 1로 설정 하여 처리결과를 return 하도록 설정
        # 메시지에 대한 압축은 압축률이 높은 gzip을 채택        
        # value는 utf-8로 설정
        self.uri = f"{host}:{str(port)}"
        logger.info(f"connect to kafka server {self.uri}")
        try:
            self.conn = KafkaProducer(
                acks=1,
                compression_type="gzip",
                bootstrap_servers=[self.uri],
                value_serializer=lambda x: dumps(x).encode("utf-8"),
            )
        except Exception as err:
            logger.error(f"kafka connection to {self.uri} failed: {err}")
            raise

    def disconnect(self):
        if self.conn:
            logger.info(f"disconnect from {self.uri}")
            self.conn.close()
            self.conn = None

    def send_messages(self, msg_list):
        for topic, msg, delay in msg_list:
            logger.info(f"send message: topic={topic}, message={msg}, delay={delay}")
            self.conn.send(topic, value=msg)
            time.sleep(delay)
        self.conn.flush()
