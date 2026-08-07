# Network discovery and active agent auto autoregistration.

Monitoring a static infrastructure is relatively straightforward. But in today's
dynamic IT environments — with cloud instances, containers, virtual machines, and
frequently changing hardware — manually adding and maintaining hosts quickly
becomes impractical.

This chapter focuses on **Zabbix Discovery**, one of the most powerful automation
features in Zabbix. Discovery allows you to automatically detect and start
monitoring new hosts and resources with minimal manual effort.

In this chapter we cover two important discovery methods:

### Active Agent Autoregistration

Learn how to configure Zabbix Agents to register themselves automatically when
they come online. This method is particularly useful for dynamic environments
such as cloud, automated server provisioning, and large-scale deployments.

### Network Host Discovery

Explore how Zabbix can actively scan your network using IP ranges to discover
hosts, services, and available SNMP devices. This is ideal for traditional
on-premise networks and for initial inventory of unknown infrastructure.

By the end of this chapter you will understand how to combine discovery techniques
with templates and actions to create a highly automated, scalable monitoring setup
that grows with your infrastructure.
