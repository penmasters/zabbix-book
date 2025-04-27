# Simple checks
What would a Zabbix book be without setting up the actual monitoring itself, because in 
the end a monitoring system is all about collecting data through various different protocols. 

Simple checks are one (or actually several) of such protocols. Zabbix has a bunch of built-in 
checks we can do, executed from the Zabbix server or proxy towards our monitoring targets. The simple 
checks contain protocol checks such as `ICMP Ping`, `TCP/UDP` but also built in `VMware` monitoring.

Without further ado, let's set up our first items. Please keep in mind that we will be building
everyhting on a host level for now. Check out Chapter 06 to learn how to do this properly on a template.

## ICMP Ping


## TCP Ports