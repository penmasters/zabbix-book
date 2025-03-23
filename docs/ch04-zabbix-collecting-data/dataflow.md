# Dataflow
The Zabbix dataflow is a concept that is meant to guide us through the various different stages of building up our monitoring system. In the end, when building a Zabbix environment we want to achieve a few things:

- Collected metrics are stored, can be easily found and are visualised
- Problems are created from our data and shown in the frontend
- We take action on important problems by sending a message or executing commands

Those three parts of the Zabbix dataflow in our Zabbix environment can be easily identified as:

- Items 
- Triggers
- Actions

But when we look at items specifically, it's also possible to alter our data before storing the metrics in Zabbix. This is something we do with a process called pre-processing, which will take the collected data and change it before storing it in the Zabbix database. Our dataflow in the end then looks as such:

![overview](./dataflow/dataflow1.png){ align=left }
*1.1 Zabbix basic dataflow*

Now that we have identified what parts to look at, let's dive a bit deeper into what each of those parts does. 