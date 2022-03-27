import copy
import pytest
import random
import time

from datetime import datetime
from typing import Optional

from akoin_blockchain.blockchain import Blockchain
from akoin_blockchain.key_master import KeyMaster
from akoin_blockchain.transaction import Transaction

from akoin_blockchain.constants import INITIAL_CURRENCY_SUPPLY

Blockchain.Block.difficulty = 2  # to save time
KEYS = KeyMaster.generate_keys()
OTHER_KEYS = KeyMaster.generate_keys()
BLOCK_DIFFICULTY = Blockchain.Block.difficulty
MAX_BLOCK_TRANSACTIONS = Blockchain.Block.max_size
DEFAULT_PREVIOUS_HASH = '0'
DEFAULT_BLOCK_INDEX = 0


TRANSACTION_TEMPLATE = {'sender': KEYS['public_key_string'],
                        'receiver': OTHER_KEYS['public_key_string'],
                        'amount': 100,
                        'fee': 30}

def make_signed_transaction(transactions=TRANSACTION_TEMPLATE) -> Transaction:
    t = Transaction(**transactions)
    t.add_signature(KeyMaster.sign(t.serialized, KEYS['private_key']))
    return t
    
def make_transaction_list(n: Optional[int]=3):
    return[make_signed_transaction() for _ in range(n)]

def make_block(transactions, 
               idx=DEFAULT_BLOCK_INDEX, 
               prev_hash=DEFAULT_PREVIOUS_HASH):
    return Blockchain.Block(idx, transactions, prev_hash, 
                            KEYS['public_key_string'])

def test_block_difficulty():
    before = datetime.now()
    #  Hashing time has a random element,
    #  multiple timesoperations will get closer to mean, but might still fail!
    blocks = [make_block(make_transaction_list(1)) for _ in range(100)] 
    after = datetime.now()
    assert (after - before).seconds > 0
    
    for block in blocks:
        assert block.hashcode.startswith('0' * BLOCK_DIFFICULTY)
        
def test_block_max_transactions():
    transactions = make_transaction_list(10)
    make_block(transactions)
    transactions.append(make_signed_transaction())
    assert len(transactions) > MAX_BLOCK_TRANSACTIONS
    with pytest.raises(Exception):
        make_block(transactions)
    
def test_genesis_block():
    blockchain = Blockchain(KEYS['public_key_string'])
    genesis_block = blockchain.chain[0]
    assert genesis_block.index == 0
    assert genesis_block.previous_hash == '0'
    assert genesis_block.hashcode.startswith('0' * BLOCK_DIFFICULTY)
    time.sleep(0.1)
    assert time.time() - genesis_block.unix_timestamp > 0
    
    genesis_transaction = genesis_block.transactions[0]
    assert genesis_transaction.sender == '0' * len(KEYS['public_key_string'])
    assert genesis_transaction.receiver == KEYS['public_key_string']
    assert genesis_transaction.amount == INITIAL_CURRENCY_SUPPLY
    assert genesis_transaction.fee == 0
    
    
def test_block_validation():
    blockchain = Blockchain(KEYS['public_key_string'], with_genesis=False)
    block = make_block(make_transaction_list(10))
    assert blockchain.is_block_valid(block)
    
    #  previouse nonce would not have resulted in valid hashcode
    block.nonce -= 1
    assert not blockchain.is_block_valid(block)
    block.nonce += 1
    assert blockchain.is_block_valid(block)
    
    valid_unix_timestamp = block.unix_timestamp
    time.sleep(0.1)
    block.unix_timestamp = time.time()
    assert not blockchain.is_block_valid(block)
    block.unix_timestamp = valid_unix_timestamp
    assert blockchain.is_block_valid(block)
    
    valid_timestamp = block.timestamp
    time.sleep(0.1)
    block.timestamp = str(datetime.now())
    assert not blockchain.is_block_valid(block)
    block.timestamp = valid_timestamp
    assert blockchain.is_block_valid(block)
    
    block.previous_hash = '11'
    assert not blockchain.is_block_valid(block)
    block.previous_hash = DEFAULT_PREVIOUS_HASH
    assert blockchain.is_block_valid(block)
    
    block.index = 11
    assert not blockchain.is_block_valid(block)
    block.index = DEFAULT_BLOCK_INDEX
    assert blockchain.is_block_valid(block)
    
    block.transactions.append(make_signed_transaction())
    assert not blockchain.is_block_valid(block)
    
def test_chain_validation():
    blockchain = Blockchain(KEYS['public_key_string'])
    blockchain.Block.difficulty = 1
    for _ in range(5):
        blockchain.create_block(make_transaction_list(7))
        
    assert blockchain.is_chain_valid()
    
    #  removing a transaction in any given block invalidates it, 
    #  thus invalidating the entire chain    
    blockchain.chain[3].transactions.pop()
    
    assert not blockchain.is_chain_valid()
    
def test_optimal_transaction_selection():
    blockchain = Blockchain(KEYS['public_key_string'])
    transaction_bank = make_transaction_list(12)
    template = copy.copy(TRANSACTION_TEMPLATE)
    template['fee'] = 35
    good_transaction_high_fee = make_signed_transaction(template)
    transaction_bank.append(good_transaction_high_fee)
    template['fee'] = 25
    good_transaction_low_fee = make_signed_transaction(template)
    transaction_bank.append(good_transaction_low_fee)
    template['fee'] = 40
    template['amount'] = INITIAL_CURRENCY_SUPPLY * 2
    bad_transaction_high_fee = make_signed_transaction(template)
    transaction_bank.append(bad_transaction_high_fee)
    
    random.shuffle(transaction_bank)
    
    selected_transactions = blockchain.create_block_transactions(transaction_bank)
    assert len(selected_transactions) == MAX_BLOCK_TRANSACTIONS
    
    json_transactions = [t.as_json() for t in selected_transactions]
    assert good_transaction_high_fee.as_json() in json_transactions
    assert good_transaction_low_fee.as_json not in json_transactions
    assert bad_transaction_high_fee.as_json not in json_transactions
    
def test_replace_chain():
    blockchain_1 = Blockchain(KEYS['public_key_string'])
    blockchain_2 = Blockchain(KEYS['public_key_string'])
    blockchain_1.Block.difficulty = 1
    blockchain_2.Block.difficulty = 1
    
    for _ in range(3):
        blockchain_1.create_block(make_transaction_list(1))
        blockchain_2.create_block(make_transaction_list(1))
    
    blockchain_1.create_block(make_transaction_list(1))
       
        
    assert not blockchain_1.replace_chain(blockchain_2.get_chain())
    assert blockchain_2.replace_chain(blockchain_1.get_chain())
    
    for i, block in enumerate(blockchain_2.chain):
        assert str(block) == str(blockchain_1.chain[i])
    