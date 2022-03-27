import json
import time

from typing import Optional
from ellipticcurve.signature import Signature

from .helper_functions import get_logger
from .key_master import KeyMaster

logger = get_logger(__name__)


class Transaction:
    def __init__(self, sender: str, receiver: str, amount: int, fee: int, 
                 timestamp: Optional[float]=None):
        self.fee = fee
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()
        logger.debug('New transaction created')
                  
    @property
    def serialized(self) -> str:
        return json.dumps({'sender': self.sender,
                           'receiver': self.receiver,
                           'amount': self.amount,
                           'fee': self.fee,
                           'timestamp': self.timestamp}, 
                          sort_keys=True)
    
    def add_signature(self, signature: Signature):
        if not KeyMaster.is_verified(self.serialized, 
                                     signature, 
                                     self.sender):
            logger.error('Signature not varified for transaction!')
            raise Exception('Unverified!') 
            
        self.signature = signature
        
    def as_json(self) -> str:
        return json.dumps({'serialized': self.serialized,
                           'fee': self.fee,
                           'signature': self.signature._toString()
                           })
    
    @classmethod
    def from_json(cls, json_transaction: str) -> 'Transaction':
        obj = json.loads(json_transaction)
        signature = KeyMaster.signature_from_string(obj['signature'])
        init_dict = json.loads(obj['serialized'])
        
        t = cls(**init_dict)
        t.add_signature(signature)
        logger.debug(f'Transaction recovered from json: {t.serialized}')
        return t
