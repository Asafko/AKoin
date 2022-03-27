from akoin_blockchain.node import Node
from akoin_blockchain.constants import (INITIAL_CURRENCY_SUPPLY)

#  Welcome to this code tutorial, in order to use it please open two terminal
#  windows and run the "akoin_node_listener.py" script. If you kept constants.py
#  the same this script should work, changing the constants might break the 
#  script since it was kept verbose to simplify the reader's learning experiance.
#  The tutorial is inteded for reading and understanding how blockchains work,
#  it is very basic and in some places might not reflect the way things work
#  in the real world.
#  please feel free to experiment with it or to improve upon it.
#  Enjoy :)
# ----------------------------------------------------------------------------


#  this node will have no listener, other nodes would not be able to initiate
#  p2p communication with it, but would be able to respond it it's requests
node = Node('http://127.0.0.1:7777')  
#  connect to 1st node
node.network_manager.register_new_node('http://127.0.0.1:1620')
#  connect to 2nd node
node.network_manager.register_new_node('http://127.0.0.1:1621')

#  get other nodes network details
r = node.network_manager.message_all_nodes('get_chain_address', {})
print(f'get chain address responses: \n {r}')

#  make a list of detail dicts from the response
node_1_chain_address = r[0]['chain-address']
node_2_chain_address = r[1]['chain-address']
other_nodes_details = [{'blockchain_address': node_1_chain_address,
                        'web_address': 'http://127.0.0.1:1620'},
                       {'blockchain_address':node_2_chain_address,
                        'web_address': 'http://127.0.0.1:1621'}]

#  add other nodes to our node peers set
for ond in other_nodes_details:
    node.add_node(ond)



#  connect 1st node and 2nd node
r = node.network_manager.message_node(node.network_manager.socket_list[0],
                                      'register_node',
                                      {'blockchain_address': node_2_chain_address,
                                       'web_address': 'http://127.0.0.1:1621'})

print(f'get register node response: \n {r}')

#  make sure 1st node connected to 2nd node
r = node.network_manager.message_node(node.network_manager.socket_list[0],
                                      'get_nodes', {})
print(f'get nodes response: \n {r}')
assert node_2_chain_address in r['nodes']
assert 'http://127.0.0.1:1621' in r['nodes'][node_2_chain_address]

r = node.network_manager.message_node(node.network_manager.socket_list[1],
                                      'register_node',
                                      {'blockchain_address': node_2_chain_address,
                                       'web_address': 'http://127.0.0.1:1620'})

print(f'get register node response: \n {r}')

#  make sure 2st node connected to 1nd node
r = node.network_manager.message_node(node.network_manager.socket_list[1],
                                      'get_nodes', {})
print(f'get nodes response: \n {r}')
assert node_2_chain_address in r['nodes']
assert 'http://127.0.0.1:1620' in r['nodes'][node_2_chain_address]

#  let's add a new transaction to the blockchain 
#  node 1 will be a valid receiver
send_amount = 1000
fee = 5
t = {
     'receiver_address': node_1_chain_address, 
     'amount': send_amount, 
     'fee': fee
     }

node.create_signed_transaction(**t)

#  we transmit the transaction to the mempool
node.transmit_transactions()

#  and mine a new block on our chain
node.mine_new_block()

#  now our chain should be the longest valid chain and other nodes should
#  replace their chains with ours. let's make sure that happened, the length 
#  of all chains should be 2. 
r = node.network_manager.message_all_nodes('get_chain_length', {})
print(f'get chain length response: \n {r}')
for response_object in r:
    assert response_object['chain-length'] == 2
 
#  now lets make sure the last block mined contains out transaction
r = node.network_manager.message_all_nodes('get_chain', {})
print(f'get chain response: \n {r}')
for response_object in r:
    assert response_object['chain'][-1].transactions[0].receiver == node_1_chain_address

#  let's also make sure the balances in the chain changed
#  remember the fee was payed to us as we mined the block
assert node.account.get_balance() == INITIAL_CURRENCY_SUPPLY - send_amount
assert node.account.get_balance_of(node_1_chain_address, 
                                   node.blockchain.chain) == send_amount

#  let's make another transaction, this time node 1 which has a balance of 1000
#  will send some AKoins to node 2
half_send_amount = send_amount // 2
t = {
     'receiver_address': node_2_chain_address, 
     'amount': half_send_amount, 
     'fee': fee
     }

#  node 1 has to sign the transaction itself, please note this is not reflective
#  of a normal blockchain and would be considered a security breach. this method
#  (and the entire project) exists for learning purposes only!
r = node.network_manager.message_node(node.network_manager.socket_list[0],
                                      'add_transaction', t)
print(f'add transaction response: \n {r}')

#  now node 1 will mine the new block
r = node.network_manager.message_node(node.network_manager.socket_list[0],
                                      'mine', {})
print(f'mine response: \n {r}')

#  lets make sure all nodes have the same chain
r = node.network_manager.message_all_nodes('get_chain_length', {})
print(f'get chain length response: \n {r}')
for response_object in r:
    assert response_object['chain-length'] == 3
    
#  now lets make sure the new chain is valid and replace our chain with it
#  in real world block chain this would have happened automatically, but our
#  node has no listener so we have to do it manually

#  we will take the chain from node 2 just to make sure chain replacement went
#  smoothly there
r = node.network_manager.message_node(node.network_manager.socket_list[1],
                                      'get_chain', {})
print(f'get chain response: \n {r}')
node.replace_chain(r['chain'])
assert node.blockchain.chain_length == 3

#  and now let's make sure the balances for the other nodes changed
assert node.account.get_balance_of(node_1_chain_address, 
                                   node.blockchain.chain) == half_send_amount

assert node.account.get_balance_of(node_2_chain_address, 
                                   node.blockchain.chain) == half_send_amount

#  Finally lets get node 1 to mine another block, this time with
#  a transaction signed by our node. we will use the previous transaction 
#  for bravity (remember amount is 500 AKoins now, fee is still 5 and node 2
#  is the receiver).
node.create_signed_transaction(**t)
node.transmit_transactions()
r = node.network_manager.message_node(node.network_manager.socket_list[0],
                                      'mine', {})
print(f'add transaction response: \n {r}')

#  make sure chain length increased and check the balances
r = node.network_manager.message_all_nodes('get_chain_length', {})
print(f'get chain length response: \n {r}')
for response_object in r:
    assert response_object['chain-length'] == 4
    
#  get the chain from node 2, validate and replace our chain with it
r = node.network_manager.message_node(node.network_manager.socket_list[1],
                                      'get_chain', {})
print(f'get chain response: \n {r}')
node.replace_chain(r['chain'])
assert node.blockchain.chain_length == 4

#  lets check the balances on the AKoin ladger one last time
assert node.account.get_balance() == (INITIAL_CURRENCY_SUPPLY - send_amount 
                                      - half_send_amount - fee)

assert node.account.get_balance_of(node_1_chain_address, 
                                   node.blockchain.chain) == half_send_amount + fee

assert node.account.get_balance_of(node_2_chain_address, 
                                   node.blockchain.chain) == send_amount

#  Hope you enjoyed this tutorial, feel free to experiment with the 
#  blockchain yourself! Happy hacking!

print('Done :)')

