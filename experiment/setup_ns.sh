#!/bin/bash
set -x

##########################
# Setup network namespaces
##########################

# Server
SERVER_VETH_LL_ADDR=00:00:00:00:00:02
SERVER_NS=srv_ns
SERVER_VETH=srv_ve

# Client
CLIENT_NS=cli_ns
CLIENT_VETH_LL_ADDR=00:00:00:00:00:01
CLIENT_VETH=cli_ve

ip netns add ${SERVER_NS}
ip netns add ${CLIENT_NS}

# Add virtual link of types VETH
ip link add \
   name ${SERVER_VETH} \
   address ${SERVER_VETH_LL_ADDR} \
   netns ${SERVER_NS} type veth \
   peer name ${CLIENT_VETH} \
   address ${CLIENT_VETH_LL_ADDR} \
   netns ${CLIENT_NS}

ip netns exec ${SERVER_NS} \
   ip link set dev ${SERVER_VETH} up
ip netns exec ${SERVER_NS} \
   ip link set dev lo up
ip netns exec ${SERVER_NS} \
   ip addr add 10.0.0.1/24 dev ${SERVER_VETH}

ip netns exec ${CLIENT_NS} \
   ip addr add 10.0.0.2/24 dev ${CLIENT_VETH}
ip netns exec ${CLIENT_NS} \
   ip link set dev lo up
ip netns exec ${CLIENT_NS} \
   ip link set dev ${CLIENT_VETH} up
ip netns exec ${CLIENT_NS} \
   ip link set dev lo up

# Add neighbour objects for IP connection
ip netns exec ${SERVER_NS} \
   ip neigh add 10.0.0.2 \
      lladdr ${CLIENT_VETH_LL_ADDR} \
      dev ${SERVER_VETH}
ip netns exec ${CLIENT_NS} \
   ip neigh add 10.0.0.1 \
      lladdr ${SERVER_VETH_LL_ADDR} \
      dev ${CLIENT_VETH}

# Turn off optimizations
# that dent realism.
ip netns exec ${CLIENT_NS} \
   ethtool -K ${CLIENT_VETH} gso off gro off tso off

ip netns exec ${SERVER_NS} \
   ethtool -K ${SERVER_VETH} gso off gro off tso off

# Add netem as qdisc for traffic control
ip netns exec ${CLIENT_NS} \
   tc qdisc add \
      dev ${CLIENT_VETH} \
      root netem
ip netns exec ${SERVER_NS} \
   tc qdisc add \
      dev ${SERVER_VETH} \
      root netem
