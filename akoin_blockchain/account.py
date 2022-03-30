from .aux_data_structures import MerkleTree
from .helper_functions import get_logger
from .transaction import Transaction

logger = get_logger(__name__)


class Account:
    def __init__(self, address: str):
        self.address = address
        self._chain = None
        logger.info('Account created')
     
    @property
    def chain(self) -> list:
        return self._chain
    
    @chain.setter
    def chain(self, chain: list):
        logger.debug('chain was set')
        self._chain = chain
    
    @staticmethod
    def get_balance_of(address: str, chain: list) -> int:
        balance = 0
        
        for block in chain:
            miner_address = block.miner
            for t in block.transactions:
                if address == t.sender:
                    balance -= t.amount
                    balance -= t.fee
                if address == t.receiver:
                    balance += t.amount
                if miner_address == address:
                    balance += t.fee
        
        logger.info(f'Account balance for {address} is {balance}')
        return balance

    def get_balance(self) -> int:
        return self.get_balance_of(self.address, self.chain)
    
    def is_transaction_in_block(self, 
                                block_index: int,
                                transaction_index: int,
                                transaction: Transaction,
                                proof_list: list) -> bool:
        
        transaction_hash = MerkleTree.get_single_hash(transaction.serialized)
        
        root = proof_list[-1].decode('utf-8')
        block_root = self._chain[block_index].merkle_root
        
        return root == block_root and MerkleTree.validate_leaf_hash(transaction_hash, 
                                                                   transaction_index, 
                                                                   proof_list)
    
    def generate_transaction_in_block_proof(self, 
                                            transaction_index: int, 
                                            block_index: int) -> dict:
        block = self._chain[block_index]
        proof_list = MerkleTree.get_proof_list(block.merkle_tree, 
                                               transaction_index)
        return {'transaction': block.transactions[transaction_index],
                'transaction_index': transaction_index,
                'proof_list': proof_list}
        
        
        
        
