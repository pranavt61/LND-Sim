# Python script to manage lnd nodes
import subprocess
import os
import shutil

# one dict entry for each node
# use id as key
# {
#   id
#   wallet_balance
#   peer_ids
#   channels
#   peer_port
#   rpc_port
#   rest_port
#   data_dir
#   log_dir
#   output_pipe
# }
nodes = {}
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
    --datadir={} 
    --logdir={} 
    --debuglevel=debug 
    --bitcoin.simnet 
    --bitcoin.active 
    --bitcoin.node=btcd 
    --btcd.rpcuser=kek 
    --btcd.rpcpass=kek """;

def main():

    for i in range(0, 1):
        start_node()

    return

def start_node():
    global NEXT_NODE_ID
    global nodes

    NEXT_NODE_ID += 1

    if NEXT_NODE_ID == MAX_NODES:
        # No new 
        print("ERROR: max nodes limit reached; Cannot create more nodes")
        return

    node_id = NEXT_NODE_ID
    node_rpc = str(10000 + node_id)
    node_peer = str(10010 + node_id)
    node_rest = str(8000 + node_id)
    node_dir = NODES_DIR + '/' + str(node_id)
    node_data = node_dir + "/data"
    node_logs = node_dir + "/logs"

    # delete dir
    dir_list = os.listdir(NODES_DIR)
    if str(node_id) in dir_list:
        shutil.rmtree(node_dir)

    # create dir
    os.mkdir(node_dir)
    os.mkdir(node_data)
    os.mkdir(node_logs)

    # start lnd
    lnd_cmd = start_up.format(node_rpc, node_peer, node_rest, node_data, node_logs)
    lnd_output = cmd(lnd_cmd)

    # add to node map
    nodes[node_id] = {
        "node_id": node_id,
        "node_rpc": node_rpc,
        "node_peer": node_peer,
        "node_rest": node_rest,
        "node_dir": node_dir,
        "node_data": node_data,
        "node_logs": node_logs,
        "output_pipe": lnd_output
    }

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
