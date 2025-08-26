# Monitoring Java Applications with JMX

One of the neat features that Zabbix offers out of the box is the ability to monitor
Java applications. To make this happen, Zabbix uses something called the
`Java Gateway`, which communicates with Java applications via the `Java Management Extensions`
JMX, for short.

`JMX` is a built-in Java technology designed specifically for monitoring and managing
Java applications and the `Java Virtual Machine` (JVM). It works through components
called `MBeans` (Managed Beans), which act like data sensors and control points.
These MBeans can expose useful information like memory usage, thread counts, and
even allow runtime configuration changes, all while the application is running.

One of the strengths of JMX is its flexibility. It supports both local and remote
access, so whether your Java app is on the same machine or halfway across the
network, Zabbix can still keep an eye on it. Combined with the Java Gateway, this
makes JMX a powerful and scalable option for monitoring Java-based environments
with minimal setup. Also JMX was an extension but is part of JAVA SE since java 5.

## Key Concepts in JMX Monitoring

Before diving into JMX monitoring with Zabbix, it helps to get familiar with a
few core building blocks that make it all work:

**Managed Beans (MBeans):**
These are the heart of JMX. MBeans are Java objects that expose useful bits of
data (called attributes) and operations (as regular methods) from your application.
Think of them as little control panels inside your Java app, you can read metrics,
tweak settings, or trigger actions through them.

**JMX Agent:**
This is the engine behind the scenes. Running inside the Java Virtual Machine (JVM),
the JMX agent connects everything together. It's what lets management tools
(like Zabbix) interact with the MBeans.

**MBean Server:**
A key part of the JMX agent, the MBean server is like a central registry where
MBeans are registered and managed. It keeps everything organized and accessible.

**Connectors:**
Want to monitor your Java app remotely? That's where connectors come in. They
let external tools connect to the JMX agent over a network. So you're not limited
to local monitoring.

**Adaptors:**
Sometimes you need JMX data to speak a different language. Adaptors convert JMX
info into formats that non-Java tools can understand, like HTTP or SNMP, making
integration easier with broader monitoring ecosystems.

## Where Does the Zabbix Java Gateway Fit in this picture?

The Zabbix Java Gateway is an external component in the Zabbix ecosystem specifically
designed to handle JMX monitoring. While it's not part of the JMX framework itself,
it acts as a JMX client that connects to your Java application’s JMX agent and
collects data from MBeans. So, if we map it to the components we just discussed,
here's how it fits:

**Category: Connectors (Client-Side)**

Why? Because the Zabbix Java Gateway is essentially a remote management application
that connects to the JMX agent running inside your Java app’s JVM. It uses JMX's
remote communication protocols (usually over RMI) to pull data from the MBean server.

Think of it like this:

- Your Java app exposes data via MBeans.
- The JMX agent and MBean server inside the JVM make that data available.
- The Zabbix Java Gateway reaches in from the outside, asks for that data,
  and passes it along to your Zabbix server.

So, while connectors in JMX terminology usually refer to the part inside the JVM
that allows remote access, the Java Gateway is the counterpart on the outside.
The client that initiates those connections.

```mermaid
flowchart LR
    subgraph JVM["Java Application (JVM)"]
        subgraph JMX["JMX Agent"]
            MBServer["MBean Server"]
            Connector["Connectors"]
            Adaptor["Adaptors"]
            M1["MBean"]
            M2["MBean"]

            MBServer --- M1
            MBServer --- M2
            MBServer --- Connector
            MBServer --- Adaptor
        end
    end

    ZS["Zabbix Server"]
    JGW["Zabbix Java Gateway"]

    ZS --> JGW
    JGW --> Connector

```

## Setup Tomcat to monitor with Zabbix.

We need a dedicated machine to test JMX monitoring with Zabbix. While you could set
this up on your Zabbix server, using a separate host more accurately reflects a
real-world monitoring scenario. For this purpose, we'll use a fresh virtual machine
running either Rocky or Ubuntu. Our goal is to install and correctly configure
Tomcat on this machine, which will serve as our JMX-enabled target.

???+ info "Setup Tomcat"

    Red hat
    ```
    dnf install tomcat
    vi /etc/sysconfig/tomcat
    ```
    Ubuntu
    ```
    ```
    Add the following config:

    ```yaml
    JAVA_OPTS="\
      -Dcom.sun.management.jmxremote=true \
      -Dcom.sun.management.jmxremote.port=8686 \
      -Dcom.sun.management.jmxremote.rmi.port=8686 \
      -Dcom.sun.management.jmxremote.authenticate=false \
      -Dcom.sun.management.jmxremote.ssl=false \
      -Djava.rmi.server.hostname=<local ip or hostname>"
    ```

### Explanation of Each Line

Let's go over the lines we just configured. They are a set of configuration options,
called **JMX options**, passed to the Java Virtual Machine (JVM) at startup. These
options enable and configure the Java Management Extensions (JMX) agent, which
allows for remote monitoring and management of the application, in this case,
Apache Tomcat.

- **`JAVA_OPTS="... "`**
  This is a variable used by Tomcat's startup scripts to hold a collection of
  command-line arguments for the Java process. The backslash (`\`) at the end of
  each line is a shell syntax feature that allows a single command or variable
  to span multiple lines, making the configuration easier to read.

- **`-Dcom.sun.management.jmxremote=true`**
  This is the main switch to enable the JMX remote agent. By setting this to `true`,
  you're telling the JVM to start the JMX management server.

- **`-Dcom.sun.management.jmxremote.port=8686`**
  This option specifies the **port number** for the JMX agent to listen on for
  incoming connections. In this case, it's set to `8686`.

- **`-Dcom.sun.management.jmxremote.rmi.port=8686`**
  This sets the port for the **RMI (Remote Method Invocation) server**. The JMX
  agent uses RMI to communicate with remote clients. In this configuration,
  both the JMX agent and the RMI server are configured to use the same port,
  simplifying the setup.

- **`-Dcom.sun.management.jmxremote.authenticate=false`**
  This disables authentication for JMX connections. For production environments,
  this should be set to `true` to require a username and password. Setting it to
  `false` is only suitable for development or testing environments.

- **`-Dcom.sun.management.jmxremote.ssl=false`**
  This disables Secure Sockets Layer (SSL) for JMX connections, meaning communication
  is not encrypted. Like authentication, this should be set to `true` in a production
  environment to secure the connection.

- **`-Djava.rmi.server.hostname=<local ip>"`**
  This is a crucial option that tells the RMI server which **IP address** to announce
  to clients. Clients will use this hostname to connect to the server. If this
  is not explicitly set, the RMI server might use the server's internal hostname
  or a loopback address (`127.0.0.1`), which would prevent external connections.
  By setting it to `<your local IP>`, you ensure that the JMX port is bound to
  the correct network interface for remote access.

???+ Note

    ``` bash
    There isn't a single, universally "standard" port for JMX that is accepted
    across all applications and vendors. The JMX specification itself does not
    define a default port, leaving it to the implementer to choose one.

    However, certain ports have become common or de facto standards within the Java
    ecosystem. The most frequently seen ports for JMX are in the high-number range,
    typically:

    - 1099: This port is a historic default for the RMI Registry, which JMX often
      uses for communication. While it's not strictly a JMX port, it's often
      associated with older JMX configurations.

    - 8686: This port is a well-accepted and formally registered port for JMX with
      the Internet Assigned Numbers Authority (IANA). The IANA service name for port
      8686 is sun-as-jmxrmi. This makes it a great choice because it's officially
      recognized and less likely to conflict with other common services.

    Why Port 8686 is a Good Choice?
    Port 8686 is a User Port (1024-49151), which means it's available for registered
    services but isn't a "well known" port that requires a special permission level
    to use. It's IANA registration as sun-as-jmxrmi makes it a safe and logical
    choice for JMX monitoring, especially when you need to standardize port assignments
    across a large infrastructure.
    ```

## Setup Zabbix to monitor JMX

Now that we've set up a JMX-enabled application, we need to configure Zabbix to
monitor it. Since Zabbix can't connect directly to JMX endpoints, we need an
intermediary tool: the **Zabbix Java Gateway**.

This gateway needs to be installed and configured on your Zabbix server or proxy,
allowing a single gateway to service multiple JMX applications. The gateway operates
in a passive mode, which means it polls data directly from your JMX application.
The Zabbix server or proxy then polls the gateway to retrieve this data, completing
the connection chain.

![Zabbix java gateway](ch04.35-jmx-zabbix.png)

_04.35 JMX Gateway_

???+ Info "Install the JAVA Gateway"

    Red Hat
    ```
    dnf install zabbix-java-gateway
    ```
    Ubuntu
    ```
    Todo
    ```

## Configuring Zabbix and the JAVA Gateway

After installing the gateway, you'll find its configuration file at `/etc/zabbix/zabbix_java_gateway.conf`.
The default `LISTEN_IP` is set to 0.0.0.0, which means it listens on all network
interfaces, though you can change this. The gateway listens on port 10052, a non
IANA registered port, which can also be adjusted using the `LISTEN_PORT` option
if needed.

The first setting we'll change is `START_POLLERS`. We need to uncomment this line
and set a value, for example, `START_POLLERS=5` to define the number of concurrent
connections. The TIMEOUT option controls network operation timeouts, while
`PROPERTIES_FILE` allows you to define or override additional key-value properties,
such as a keystore password, without exposing them in a command line.

For your Zabbix server, you'll need to update the configuration file at `/etc/zabbix/zabbix_server.conf`.

You'll need to modify three key options:

- **JavaGateway:** Uncomment this line and set its value to the IP address of
  the host running your Java gateway. This will likely be your Zabbix
  server itself, but it can be on a separate VM or proxy.

- **JavaGatewayPort:** This option should remain at the default `10052` unless
  you've changed the port in your gateway's configuration.

- **StartJavaPollers:** Uncomment and set this option to define the number of
  concurrent Java pollers the server will use. A good starting
  point is to match the number you set on the gateway, for
  example, 5.

After making the changes to `/etc/zabbix/zabbix_server.conf` and `/etc/zabbix/zabbix_java_gateway.conf`,
you need to restart the following services:

- Zabbix Java Gateway
- Zabbix Server

Restarting these two services applies the new configuration, allowing the server
to communicate with the Java Gateway and begin polling for JMX data. Also don't
forget to enable the `Zabbix Java Gateway` service.

???+ Info "Restart the services"

    RedHat and Ubuntu
    ```
    systemctl enable zabbix-java-gateway --now
    systemclt restart zabbix-server
    ```

On the application side don't forget to open the firewall so that our
`zabbix-java-gateway` can connect to our application.

`firewall-cmd --add-port=8686/tcp --permanent`

`firewall-cmd --reload`

???+ Warning

    ```
    Don't forget to place SeLinux in permissive mode before you start else the
    JAVA gateway will not work. You should fix SeLinux permissions once the setup
    is working.
    ```

## Monitoring JMX items

After having setup everything, we can now connect to our Java application's JMX port to
verify everything is working.

For this, we can use JConsole, a monitoring tool that comes with the Java Development
Kit (JDK). Another great option is VisualVM, which offers a more visual and feature
rich experience. You can download it from [https://visualvm.github.io/download.html](https://visualvm.github.io/download.html).

Start your preferred application and connect to our JMX port on 8686.

![Jconsole](ch04.36-jconsole.png)

_04.36 Jconsole_

After a successful login you should be greeted with a screen like this. Were you
have a tree view overview of all the Mbeans we can use to gather information
from.

![ch04.37 Succesful login](ch04.37-jconsole-mbeans-tree.png)

_04.37 Login screen_

Before we can do this we need to create a new host in our Zabbix server. Let's
go to `Data collection` - `Hosts` and click on `Create host` in the upper right
corner. Use the following settings to create our host:

- Hostname : Tomcat
- Host groups: JMX
- Interfaces: JMX
    - IP address: IP of your Tomcat server
    - Port : 8686 or the port you specified in your Tomcat configuration.

Press the `Add` button when ready.

???+ Note

    ```
    It seems weird that we not specify the JavaGateway here but it's actually
    normal. Zabbix knows from its configuration file where the gateway is. So we
    need to specify the IP and the PORT of the JAVA application here that we would
    like to monitor.
    ```

### Create our first item

On our host Tomcat create a new item and add the following information.

- *Name:* requestCount
- *Type:* JMX Agent
- *Key:* jmx["Catalina:type=GlobalRequestProcessor,name=\"http-nio-8080\"", "requestCount"]
- *Type of information:* Numeric(unsigned)
- *Host interface:* The JMX interface we just created on our host.

![JMX Item](ch04.38-jmx-requestCount-item.png)

_ch04.38 JMX item_

The rest we can keep as is. Before you safe the item you can press the `Test`
button. When you press `Get value` or `Get value and test` you should get some
information back in the value field. This indicates our items works so you can
safe it.

So this was easy but how did we actually go to the item key ? Let me show you.

Open your Jconsole and in the Mbeans tab go to `Catalina` -
`GlobalRequestProcessor` - `http-nio-8080`. In the field on the right you will
see ObjectNAme. This is actually the name you need to copy to paste into the
item key. `Catalina:type=GlobalRequestProcessor,name="http-nio-8080"` the only
issue with this key and that's why I have chose this key is that the key needs
to be quoted with " " but we already have double " in the name so we have to
escape them with a \. So the result will be
`jmx["Catalina:type=GlobalRequestProcessor,name=\"http-nio-8080\""]` but this is
not complete yet we still have to point to the attribute we like to monitor.
You can choose one of the many attributes maxTime, requestCount, bytesReceived,
.... and add it at the end of our key between "" separated with a comma.

`jmx["Catalina:type=GlobalRequestProcessor,name=\"http-nio-8080\"","requestCount"]`

![requestCount item](ch04.39-jconsole-requestCount.png)

_04.39 requestCount item_

The `java.lang.management.Memory` Mbean is also a nice example it has an
attribute `HeapMemoryUsage`. This MemoryUsage object is an instance of CompositeData,
a special type in JMX used to represent complex data structures.

Therefore, you're not calling init, used, committed, or max directly on the MBean
itself, but rather on the MemoryUsage object that is returned when you access the
HeapMemoryUsage MBean attribute.

For this we would need an item key like `jmx["java.lang:type=Memory","HeapMemoryUsage.max"]`.

![](ch04.40-jconsole-HeapMemory.Max.png)

_04.40 HeapMemoryUsage

To get the tabular data overview double click on the `value` after the
`attribute value` `HeapMemoryUsage`.

Zabbix has 3 `item keys` that it can use with JMX we use the jmx[] key but there
is also jmx.get[] and jmx.discovery[] both are used with LLD but the jmx.get can
also be used as a normal item key with preprocessing.

### Making use of jmx.get[]

jmx.get[] Return a JSON array with MBean objects or their attributes. Compared
to jmx.discovery it does not define LLD macros but it can be used for LLD.

We will cover these items in the LLD Chapter of this book. But to give you an
idea already of what jmx.get does, as it can be used with dependent items without LLD.

you could create an item like `jmx.get[attributes,"*:type=GarbageCollector,name=PS MarkSweep"]`
This would return a JSON with all the info about the attributes of our garbage
collector `PS MarkSweep` like this:

``` json
[
  {
    "name": "CollectionCount",
    "description": "java.lang:type=GarbageCollector,name=PS MarkSweep,CollectionCount",
    "type": "java.lang.Long",
    "value": "0",
    "object": "java.lang:type=GarbageCollector,name=PS MarkSweep"
  },
  ...
  ...
  ...
  ...
  {
    "name": "ObjectName",
    "description": "java.lang:type=GarbageCollector,name=PS MarkSweep,ObjectName",
    "type": "javax.management.ObjectName",
    "value": "java.lang:type=GarbageCollector,name=PS MarkSweep",
    "object": "java.lang:type=GarbageCollector,name=PS MarkSweep"
  }
]
```

## Conclusion

## Questions

## Useful URLs

- [https://www.youtube.com/watch?v=aKGYa6Y9r60&t=87s](https://www.youtube.com/watch?v=aKGYa6Y9r60&t=87s)
- [https://docs.oracle.com/javase/1.5.0/docs/guide/management/agent.html](https://docs.oracle.com/javase/1.5.0/docs/guide/management/agent.html)
- [https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/jmx_monitoring](https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/jmx_monitoring)
