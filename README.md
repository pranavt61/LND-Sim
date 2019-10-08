# One-Click Lightning Network

Script to automate and monitor an LND cluster. Allows for custamizable topologies.

## Getting Started

### Prerequisites

Install Python3, BTCD, LND

[Python3](https://www.python.org/downloads/)

[BTCD](https://github.com/btcsuite/btcd)

[LND](https://github.com/lightningnetwork/lnd)

Test Python installation:
```
python3 --version
```

Test BTCD installation:
```
btcd --txindex --simnet --rpcuser=kek --rpcpass=kek
btcctl --simnet --rpcuser=kek --rpcpass=kek getinfo
```

Test LND installation:
```
lnd 
  --rpclisten=localhost:10001
  --listen=localhost:10011 
  --restlisten=localhost:8001 
  --datadir=data 
  --logdir=log 
  --debuglevel=info 
  --bitcoin.simnet 
  --bitcoin.active 
  --bitcoin.node=btcd 
  --btcd.rpcuser=kek 
  --btcd.rpcpass=kek
  --no-macaroons

lncli 
  --rpcserver=localhost:10001
  --no-macaroons
  getinfo
```

### Installing

Pull project from home dir
```
cd
git pull https://github.com/pranavt61/LND-Sim.git
```

Run lnd-cluster.py script:
```
cd LND-Sim
python3 lnd-cluster.py <NUM_NODES> <TOPOLOGY> <ROUTING>
```

Number of nodes:
```
2 <= NUM_NODES <= 30
```

Topologies:
```
TOPOLOGY= {
  ring,
  tree,
  central
}
```

Routing:
```
TOPOLOGY= {
  random,
  merchant
}
```

###Custom topologies:

1) open scripts/graphs.py

2) create a function that takes number of nodes as input and an adjacency list as an output
[adjacency lists](https://en.wikipedia.org/wiki/Adjacency_list)

3) add function entry to dictionary at the end of the script

4) launch the script 
```
python3 lnd-cluster.py <NUM_NODES> <MY CUSTOM TOPOLOGY> <ROUTING>
```

###Custom routing:

1) open scripts/routing.py

2) create a function that takes number of nodes as input and creates invoices using the pay_invoice() function

3) add function entry to dictionary at the end of the script

4) launch the script 
```
python3 lnd-cluster.py <NUM_NODES> <TOPOLOGY> <MY CUSTOM ROUTING>
```
