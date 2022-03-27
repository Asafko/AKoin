from .helper_functions import get_logger

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
