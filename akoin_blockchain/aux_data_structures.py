from hashlib import sha256
from typing import List


class MerkleTree:
    
    @staticmethod
    def get_single_hash(n: any) -> str:
        return sha256(str(n).encode('utf-8')).hexdigest().encode('utf-8')
    
    @staticmethod
    def normalize(data: list) -> list:
        return [str(d).encode('utf-8') for d in data]
    
    @staticmethod
    def make_tree(data_list: list) -> List[list]:
        if len(data_list) == 0:
            return []
        data = MerkleTree.normalize(data_list)
        tree = []
        leafs = [sha256(x).hexdigest() for x in data]
        if len(data_list) == 1:
            return [leafs]
        
        tree.append(leafs)
        layer_below = MerkleTree.normalize(leafs)
        while len(layer_below) > 1:
            next_layer = []
            for i in range(0, len(layer_below), 2):
                try:
                    next_layer.append(sha256(layer_below[i] + 
                                             layer_below[i + 1]).hexdigest())
                except IndexError:
                    next_layer.append(sha256(layer_below[i] + 
                                             layer_below[i]).hexdigest())
            tree.append(next_layer)
            layer_below = MerkleTree.normalize(next_layer)
            
        return tree
    
    @staticmethod        
    def validate_leaf_hash(leaf_hash: str, 
                           leaf_index: int, proof_list: list) -> bool:
        root = proof_list.pop()        
        current_hash = leaf_hash
        idx = leaf_index
        for i in range(len(proof_list)):
            if idx % 2 == 0:
                current_hash = sha256(current_hash + 
                                      proof_list[i]).hexdigest().encode('utf-8')
            else:
                current_hash = sha256(proof_list[i] + 
                                      current_hash).hexdigest().encode('utf-8')
                
            idx = idx // 2
            
        return current_hash == root
    
    @staticmethod
    def get_proof_list(tree: List[list], idx: int) -> list:
        proof_list = []
        
        for i in range(len(tree)):
            if idx % 2 == 0:
                if len(tree[i]) == idx + 1:
                    proof_list.append(tree[i][idx])
                else:
                    proof_list.append(tree[i][idx + 1])
            else:
                proof_list.append(tree[i][idx - 1])
                
            idx = idx // 2
            
        return [x.encode('utf-8') for x in proof_list]
