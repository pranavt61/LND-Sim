# Start bitcoin node on simnet
#	Usage 1: sh btcd-start.sh <Minning Addr>
#	Usage 2: sh btcd-start.sh

cmd="btcd --txindex --datadir=~/LND-Sim/btcd/data --logdir=~/LND-Sim/btcd/log --simnet --rpcuser=kek --rpcpass=kek"
if [ "$#" -eq 1 ]; then
	echo "asdasd"
	cmd="${cmd} --minningaddr=$1"
fi

eval "$cmd"
