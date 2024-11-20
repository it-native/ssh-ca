#!/bin/bash

set -e

# Get the role ID
roleid=$(cat /opt/secrets/roleid.txt)
# Get the SSH public key
ssh_public_key=$(cat /etc/ssh/ssh_host_ed25519_key.pub)

# Obtain a token from Vault
token=$(
    curl -s -XPOST \
        --data "{\"role_id\": \"${roleid}\"}" \
        "https://vault.domain.com:8200/v1/auth/server-login/login" \
    | jq -r ".auth.client_token"
)

# Collect the SSH public key
ssh_public_key=$(cat /etc/ssh/ssh_host_ed25519_key.pub)

# Get a new certificate
cert=$(
    curl -s -XPOST \
        --header "X-Vault-Token: $token" \
        --data "{ \
            \"public_key\": \"$ssh_public_key\", \
            \"cert_type\": \"host\"\
        }" \
        "https://vault.domain.com:8200/v1/ssh-server-ca/sign/server-signing" \
    | jq -r ".data.signed_key"
)

# Put the new certificate to the correct position
echo $cert > /etc/ssh/ssh_host_ed25519_key-cert.pub
