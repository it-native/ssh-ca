#!/bin/bash

set -e

do_install() {

    hostname="{{ hostname }}"

    basedir=/opt/secrets

    ssh_key=$(cat /etc/ssh/ssh_host_ed25519_key.pub)

    echo Setting up the host in the CA
    curl -sf \
        "{{ url_for('setup_host_v1', hostname=hostname) }}" \
        --data "{\"ssh_key\": \"$ssh_key\"}" \
        -H "Content-Type: application/json" \
        > /dev/null
    echo Host setup successful.

    # Fetch and store CA public key
    echo Setup CA certificate
    curl -s "{{ url_for('get_ca_certificate') }}" > /etc/ssh/ca.pub

    echo Setup scripts for automatic renewal
    # Create scripts directory
    mkdir -p $basedir
    # Fetch the certificate checker file
    filename=$basedir/check-ssh-host-certificate-renew.sh
    curl -s "{{ url_for('get_script_checker') }}" > $filename
    chmod 755 $filename
    filename=$basedir/renew-ssh-host-certificate.sh
    curl -s "{{ url_for('get_script_renewer', hostname=hostname) }}" > $filename
    chmod 755 $filename
    filename=/etc/systemd/system/ssh-host-certificate-renew.timer
    curl -s "{{ url_for('get_systemd_timer') }}" > $filename
    filename=/etc/systemd/system/ssh-host-certificate-renew.service
    curl -s "{{ url_for('get_systemd_service') }}" > $filename

    echo Fetching my SSH certificate
    /opt/secrets/renew-host-certificate.sh

    echo Setting up your SSH daemon
    curl -s "{{ url_for('get_ssh_config_file') }}" > /etc/ssh/sshd_config.d/ca-config.conf

    echo Enabling automatic SSH certificate renewal
    systemctl daemon-reload
    systemctl start ssh-host-certificate-renew.timer

    echo Restarting the SSH daemon
    systemctl restart ssh

    # Checking that the directory exists - this
    # created some errors for me
    mkdir -p /run/sshd
}

# Taken from https://get.docker.com: Wrap everything
# into a function so that getting only a half file
# won't happen
do_install $1
