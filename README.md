# SSH CA

tl;dr: Read and follow the instructions in [sample setup](#sample-setup) and be happy.

Contents:

- [SSH CA](#ssh-ca)
  - [Why?](#why)
  - [Sample setup](#sample-setup)
  - [Renewing certificates](#renewing-certificates)
  - [What I want to add in this repo](#what-i-want-to-add-in-this-repo)

## Why?

tl;dr below.

Type `ssh somebody@server` - On first connect, your SSH client will ask you "Do you trust this server?". It will show you a very long sequence of characters. Since you care about computer security, you compare the public SSH host key of the server against this sequence and type "yes" - after having done so.

This is the first problem I want to solve: I do not want to blindly trust the server to be the right one. Using a certificate, I can bypass this problem.

Next, I have loads of (virtual) servers - currently, two machines with about five virtual servers each - makes 12 machines I want to handle using SSH. Obviously, each of them has a password of at least 32 characters, each one is different (thanks so much to my password manager!). I am typing `ssh some_server` quite some times every day. Typing a password (or actually, copy/pasting it - thanks so much to my password manager!) I prefer using SSH key-based authentication. Hence, I deployed the SSH public key of my local machine to each of my servers. Only one password remains to be typed - the one of my SSH key.

Now I had the idea of having a backup machine (VM number 13!) which I can access using RDP all the time. The public key of that one should also be deployed on each server. Also, there is the computer I got from my company for work. The third public key to be deployed. Oh wait, it is a Windows machine and I have WSL there. The fourth one (actually, I ignore the third one and just use SSH via WSL).

Now I reset my private computer some time ago. And, silly me, forgot to store my private SSH key somewhere. Next, I found out that RSA encryption is quite old and ed_25519 should be used instead (no source on that one!). Did you keep up, which SSH keys should be deployed on which server? No? Me neither.

Hence my second problem: I do not really want to deploy all my public SSH keys to each server. I did not know ansible at the time (I do now), which would have made the problem easier. Well, at the time, I remembered an article I overread some time ago: [If you’re not using SSH certificates you’re doing SSH wrong](https://smallstep.com/blog/use-ssh-certificates/). Well, let's give it a shot. And here I am.

**tl;dr**:

-   I do not want to deploy public SSH keys of multiple clients to all my servers.
-   I do not want to check authenticity of a server on first connect.

## Sample setup

For the setup of my certificate authority (CA), I will use the following machines:

-   `auth-server`: The server which will hold the CA private key and sign the certificates. Only one directory of the server will be required (for now: `/root/ssh-ca`; this may become flexible in the future). The `auth-server` can be the same computer as your desktop or server, I am just going to use a different name to not confuse anybody.
-   `desktop`: The client machine. Most probably the machine you are reading this README on.
-   `server`: The server you want to connect to. Hence, on `desktop` you want to type the command `ssh somebody@server`.

Now for initial setup, do the following:

1. The SSH certificate authority itself essentially is a public/private key pair. Create it: `root@auth-server:/root/ssh-ca# ssh-keygen -t ed25519 -C ca@your.domain -f ca`. Put a password on this one.
2. Create the desktop certificate:
    1. Create a directory `auth-server:/root/ssh-ca/desktop`. The last part (`desktop`) needs to be unique per client/server! Also, for a server, it should be the domain name - so, `server.example.com`. This will be used as principal.
    2. Copy `user@desktop:~/.ssh/id_{rsa,ed25519,...}.pub` to `root@auth-server:/root/ssh-ca/desktop/id_{...}.pub`
    3. Create the file `auth-server:/root/ssh-ca/desktop/principals` and add only one line: `server_username` - the username you want login as on the server
    4. Go to the base directory of this script and run `root@auth-server:/root/ssh-ca# ./cert.sh desktop`
    5. Find a new file `auth-server:/root/ssh-ca/desktop/current-cert.pub`. Be excited!
    6. Copy this `current-cert.pub` to `user@desktop:~/.ssh/id_{same_as_before}-cert`. Omit the `.pub` part of the filename!
    7. Continue reading the next step. This is important - otherwise, you have nothing.
3. Authorize signed certificates on the server
    1. Copy `auth-server:/root/ssh-ca/ca.pub` to `server:/etc/ssh/ca.pub`
    2. Edit `server:/etc/ssh/sshd_config` and add the following line: `TrustedUserCAKeys /etc/ssh/ca.pub`. Hence, if the client authenticates with a certificate signed by the CA, accept it (depending on the principals)
    3. Restart sshd: `root@server:_# systemctl restart sshd` on debian/Ubuntu. This may differ on your server - but `sshd` should be called `sshd` on the most common Linux distributions.
    4. Now, try to login using SSH: `user@desktop:_$ ssh server_username@server.domain.com`. Remember that `server_username` needs to match the username you wrote into the `principals` file on the CA.
    5. If you are feeling lucky, delete `server_username@server:~/.ssh/authorized_keys` and try to login again. Do not forget to keep a backup (and an open SSH session to the server in case something does not work)!
    6. Now, be excited!
4. Create the server certificate:
    1. Create the directory `auth-server:/root/ssh-ca/server.example.com`. Here, `server.example.com` needs to resolve to your `server` - you can also use the IP address of your host if you are unsure.
    2. Do not create a principals file for now. It is not required.
    3. Copy `server:/etc/ssh/ssh_host_ed25519_key.pub` to `auth-server:/root/ssh-ca/server.example.com/ssh_host_ed25519_key.pub`
    4. Create the certificate: `root@auth-server:/root/ssh-ca# ./cert.sh server.example.com`
    5. Be excited once again
    6. Copy `auth-server:/root/ssh-ca/server.example.com/current-cert.pub` to `server:/etc/ssh/ssh_host_ed25519_key-cert.pub`
    7. Edit `server:/etc/ssh/sshd_config` once more and add the line `HostCertificate /etc/ssh/ssh_host_ed25519_key-cert.pub`
    8. Again, restart sshd - see above
    9. Again, continue reading the next step - otherwise, nothing will change.
5. Adapt known_hosts: Let your client know that it can trust servers with a certificate signed by your CA
    1. Edit `desktop:~/.ssh/known_hosts` (Backup!)
    2. If you are feeling lucky (Backup!!), delete all the contents of the file. Remember that it's not my fault.
    3. Add a new line that reads as follows: `@cert-authority *.domain.com ssh-ed25519 *`.
        - The `ssh-ed25519 *` part should be the contents of the `ca.pub` file.
        - `*.domain.com` could also be IP addresses - for example, `192.168.0.*`. Don't nail me down on that one - I did only try the `*.domain.com` part until now. In any case, it should match the `server` part of `ssh somebody@server` command you are running. TODO.
    4. SSH to your server. Hope to not see an `Authenticate?` question. If you really want to test it, delete all the other lines in the `known_hosts` file. Hence, the only option for the server to authenticate is to present a signed certificate.

## Renewing certificates

If you want to renew a certificate, just run `./cert.sh {your_device}` and renew the certificate file on the device.

## What I want to add in this repo

-   Commands I found helpful
-   Principals - How I use them and how they _should_ be used
-   Description what the script does
-   Setup - Create SSH CA key, serial
-   Ansible!
-   Plans for the future
    -   Web Server
        -   Initial deployment for server and client - with preface on auth-server
        -   Renewal for client and server
        -   Update principals? Better not - due to security...
-   About expiration of certificates
-   Trouble shooting?
