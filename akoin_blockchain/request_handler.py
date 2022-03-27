from typing import List

from akoin_blockchain.helper_functions import get_logger
from akoin_blockchain.node import Node


logger = get_logger(__name__)


class RequestHandler:
    
    @staticmethod   
    def mine(node: Node, data: dict) -> dict:
        try:
            node.mine_new_block()
            return {'message': 'block mined!', 
                    'success': True}   
        except Exception:
            logger.exception('Error mining block')
            return {'success': False,
                    'message': 'Error mining block'}
       
    @staticmethod
    def get_chain(node: Node, data: dict) -> dict:
        return {'message': 'got chain', 
                'chain': node.blockchain.get_chain(), 
                'success': True}
    
    @staticmethod
    def get_chain_length(node: Node, data: dict) -> dict:
        return {'message': 'got chain length', 
                'chain-length': node.blockchain.chain_length,
                'success': True}
    
    @staticmethod
    def get_chain_address(node: Node, data: dict) -> dict:
        return {'message': 'got address', 
                'chain-address': node.blockchain_address,
                'success': True}
    
    @staticmethod
    def add_transaction(node: Node, data: dict) -> dict:
        try:
            t = node.create_signed_transaction(**data)
            node.transmit_transactions()
            return {'message': 'new transaction created',
                    'transaction': t.as_json(), 'success': True}
        except:
            logger.exception('bad transaction data')
            return {'message': 'bad transaction data', 'success': False}
    
    @staticmethod
    def replace_chain(node: Node, data: dict) -> dict:
        try:
            replaced = node.replace_chain(data)
            replaced_message = '' if replaced else 'not'
            return {'message': f'chain {replaced_message} replaced!', 
                    'replaced': replaced,
                    'success': True}
        except:
            logger.exception('bad chain data')
            return {'message': 'bad chain data', 'success': False}
        
    @staticmethod
    def get_nodes(node: Node, data: dict) -> dict:
        return {'message': 'got nodes', 'nodes': node.nodes, 'success': True}
    
    @staticmethod
    def register_node(node: Node, data: Node) -> dict:
        try:
            own_node = node.add_node(data)
            return {'message': 'node added!', 
                    'node': own_node, 
                    'success': True}
        except:
            logger.exception('bad node data')
            return {'message': 'bad node data', 'success': False}
        
    @staticmethod
    def register_new_transactions(node: Node, data: List[str]) -> dict:
        try:
            node.receive_transactions(data)
            return {'message': 'transactions accepted to mempool', 
                    'success': True}
        except:
            logger.exception('bad transaction data')
            return {'message': 'bad transaction data', 'success': False}
    
    @staticmethod
    def handle_request(node: Node, req: dict) -> dict:
        try:
            logger.info(f'got request: {req}')
            return getattr(RequestHandler, req['path'])(node, req['data'])
        except AttributeError:
            logger.exception(f'bad request path {req}')
            return {'message': f'unknown request path {req}'}
        except Exception as e:
            logger.exception('Unknown Error occured!')
            return {'message': f'Internal Error: {e}'}
