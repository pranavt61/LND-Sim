# List channels and payments routes for each node
import sys
import os
import json
import subprocess

NODES_DIR = "/home/ubuntu/LND-Sim/nodes/"

# Command to interact with lncli
#   lncli_cmd.format(<node_id>, <rpc port>, <command>)
lncli_cmd = """
    lncli
    --no-macaroons 
    --tlscertpath=""" + NODES_DIR + "/{}/tls.cert " + """
    --rpcserver=localhost:{} 
    {}
"""

def main():
    # payments[node_id]
    payments = {};

    print("Number of payments routed: ")

    dirs = None
    try:
        dirs = os.listdir(NODES_DIR)
    except:
        print("ERROR: NODES_DIR ({}) not a directory".format(NODES_DIR))
    for node_id_str in dirs:
        node_id = int(node_id_str)

        payments[node_id] = {
            'num_routed': 0,
            'num_channels': 0
        };

        # count channels
        channels_output = cmd(lncli_cmd.format(node_id_str, str(10000 + node_id), "listchannels"))
        channels_json = json.loads(channels_output)
        payments[node_id]['num_channels'] = len(channels_json['channels'])

        # count routed payments
        routed_output = cmd("wc -l {}".format(NODES_DIR + node_id_str + '/payments_routed.txt'))
        payments[node_id]['num_routed'] = int(str(routed_output).split(' ')[0].split('\'')[1])

        print("Node " + node_id_str + ': ' + str(payments[node_id]))

    return

def cmd(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE);
    output, error = process.communicate();

    return output

main()
