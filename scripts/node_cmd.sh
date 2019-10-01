cmd="lncli --no-macaroons --tlscertpath=../nodes/$3/tls.cert --rpcserver=localhost:$2 $1"

eval $cmd
