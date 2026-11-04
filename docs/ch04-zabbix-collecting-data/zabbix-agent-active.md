---
description: |
    Configure Zabbix Agent in active mode, agent self-initiates connection to the
    server, fetches item configs, and pushes data continuously for proactive monitoring.
tags: [advanced]
---

# Zabbix Agent Active monitoring

In the previous section we installed our Zabbix agent and started monitoring a host
in the `Passive` mode. But as mentioned before, the Zabbix agent can also work in 
`Active` mode which has different advantages.

So let's now look at the Zabbix agent in `Active` mode. In `Active` mode our 
Zabbix agent will be configured to initiate the connection to the Zabbix server 
or proxy. It will request its configuration data and receive it back in the same
TCP session. After receiving its configuration it will then start sending the 
requested item data according to the configuration received. The connection as 
such is always initiated from the Zabbix agent side, meaning you will have to allow
your many agents to connect to your Zabbix servers or proxies instead.

![Zabbix Agent active hosts](ch04.25-windows-linux-active-agent.png){ align=center }

_4.25 Zabbix Agent active hosts_

---

## Setting up the active agent

It's possible to set up a Zabbix agent to work in both passive and active mode 
at the same time. Sometimes, we see this as passive mode was being used but an 
active only check is added later.  For clarity, in our example we will use a 
different Linux and Windows server for the active agent. 
We will call these hosts:

- **zbx-agent-active-rocky**
- **zbx-agent-active-windows**

Installation of the Zabbix agent here is the same as described in the previous section,
so we will not go through that again. We will start with the configuration of the active agent.
However, as explained in the Active vs Passive comparison in the previous section,
it is especially important to have correct time synchronisation when using `Active` agents. 
Refer to the chapter: [_Getting started_](../ch00-getting-started/Requirements.md)
to set up a time server.

Because the Zabbix active agent will need to know where to request its configuration
and where to start sending data to, the setup for the active agent is a bit different.
The setup process however is the same for both Linux and Windows. Let's start 
by editing the Zabbix agent configuration file.

There are two important parameters to configure. First, let's make sure our 
Zabbix agent will know where to connect to.

???+ example "Set ServerActive parameter"

    ```ini
    ServerActive=192.168.46.30
    ```

In the example `192.168.46.30` is the IP address of our Zabbix server (or proxy).
Do not forget to remove `127.0.0.1` in this case. It's important to remember that
our Zabbix agent in active mode will connect to every single IP address or DNS
name entered in the `ServerActive=` parameter. Unlike the `Server=` parameter we
used to set up passive mode, which functions as an allowlist.

Next up, our Zabbix agent needs to know which configuration data to collect. It
will connect to the Zabbix server (or proxy) on the IP specified and send over
its `Hostname=` parameter. By default this is set to `Hostname=Zabbix server`
which is incorrect in all cases except maybe on the Zabbix server itself.
So we need to change this parameter:

???+ example "Set Hostname parameter"

    Linux:

    ```ini
    Hostname=zbx-agent-active-rocky
    ```

    Windows

    ```ini
    Hostname=zbx-agent-active-windows
    ```

It is also possible to comment the `#Hostname=` parameters, in which case it will
use the `system.hostname` item key to determine the hostname. This makes it easy
for environments where the hostname is the same on the system as it will be in
Zabbix (best practice).

There is also the `HostnameItem=` parameter which you can use to set your own
item to determine the hostname used. This can be an existing item, but also a 
`UserParameter` (more on those later). With this functionality, you can even
execute a Bash or PowerShell script to set a custom hostname like that.

### Restricting which item keys the agent can execute

Now that our Zabbix agent knows where to connect, let's have a look at the security aspect.
By default, Zabbix can execute all item keys. We might want to allow the monitoring of
only certain item keys. For example monitoring specific files, but preventing other files 
from being read through the agent. We can do this with the `AllowKey` and `DenyKey` parameters 
in the Zabbix agent configuration file. Keep in mind that these parameters work for both 
`Passive` and `Active` checks, in both Zabbix agent and Zabbix agent 2.

#### Using AllowKey and DenyKey

The `AllowKey` parameter allows an item key to be executed, while `DenyKey`
blocks it. We can specify an exact item key or use the wildcard `*` to match
any number of characters.

Let's say we want to collect the size of a specfic application log file, but we do 
not want to allow file size checks for other files. We also want to block checks
that read file contents. To do this, we can add the following parameters to our Zabbix
agent configuration file.

???+ example "Allow and deny item keys"

    ```ini
    AllowKey=vfs.file.size[/var/log/myapp.log]
    DenyKey=vfs.file.size[*]
    DenyKey=vfs.file.contents[*]
    ```

As you can see, we first allow `vfs.file.size[/var/log/myapp.log]`. We then deny
all other file size checks with `DenyKey=vfs.file.size[*]`. So a parameter like
`vfs.file.size[/etc/passwd]` will not be allowed. The last parameter blocks all
checks using `vfs.file.contents`, regardless of which file is requested.

This makes sure that we can read the log file we need, but block the monitoring of
all other file sizes and especially their content. Of course, Zabbix agent (on Linux)
run as the `zabbix` user by default, already giving us limited permissions. But the 
AllowKey and DenyKey paramters give us additional options to secure our agent 
configuration further.

!!! tip "Put specific rules first"

    It's important to remember that the agent checks these rules in the configuration
    order (Top to Bottom). The first matching rule decides whether the item key is 
    allowed or denied. In our example, placing `DenyKey=vfs.file.size[*]` first would also
    block the application log file. Do not forget to place the `DenyKey` as an `AllowKey` parameter does not automatically block all other item keys without it.

#### Using AllowKey and DenyKey regular expressions

What if we have multiple application log files and want more control over which
files we allow monitoring on? Since Zabbix 8.0, we can also use `AllowKeyRegexp` and
`DenyKeyRegexp`, which give us more granular control using regular expressions. These 
Regular Expressions allow us to match item keys and their parameters in more detail.

Instead of the previous example, let's allow file size checks for two
application log files.

???+ example "Allow and deny item keys with regular expressions"

    ```ini
    AllowKeyRegexp=^vfs\.file\.size\[/var/log/myapp[12]\.log\]$
    DenyKeyRegexp=^vfs\.file\.size\[.*\]$
    DenyKeyRegexp=^vfs\.file\.contents\[.*\]$
    ```

With `[12]` we allow either `myapp1.log` or `myapp2.log`. The next two rules 
block other file size checks and all file contents checks, just as in our 
previous example. We can also combine the regular expression parameters with the 
regular `AllowKey` and `DenyKey`, but the first matching rule still makes the decision.

#### Keeping rules in a separate configuration file

It's also possible to keep these parameters in a separate `.conf` file. This
makes it easier to keep our custom settings together. For our Zabbix agent 2
on Linux, let's create a file in the `zabbix_agent2.d` directory.

!!! info "Create an additional agent configuration file"

    Linux

    ```bash
    sudo vi /etc/zabbix/zabbix_agent2.d/key-access.conf
    ```

Add one of the example rule sets above to this file. Then make sure the main
`zabbix_agent2.conf` file includes the directory. Depending on your installation,
the following parameter might already be configured.

???+ example "Include additional configuration files"

    ```ini
    Include=/etc/zabbix/zabbix_agent2.d/*.conf
    ```

Do not forget to check the existing `Include` parameters first, so the same
configuration file is not loaded twice.

!!! tip "Keep related rules together"

    Keep allow and deny rules that depend on each other in the same file.
    We cannot rely on the order in which files from an included directory are
    loaded, even if we give them names that sort alphabetically.

With this configuration set you can restart the Zabbix agent to make the changes
take effect. In `Windows` restart the Zabbix Agent 2 service, for `Linux` issue the command below.

!!! info "Restart Zabbix agent on Linux"

    ```bash
    systemctl restart zabbix-agent2
    ```

This finalises the configuration file changes. Now we need to configure the host
 in Zabbix.

![Zabbix Agent active hosts in Zabbix](ch04.26-windows-linux-active-agent-host.png){ align=center }

_4.26 Zabbix Agent active hosts in Zabbix_

All we need to do here is make sure to match the hostname of what we configured
in the Zabbix agent configuration file. Keep in mind that the `Hostname` field
has to match the `Hostname=` parameter in the configuration file. 
The `Visible name` field does not have an effect on the active agent functioning.

---

## Creating active items

Now that the agent is configured to perform active checks, we can now start to
create some items on our active agent host in Zabbix frontend. Let's click on
`Items` for our host and configure a new Zabbix active type item.

![Zabbix Agent active item](ch04.27-active-agent-item.png){ align=center }

_4.27 Zabbix Agent active item_

Make sure to set the item `Type` to `Zabbix agent (active)`. Most item keys will
be the same between `Passive` and `Active` mode, but the `Type` needs to be set
correctly.

Also, do not forget to add the tag to this item.

![Zabbix Agent active item tag](ch04.28-active-agent-item-tag.png){ align=center }

_4.28 Zabbix Agent active item tag_

Your `ZBX` icon for this host should now turn green, even in active mode.

---

## Conclusion

In this section we have seen how to set up a Zabbix agent in `Active` mode. We
have created a new host in Zabbix and configured it to match the `Hostname` parameter
in the Zabbix agent configuration file. We have also created a new item of type
`Zabbix agent (active)` to start collecting data from our active agent.

We have now seen both the `Passive` and `Active` mode of the Zabbix agent. Both have their
advantages and disadvantages, and both can be used in different scenarios.

---

## Questions

- Why does the `Hostname` parameter need to match the hostname in Zabbix?
- Why is time synchronisation important for active agents?
- Can you use the same host for both passive and active checks?

---

## Useful URLs

- [https://blog.zabbix.com/zabbix-agent-active-vs-passive/](https://blog.zabbix.com/zabbix-agent-active-vs-passive/)
- [https://www.zabbix.com/documentation/current/en/manual/appendix/items/activepassive](https://www.zabbix.com/documentation/current/en/manual/appendix/items/activepassive)
