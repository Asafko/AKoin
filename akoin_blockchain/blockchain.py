import hashlib
import json
import time

from datetime import datetime
from typing import List, Optional

from .account import Account
from .helper_functions import get_logger
from .transaction import Transaction

from .constants import (BLOCK_DIFFICULTY, MAX_BLOCK_TRANSACTIONS, 
                        INITIAL_CURRENCY_SUPPLY, GENESIS_BLOCK_FEE)

logger = get_logger(__name__)


class Blockchain:
    class Block:
        difficulty = BLOCK_DIFFICULTY
        max_size = MAX_BLOCK_TRANSACTIONS
        
        def __init__(self, index: int, 
                     transactions: List[Transaction], 
                     previous_hash: str,
                     miner: str):
            
            self.index = index
            self.transactions = transactions
            self.timestamp = str(datetime.now())
            self.unix_timestamp = time.time()
            self.previous_hash = previous_hash
            self.nonce = 0
            self.miner = miner

            if len(transactions) > 10:
                raise Exception('Invalid block! (max transactions exeeded)')
                
            self.hashcode = self.proof_of_work()
            logger.info(f'New Block created, hashcode: {self.hashcode}')
              
        def __str__(self) -> str:
            return json.dumps(self.as_object(), sort_keys=True)
        
        def as_object(self, with_hash: Optional[bool]=True) -> dict:
            obj = {'index': self.index,
                   'timestamp': self.timestamp,
                   'unix_timestamp': self.unix_timestamp,
                   'previous_hash': self.previous_hash,
                   'nonce': self.nonce,
                   'miner': self.miner,
                   'transactions': [t.serialized for t in self.transactions]}
            if with_hash:
                obj['hashcode'] = self.hashcode
            
            return obj
        
        def as_json_pre_hash(self) -> str:
            return json.dumps(self.as_object(with_hash=False), sort_keys=True)
    
        def compute_hash(self) -> str:
            return hashlib.sha256(self.as_json_pre_hash().encode()).hexdigest()
    
        def proof_of_work(self) -> str:
            computed_hash = self.compute_hash()
            while not computed_hash.startswith('0' * self.difficulty):
                self.nonce += 1
                computed_hash = self.compute_hash()
    
            return computed_hash

    def __init__(self, public_key_string: str, with_genesis=True):
        self.chain = []
        self.chain_length = 0
        self.public_key_string = public_key_string
        if with_genesis:
            self.create_genesis_block()
    
    def is_block_valid(self, block: Block) -> bool:        
        return all([block.compute_hash().startswith('0' * self.Block.difficulty),
                    len(block.transactions) <= self.Block.max_size])

    def create_genesis_block(self):
        transaction = Transaction('0' * len(self.public_key_string), 
                                  self.public_key_string, 
                                  INITIAL_CURRENCY_SUPPLY, GENESIS_BLOCK_FEE)
        
        block = self.Block(**{
                        'index': 0,
                        'previous_hash': '0',
                        'transactions': [transaction],
                        'miner': self.public_key_string,
                        })
        
        self.chain.append(block)
        self.chain_length += 1
        
        logger.info('Genesis block mined!')
 
    def get_top_possible_transactions(self, 
                                      sorted_transactions: 
                                          List[Transaction]) -> List[Transaction]:
        logger.debug(sorted_transactions)
        if len(self.chain) == 0:
            return sorted_transactions
        
        while True:
            logger.debug('enter while loop')
            possible_transactions = sorted_transactions[: self.Block.max_size]
            balances = {}
            bad_transactions = 0
            
            for t in possible_transactions:
                if t.sender in balances:
                    continue
                
                balances[t.sender] = Account.get_balance_of(t.sender, self.chain)
            
            for t in possible_transactions:
                if t.receiver in balances:
                    balances[t.receiver] += t.amount
                balances[t.sender] -= t.amount + t.fee
                
                if balances[t.sender] < 0:
                    balances[t.sender] += t.amount + t.fee
                    sorted_transactions.remove(t)
                    logger.debug(f'bad transaction: {t}')
                    bad_transactions += 1
                    
            if bad_transactions == 0:
                logger.info(f'Top valid transactions gathered: {possible_transactions}')
                return possible_transactions
                    
    def create_block_transactions(self, transactions: 
                                  List[Transaction]) -> List[Transaction]:
        
        sorted_transactions = sorted(transactions, 
                                     key=lambda t: t.fee, 
                                     reverse=True)
        return self.get_top_possible_transactions(sorted_transactions)
    
    def create_block(self, transactions: List[Transaction]) -> List[Transaction]:
        if len(transactions) == 0:
            return []
        
        prev_hash = self.chain[-1].hashcode
        transactions = self.create_block_transactions(transactions)
        block_idx = len(self.chain)
        
        block = self.Block(**{
                        'index': block_idx,
                        'previous_hash': prev_hash,
                        'transactions': transactions,
                        'miner': self.public_key_string,
                        })
        
        self.chain.append(block)
        self.chain_length += 1
        
        logger.info('New block mined!')
        
        return transactions
    
    def is_chain_valid(self, chain: Optional[List[Block]]=None) -> bool:
        if chain is None:
            logger.warning('Got null chain object')
            chain = self.chain

        previous_block = chain[0]
        for block in chain[1:]:
            if block.previous_hash != previous_block.hashcode:
                logger.info('Bad block found!')
                logger.debug(f'{block}')
                return False
            if not self.is_block_valid(block):
                logger.info('Invalid block found!')
                logger.debug(f'{block}')
                return False
            previous_block = block
            
        logger.debug('Chain validated')            
        return True
    
    def get_last_block(self) -> Block:
        return self.chain[-1]
    
    def get_chain(self):
        return self.chain
    
    def replace_chain(self, chain: List[Block]) -> bool:
        if len(chain) <= self.chain_length:
            logger.info('chain rejected (too short)')
            return False
        
        if not self.is_chain_valid(chain):
            logger.info('chain rejected (invalid!)')
            return False
        
        self.chain = chain
        self.chain_length = len(chain)
        logger.info('chain replaced!')
        return True
