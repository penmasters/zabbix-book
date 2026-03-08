---
description: |
    Extend monitoring with Zabbix external checks. Run custom scripts or commands
    on the server to collect data from systems not covered by built-in items.
tags: [advanced]
---

# External checks

Zabbix is remarkably capable out of the box, but the real world has a
habit of throwing requirements at you that no built in item type can
neatly address. Maybe you need to query a proprietary API, scrape a
value from a legacy system, or run a bespoke health check that only your
team understands. That is exactly the problem external checks solve.
An external check is a Zabbix item that, instead of communicating
directly with a host, asks the Zabbix server (or proxy) to run an
arbitrary shell script or binary on its behalf. Whatever that script
prints to standard output becomes the item value. No agent is required
on the monitored host, the script runs entirely on the Zabbix server
or proxy machine.


## How It Works

When the item is due for collection, Zabbix looks up the ExternalScripts
directory (configured in zabbix_server.conf or zabbix_proxy.conf) and
forks a new process to execute the named script. The script runs under
the same OS user as the Zabbix server or proxy process, so file
permissions and environment variables must be set up accordingly.
The item key follows this syntax:

```ini
script[<parameter1>,<parameter2>,...]
```

If no parameters are needed, either of the following forms is
acceptable:

```ini
script
script[]
```

Parameters are passed to the script as individual quoted command line
arguments. Zabbix macros such as {HOST.CONN} or {HOST.NAME} can be used
inside parameter values, they are resolved before the script is
called. This means you can write a single generic script and rely on
macros to supply the host-specific details at runtime.

???+ note

    When a host is monitored through a Zabbix proxy, the
    external check script is executed by the proxy, not by the central
    server. Make sure your scripts are deployed on every machine that needs
    to run them.


## Return Value and Error Handling

The item value is formed from whatever the script writes to standard
output (stdout), combined with any message written to standard error
(stderr). Trailing whitespace is stripped automatically. The total
return value of the script is capped at 16 MB, this should be more than
enough for any reasonable monitoring purpose.

**There are however a few situations worth knowing about:**

- If the script cannot be found or Zabbix lacks execute permission,
  the item becomes unsupported and an error message is logged.
- If the script times out, it is terminated, the item becomes
  unsupported, and a timeout error is recorded.
- For text-type items (character, log, or text), a non-empty stderr
  output alone does not cause the item to become unsupported.


!!!+ warning

    Every external check creates a new forked process. Running dozens of them
    at a short collection interval can noticeably impact Zabbix server
    performance. Use external checks for things that genuinely cannot be done
    another way, and keep collection intervals as long as your monitoring
    requirements allow.

## Practical example : Counting Logged-In Users

To show you an easy example, let's build something you can try right now on the
machine where Zabbix is installed. The script will count how many users are
currently logged into the local system, using the who command, which is part of the
standard coreutils package present on every installation.

You will create the item on the Zabbix server host itself the one
that already appears in your host list as "Zabbix server". The script
runs locally on that same machine, so there is nothing to connect to and
no credentials to manage.

### Creating the Script

Create the file 'check_logged_users.sh' in the ExternalScripts directory.
On most systems this is **/usr/lib/zabbix/externalscripts/** you can check your
zabbix_server.conf if unsure:

``` bash
#!/bin/bash
# Returns the number of users currently logged into the system.
# No arguments needed.
who | wc -l
```

That is the entire script, four lines including the comments. The who
command lists one line per active login session; wc -l counts those
lines. 

Make the script executable:

``` bash
chmod +x /usr/lib/zabbix/externalscripts/check_logged_users.sh
```

You can verify it works straight away by running it manually as the
zabbix user:

``` bash
sudo -u zabbix /usr/lib/zabbix/externalscripts/check_logged_users.sh
```

### Create the Item in Zabbix

Now that we have our script we need to create an item in Zabbix as our final
step. In the Zabbix web interface, go to `Data collection → Hosts`, open the
Zabbix server host, and add a new item with these settings:

| Field                  | Value                      |
| :---                   | :---                       |
| Name                   | Number of logged-in users  |
| Type                   | External check             |
| Key                    | check_logged_users.sh      |
| Type of information    | Numeric (unsigned)         |
| Units                  | users                      |
| Update interval        | 1m                         |


### Check the Result

Save the item and navigate to `Monitoring → Latest data`. Within a minute
you should see a value like 2 ( depending on your system ) appear next to your
new item, reflecting the number of active sessions on the Zabbix server at that
moment. Open a second terminal to SSH in, wait for the next collection cycle,
and watch the number go up to 3 ( or 1 higher then previous number ). Close it,
and it comes back down. From here you could add a trigger to alert when the count
exceeds an expected threshold, useful for detecting unexpected logins on a
production server.


!!! note "A word of wisdom when it comes to scripts"

    A colleague of me once created an external check
    that itself called another monitoring tool, which in turn called a
    Python script that imported a module and complained about a missing
    dependency.

    The lesson: keep your external scripts as simple and self-contained as
    possible. If your script needs a PhD thesis to maintain, it probably
    deserves to be a proper Zabbix plugin instead.

## Conclusion

External checks give you an escape hatch from the boundaries of built-in Zabbix
item types. You write a script, drop it in the ExternalScripts directory,
and reference it with a standard item key. Zabbix handles scheduling, macro
substitution, and value storage, you only have to worry about what the script
does. Used sensibly and sparingly, external checks are one of the most powerful
extensibility mechanisms Zabbix offers.

## Questions

- You configure an external check on a host that is monitored through a Zabbix proxy.
  On which machine does the script actually execute

- An external check item suddenly becomes unsupported and the error message reads
  "Cannot execute external check command." What are the two most likely causes ?

- You have written a script that takes 45 seconds to complete. The item's update interval
  is set to 1 minute. What risk does this create, and what would you do to address it?

- Your script writes a warning message to stderr but also returns a valid numeric value
  on stdout. The item type is set to Numeric (unsigned). Will the item become unsupported?
  What would happen if the item type were set to Text instead?

## Useful URLs

- [https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/external](https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/external)

