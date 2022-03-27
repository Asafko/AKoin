import copy

from akoin_blockchain.key_master import KeyMaster
from akoin_blockchain.node import Node
from akoin_blockchain.request_handler import RequestHandler
from akoin_blockchain.transaction import Transaction

from akoin_blockchain.constants import (INITIAL_WEB_ADDRESS, 
                                        INITIAL_CURRENCY_SUPPLY)

TRANSACTION_DATA = {'receiver_address': '000','amount': 10, 'fee': 10}
BAD_TRANSACTION_DATA = {'receiver_address': '000',
                        'amount': INITIAL_CURRENCY_SUPPLY * 10 ,
                        'fee': 10}

def validate_response(res, data_field_name):
    assert res['success']
    assert data_field_name in res
    
def add_block_to_node(node):
    #  let's not waste time
    node.blockchain.Block.difficulty = 1
    node.create_signed_transaction(**TRANSACTION_DATA)
    node.mine_new_block()
    
def test_mine():
    node = Node(INITIAL_WEB_ADDRESS)
    transaction = node.create_signed_transaction(**TRANSACTION_DATA)
    initial_chain_length = len(node.blockchain.chain)
    req = {'path': 'mine', 'data': None}
    res = RequestHandler.handle_request(node, req)
    validate_response(res, 'message')
    assert len(node.blockchain.chain) == initial_chain_length + 1
    
    transactions = node.blockchain.chain[-1].transactions
    assert len(transactions) == 1
    assert transactions[0].as_json() == transaction.as_json()

def test_get_chain():
    node = Node(INITIAL_WEB_ADDRESS)
    req = {'path': 'get_chain', 'data': None}
    res = RequestHandler.handle_request(node, req)
    
    validate_response(res, 'chain')
    assert len(res['chain']) == len(node.blockchain.chain)
    
    add_block_to_node(node)
    res = RequestHandler.handle_request(node, req)
    validate_response(res, 'chain')
    
    assert len(res['chain']) == len(node.blockchain.chain)
    
    for i, block in enumerate(node.blockchain.chain):
        assert block == res['chain'][i]
        
def test_get_chain_length():
    node = Node(INITIAL_WEB_ADDRESS)
    req = {'path': 'get_chain_length', 'data': None}
    res = RequestHandler.handle_request(node, req)
    
    validate_response(res, 'chain-length')
    assert res['chain-length'] == len(node.blockchain.chain)
    
    add_block_to_node(node)
    res = RequestHandler.handle_request(node, req)
    
    validate_response(res, 'chain-length')
    assert res['chain-length'] == len(node.blockchain.chain)
    
def test_get_chain_address():
    node = Node(INITIAL_WEB_ADDRESS)
    req = {'path': 'get_chain_address', 'data': None}
    res = RequestHandler.handle_request(node, req)
    validate_response(res, 'chain-address')
    
    assert res['chain-address'] == node.blockchain_address
    
def test_add_transaction():
    node = Node(INITIAL_WEB_ADDRESS)
    req = {'path': 'add_transaction', 'data': TRANSACTION_DATA}
    res = RequestHandler.handle_request(node, req)
    validate_response(res, 'transaction')
    t = Transaction.from_json(res['transaction'])
    
    assert t.receiver == TRANSACTION_DATA['receiver_address']
    assert t.amount == TRANSACTION_DATA['amount']
    assert t.fee == TRANSACTION_DATA['fee']
    
    req = {'path': 'add_transaction', 'data': BAD_TRANSACTION_DATA}
    res = RequestHandler.handle_request(node, req)
    assert not res['success']
    
def test_replace_chain():
    node = Node(INITIAL_WEB_ADDRESS)
    
    for _ in range(3):
        add_block_to_node(node)
        
    chain = copy.deepcopy(node.blockchain.chain)
    
    for _ in range(2):
        node.blockchain.chain.pop()
    
    assert len(chain) > len(node.blockchain.chain)
    node.blockchain.chain_length = len(node.blockchain.chain)
    
    req = {'path': 'replace_chain', 'data': chain}
    res = RequestHandler.handle_request(node, req)
    validate_response(res, 'replaced')
    
    assert res['replaced']
    assert len(node.account.chain) == len(chain)
    
    for i, block in enumerate(chain):
        assert block == node.blockchain.chain[i]
        
    chain = copy.deepcopy(node.blockchain.chain)
    add_block_to_node(node)
    assert len(chain) < len(node.blockchain.chain)
    
    req = {'path': 'replace_chain', 'data': chain}
    res = RequestHandler.handle_request(node, req)
    validate_response(res, 'replaced')
    
    assert not res['replaced']
    
def test_register_and_get_nodes():
    node_1 = Node(INITIAL_WEB_ADDRESS)
    node_2 = copy.deepcopy(node_1)
    node_2.web_address = f'{INITIAL_WEB_ADDRESS}/node2'
    node_2.blockchain_address = KeyMaster.generate_keys()['public_key_string']
    
    node_2_data = {'blockchain_address': node_2.blockchain_address,
                   'web_address': node_2.web_address}
    
    req = {'path': 'register_node', 'data': node_2_data}
    res = RequestHandler.handle_request(node_1, req)
    validate_response(res, 'node')
    
    assert node_1.blockchain_address in res['node']
    assert res['node'][node_1.blockchain_address] == INITIAL_WEB_ADDRESS
    
    req = {'path': 'get_nodes', 'data': None}
    res = RequestHandler.handle_request(node_1, req)
    validate_response(res, 'nodes')
    
    assert node_2.blockchain_address in res['nodes']
    assert res['nodes'][node_2.blockchain_address] == node_2.web_address
    
def test_register_new_transactions():
    node = Node(INITIAL_WEB_ADDRESS)
    good_transaction = node.create_signed_transaction(**TRANSACTION_DATA)
    req = {'path': 'register_new_transactions', 
           'data': [good_transaction.as_json()]}
    res = RequestHandler.handle_request(node, req)
    validate_response(res, 'message')
    
    bad_transaction = good_transaction
    bad_transaction.amount += 1
    req = {'path': 'register_new_transactions', 
           'data': [bad_transaction.as_json()]}
    res = RequestHandler.handle_request(node, req)
    assert not res['success']
    