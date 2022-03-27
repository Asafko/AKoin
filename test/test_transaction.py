import copy
import pytest
import time

from akoin_blockchain.key_master import KeyMaster
from akoin_blockchain.transaction import Transaction

TRANSACTION_TEMPLATE = {'sender': '0000', 
                        'receiver': '0000', 
                        'amount': 100, 
                        'fee': 5}

KEYS = KeyMaster.generate_keys()

def make_unsigned_transaction() -> Transaction:
    template = copy.copy(TRANSACTION_TEMPLATE)
    template['sender'] = KEYS['public_key_string']
    return Transaction(**template)
    

def test_instantiation_with_timestamp():
    template = copy.copy(TRANSACTION_TEMPLATE)
    template['timestamp'] = time.time()
    
    t = Transaction(**template)
    for k, v in template.items():
        assert getattr(t, k) == v
        
def test_instantiation_without_timestamp():
    ts = time.time()
    t = Transaction(**TRANSACTION_TEMPLATE)
    
    assert ts - t.timestamp < 0.001
    
def test_serialized_transaction():
    template = copy.copy(TRANSACTION_TEMPLATE)
    template['timestamp'] = time.time()
    
    t = Transaction(**template)
    
    last_idx = 0
    for k in sorted(template.keys()):
        idx = t.serialized.index(k)        
        assert idx > last_idx
        last_idx = idx
    
def test_signiture():
    t = make_unsigned_transaction()
    
    signature = KeyMaster.sign(t.serialized, KEYS['private_key'])
    t.add_signature(signature)
    assert signature == t.signature
    
def test_sender_signature():
    t = Transaction(**TRANSACTION_TEMPLATE)
    signature = KeyMaster.sign(t.serialized, KEYS['private_key'])
    with pytest.raises(Exception):
        t.add_signature(signature)
        
def test_bad_signature():
    t = make_unsigned_transaction()
    
    other_keys = KeyMaster.generate_keys()
    bad_signature =  KeyMaster.sign(t.serialized, other_keys['private_key'])
    
    with pytest.raises(Exception):
        t.add_signature(bad_signature)
        
def test_full_json_serialization():
    t = make_unsigned_transaction()
    t.add_signature(KeyMaster.sign(t.serialized, KEYS['private_key']))
    json_t = t.as_json()
    from_json_t = Transaction.from_json(json_t)
    assert KeyMaster.is_verified(from_json_t.serialized, 
                                 from_json_t.signature, 
                                 from_json_t.sender)
        