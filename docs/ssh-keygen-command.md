# SSH Keygen command

Some important flags and what they do.

-   `-I`: This identity will be shown in all logs. Make it something meaningful, like the name of the developer or server.
-   `-n`: It denotes what users I will have access to on the server, and accepts multiple comma-separated values <br>
    Example: `-n root,pi` - I will have access to the root and the pi user.
-   `-V`: Validity. `+1d` denotes 24h validity from now on.
-   `-z`: Serial number. If multiple certificates are issued to a single client, this can help in tracking. <br>
    Not quite sure if I agree this one. Very important, serial numbers have the nice property of allowing to revoke a certificate (with a given serial number).

# Sources
* [Betterprogramming.pub](https://betterprogramming.pub/how-to-use-ssh-certificates-for-scalable-secure-and-more-transparent-server-access-720a87af6617)
