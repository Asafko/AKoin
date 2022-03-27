import pytest

from akoin_blockchain.key_master import KeyMaster
from akoin_blockchain.helper_functions import generate_random_string
  

def test_key_generation():
    keys = KeyMaster.generate_keys()
    assert all([k in keys for k in ['private_key', 
                                    'public_key', 
                                    'public_key_string']])
    
def test_signature_verification():
    keys = KeyMaster.generate_keys()
    rs = generate_random_string()
    signature = KeyMaster.sign(rs, keys['private_key'])
    assert KeyMaster.is_verified(rs, signature, keys['public_key_string'])
    
def test_signature_fails_with_public_key():
    keys = KeyMaster.generate_keys()
    rs = generate_random_string()
    with pytest.raises(Exception):
        KeyMaster.sign(rs, keys['public_key'])
        
def test_other_keys_verification_fails():
    keys = KeyMaster.generate_keys()
    other_keys = KeyMaster.generate_keys()
    rs = generate_random_string()
    signature = KeyMaster.sign(rs, keys['private_key'])
    is_verified = KeyMaster.is_verified(rs, 
                                        signature, 
                                        other_keys['public_key_string'])
    assert not is_verified
    
def test_signature_from_string():
    keys = KeyMaster.generate_keys()
    rs = generate_random_string()
    signature = KeyMaster.sign(rs, keys['private_key'])
    assert KeyMaster.is_verified(rs, signature, keys['public_key_string'])
    signature_str = signature._toString()
    with pytest.raises(Exception):
        KeyMaster.is_verified(rs, signature_str, keys['public_key_string'])
        
    signature_from_string = KeyMaster.signature_from_string(signature_str)
    assert  KeyMaster.is_verified(rs, 
                                  signature_from_string, 
                                  keys['public_key_string'])
    
def test_is_public_key_string_valid():
    keys = KeyMaster.generate_keys()
    assert KeyMaster.is_public_key_string_valid(keys['public_key_string'])
    assert not KeyMaster.is_public_key_string_valid(generate_random_string())