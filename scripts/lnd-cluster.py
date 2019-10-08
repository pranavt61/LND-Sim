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
import random
import sys
import re

import graphs
import routing

NEXT_NODE_ID = 0
MAX_NODES = 10
NODES_DIR = "/home/ubuntu/LND-Sim/nodes"
BTCD_DIR = "/home/ubuntu/LND-Sim/btcd"

# Log flags
BTCD_LOG_FLAG = False
LND_LOG_FLAG = False

# Command for btcd node
btcd_start_up = """btcd 
    --txindex 
    --datadir=""" + BTCD_DIR + """/data 
    --logdir=""" + BTCD_DIR + """/log 
    --simnet 
    --miningaddr=roF5YRWAjZy5tPB5Nib5kJ76EsXmLue4NK
    --rpcuser=kek 
    --rpcpass=kek
    """

btcctl_cmd = """btcctl 
     --simnet 
     --rpcuser=kek 
     --rpcpass=kek 
     {}"""

# Command need .format()
#   ln_start_up.format(<rpc port>, <peer port>, <rest port>, <data>, <log>)
ln_start_up = """ lnd 
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

# Command to interact with lncli
#   lncli_cmd.format(<node_id>, <rpc port>, <command>)
lncli_cmd = """
        lncli
        --no-macaroons 
        --tlscertpath=""" + NODES_DIR + "/{}/tls.cert " + """
        --rpcserver=localhost:{} 
        {}
        """

# initial node seed for node # 1
#   used to preserve funds and have a consistant
#   minning addr
node_seed = b'\x00\x00\x00\x00\x07\x80\x00\x03\x00\x00\x00\x00\x07\x80\x00\x03'

def main():
    if len(sys.argv) < 3:
        # missing num nodes
        print("Usage:")
        print("     py lnd-cluster.py <NUM_NODES> <GRAPH_TYPE> <ROUTING_TYPE>")
        print("     Graph types: tree, central, ring")
        print("     Routing types: random, merchant")
        exit(1)
    
    NUM_NODES = int(sys.argv[1])
    GRAPH_TYPE = sys.argv[2]
    ROUTING_TYPE = sys.argv[3]
    WALLET_PASS = bytes('00000000', 'utf-8')
    MINNING_ADDR = "SY6RbmrfYo2Vg9P9RuTreucM7G1SyVqhhb"

    ### ARG Checking ###
    if GRAPH_TYPE not in graphs.graph_types:
        print("ERROR: invalid graph type -> " + GRAPH_TYPE)
        exit()
    if ROUTING_TYPE not in routing.routing_types:
        print("ERROR: invalid routing type -> " + ROUTING_TYPE)
        exit()

    ### Create BTCD dir ###
    if os.path.exists(BTCD_DIR) == False:
        os.makedirs(BTCD_DIR)

    ### Create Nodes dir ###
    if os.path.exists(NODES_DIR) == False:
        os.makedirs(NODES_DIR)

    ### Clean Nodes dir ###
    dir_list = os.listdir(NODES_DIR)
    for node_id in dir_list:
        node_dir = NODES_DIR + '/' + str(node_id)
        shutil.rmtree(node_dir)

    ### Thread data ###

    # btcd thread proc
    btcd = None

    # Stores all node data
    # {
    #   id,
    #   thread,
    #   stub_wal,
    #   addr
    # }
    nodes = []

    ### Start Threads ###

    # start btcd thread
    btcd = Process(target=btcd_start_node)
    btcd.start()

    # start lnd threads
    for node_id in range(0, NUM_NODES):
        nodes.append({
            "id": node_id,
            "thread": Process(target=ln_start_node, args=(node_id,))
        })
        nodes[node_id]["thread"].start()
    time.sleep(1)
    
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'

    ### init RPC stubs ###
    for node_id in range(0, NUM_NODES):
        while True:
            try:
                print("Node {} reading cert file...".format(str(node_id)))
                cert = open(NODES_DIR + '/' + str(node_id) + '/tls.cert', 'rb').read()
                break
            except:
                print("ERROR: cannot find cert file: " + str(NODES_DIR + '/' + str(node_id) + '/tls.cert'))

        ssl_creds = grpc.ssl_channel_credentials(cert)
        channel = grpc.secure_channel('localhost:' + str(10000 + node_id), ssl_creds)

        stub_wal = lnrpc.WalletUnlockerStub(channel)

        nodes[node_id]["stub_wal"] = stub_wal

    ### Init a node ###
    for node_id in range(0, NUM_NODES):
        stub_wal = nodes[node_id]['stub_wal']

        # Gen Seed
        request = None
        if node_id == 0:
            # use same seed for first node
            # keeps minning address constant
            request = ln.GenSeedRequest(seed_entropy=bytes(node_seed))
        else:
            request = ln.GenSeedRequest()
        response = stub_wal.GenSeed(request)

        cipher_seed_mnemonic = response.cipher_seed_mnemonic
        print(bytes(node_seed))
        print(response)

        # Init Wallet
        request = ln.InitWalletRequest(
            wallet_password=WALLET_PASS,
            cipher_seed_mnemonic=cipher_seed_mnemonic)
        response = stub_wal.InitWallet(request)

        print(response)

    ### wait for rpc servers to init ###
    for node_id in range(0, NUM_NODES):
        while True:
            output = cmd_async(lncli_cmd.format(str(node_id), str(10000 + node_id), "getinfo"))
            try:
                # if rpc server is active,
                # the response will be json
                info_output = json.loads(output)
                nodes[node_id]['id_pubkey'] = info_output["identity_pubkey"]
                print(info_output)
                break
            except:
                print("======== ERROR: RPC server not active yet ========")
                print("========             node_id: {}           ========".format(node_id))

            time.sleep(1)

        # New Address
        output = cmd_async(lncli_cmd.format(str(node_id), str(10000 + node_id), "newaddress np2wkh"))
        nodes[node_id]["addr"] = json.loads(output)["address"]

    ### Fund All Nodes ###
    COINS_PER_NODE = " 100000000";

    output_node_0_balance = cmd_async(lncli_cmd.format("0", "10000", "walletbalance"))
    print(output_node_0_balance)

    # Mine coins
    output_mining = cmd_async(btcctl_cmd.format("generate 200"))
    time.sleep(5)                                                   # Wait for mining

    # Send Coins
    for node_id in range(1, NUM_NODES):
        lnc_command = lncli_cmd.format("0",
                "10000",
                "sendcoins " + nodes[node_id]['addr'] + COINS_PER_NODE);
        output_sendcoins = cmd_async(lnc_command)
        print(output_sendcoins)
    
    # Mine transactions
    cmd_async(btcctl_cmd.format("generate 100"))
    time.sleep(5)                                                   # Wait for mining

    ### Connect Peers and Create Channels ###
    
    # create graph
    graph = graphs.graph_types[GRAPH_TYPE](NUM_NODES)

    # connect peers and open channels
    for node_id in range(0, NUM_NODES):
        peers = graph[node_id]
        for peer_i in range(0, len(peers)):
            peer = nodes[peers[peer_i]]

            # connect peers
            lnc_command = lncli_cmd.format(
                    str(node_id),
                    str(10000 + node_id),
                    "connect " + peer["id_pubkey"] + "@localhost:" + str(20000 + peer['id'])
                    )
            output_connect = cmd_async(lnc_command)
            print(output_connect)

            # open channels
            lnc_command = lncli_cmd.format(
                    str(node_id),
                    str(10000 + node_id),
                    "openchannel --node_key=" + peer["id_pubkey"] + " --local_amt=1000000 --push_amt=100000"
                    )
            output_channel = cmd_async(lnc_command)
            print(output_channel)

    # Mine channels
    output_mining = cmd_async(btcctl_cmd.format("generate 20"))
    time.sleep(5)                                                   # Wait for mining

    ### Simulate Routing ###
    routing.routing_types[ROUTING_TYPE](NUM_NODES)

    return

def btcd_start_node():
    print("START BTCD")
    btcd_cmd = btcd_start_up

    btcd_output = cmd(btcd_cmd)
    for l in btcd_output:
        if BTCD_LOG_FLAG:
            print("BTCD => " + l, end='')
        continue

def ln_start_node(node_id):
    print("START LND - " + str(node_id))

    node_rpc = str(10000 + node_id)
    node_peer = str(20000 + node_id)
    node_rest = str(8000 + node_id)
    node_dir = NODES_DIR + '/' + str(node_id)

    # clear ports
    cmd_async("fuser -k {}/tcp".format(node_rpc))
    cmd_async("fuser -k {}/tcp".format(node_peer))
    cmd_async("fuser -k {}/tcp".format(node_rest))

    # delete dir
    dir_list = os.listdir(NODES_DIR)
    if str(node_id) in dir_list:
        shutil.rmtree(node_dir)

    # create dir
    os.mkdir(node_dir)

    # start lnd
    lnd_cmd = ln_start_up.format(node_rpc, node_peer, node_rest, node_dir)
    lnd_output = cmd(lnd_cmd)

    # create output file
    output_file = open(node_dir + '/payments_routed.txt', 'w+')
    payments_routed = []

    while True:
        try:
            for l in lnd_output:
                if LND_LOG_FLAG:
                    print("LND {} => ".format(node_id) + l, end='')

                try:
                    # check for routed payments
                    match_r = re.search("((.*)Received UpdateAddHTLC(.*))", l)
                    match_s = re.search("((.*)Sending UpdateAddHTLC(.*))", l)

                    if match_r:
                        from_addr = l.split(' from ')[1].split('@')[0]
                        timestamp = l.split(' [DBG] ')[0]
                        from_amt = l.split(', ')[2].split('=')[1]

                        payments_routed.append({
                            "from": from_addr,
                            "timestamp": timestamp
                        })
                    elif match_s:
                        if len(payments_routed) == 0:
                            continue
                        if "to" in payments_routed[len(payments_routed) - 1]:
                            continue

                        to_addr = l.split(' to ')[1].split('@')[0]
                        timestamp = l.split(' [DBG] ')[0]
                        to_amt = l.split(', ')[2].split('=')[1]

                        payments_routed[len(payments_routed) - 1]["to"] = to_addr
                        payments_routed[len(payments_routed) - 1]["amt"] = to_amt

                        print(payments_routed[len(payments_routed) - 1])
                        output_file.write(str(payments_routed[len(payments_routed) - 1]) + '\n')
                except Exception as ex:
                    output_file.write(str(ex))
                    continue
        except:
            continue


# takes command in one string
def cmd(command):
    popen = subprocess.Popen(command.split(), stdout=subprocess.PIPE, universal_newlines=True);
    for lines in iter(popen.stdout.readline, ""):
        yield lines;
    popen.stdout.close();
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def cmd_async(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE);
    output, error = process.communicate();

    return output

main()
