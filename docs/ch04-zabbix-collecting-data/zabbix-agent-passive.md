---
description: |
    Zabbix Agent in passive mode. The server polls the agent (on TCP 10050) for
    item data; agent responds to requests when queried. Efficient agent-server
    communication.
tags: [advanced]
---

# Zabbix Agent installation and Passive monitoring

At this point we are familiar with the Zabbix dataflow, how to create hosts and,
add interfaces and items to a host. As a system administrator or anyone else working
with Linux, Unix or Windows systems usually we jump right into installing the Zabbix
agent and monitoring with it. Using our previous steps however, we have laid the
groundwork for building a proper monitoring solution. We have prepared our systems
before monitoring, which is the most important part to avoid `Monitoring fatigue`
later on.

???+ note "Monitoring fatigue and Alert fatigue"

    **Monitoring fatigue** and **Alert fatigue** are two terms heard in monitoring 
    and observability:

    - **Alert fatigue** happens in Zabbix when you configure too many (incorrect) 
      triggers. When you flood your dashboards or even external media like Teams 
      or Signal with too many alerts your users will not respond to them any longer.

    - **Monitoring fatigue** happens in Zabbix when you misconfigure things like 
      dashboards, items, host groups, tags and other internal systems that keep 
      things structured. The result is that you or your co-workers do not want 
      to use your own system any longer as it does not deliver the right 
      information easily enough.

Now, we are ready to start monitoring an actual system.

## Agent basics

We have prepared an example setup in our Book LAB environment.

![Zabbix Agent passive hosts](ch04.14-windows-linux-agent.png){ align=center }

_4.14 Zabbix Agent passive hosts_

What we can see here is a setup you might see in any datacenter or office server
cabinet. We have a Zabbix server monitoring one Windows server and one Linux server
directly (or through a proxy). We call Zabbix a network monitoring solution as it
communicates over the network. In Zabbix we have two methods of communication.

- **Passive** Otherwise known as `polling`. We communicate from the Zabbix server
  (or proxy) towards the monitoring target. The monitoring target is listening
  on a port waiting for Zabbix to request data.
- **Active** Otherwise known as `trapping`. We communicate from the monitoring
  target towards the Zabbix server (or proxy). The Zabbix server is listening
  on a port waiting for the monitoring target to send data.

As you can imagine there is quite a big difference between these two methods of 
communication. Often times it depends on the protocol which method is preferred.
For example SNMP traps are always an active type of check.

The Zabbix agent however can communicate in either `Active` or `Passive` mode. 
It can even do those simultaneously. Simultaneous communication can be useful when
you want to use `Passive` mode for all communication, but still want to execute
some items that are `Active` only. `Active` items can do everything `Passive` 
items can do however.

### Active vs Passive communication

The Zabbix agent can operate in two modes: `Active` and `Passive`. Each 
mode has distinct behaviors and use cases, affecting how the agent communicates 
with the Zabbix server.

#### Passive Agent Mode

In `Passive` mode, the Zabbix server initiates the connection to the agent to 
request data. 

For each `Passive` item, the server will periodically poll the agent for 
the metric, and then wait for the agent to collect and return the requested data
or until the item `Timeout` setting is reached. The item data is then returned
by the agent within the same TCP session which is then closed.

The timestamp of the item is set by the server on the collected value, 
not by the agent when it collects the item. This may result in less accurate 
timestamps.

The Zabbix agent can start multiple passive threads (default: 3), allowing for 
simultaneous checks. This means that if one check (for example a custom script)
takes longer to finish, the other threads can continue serving metrics on server
request.

This mode is straightforward and works well in environments where the server can
reliably reach the agent.

**Pros:**

  - Simple to configure and manage.
  - Works well when the Zabbix server or proxy can directly access the agent.
  - Zabbix agent can start multiple passive threads (default: 3), allowing for 
    simultaneous checks. 
  - Is not bound to the hostname configured in the agent configuration file, 
    which means that you can use the same agent configuration file on multiple
    hosts and just change the hostname on the Zabbix frontend. Or even query the
    same agent from multiple *hosts* in the Zabbix frontend.

**Cons:**

  - The server must actively poll each agent for each item, which can increase
    network traffic and server load as the number of agents and passive items grows.
  - If the agent is behind a firewall or NAT, additional configuration may be
    required to allow incoming connections from the server. This however can be
    a security risk or even not allowed by your network policies.
  - If the server cannot reach the agent, data collection will be interrupted 
    until the connection is restored.
  - A few items, such as log item keys, can not be executed in passive mode.
  - Timestamps may be less accurate as they are set to the time when the server 
    receives the data, not when the agent collects it.

#### Active Agent Mode

In `Active` mode, the Zabbix agent takes the initiative to send data to the 
server. The agent will ask the server what items to check and then
periodically collect and send requested metrics to the server or proxy without
waiting for a request. This mode is particularly useful in environments where
the agent cannot be directly accessed by the server due to network restrictions 
or security policies.

Additionally, when using Zabbix Agent 2, you can configure it to buffer active 
check results in case the server or proxy is not available for a short time, 
ensuring that data collection is not interrupted.

During data collection, the agent will add a timestamp to the collected value 
directly on the agent side, which can provide more accurate timestamps. However,
this also means that if the agent's time is not synchronized with the server,
it can lead to issues with data accuracy and trigger evaluations. So when using
`Active` mode it is important to have a time server configured on your monitoring
targets as outlined in the chapter: [_Getting started_](../ch00-getting-started/Requirements.md).

**Pros:**

  - Reduces the load on the Zabbix server by eliminating the need for constant 
    polling.
  - Works well in environments with strict firewall rules or NAT, as the agent 
    initiates the connection.
  - Can improve performance and scalability in large environments due to some
    load being distributed.
  - Zabbix Agent 2 can be configured to buffer active checks in case the server 
    is not available for a short time, ensuring that data collection is not 
    interrupted.
  - Timestamps are more accurate as they are set by the agent at the time of
    collection, not by the server when it receives the data.

**Cons:**

  - Requires the hostname set in the Zabbix agent configuration to match the 
    hostname configured in the Zabbix frontend, which can make it less flexible 
    in certain scenarios.
  - Active checks use a single thread for collecting andsending data, which means
    that if a check takes longer to perform, it will delay subsequent checks.
  - Correct time synchronization on both the agent and server is crucial for 
    accurate data and trigger evaluations.

#### Choosing between Active and Passive modes

As you see, both `Active` and `Passive` modes have their own advantages and 
disadvantages. The choice between them depends on your specific environment and 
requirements. If your Zabbix server can reliably access the agents and you prefer 
a simpler configuration, `Passive` mode may be suitable. However, if you have 
network restrictions or want to reduce server load, `Active` mode may be the better 
choice.

In many cases, a combination of both modes can be used to leverage the advantages
of each. For example, you might use `Active` mode for most checks but configure
specific items in `Passive` mode, such as longer running checks to prevent other
checks from being delayed. Or checks that require a different hostname than the 
one configured in the agent configuration file. 

Finally, let's do a bit of a comparison between the two modes.

|                     | Active Zabbix agent                 | Passive Zabbix agent   |
| :------------------ | :---------------------------------- | :--------------------- |
| Timestamp           | Zabbix agent                        | Zabbix server or proxy |
| (event)log items    | Supported                           | Not supported          |
| Port                | No port listening, connect to 10051 | Listening on 10050     |
| Hostname            | Has to match                        | Can be anything        |
| Remote commands     | Supported                           | Supported              |
| Concurrency         | Single thread                       | Multiple threads       |
| Buffering on outage | Yes (if configured on Agent 2)      | No                     |

The flexibility of Zabbix allows you to tailor your monitoring solution to best 
fit your needs.

In the current section we will start with the `Passive` mode, and in the next 
section we will look at the `Active` mode.

### Zabbix agent vs Zabbix agent 2

Before we can configure either though, we will have to install our Zabbix agent
first. When installing on Linux and Windows we have a choice between two different
agents, `Zabbix agent` and `Zabbix agent 2`. Both of these Zabbix agents are still
in active development and receive both major (LTS) and minor updates. The difference
between them is in Programming language and features.

|                      | Zabbix agent                     | Zabbix agent 2                          |
| :------------------- | :------------------------------- | :-------------------------------------- |
| Features             | No focus to include new features | Supports everything agent 1 does + more |
| Programming language | C                                | GoLang                                  |
| Extensions           | C Loadable Modules               | GoLang plugins                          |
| Platforms            | All                              | Linux and Windows                       |
| Concurrency          | In sequence                      | Concurrently                            |
| Storage on outage    | No                               | Sqlite                                  |
| Item timeouts        | Agent wide                       | Per plugin                              |

???+ note 

    As you can see, `Zabbix agent 2` is the more feature-rich agent and is the 
    recommended agent to use when available. However, `Zabbix agent` is equally 
    supported and can be used when `Zabbix agent 2` is not available for your platform 
    or if you have specific use cases that require `Zabbix agent`. For example, if you 
    want to use a C Loadable Module that has not yet been ported to `Zabbix agent 2`, 
    you will have to use `Zabbix agent`.
    Also, as C is a lower level programming language, `Zabbix agent` can be more
    performant in certain use cases such as monitoring embedded devices or devices
    with very limited resources.

## Agent installation on Linux

Installation on Linux can be done in one of three ways. Through direct install
files like `.rpm` and `.deb`, by building from sources and through packages pulled
from the repository. Installation through the packages is preferred as this means
Zabbix agent will be updated when updating with commands like `dnf update` and
`apt upgrade`. Keep in mind, Zabbix agent is a piece of software just like any
other and as such news versions will contain security and bug fixes. Whatever
installation method you choose, keep your Zabbix agent up-to-date.

We will be using the packages on RedHat-, SUSE-based or Ubuntu to install 
`Zabbix agent 2`. To use the packages we will need to prepare our system 
as outlined in chapter: [_Getting started_](../ch00-getting-started/preparation.md).
Only adding the Zabbix repository is mandatory here, however following the 
[_Requirements_](../ch00-getting-started/Requiremens.md) outlined in that chapter
is also recommended to make sure you have all the necessary tools to work with
Zabbix.

After adding the repository, we should be able to install `Zabbix agent 2`.

!!! info "install Zabbix agent 2 package"

    Redhat

    ```bash
    dnf install zabbix-agent2
    ```

    SUSE
    ```bash
    zypper install zabbix-agent2
    ```

     Ubuntu

    ```bash
    sudo apt install zabbix-agent2
    ```

After installation make sure to start and enable the Zabbix agent.

!!! info "Start and enable Zabbix agent 2"


    ``` yaml
    systemctl enable zabbix-agent2 --now
    ```

Your agent is now installed under the `zabbix` user and ready to be configured.

## Agent installation on Windows

On Windows, we have two options to install our Zabbix agent. Through downloading
the `.exe` file and placing the configuration files in the right location or the
easy option. Downloading the `.msi` and going through the installation wizard.
Whichever method you prefer, you'll first have to navigate to the Zabbix download
page. We will be using the `.msi` in our example.

<https://www.zabbix.com/download_agents?os=Windows>

Here you will be presented with the choice to download either `Zabbix agent` or
`Zabbix agent 2`. Choose whichever one you would like to install, but by now we
recommend `Zabbix agent 2` as it is stable and includes more features.

Once downloaded, we can open the new `zabbix_agent2-x.x.x-windows-amd64-openssl.msi`
file and it will take us to the wizard window.

![Zabbix Agent Windows install step 1](ch04.15-windows-agent-install-step1.png){ align=center }

_4.15 Zabbix Agent Windows install step 1_

Step 1 is a simple welcome screen, nothing to do here except click on `Next`.

![Zabbix Agent Windows install step 1](ch04.16-windows-agent-install-step2.png){ align=center }

_4.15 Zabbix Agent Windows install step 2_

For step 2, make sure to read the `License Agreement` (or don't, we do not give 
legal advice). Then click `Next`.

![Zabbix Agent Windows install step 1](ch04.17-windows-agent-install-step3.png){ align=center }

_4.15 Zabbix Agent Windows install step 3_

For step 3 we have some more actions to execute. By default the Zabbix agent on
Windows `.msi` installer includes `Zabbix sender` and `Zabbix get`. These are
separate utilities that we do not need on every Windows server. I will not install
them now, but we can always use the `.msi` to install them later. The Zabbix agent
will function fine without them.

![Zabbix Agent Windows install step 1](ch04.18-windows-agent-install-step4.png){ align=center }

_4.15 Zabbix Agent Windows install step 4_

Step 4 is our most important step. Here we will already configure our Zabbix agent
configuration file, straight from the `.msi` installer. Let's make sure to set
the `Hostname`, `Zabbix server IP/DNS` (`192.168.46.6` in our case) and let's
also set the `Server or proxy for active checks` parameter. As you can see we
could also immediately configure encryption with the `Enable PSK` option, but
we will do this later.

![Zabbix Agent Windows install step 1](ch04.19-windows-agent-install-step5.png){ align=center }

_4.15 Zabbix Agent Windows install step 5_

Now there is nothing left to do except press `Install` and our Zabbix agent will
be both installed and configured.

## Agent installation on Unix

For Unix based systems, simply download the files on the Zabbix download page for
 either `AIX`, `FreeBSD`, `OpenBSD` or `Solaris`.

<https://www.zabbix.com/download_agents>

## Agent installation on MacOS

For MacOS systems, simply download the files on the Zabbix download page and run
through the `.pkg` installer.

<https://www.zabbix.com/download_agents?os=macOS>

## Agent side configuration

Configuring the Zabbix agent is similar for all installations. Whether you are on
`Linux`, `Unix`, `Windows` or `MacOS` you will always find the `zabbix_agent2.conf` file.
The parameters in this configuration file are mostly the same, regardless of the
operating system.

!!! warning "SUSE Linux"

    On SUSE Linux (SLES or OpenSUSE) 16 or higher, the Zabbix agent configuration
    file is located at `/usr/etc/zabbix/zabbix_agent2.conf` and should not be edited
    as it will be overwritten when the package is updated. 
    Alternatively, you need to create an additional configuration file in the 
    `/etc/zabbix/zabbix_agent2.conf.d/` directory and include your custom 
    configuration there. This way you can keep the original configuration file 
    intact and only add your custom settings in the new file.

For `Passive` Zabbix agent connections we have only one important parameter to
configure out of the box. The `Server=` parameter. This parameter functions as an
allowlist, where we can add IP addresses, IP ranges and DNS entries to a list.
All of the entries in this `Server=` allowlist will be allowed to make a connection
to the `Passive` Zabbix agent and collect data from it.

Edit your configuration file to include your Zabbix server (or proxy) IP address,
IP range or DNS entry.

!!! info "edit the Server= parameter"

    ```ini
    Server=127.0.0.1,192.168.46.30
    ```

As you can see in the example, I've left `127.0.0.1`. Although not required, this
can be useful in certain situations. Through the use of a comma `,` we have indicated
that both `127.0.0.1` and `192.168.46.30` are allowed to connect. If you are running
Zabbix server in HA mode or if you are using Proxy Groups, make sure to include all
entries for the Zabbix components that need to connect.

After making changes to the Zabbix agent configuration file, make sure to restart
the Zabbix Agent 2 service. On Windows systems, use the service manager, on Linux
systems use `sytemctl` to restart.

!!! info "Restart Zabbix agent"

    Linux
    ```bash
    systemctl restart zabbix-agent2
    ```

If you do not restart, the changes will not take effect.

Also make sure to check if you have a local firewall running on your system. 
If you do, to be able to use the `Passive` agent, make sure to configure the 
firewall to allow incoming connections to the service `zabbix-agent` or explicitly
open up the port `10050/tcp` to allow the Zabbix server or proxy to connect
to the agent.

## Server side configuration

On the Zabbix server side we can now create a new host to monitor. Let's call
it `zbx-agent-passive-rocky` or `zbx-agent-passive-windows` and let's add the interface.

![Zabbix Agent passive Linux host](ch04.20-passive-agent-linux-host.png){ align=left }

_4.20 Zabbix Agent passive Linux host_

For Windows it looks similar.

![Zabbix Agent passive Windows host](ch04.21-passive-agent-windows-host.png){ align=left }

_4.21 Zabbix Agent passive Windows host_

With the host added, correctly with an interface, we can now start monitoring.
To do so, let's create one `Zabbix agent` item type as an example. For your new host
`zbx-agent-passive-rocky` or `zbx-agent-passive-windows` in the Zabbix frontend,
click on `Items` and then `Create item` in the top right corner.

Let's create an item `System hostname`, making sure that if we have more system
items alphabetical sorting will group them together. For `Passive` Zabbix agent
the type `Zabbix agent` is used and we have to specific an `Interface`. We will
use the item key `system.hostname`.

![Zabbix Agent passive host item](ch04.22-passive-agent-item.png){ align=left }

_4.22 Zabbix Agent passive host item_

Do not forget to add the standard `component` tag to the item to follow the best
practice.

![Zabbix Agent passive host item tag](ch04.23-passive-agent-item-tag.png){ align=left }

_4.23 Zabbix Agent passive host item tag_

## Conclusion

We learned about the two communication methods of the Zabbix agent, `Active` and 
`Passive`. We discussed the differences between these two methods and their pros 
and cons so that you can make an informed decision on which method to use when 
in your environment.

Installing the Zabbix agent can be done with either `Zabbix agent` or 
`Zabbix agent 2`. By now `Zabbix agent 2` is recommended when available, but 
`Zabbix agent` is also fully supported. Make sure to install the Zabbix 
agent through the most easily secured method and keep it updated.

Once installed, for `Passive` communication we used the `Server=` parameter 
to keep our agent secured. We do not want everyone to be able to connect and query
this agent, even when there might still be a firewall or two in between.

Finaly, we created a host and an item to start monitoring with our `Passive` 
Zabbix agent.

## Questions

- What are the differences between `Zabbix agent` and `Zabbix agent 2`?
- What are the differences between `Passive` and `Active` Zabbix agent communication?
- Why may you want to use `Passive` mode for a long running custom script item?

## Useful URLs

- [https://www.zabbix.com/documentation/current/en/manual/concepts/agent](https://www.zabbix.com/documentation/current/en/manual/concepts/agent)
- [https://www.zabbix.com/documentation/current/en/manual/concepts/agent2](https://www.zabbix.com/documentation/current/en/manual/concepts/agent2)
- [https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages](https://www.zabbix.com/documentation/current/en/manual/installation/install_from_packages)
- [https://www.zabbix.com/documentation/current/en/manual/appendix/agent_comparison](https://www.zabbix.com/documentation/current/en/manual/appendix/agent_comparison)