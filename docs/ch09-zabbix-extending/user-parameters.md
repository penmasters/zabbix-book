---
description: |
    UserParameter is a quick way to extend agent to collect custom metrics.
tags: [advanced]
---

# User Parameters

## What is `UserParameter` and when to use it?

`UserParameter` is one of the ways to tell Zabbix agent that you want to
collect something custom.

"Custom" in this context of data collection means something that is not already
provided as an item by Zabbix agent. So before implementing anything custom, be
sure that Zabbix doesn't provide it already out-of-the-box - either directly or
in combination with some other Zabbix native features, such as preprocessing or
dependent items. For example, you would not use it to measure CPU load, since
Zabbix agent has `system.cpu.load[]` item. Or you would not use it for simply
getting one line from some file because there is `vfs.file.contents[]` which
you can combine with preprocessing to extract specific line.

Configuring `UserParameter` is pretty straightforward and benefits can be
enormous, depending on your abilities to correctly collect and structure the
data of your interest. In the end, it is something that Zabbix agent executes
in order to collect data. It can be simple one liner or some sophisticated
sequence of commands. So it is highly related to one's ability to write those
"to be executed" commands in neat and efficient manner.

Main benefit of `UserParameter` is that logic behind data collection can be
absolutely anything. You have total freedom, there is no dependency on specific
technologies, programming languages or frameworks. There is basically one main
requirement – Zabbix agent should be able to execute whatever you provide for
it as a command and it should produce some (hopefully meaningful) output.

???+ tip
    `UserParameter` can be used not only to collect data, but also as a custom
    LLD (Low level discovery) rule.

There are some other methods that allow you to collect custom data:

- `zabbix_sender`
- Zabbix API (via `history.push`)
- `system.run[]` item

Those are all great ways and have some clear use cases when you want to use each
of them. However, `UserParameter` is probably the most common and most widely
adopted way. It is kind of a perfect balance between simplicity in setting it
up and flexibility it brings. For example:

- once setting `UserParameter` up you don't have to care about running it and
also about checking interval. Zabbix agent will take care of running it and
you'll set checking frequency in Zabbix GUI once creating item there (opposite
to `zabbix_sender` case which is kind of a standalone in relation to Zabbix
server, thus you have to take care of running it on your own)
- there is no need to take care of communication with Zabbix server itself or
knowing your item ID (opposite to Zabbix API approach)

## Creating a `UserParameter`

`UserParameter` is available for any OS where Zabbix agent can be installed. In
the following section we will talk about configuring it under Linux. However,
same main principles of configuring `UserParameter` on other systems are also
applicable.

### Most simple implementation

In most simple case, Zabbix agent configuration could be enriched with some
`UserParameter` directives directly in its main configuration. It has this
section in `zabbix_agent.conf`:

???+ info "Default `UserParameter` section from `zabbix_agent.conf`"

    ```
    ### Option: UserParameter
    #       User-defined parameter to monitor. There can be several user-defined parameters.
    #       Format: UserParameter=<key>,<shell command>
    #       See 'zabbix_agentd' directory for examples.
    #
    # Mandatory: no
    # Default:
    # UserParameter=

    UserParameter=my.user.parameter,echo "Hello World"
    ```

### Most simple implementation: the better way

However, you should avoid such approach as above and better stick to keeping
your `UserParameter` definitions in separate files under `zabbix_agentd.d` (or
some other directory of your choice) for Zabbix agent to include:

???+ info "Default `Include` section from `zabbix_agent.conf`"

    ```
    ### Option: Include
    #       You may include individual files or all files in a directory in the configuration file.
    #       Installing Zabbix will create include directory in /usr/local/etc, unless modified during the compile time.
    #
    # Mandatory: no
    # Default:
    # Include=

    Include=/etc/zabbix/zabbix_agentd.d/*.conf
    ```

???+ note

    For "Zabbix agent 2" this default `Include` directory is
    `Include=/etc/zabbix/zabbix_agent2.d/*.conf`

Here is an example of such `.conf` file:

```bash
binary@binary:~$ cat /etc/zabbix/zabbix_agentd.d/userparameter_book.conf
UserParameter=my.user.parameter,echo "Hello World"
binary@binary:~$
```

This way you have much cleaner approach of creating `UserParameter`
definitions. You can group them logically, you are not affected by main
configuration changes after Zabbix agent version upgrades, etc.

Please note, that you can specify as many `UserParameter` lines as you wish in
one such `.conf` file. That is how you can group them - by splitting into
different files if they have something in common.

### Most simple implementation: the best way

In case your `UserParameter` is not a one liner or just a few commands, you
should better store it as a script and define it in a way that this script is
being called, not a long sequence of commands. Technically script is also a
sequence of commands, but much easier to maintain, especially as it grows.

So our final first `UserParameter` configuration could be such:

```bash
binary@binary:~$ cat /etc/zabbix/zabbix_agentd.d/userparameter_book.conf
UserParameter=my.user.parameter,/opt/scripts/binary/my.sh
binary@binary:~$ cat /opt/scripts/binary/my.sh
#!/bin/bash

echo "Hello World"

exit 0
binary@binary:~$
```

???+ warning

    IMPORTANT! You must restart Zabbix agent after adding new `UserParameter`
    (or use `zabbix_agentd -R userparameter_reload`)

### Creating item on Zabbix server side

So we just learned about adding `UserParameter` on Zabbix agent side. But in
order for it to be collecting data, Zabbix server must also know about it.
Good thing is that instructing Zabbix server is really easy. It is not different
from creating any other item. The only difference is that you have to pay
attention to item key - it must match with the one you just configured on agent
side.

So just hit "Create item" on your host (or, of course, better on your template)
and fill in all the needed fields:

![New Custom Item](ch09-user-parameters-new-item.png)

Depending on the nature of the data that you are collecting, set correct "Type
of information" as well as needed "Update interval". Once you are finished,
you will see data being collected:

![New Custom Item - Result](ch09-user-parameters-new-item-result.png)

### Creating flexible `UserParameter`

Sometimes it's useful to have ability to pass some parameters for your
`UserParameter`. To be able to do so, configuration is a bit different. Once
creating `UserParameter`, you must use `[*]` along with your custom item key.
For example, let's create an item which will draw sine wave. It will accept
several parameters so we can draw different waves:

```bash
binary@binary:~$ cat /etc/zabbix/zabbix_agentd.d/userparameter_sin.conf
UserParameter=sin[*],/opt/scripts/binary/sin.sh $1 $2 $3 $4
binary@binary:~$ cat /opt/scripts/binary/sin.sh
#!/bin/bash

# $1 - frequency multiplier (times_pi)
# $2 - amplitude
# $3 - phase shift in multiples of pi
# $4 - period length in seconds

times_pi="$1"
amplitude="$2"
time_shift="$3"
period="$4"

pi=3.141592653589793

now=$(( $(date +%s) % period ))

value=$(bc -l <<EOF
scale=14
${amplitude} * s( (${time_shift} * ${pi}) + 2 * ${pi} * ${times_pi} * ${now} / ${period} )
EOF
)

printf "%.8f\n" "${value}"

exit 0
binary@binary:~$
```

So now once creating items, we can provide parameters in `[]` part of item
keys, like:

![New Custom Item](ch09-user-parameters-new-flexible-item.png)

Given that we want multiple different waves, we will clone such item with
different sets of parameters and end up in having all of them being collected:

![New Custom Item - Result](ch09-user-parameters-new-flexible-item-result.png)

???+ note

    If you use `awk` in `UserParameter`, pay attention to using double dollar
    sign `$$`, so that positional references remain unaltered, for example:
    `UserParameter=demo.awk[*],echo $1 $2 | awk '{print $$2}'`

## Tips and tricks

*Test before going live*

As mentioned, you need to restart Zabbix agent after adding new checks. If you
add them incorrectly, agent will stop and fail to start once being restarted,
thus better idea is to check it in advance with `zabbix_agentd -t`. For
example, here we have duplicated entries (same item key defined twice):

```bash
zabbix@binary:/$ cat /etc/zabbix/zabbix_agentd.d/userparameter_book.conf
UserParameter=my.user.parameter,echo "Hello World"
UserParameter=my.user.parameter,echo "Hello World 2"
zabbix@binary:/$ zabbix_agentd -t my.user.parameter
zabbix_agentd [1505972]: ERROR: cannot load user parameters: user parameter "my.user.parameter,echo "Hello World 2"": key "my.user.parameter" already exists
zabbix@binary:/$
```

After removing the duplicate and checking once again, we will get value for the
defined item:

```bash
zabbix@binary:/$ cat /etc/zabbix/zabbix_agentd.d/userparameter_book.conf
UserParameter=my.user.parameter,echo "Hello World"
zabbix@binary:/$ zabbix_agentd -t my.user.parameter
my.user.parameter                             [t|Hello World]
zabbix@binary:/$
```

*Make it executable and reachable*

If `UserParameter` is a script and your environment is *nix, don't forget to
make it executable. Also, you will most likely craft your script under some
different user than the one Zabbix agent is running under (user `zabbix` by
default), so make sure this very user can run it (e.g. permissions to reach
script itself or do anything that is being done inside the script). Best way to
test it is to switch to this user and try to run it. For example, here we
forget that one of the directories in path where our script lives is not
reachable by anyone except us. So, it might look like this script is working,
but it is working just for us:

```bash
binary@binary:~$ /opt/scripts/binary/my.sh
Hello World
binary@binary:~$ sudo -u zabbix bash -c "cd / && exec bash"
zabbix@binary:/$ /opt/scripts/binary/my.sh
bash: /opt/scripts/binary/my.sh: Permission denied
zabbix@binary:/$ whoami
zabbix
zabbix@binary:/$ exit
exit
binary@binary:~$ namei -mo /opt/scripts/binary/my.sh
f: /opt/scripts/binary/my.sh
 drwxr-xr-x root   root   /
 drwxr-xr-x root   root   opt
 drwxrwxrwt root   root   scripts
 drwxrwx--- binary binary binary
 -rwxrwxr-x binary binary my.sh
binary@binary:~$
```

*Be as fast as possible*

Always pay attention to how long it takes for your `UserParameter` to collect
data. If it runs for too long you might hit Zabbix agent timeout. This timeout
is configurable on item level, so you can adjust it:

![Custom Item - Timeout](ch09-user-parameters-timeout.png)

Also, be wise with number of such items. If you have many, especially more
heavy ones, observe if it doesn't affect overall agent (or even host itself!)
performance in collecting data. If checks are set to be in "active" mode and
run for relatively long time, they will eventually start blocking other active
checks, because active checks (on classic Agent, not Agent 2) are not processed
in parallel.

*Use dependent items for splitting*

If there are many similar data points to be collected, avoid having separate
`UserParameter` for each of them. Better have one master "text" type of item
with some structured format and apply dependent items on top.

*Using UnsafeUserParameters*

Some symbols are not allowed by default to be passed in arguments for the
`UserParameter`.

These are ``\ ' " ` * ? [ ] { } ~ $ ! & ; ( ) < > | # @``, plus newline
character.

If you really need it, you can enable it by setting `UnsafeUserParameters=1` in
Zabbix agent configuration.

One good example when you would like to enable it is if you want to pass
regular expressions as parameters. Their syntax often contains symbols in this
forbidden list.

## Conclusion

When setting up monitoring in whatever area, you will inevitably deal with a
need to monitor something "custom". Zabbix offers multiple ways to achieve it,
`UserParameter` being one of the most widely used.

In this section you have learned how to create simple custom checks, as well as
something more advanced.

As long as you are able to write some code which fulfils your custom needs,
Zabbix will be there to help you collect and visualize it!

## Questions

- Can you only use shell scripts as `UserParameter` under Linux?
- Is it possible to pass some custom parameters for your `UserParameter`?
- Your have a `UserParameter` that can produce both positive and negative
numbers as an output. Which "Type of information" will you choose once creating
item?

## Useful URLs

- [https://www.zabbix.com/documentation/current/en/manual/config/items/userparameters](https://www.zabbix.com/documentation/current/en/manual/config/items/userparameters)
- [https://blog.zabbix.com/extending-zabbix-the-power-of-scripting/](https://blog.zabbix.com/extending-zabbix-the-power-of-scripting/)
