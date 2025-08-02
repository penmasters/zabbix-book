# Triggers
In the previous chapter we have been hard at work to collect our data from various monitoring targets. Because of that our Zabbix environment is filled with useful and important information about our IT infrastructure. However, when you want to know something about your various different devices and applications you have to go through a mountain of data. This is where triggers come in.

Triggers in Zabbix work as a way for us to collect a mountain worth of data, while being alerted about what's important. It allows us to set our own expressions that will define exactly when Zabbix should log and alert us about something happening with our data. The easiest example being something like a CPU going to 90% utilization.


## Preparing the environment
In the previous chapter we created some hosts to monitor the active Zabbix agent, which are great for some example triggers. We created this host under the hostname `zbx-agent-active-rocky` or `zbx-agent-active-windows`, either should work for the example. We also should already have an item on this host to monitor the `Zabbix agent ping` with item key `agent.ping`. Let's add one item to our `zbx-agent-active-*` host, specifically to monitor the CPU load in percentage. 

![Zabbix Agent active CPU util](ch05.1-cpu-util-item){ align=center }

_5.1 Zabbix Agent active CPU util item_

Let's not forget to add the tag.

![Zabbix Agent active CPU util tag](ch05.1-cpu-util-item-tag){ align=center }

_5.2 Zabbix Agent active CPU util item tag_





## Conclusion

## Questions

## Useful URLs
