# HA Setup

In this section, we will set up Zabbix in a High Availability (HA) configuration.
This feature, introduced in Zabbix 6, is a crucial enhancement that ensures continued
monitoring even if a Zabbix server fails. With HA, when one Zabbix server goes down,
another can take over seamlessly.

For this guide, we will use two Zabbix servers and one database, but the setup allows
for adding more zabbix servers if necessary.

![HA-Setup](./ha-setup/ch01-HA-setup.png)

It's important to note that Zabbix HA setup is straightforward, providing redundancy
without complex features like load balancing.

Just as in our basic configuration, we will document key details for the servers
in this HA setup. Below is the list of servers and some place to add their
respective IP addresses for your convenience :

|Server           | IP Address      |
|:----            |:-----           |
| Zabbix Server 1 |                 |
| Zabbix Server 2 |                 |
| Database        |                 |
| Virtual IP      |                 |

???+ note
    Our database (DB) in this setup is not configured for HA. Since it's not a
    Zabbix component, you will need to implement your own solution for database
    HA, such as a HA SAN or a database cluster setup. A DB cluster configuration
    is out of the scope of this guide and unrelated to Zabbix, so it will not be
    covered here.

## Installing the Database

Refer to the [*Basic Installation*](basic-installation.md) chapter for detailed
instructions on setting up the database. That chapter provides step-by-step guidance
on installing either a PostgreSQL or MariaDB database on a dedicated node running
Ubuntu or Rocky Linux. The same installation steps apply when configuring the
database for this setup.

## Installing the Zabbix cluster

Setting up a Zabbix cluster involves configuring multiple Zabbix servers to work
together, providing high availability. While the process is similar to setting up
a single Zabbix server, there are additional configuration steps required to
enable HA (High Availability).

Add the Zabbix Repositories to your servers.

First, add the Zabbix repository to both of your Zabbix servers:

Redhat

```bash
# rpm -Uvh https://repo.zabbix.com/zabbix/7.2/release/rocky/9/noarch/zabbix-release-latest-7.2.el9.noarch.rpm
# dnf clean all
```

Ubuntu

```bash
# wget https://repo.zabbix.com/zabbix/7.2/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.2+ubuntu24.04_all.deb
# dpkg -i zabbix-release_latest_7.2+ubuntu24.04_all.deb
# apt update
```

Once this is done we can install the zabbix server packages.

Redhat

```bash
# dnf install zabbix-server-pgsql -y
or if your database is MariaDB
# dnf install zabbix-server-mysql -y
```

Ubuntu

```bash
# apt install zabbix-server-pgsql -y
or if your databqse is MariaDB
# apt install zabbix-server-mysql -y
```

### Configuring Zabbix Server 1

Edit the Zabbix server configuration file,

```bash
# vi /etc/zabbix/zabbix_server.conf
```

Update the following lines to connect to the database:

```bash
DBHost=<zabbix db ip>
DBName=<name of the zabbix DB>
DBUser=<name of the db user>
DBSchema=<db schema for the PostgreSQL DB>
DBPassword=<your secret password>
```

Configure the HA parameters for this server:

```bash
HANodeName=zabbix1 (or choose a name you prefer)
```

Specify the frontend node address for failover scenarios:

```bash
NodeAddress=<Zabbix server 1 ip>:10051
```

### Configuring Zabbix Server 2

Repeat the configuration steps for the second Zabbix server. Adjust the `HANodeName`
and `NodeAddress` as necessary for this server.

### Starting Zabbix Server

After configuring both servers, enable and start the zabbix-server service on each:

```bash
# systemctl enable zabbix-server --now
```

### Verifying the Configuration

Check the log files on both servers to ensure they have started correctly and
are operating in their respective HA modes.

On the first server:

```bash
# grep HA /var/log/zabbix/zabbix_server.log
```

You should see:

```bash
22597:20240309:155230.353 starting HA manager
22597:20240309:155230.362 HA manager started in active mode
```

On the second server (and any additional nodes):

```bash
# grep HA /var/log/zabbix/zabbix_server.log
```

You should see:

```bash
22304:20240309:155331.163 starting HA manager
22304:20240309:155331.174 HA manager started in standby mode
```

Your Zabbix cluster should now be set up with high availability, ensuring continuous
monitoring even if one of the servers fails.

## Installing the frontend

Before proceeding with the installation and configuration of the web server, it
is essential to install Keepalived. Keepalived enables the use of a Virtual IP
(VIP) for frontend services, ensuring seamless failover and service continuity.
It provides a robust framework for both load balancing and high availability,
making it a critical component in maintaining a resilient infrastructure.

### Setting up keepalived

So let's get started. On both our servers we have to install keepalived.

Redhat

```bash
# dnf install keepalived
```

Ubuntu

```bash
todo
```

Next, we need to modify the Keepalived configuration on both servers. While the
configurations will be similar, each server requires slight adjustments. We will
begin with Server 1. To edit the Keepalived configuration file, use the following
command:

Redhat

```bash
# vi /etc/keepalived/keepalived.conf
```

Ubuntu

```bash
todo
```

Delete all content in the file and replace it with the following lines:

```bash
vrrp_track_process track_nginx {
    process nginx
    weight 10
}

vrrp_instance VI_1 {
    state MASTER
    interface enp0s1
    virtual_router_id 51
    priority 244
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 12345
    }
    virtual_ipaddress {
        192.168.0.135
    }
    track_process {
         track_nginx
      }
}
```

???+ warning
    Replace `enp0s1` with the interface name of your machine and replace the `password`
    with something secure. For the virual_ipaddress use a free IP from your network.
    This will be used as our VIP.

We can now do the same modification on our `second` Zabbix server. Delete everything
again in the same file like we did before and replace it with the following lines:

```bash
vrrp_track_process track_nginx {
      process nginx
      weight 10
}

vrrp_instance VI_1 {
    state BACKUP
    interface enp0s1
    virtual_router_id 51
    priority 243
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 12345
    }
    virtual_ipaddress {
        192.168.0.135
    }
    track_process {
         track_nginx
      }
}
```

Just as with our 1st Zabbix server, replace `enp0s1` with the interface name of
your machine and replace the `password` with your password and fill in the
virual_ipaddress as used before.

This ends the configuration of keepalived. We can now continue adapting the frontend.

### Install and configure the frontend

On both servers we can run the following commands to install our web server and the
zabbix frontend packages:

RedHat

```bash
# dnf install nginx zabbix-web-pgsql zabbix-nginx-conf
```

Ubuntu

```bash
todo
```

Additionally, it is crucial to configure the firewall. Proper firewall rules ensure
seamless communication between the servers and prevent unexpected failures.
Before proceeding, verify that the necessary ports are open and apply the required
firewall rules accordingly.

RedHat

```bash
# firewall-cmd --add-service=http --permanent
# firewall-cmd --add-service=zabbix-server --permanent
# firewall-cmd --reload
```

Ubuntu

```bash
todo
```

With the configuration in place and the firewall properly configured, we can now
start the Keepalived service. Additionally, we should enable it to ensure it
automatically starts on reboot. Use the following commands to achieve this:

RedHat

```bash
# systemctl enable keepalived nginx --now
```

Ubuntu

```bash
todo
```

### Configure Zabbix frontend

todo

## Conclusion

In this chapter, we have successfully set up a high-availability (HA) Zabbix
environment by configuring both the Zabbix server and frontend for redundancy.
We first established HA for the Zabbix server, ensuring that monitoring services
remain available even in the event of a failure. Next, we focused on the frontend,
implementing a Virtual IP (VIP) with Keepalived to provide seamless failover and
continuous accessibility.  

Additionally, we configured the firewall to allow Keepalived traffic and ensured
that the service starts automatically after a reboot. With this setup, the Zabbix
frontend can dynamically switch between servers, minimizing downtime and improving
reliability.  

While database HA is an important consideration, it falls outside the scope of
this setup. However, this foundation provides a robust starting point for building
a resilient monitoring infrastructure that can be further enhanced as needed.

## Questions

## Useful URLs

- <https://www.redhat.com/sysadmin/advanced-keepalived>
- <https://keepalived.readthedocs.io/en/latest/introduction.html>
