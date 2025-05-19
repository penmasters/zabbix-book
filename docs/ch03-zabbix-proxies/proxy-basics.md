# Proxy basics

In this chapter we will cover the basic needs for our proxies. We won't pay
attention to active or passive proxies yet this is something we cover later
in the next chapters.

## Proxy requirements
If you like to setup a few proxies for test or in your environment you will need
a few Linux hosts to install the Proxies on. Proxies are also available in containers
so a full VM is not needed. However here we will use a VM so we can show you how to
install a proxy. Don't worry we will cover containers as well. When it comes to
proxies they are very lightweight however since Zabbix 4.2 Proxies are able to
do Item value preprocessing and this can use a lot of CPU power. So the number
of CPUs and memory will depends on how many machines you will monitor and how many
preprocessing rules you have on your hosts.

So in short a Zabbix proxy can be used to:

- Monitor remote locations
- Monitor locations that have unreliable connections
- Offload the Zabbix server when monitoring thousands of devices
- Simplify the maintenance and management


???+ note
     Imagine that you need to restart your Zabbix server and that all proxies start
     to push the data they have gathered during the downtime of the Zabbix server.
     This would create a huge amount of data being sent at once to the Zabbix server
     and bring it to its knees in no time. Since Zabbix 6 Zabbix has added protection
     for overload. When Zabbix server history cache is full the history cache write
     access is being throttled. Zabbix server will stop accepting data from proxies
     when history cache usage reaches 80%. Instead those proxies will be put on a
     throttling list. This will continue until the cache usage falls down to 60%.
     Now server will start accepting data from proxies one by one, defined by the
     throttling list. This means the first proxy that attempted to upload data during
     the throttling period will be served first and until it's done the server will
     not accept data from other proxies.

This table gives you an overview of how and when throttling works in Zabbix.

|History write cache usage 	| Zabbix server mode	| Zabbix server action 	|
|----                       |----                 |----                   |
|Reaches 80%                |Wait                 |Stops accepting proxy data, but maintains a throttling list (prioritized list of proxies to be contacted later).|
|Drops to 60%               |Throttled            |Starts processing throttling list, but still not accepting proxy data.	|
|Drops to 20%	              |Normal               |Drops the throttling list and starts accepting proxy data normally.|


### Active versus Passive proxy

Zabbix proxies have been available since Zabbix 1.6, at that time they where available
only as what we know today as `Active proxies`. Active means that the proxy will
initiate the connection by itself to the Zabbix Server. Since version 1.8.3 passive
proxies where introduced. This allowed the server to connect to the proxy. As mentioned
before Zabbix agents can be both active and passive however proxies cannot be both
so we have to choose the way of the communication when we install a proxy. Just
remember that choosing the proxy mode `active` or `passive` has no impact on how
Zabbix agents can communicate with our proxy. It's perfectly fine to have an `active proxy`
and a `passive agent` working together.

???+ warning
     Before you continue with the setup of your active or passive proxy make sure
     your OS is properly configure like explained in our chapter `Getting Started` 
     => `System Requirements`. As it's very important to have your firewall and
     time server properly configured.
