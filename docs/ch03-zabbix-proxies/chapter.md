# Proxies and the Web services component

Proxies are often regarded as an advanced topic in Zabbix, but in reality,
they are a fundamental part of many installations and one of the first components
we set up for numerous customers. In this chapter, we'll make proxies the third
subject we cover, encouraging you to consider them from the very beginning of your
Zabbix journey.

We'll start with a basic proxy setup, providing straightforward steps to get you
up and running quickly. Then, we'll take a deep dive into the mechanics of proxies
how they operate within the Zabbix ecosystem, their benefits, and the critical
role they play in distributing monitoring load and enhancing system scalability.

Understanding proxies from the start can significantly improve your architecture,
especially in distributed or large scale environments. Whether you're new to Zabbix
or looking to refine your existing setup, this chapter will offer valuable insights
into why proxies should be an integral part of your monitoring strategy from the start.

By the end, you'll not only know how to set up a basic proxy but also have a clear
understanding of their underlying workings and strategic advantages,
ensuring you make informed decisions as you scale your Zabbix installation.

## Proxy requirements
If you like to setup a few proxies for test or in your environment you will need
a few Linux hosts to install the Proxies on. Proxies are also available in containers
so a full VM is not needed. However here we will use a VM so we can show you how to
install a proxy. Don't worry we will cover containers as well. When it comes to
proxies they are very lightweight however since Zabbix 4.2 Proxies are able to
do Item value preprocessing and this can use a lot of CPU power. So the number
of CPUs and memory will depends on how many machines you will monitor and how many
preprocessing rules you have on your hosts.
