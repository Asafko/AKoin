from typing import Dict, List

from .account import Account
from .blockchain import Blockchain
from .key_master import KeyMaster
from .network_manager import NetworkManager
from .transaction import Transaction

from .helper_functions import days_ago, is_url_valid, get_logger
from .constants import TRANSACTION_MAX_DAYS

logger = get_logger(__name__)


class Node:
    def __init__(self, web_address: str):
        self.keys = KeyMaster.generate_keys()
        self.web_address = web_address
        self.network_manager = NetworkManager()
        self.blockchain_address = self.keys['public_key_string']
        self.account = Account(self.keys['public_key_string'])
        self.nodes = {}
        self.transactions = set()
        self.mempool = set()
        self.blockchain = Blockchain(self.keys['public_key_string'])
        self.account.chain = self.blockchain.chain
        logger.info('Node Created!')
 
    @staticmethod
    def is_transaction_verified(t: Transaction) -> bool:
        return KeyMaster.is_verified(t.serialized, t.signature, t.sender)

    def is_fee_valid(self, t: Transaction) -> bool:
        return self.account.get_balance_of(t.sender, 
                                           self.account.chain) >= t.fee + t.amount
    
    def verify_total_amounts(self) -> bool:
        total_amount = sum((t.fee + t.amount) for t in self.transactions)
        logger.debug(f'total amount: {total_amount}')
        return self.account.get_balance() >= total_amount
        
    def is_node_valid(self, node: dict) -> bool:
        return all([is_url_valid(node['web_address']),
                   KeyMaster.is_public_key_string_valid(node['blockchain_address'])])
        
    def register(self):
        node = {self.blockchain_address: self.web_address}
        
        res = self.network_manager.message_all_nodes('register_nodes', node)
        for r in res:
            if r['success']:
                self.add_node(r['node'])
                logger.info(f'Registered with node: {r["node"]}')
                
    def add_new_nodes(self, net_urls: List[str]) -> Dict[str, str]:
        for nu in net_urls:
            self.network_manager.register_new_node(nu)
        self.register()
                
    def add_node(self, node: dict) -> Dict[str, str]:
        if not self.is_node_valid(node):
            logger.debug('Node not valid!')
            return False
        
        node_dict = {node['blockchain_address']: node['web_address']}
        len_before = len(self.nodes)
        self.nodes = dict(node_dict, **self.nodes)
        
        if len(self.nodes) > len_before and node['web_address'] != self.web_address:
            self.network_manager.register_new_node(node['web_address'])        
            logger.info(f'added node: {node_dict}')
        else:
            logger.info(f'node already in peers: {node_dict}')
            
        return {self.blockchain_address: self.web_address}
    
    def create_signed_transaction(self, receiver_address: str, amount: int, 
                                  fee: int) -> Transaction:
        if fee < 0 or amount < 0 or amount + fee > self.account.get_balance():
            logger.error('Transaction Invalid!')
            raise Exception('Transaction Invalid!')
            
        transaction = Transaction(self.blockchain_address, 
                                  receiver_address,
                                  amount, 
                                  fee)
        
        transaction.add_signature(KeyMaster.sign(transaction.serialized,
                                                 self.keys['private_key']))
        self.transactions.add(transaction)
        self.mempool.add(transaction.as_json())
        logger.info('Transaction created and added to mempool')
        return transaction
    
    def transmit_transactions(self):
        self.verify_total_amounts()
        self.network_manager.message_all_nodes('register_new_transactions',
                                               self.mempool)
            
    def verify_transactions(self):
        if not all([self.is_transaction_verified(t) for t in self.transactions]):
            logger.error('Unverified Transaction in list')
            raise Exception('Transaction list contains non valid transactions!')
            
    def add_transaction(self, json_transaction: str) -> bool:
        t = Transaction.from_json(json_transaction)
        
        if not self.is_transaction_verified(t):
            logger.info('Transaction not verified')
            return False
        
        if not self.is_fee_valid(t):
            logger.info('Insufficient balance for transaction')
            return False
        
        mempool_size_before_addition = len(self.mempool)
        self.mempool.add(json_transaction)
        if len(self.mempool) > mempool_size_before_addition:
            self.transactions.add(t)
            logger.info('transaction added to mempool')
            return True
        
        logger.info('Transaction already found in mempool')
        
    def is_transaction_executed(self, t: Transaction) -> bool:
        for block in self.blockchain.chain[1:]:
            try:
                json_transactions = {bt.as_json() for bt in block.transactions}
                return t.as_json() in json_transactions
            except AttributeError:
                logger.exception(f'Bad Transaction in block: {block.index}')
                logger.critical('Bad Block in Chain!')
                
    def cleanup_transactions(self, new_chain=False):
        logger.info('Transaction cleanup initiated')
        cleanup = []
        for t in self.transactions:
            if days_ago(t.timestamp) > TRANSACTION_MAX_DAYS:
                cleanup.append(t)
            elif new_chain and self.is_transaction_executed(t):
                cleanup.append(t)
                
        self.transactions.difference_update(cleanup)
        self.mempool = {t.as_json() for t in self.transactions}
        logger.info('Transaction cleanup done')
        
    def receive_transactions(self, json_transactions: str):
        for jt in json_transactions:
            self.add_transaction(jt)
            self.cleanup_transactions()
            
    def remove_executed_transactions(self, transactions: List[Transaction]):
        self.mempool.difference_update({t.as_json() for t in transactions})
        self.transactions = {Transaction.from_json(jt) for jt in self.mempool}
        
    def request_chain_replace(self):
        self.network_manager.message_all_nodes('replace_chain', 
                                               self.blockchain.chain)
        
    def mine_new_block(self):
        executed_transactions = self.blockchain.create_block(self.transactions)
        if len(executed_transactions) > 0:
            self.remove_executed_transactions(executed_transactions)
            self.request_chain_replace()
        logger.warning('Block mined with no executed transactions')
            
    def replace_chain(self, chain: List[Blockchain.Block]) -> bool:
        if self.blockchain.replace_chain(chain):
            self.cleanup_transactions(new_chain=True)
            self.account.chain = chain
            logger.info('chain replaced')
            return True
        logger.info('chain not replaced')
        return False
