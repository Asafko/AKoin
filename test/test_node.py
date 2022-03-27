import datetime

from freezegun import freeze_time
from typing import List

from akoin_blockchain.blockchain import Blockchain
from akoin_blockchain.node import Node

from akoin_blockchain.constants import (INITIAL_CURRENCY_SUPPLY, 
                                        INITIAL_WEB_ADDRESS,
                                        TRANSACTION_MAX_DAYS)

TRANSACTIONS_DETAILS_DICT = {'receiver_address': '000',
                                'amount': INITIAL_CURRENCY_SUPPLY // 10,
                                'fee': INITIAL_CURRENCY_SUPPLY // 10
                                }


def add_transactions_to_node(node: Node, 
                             transaction_details: List[dict]) -> list:
    [node.create_signed_transaction(**td) for td in transaction_details]
    
def make_bad_block(valid_next_index):
    return Blockchain.Block(valid_next_index * 3, 
                            [], 
                            'not a valid hash', 
                            'not an address')
        
def test_transactions_total_amounts_verification():
    node = Node(INITIAL_WEB_ADDRESS)
    
    #  total amounts would equal initial currency
    transaction_details = [TRANSACTIONS_DETAILS_DICT] * 5 
    add_transactions_to_node(node, transaction_details)
    assert node.verify_total_amounts()
    
    #  total amounts would exeed initial supply
    add_transactions_to_node(node, [TRANSACTIONS_DETAILS_DICT])
    assert not node.verify_total_amounts()
    
    
def test_node_validation():
    node = Node(INITIAL_WEB_ADDRESS)
    add_transactions_to_node(node, [TRANSACTIONS_DETAILS_DICT])
    node.mine_new_block()
    
    assert node.is_node_valid({'blockchain_address': node.blockchain_address,
                               'web_address': node.web_address})
    
    node.blockchain_address = node.blockchain_address[:-1]
    
    assert not node.is_node_valid({'blockchain_address': node.blockchain_address,
                               'web_address': node.web_address})
    
def test_transaction_addition_and_automatic_removal():
    node_1 = Node(INITIAL_WEB_ADDRESS)
    node_2 =  Node(INITIAL_WEB_ADDRESS)
    
    st = node_1.create_signed_transaction(node_2.blockchain_address, 1000, 0)
    assert st.as_json() in node_1.mempool
    
    node_1.mine_new_block()
    assert st.as_json() not in node_1.mempool
    
    st = node_2.create_signed_transaction(node_1.blockchain_address, 50, 10)
    
    assert node_1.add_transaction(st.as_json())
    assert len(node_1.transactions) == len(node_2.transactions)
    assert node_1.mempool == node_2.mempool
    
def test_expired_transaction_removal():
    node = Node(INITIAL_WEB_ADDRESS)
    t1 = node.create_signed_transaction('111', 100, 10)
    t2 = node.create_signed_transaction('333', 300, 30)
    
    assert t1.as_json() in node.mempool
    assert t2.as_json() in node.mempool
    
    node.cleanup_transactions()
    assert t1.as_json() in node.mempool
    assert t2.as_json() in node.mempool
    
    now = datetime.datetime.now()
    
    #  We go to the future and make transaction expire
    with freeze_time('2222-10-06'):
        after = datetime.datetime.now()
        assert (after - now).days > TRANSACTION_MAX_DAYS
        
        node.cleanup_transactions()
        assert len(node.transactions) == 0
        assert len(node.mempool) == 0
    