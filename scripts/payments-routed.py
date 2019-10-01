# Get data from ../nodes/{id}/payments_routed.txt
import sys
import os
import json
import subprocess

NODE_DIR = "/home/ubuntu/LND-Sim/nodes/"

# Command to interact with lncli
#   lncli_cmd.format(<node_id>, <rpc port>, <command>)
lncli_cmd = """
    lncli
    --no-macaroons 
    --tlscertpath=""" + NODE_DIR + "/{}/tls.cert " + """
    --rpcserver=localhost:{} 
    {}
"""

def main():
    # payments[node_id]
    payments = {};

    print("Number of payments routed: ")

    dirs = os.listdir(NODE_DIR)
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
        routed_output = cmd("wc -l {}".format(NODE_DIR + node_id_str + '/payments_routed.txt'))
        print(routed_output)


        line = f.readline()
        while line:
            payments[node_id]['num_routed'] += 1

            line = f.readline()

        print("Node " + node_id_str + ': ' + str(payments[node_id]))
        f.close()

    return


def cmd(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE);
    output, error = process.communicate();

    return output

main()
