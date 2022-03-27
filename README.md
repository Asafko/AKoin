# AKoin Blockchain

This repo holds my simple implementation of a PoW (proof of work) blockchain using Python.
A PoW blockchain is an immutable data structure in which each block holds a hashcode both
for itself and for the previous block on the chain. This data structure is than replicated
on each of the nodes participating in the p2p (peer to peer) network, thus decentralizing it.

This implementation is meant solely for learning how blockchains work, this is by no means
a workable blockchain, it is not fully secure nor fully optimized and might produce unexpected
behavior if replicated extensively.

## How this works

In the AKoin blockchain there is no mining bonuses, The initial currency supply (which is mined
to the genesis block) is all the AKoins the chain will hold. Each AKoin block contains a limited
number of transactions and each transaction must specify the sender address, receiver address,
the amount to transfer and the fee for the miners. Mining a block will naturally select the top
transactions sorted by the fees (the highest fees would get inserted into the blocks transactions),
with one transaction for the miners to transfer the fees to themselves.
An address on the blockchain is a public key string, the public key is generated from a private key
which is used to sign transactions. The miners would validate the signature with the public key
before adding a transaction to a block (or to the mempool). 
The mempool is a distributed set of serialized transactions, because transactions are being transmitted
from node to node all the time a set is required to make sure miners would not include the transaction
more than once. Once included the transaction is marked as complete and would get cleaned up from the
mempool (it will also appear on the block so miners working on the valid chain would also clean up
any executed transaction).
The consensus mechanism in PoW chains is "Longest chain wins" so any time a block is mined the nodes 
transmit a chain-replacement request to other nodes, which in turn validate and replace their chain 
with the longer chain. In case of two chains that have the same length with different last (most recent) 
blocks the chain would only be replaced once one of the chains grows in length relative to the other.
Mining a block is done by hashing the entire block with a nonce (number only used once) so that the
resulting hash would begin with a number of zeros which equals the chain's block difficulty:
a hash starting with `00005a34d...` is valid for a block difficulty of 4 and less but invalid for any
higher difficulty.
Please feel free to tweak any of the values (found in constants.py) so you can get a better sense of
how this works.

## Installation

Clone this repository and install the requirements:

```bash
pip install -r requirements.txt
```

## Testing
Done with pytest:

```bash
pytest
```

## Usage
I have set up a tutorial file (tutorial.py) to be both run and read (the operations are explained in
the comments). In order to use it as is please run the listener twice without changing the web address
constants.

```bash
python akoin_node_listener.py
```

This will result in two nodes listening on two sockets (127.0.0.1:1620, 127.0.0.1:1621).

Than run:

```bash
python tutorial.py
```

Which will create transactions and mine blocks on the chain.
Please feel free to play around with the blockchain, tweak the values, open up more nodes etc' this should 
be a learning experience and the best learning is hands on.
Enjoy!

## Important notice
I cannot stress enough that this blockchain is meant only for educational purposes, in order to assist up and 
coming Web 3.0 developers learn the inner workings of blockchains and facilitate their understanding. 
#### This implementation should not be used for anything else. AKoins are also worthless. The AKoin blockchain is by no means "Production" suitable!

## Contributing
While I never intended the work done here to be extended, I am open for any improvements and suggestions.
Please feel free to contact me before or after making a pull request.

## License
[MIT](https://choosealicense.com/licenses/mit/)

