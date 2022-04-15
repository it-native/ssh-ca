# On the topic of user principals

- [On the topic of user principals](#on-the-topic-of-user-principals)
- [Allow principals server-wise](#allow-principals-server-wise)
  - [How to](#how-to)
  - [Why I do not like that - and why I will still have to use it](#why-i-do-not-like-that---and-why-i-will-still-have-to-use-it)
  - [What to remember](#what-to-remember)
- [Sources](#sources)

Each certificate - no matter if user or server - has principals. Here, I want to discuss how I can use principals for users.

My idea of principals: I want to allow the user to connect to `root@server1` but not `root@server2`. Hence, I would like to write into the principals: "Allow connection to `root@server1` and the server should understand that. Let's see.

# Allow principals server-wise

## How to

-   On the server, create the directory `/etc/ssh/auth_principals`.
-   On the server, create the file `/etc/ssh/auth_principals/fancy_username` with the contents `my_principal`. The user `fancy_username` obviously should exist on the machine.
-   On the server, edit `/etc/ssh/sshd_config` and add the line: `AuthorizedPrincipalsFile /etc/ssh/auth_principals/%u`
-   For the client certificate, add `my_principal` to the list of principals
-   On the client, run `ssh fancy_username@server`
-   Be happy!

## Why I do not like that - and why I will still have to use it

I would prefer keeping all the configuration on the SSH-CA server. All the other servers should keep as less configuration as possible. <br>
This can make things more complicated - I know that and I have no problem with it. <br>
Until now, my servers only know the SSH-CA public key and some configuration in the config file. I do not really expect anything more to happen.

On the other hand, this seems to be _the_ way to go - in the sense of: There seems to be not really any other option.

Even [Facebook](https://engineering.fb.com/2016/09/12/security/scalable-and-secure-access-with-ssh/) uses this method. I do not really like or trust Facebook, but I believe they would blog about it if they had any other way of authorization.

## What to remember

-   There can be multiple principals per certificate. If there is a username as principal, then logging in via the username will always work. Hence, _either_ use usernames _or_ principals which are defined in a file. Prevent using both as this is complicated.

# Sources

-   [Principals server-wise](https://betterprogramming.pub/how-to-use-ssh-certificates-for-scalable-secure-and-more-transparent-server-access-720a87af6617)
-   [Betterprogramming.pub](https://betterprogramming.pub/how-to-use-ssh-certificates-for-scalable-secure-and-more-transparent-server-access-720a87af6617)
