import concurrent.futures
import socket
import os

from dotenv import load_dotenv
from typing import Tuple

from akoin_blockchain.helper_functions import get_logger
from akoin_blockchain.network_manager import NetworkManager
from akoin_blockchain.node import Node
from akoin_blockchain.request_handler import RequestHandler

from akoin_blockchain.constants import PORT, LOCAL_HOST, MAX_CONNECTIONS

load_dotenv()
logger = get_logger(__name__)
dry_run = int(os.getenv('DRY_RUN'))

def on_client_send_message(net_objects: Tuple['socket.socket', Node]):
    client = net_objects[0]
    node = net_objects[1]
    request = None
    new_connection = True
    serialized_request = b''
    try:
        while serialized_request != b'' or new_connection:
            new_connection = False
            serialized_request = NetworkManager.parse_message_buffer(client)
            request = NetworkManager.deserialize(serialized_request)
            response = RequestHandler.handle_request(node, request)
            serialized_response = NetworkManager.serialize_message(response)
            client.send(serialized_response)
        logger.debug('socket closed (Buffer drained)')
        client.close()
    except socket.timeout:
        logger.debug('socket closed (Timeout)')
        client.close()
        
def make_listener_socket() -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_bound = False
    port = PORT
    while not socket_bound:
        try:
            s.bind((LOCAL_HOST, port))
            socket_bound = True
        except OSError as e:
            if dry_run:
                logger.warning('Port in use, will try the next one')
                port += 1
            else:
                logger.exception('Port in use!')
                raise e
                                
    s.listen(MAX_CONNECTIONS)
    s.settimeout(1)  # seconds
    return s

def make_node(sockname: tuple):
    host = sockname[0]
    port = sockname[1]
    web_address = f'http://{host}:{port}'
    logger.info(f'Node litening on {web_address}')
    node = Node(web_address)
    logger.info(f'Node blockchain address: {node.blockchain_address}')
    return node

def main():
    listener = make_listener_socket()
    node = make_node(listener.getsockname())
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            try:
                client, address = listener.accept()
                client.settimeout(10)  # seconds
                executor.submit(on_client_send_message, (client, node))
            except KeyboardInterrupt:
                listener.close()
                logger.info('Keyboard Interrupt closing')
                return
            except socket.timeout:
                logger.debug('listener socket timed out (normal)')
            

if __name__ == "__main__":
    main()
   
