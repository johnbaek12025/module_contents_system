
import socket
import logging

logger = logging.getLogger(__name__)


class SocketManager(object):

    def __init__(self):
        self.conn = None

    def connect(self, host, port):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((host, port))
        except Exception as err:
            logger.error(f"socket connection to {host}/{port} failed : {err}")
            raise

    def disconnect(self):
        if self.conn:
            logger.info(f"disconnect from socket")
            self.conn.close()

    def send(self, data):
        try:
            self.conn.send(data)
        except Exception as err:
            logger.error(f"[socket] seding '{data}' faild:{err}")
            raise

