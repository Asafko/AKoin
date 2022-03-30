import numpy as np

from copy import copy
from hashlib import sha256
from random import randint
from typing import List

from akoin_blockchain.aux_data_structures import MerkleTree

def get_merkle_tree(leaf_amount: int) -> List[list]:
    return MerkleTree.make_tree(list(range(leaf_amount)))

def test_empty_tree():
    assert get_merkle_tree(0) == []

def test_tree_structure():
    leaf_lengths = [1, 2, 10, 16, 150, 256, randint(1, 1000)]
    for leaf_length in leaf_lengths:
        merkle_tree = get_merkle_tree(leaf_length)
        assert len(merkle_tree[-1]) == 1
        log2_of_length = np.log2(leaf_length)
        if np.log2(leaf_length) % 1 == 0:
            assert len(merkle_tree) == int(log2_of_length) + 1
        else:
            assert len(merkle_tree) == int(np.floor(log2_of_length)) + 1 + 1
            
def test_get_proof_list():
    leaf_lengths = [9, 10, 12, 15, 16]
    for leaf_length in leaf_lengths:
        tree = get_merkle_tree(leaf_length)
        leaf_idx = 3
        proof_list = [tree[0][2], tree[1][0], tree[2][1], 
                      tree[3][1], tree[4][0]]
        
        proof_list = [x.encode('utf-8') for x in proof_list]
        assert proof_list == MerkleTree.get_proof_list(tree, leaf_idx)
        
def test_leaf_validation():
    leaf_lengths = [1, 2, 10, 16, 150, 256, randint(1, 1000)]
    for leaf_length in leaf_lengths:
        tree = get_merkle_tree(leaf_length)
        leaf_index = randint(0, leaf_length - 1)
        leaf_hash = tree[0][leaf_index].encode('utf-8')
        proof_list = MerkleTree.get_proof_list(tree, leaf_index)
        is_valid = MerkleTree.validate_leaf_hash(leaf_hash, 
                                                 leaf_index, 
                                                 copy(proof_list))
        assert is_valid
        
        bad_hash = sha256('18'.encode('utf-8')).hexdigest().encode('utf-8')
        is_valid = MerkleTree.validate_leaf_hash(bad_hash, 
                                                 leaf_index, 
                                                 copy(proof_list))
        assert not is_valid
        
        if leaf_length == 1:
            continue  # can't choose bad index
            
        bad_idx = randint(0, leaf_length - 1)
        while bad_idx == leaf_index:
            bad_idx = randint(0, leaf_length - 1)
            
        is_valid = MerkleTree.validate_leaf_hash(leaf_hash, 
                                                 bad_idx, 
                                                 copy(proof_list))
        assert not is_valid