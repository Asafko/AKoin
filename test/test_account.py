from akoin_blockchain.account import Account
from akoin_blockchain.blockchain import Blockchain
from akoin_blockchain.key_master import KeyMaster
from akoin_blockchain.transaction import Transaction

from akoin_blockchain.constants import INITIAL_CURRENCY_SUPPLY
KEYS = KeyMaster.generate_keys()
OTHER_KEYS = KeyMaster.generate_keys()


def add_block_to_chain(chain, sender, receiver, amount, fee):
    t = Transaction(sender, receiver, amount, fee)
    chain.create_block([t])
    

def test_account_balances():
    bc = Blockchain(KEYS['public_key_string'])
    account = Account(KEYS['public_key_string'])
    account.chain = bc.get_chain()
    miner_initial_balance = account.get_balance()
    assert miner_initial_balance == INITIAL_CURRENCY_SUPPLY
    
    fee = 50
    amount = 1000
    
    add_block_to_chain(bc, 
                       KEYS['public_key_string'], 
                       OTHER_KEYS['public_key_string'], 
                       amount, 
                       fee)
    
    miner_balance_after_1st_block = account.get_balance()
    #  mining fees payed to self
    assert miner_balance_after_1st_block == (INITIAL_CURRENCY_SUPPLY - fee 
                                             - amount + fee)
    
    wallet_balance_after_1st_bloack = account.get_balance_of(OTHER_KEYS['public_key_string'], 
                                  account.chain)
    
    assert wallet_balance_after_1st_bloack == amount
    
    amount = 300
    fee = 75
    
    add_block_to_chain(bc,
                       OTHER_KEYS['public_key_string'], 
                       KEYS['public_key_string'],
                       amount, 
                       fee)
    
    miner_balance_after_2nd_block = account.get_balance()
    
    assert miner_balance_after_2nd_block == (miner_balance_after_1st_block + 
                                             amount + fee)
    
    wallet_balance_after_2nd_bloack = account.get_balance_of(OTHER_KEYS['public_key_string'], 
                                  account.chain)
    
    assert wallet_balance_after_2nd_bloack == (wallet_balance_after_1st_bloack
                                               - amount - fee)
    
    assert INITIAL_CURRENCY_SUPPLY == (wallet_balance_after_2nd_bloack + 
                                       miner_balance_after_2nd_block)
    
    