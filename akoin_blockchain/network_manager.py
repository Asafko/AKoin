import pickle
import socket
from typing import List

from urllib.parse import urlparse

from .constants import BUFFERSIZE, HEADERSIZE, MAX_MESSAGE_SIZE
from .helper_functions import get_logger

logger = get_logger(__name__)


class NetworkManager:
    def __init__(self):
        self.url_set = set()
        self.socket_list = []
        
    @staticmethod
    def parse_message_buffer(s: 'socket.socket') -> bytes:
        msg = s.recv(BUFFERSIZE)
        full_message = msg[HEADERSIZE:]
        if not msg[:HEADERSIZE]:
            return None
        
        msglen = int(msg[:HEADERSIZE])
        
        while len(full_message) <= MAX_MESSAGE_SIZE:
            if len(full_message) == msglen:
                return full_message
            
            full_message += s.recv(BUFFERSIZE)
        
        logger.error(f'Message size Exeeded: {len(full_message)}/{MAX_MESSAGE_SIZE}')
        raise Exception("Message Size Exeeded!") 
        
    @staticmethod
    def serialize_message(message_dict: dict) -> bytes:
        msg = pickle.dumps(message_dict)
        return bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8') + msg
        
    def connect_to_node(self, ip: str, port: int) -> bool:
        try:
            self.set_up_socket(ip, port)
            logger.info(f'New Socket connection: {ip}:{port}')
            return True
        except OSError as e:
            logger.exception(f'Unable to connect to socket! \n Exception: {e}')
            return False
        
    @staticmethod
    def deserialize(r: str) -> dict:
        return pickle.loads(r)
        
    def set_up_socket(self, ip: str, port: int):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        self.socket_list.append(s)
        
    def register_new_node(self, url: str):
        if url in self.url_set:
            logger.info('Peer already connected')
            return False
        
        ip, port = urlparse(url).netloc.split(':')
        self.connect_to_node(ip, int(port))
        self.url_set.add(url)
        logger.info(f'socket connected to {ip}:{port}')
        return True
        
    def message_node(self, s: socket.socket, path: str, data: dict):
        s.send(self.serialize_message({'path': path, 'data': data}))
        return self.deserialize(self.parse_message_buffer(s))
        
    def message_all_nodes(self, path: str, data: dict) -> List[bytes]:
        responses = []
        for s in self.socket_list:
            res = self.message_node(s, path, data)
            responses.append(res)
            
        logger.debug(f'Responses: {responses}')
        return responses
