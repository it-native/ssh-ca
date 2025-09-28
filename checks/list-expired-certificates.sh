#!/bin/bash

for filename in $(find | grep "current-cert.pub$")
do
	
	cert_expiry_date=$(ssh-keygen -L -f $filename | grep "Valid:" | cut -d " " -f 13)
	cert_expiry_seconds=$(date +%s -d $cert_expiry_date)

	now=$(date +%s)

  let validity=($cert_expiry_seconds - $now)/86400

  if [[ $validity -lt 0 ]]; then
    echo "SSH certificate $PWD/$filename is expired!"
  elif [[ $validity -lt 5 ]]; then
    echo "SSH certificate $PWD/$filename will expire in $validity" days. Please refresh.
  fi
  
done
