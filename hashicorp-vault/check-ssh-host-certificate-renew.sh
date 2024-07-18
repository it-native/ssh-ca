#!/bin/bash

# Store the expiry date in a variable
cert_expiry_date=$(ssh-keygen -L -f /etc/ssh/ssh_host_ed25519_key-cert.pub | grep "Valid:" | cut -d " " -f 13)

# Store the expiry date as seconds since the epoch
cert_expiry_seconds=$(date +%s -d $cert_expiry_date)

if [ $? -ne 0 ]; then
	# If finding the date failed, do the renew for sure
	/opt/secrets/renew-ssh-host-certificate.sh
else

	# Store the time "now" as seconds since the epoch
	now=$(date +%s)

	# Compute the number of days between "now" and "cert expiry"
	# Note: No spaces for the division! Otherwise, bash fails.
	let validity=($cert_expiry_seconds - $now)/86400

	timeout=2

	if [ $validity -lt $timeout ]; then
		/opt/secrets/renew-ssh-host-certificate.sh
	fi

fi
