#!/bin/bash
set -ex

ROOT="$(dirname $(pwd))"

OPENSSL=${ROOT}/tmp/openssl/apps/openssl
OPENSSL_CNF=${ROOT}/tmp/openssl/apps/openssl.cnf

NGINX_APP=${ROOT}/tmp/nginx/sbin/nginx
NGINX_CONF_DIR=${ROOT}/tmp/nginx/conf

##########################
# Build s_timer
##########################
make s_timer.o > /dev/null

##########################
# Setup network namespaces
##########################
${ROOT}/setup_ns.sh > /dev/null

##########################
# Generate ECDSA P-256 cert
##########################
# generate curve parameters
#${OPENSSL} ecparam -out prime256v1.pem -name prime256v1

# generate CA key and cert
${OPENSSL} req -x509 -new -newkey $1 -keyout ${NGINX_CONF_DIR}/CA.key -out ${NGINX_CONF_DIR}/CA.crt -nodes -subj "/CN=OQS test ecdsap256 CA" -days 365 -config ${OPENSSL_CNF} > /dev/null

# generate server CSR
${OPENSSL} req -new -newkey $1 -keyout ${NGINX_CONF_DIR}/server.key -out ${NGINX_CONF_DIR}/server.csr -nodes -subj "/CN=oqstest CA ecdsap256" -config ${OPENSSL_CNF} > /dev/null

# generate server cert
${OPENSSL} x509 -req -in ${NGINX_CONF_DIR}/server.csr -out ${NGINX_CONF_DIR}/server.crt -CA ${NGINX_CONF_DIR}/CA.crt -CAkey ${NGINX_CONF_DIR}/CA.key -CAcreateserial -days 365 > /dev/null

##########################
# Start nginx
##########################
cp nginx.conf ${NGINX_CONF_DIR}/nginx.conf > /dev/null
ip netns exec srv_ns ${NGINX_APP} > /dev/null
