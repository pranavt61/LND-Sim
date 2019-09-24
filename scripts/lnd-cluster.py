#Python script to manage lnd nodes
from __future__ import print_function
from multiprocessing import Process
import subprocess
import os
import shutil
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
import grpc

import base64
import json
import requests
import time
import codecs

NEXT_NODE_ID = 0
MAX_NODES = 10
NODES_DIR = "/home/ubuntu/LND-Sim/nodes"

# Command need .format()
#   start_up.format(<rpc port>, <peer port>, <rest port>, <data>, <log>)
start_up = """ lnd 
    --no-macaroons 
    --rpclisten=localhost:{} 
    --listen=localhost:{} 
    --restlisten=localhost:{} 
    --lnddir={}
    --debuglevel=debug 
    --bitcoin.simnet 
    --bitcoin.active 
    --bitcoin.node=btcd 
    --btcd.rpcuser=kek 
    --btcd.rpcpass=kek """;

def main():
    NUM_NODES = 2
    node_threads = []
    node_stubs = []     # {'wal': <>, 'ln': <>}

    for node_id in range(0, NUM_NODES):
        node_threads.append(Process(target=start_node, args=(node_id,)))
        node_threads[node_id].start()

    time.sleep(1)

    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'

    # init stubs
    for node_id in range(0, NUM_NODES):

        cert = open(NODES_DIR + '/' + str(node_id) + '/tls.cert', 'rb').read()
        ssl_creds = grpc.ssl_channel_credentials(cert)
        channel = grpc.secure_channel('localhost:' + str(10000 + node_id), ssl_creds)

        stub_wal = lnrpc.WalletUnlockerStub(channel)
        stub_ln = lnrpc.LightningStub(channel)

        node_stubs.append({'wal': stub_wal, 'ln': stub_ln})

    # Gen seed and init wallet
    for node_id in range(0, NUM_NODES):
        stub_wal = node_stubs[node_id]['wal']
        stub_ln = node_stubs[node_id]['wal']

        ### Gen seed ###
        request = ln.GenSeedRequest()
        response = stub_wal.GenSeed(request)

        cipher_seed_mnemonic = response.cipher_seed_mnemonic
        print(response)

        ### Init wallet ###
        request = ln.InitWalletRequest(
                wallet_password="00000000",
                cipher_seed_mnemonic=cipher_seed_mnemonic)
        response = stub_wal.InitWallet(request)

        print(response)

    return

def start_node(node_id):
    node_rpc = str(10000 + node_id)
    node_peer = str(10010 + node_id)
    node_rest = str(8000 + node_id)
    node_dir = NODES_DIR + '/' + str(node_id)

    # delete dir
    dir_list = os.listdir(NODES_DIR)
    if str(node_id) in dir_list:
        shutil.rmtree(node_dir)

    # create dir
    os.mkdir(node_dir)

    # start lnd
    lnd_cmd = start_up.format(node_rpc, node_peer, node_rest, node_dir)
    lnd_output = cmd(lnd_cmd)

    for l in lnd_output:
        print(l, end='')

# takes command in one string
def cmd(command):
    popen = subprocess.Popen(command.split(), stdout=subprocess.PIPE, universal_newlines=True);
    for lines in iter(popen.stdout.readline, ""):
        yield lines;
    popen.stdout.close();
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

main()
