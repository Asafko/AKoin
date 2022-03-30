from random import shuffle

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
    
def add_multiple_transaction_block_to_chain(chain, transaction_details_list):
    chain.create_block([Transaction(**td) for td in transaction_details_list])
    

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
    
def test_transaction_in_block_validation():
    bc = Blockchain(KEYS['public_key_string'])
    account = Account(KEYS['public_key_string'])
    account.chain = bc.get_chain()
    
    transaction_details_list = [{'sender': KEYS['public_key_string'],
                                'receiver': OTHER_KEYS['public_key_string'],
                                'amount': i * 100,
                                'fee': i * 10} for i in range(1, 10)]
    
    add_multiple_transaction_block_to_chain(bc, transaction_details_list)
    block_index = 1
    assert len(account.chain) == 2
    assert len(account.chain[block_index].transactions) == 9
    
    transaction_index = 5
    transaction_proof = account.generate_transaction_in_block_proof(transaction_index,
                                                                    block_index)
    print(transaction_proof)
    
    assert account.is_transaction_in_block(block_index,
                                           transaction_index,
                                           transaction_proof['transaction'],
                                           transaction_proof['proof_list']
                                           )
    
    assert not account.is_transaction_in_block(block_index,
                                           transaction_index + 1,
                                           transaction_proof['transaction'],
                                           transaction_proof['proof_list']
                                           )
    
    good_amount = transaction_proof['transaction'].amount
    bad_amount = good_amount * 2
    transaction_proof['transaction'].amount = bad_amount
    assert not account.is_transaction_in_block(block_index,
                                           transaction_index,
                                           transaction_proof['transaction'],
                                           transaction_proof['proof_list']
                                           )
    
    transaction_proof['transaction'].amount = good_amount
    shuffle(transaction_proof['proof_list'])
    
    assert not account.is_transaction_in_block(block_index,
                                           transaction_index,
                                           transaction_proof['transaction'],
                                           transaction_proof['proof_list']
                                           )
    