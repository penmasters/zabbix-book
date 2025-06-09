# Running Proxies as containers

As discussed in the previous section, Zabbix proxies offer a lightweight and efficient
solution for distributed monitoring. Leveraging SQLite as their backend database,
they are inherently flexible and portable, making them well-suited for deployment
in containerized environments. This chapter provides a step-by-step guide on deploying
a Zabbix proxy within a container, outlining configuration options and best practices
for optimal performance and maintainability.

## Setting up containers under RedHat

We will begin by demonstrating how to set up containerized environments on Red Hat-based
systems using Podman. Podman is the recommended container engine on Red Hat distributions
and offers several advantages over Docker.

Firstly, Podman enhances security by supporting rootless containers, allowing containers
to run under non-privileged user accounts. Secondly, it integrates seamlessly with
SELinux, enabling robust access control and policy enforcement. Thirdly, Podman
works natively with systemd, which facilitates container lifecycle management through
systemd units and quadlets.

For this setup, you will need a virtual machine (VM) where we will install Podman
and deploy the Zabbix proxy container. This container will then be configured to
communicate with your Zabbix server.

### Add the proxy to the zabbix frontend

![Add the proxy](ch03-container-proxy-new.png)

_3.9 Add proxy
to frontend_

To keep the configuration straightforward, we will deploy an active Zabbix proxy.
In this case, only two parameters need to be configured: the proxy's hostname
(as defined in the Zabbix frontend) and the proxy’s IP address for communication
with the Zabbix server.

### Create the podman setup

Next, we begin configuring Podman on the host system where the Zabbix proxy container
will be installed and managed.

```yaml
dnf install podman -y
dnf install policycoreutils-python-utils -y
useradd podman
su - podman
```

Still as user podman create the following folders

```yaml
mkdir -p ~/.local/share/containers
```

and

```yaml
mkdir -p ~/.config/containers/systemd/
```

Once done return to user `root` and execute the following commands.

```yaml
semanage fcontext -a -e /var/lib/containers /home/podman/.local/share/containers
```

This command adds a SELinux file context mapping by creating an equivalence (-e)
between the default container storage directory /var/lib/containers and the user’s
Podman container storage path /home/podman/.local/share/containers. Essentially,
it tells SELinux to treat files in the user's container storage the same way it
treats files in the default system container storage, ensuring proper access
permissions under SELinux policy.

```yaml
restorecon -R -v /home/podman/.local/share/containers
```

After defining new SELinux contexts, this command recursively (-R) applies
the correct SELinux security contexts to the files in the specified directory.
The -v flag enables verbose output, showing what changes are made. This ensures
that all files in the container storage directory have the correct SELinux labels
as defined by the previous semanage commands.

```yaml
loginctl enable-linger podman
```

This command enables “linger” for the user podman. Linger allows user services
(such as containers managed by systemd) to continue running even when the user
is not actively logged in. This is useful for running Podman containers in the
background and ensures that containerized proxies or other services remain active
after logout or system reboots.

```yaml
echo export XDG_RUNTIME_DIR="/run/user/$(id -u podman)" >> ~/.bash_profile
```

This line ensures that the XDG_RUNTIME_DIR environment variable is correctly set
for the podman user. This variable points to the location where user-specific runtime
files are stored, including the systemd user session bus. Setting it is essential
for enabling systemctl --user to function properly with Podman-managed containers.

### Prepare the Proxy config

The next step is to create a .container unit file for our Quadlet setup. This
file should be placed in the directory ~/.config/containers/systemd/. For example,
we will create a file named `zabbix-proxy-sqlite.container`, which will define the
configuration for running the Zabbix proxy container under systemd using Podman.

```yaml
su - podman
vi ~/.config/containers/systemd/zabbix-proxy-sqlite.container
```

```ini
[Unit]
Description=ZabbixProxy

[Container]
Image=docker.io/zabbix/zabbix-proxy-sqlite3:trunk-centos
ContainerName=ZabbixProxySqlite-Quadlet
AutoUpdate=registry
EnvironmentFile=ZabbixProxy.env
PublishPort=10051:10051

[Service]
Restart=always

[Install]
WantedBy=default.target
```

The container image for the Zabbix proxy using SQLite can be sourced from Docker
Hub. Specifically, we will use the image tagged trunk-centos, which is maintained
by the official Zabbix project. This image can be found at:

[https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3/tags?name=centos](https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3/tags?name=centos)

A complete list of available image tags, including different versions and operating
system bases, is available on the image’s main page:

[https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3](https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3)

For our purposes, the trunk-centos tag provides a CentOS-based container image
that is well-suited for testing and development environments, and it includes all
necessary components to run the Zabbix proxy with SQLite.

In addition to the .container unit file, we also need to create an environment
file that defines the configuration variables for the container. This file must
reside in the same directory as the .container file `~/.config/containers/systemd/`
and should be named `ZabbixProxy.env`, as referenced in our .container configuration.

This environment file allows us to override default container settings by specifying
environment variables used during container runtime. The list of supported variables
and their functions is clearly documented on the container's Docker Hub page:

[https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3](https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3)

These variables allow you to configure key parameters such as the proxy mode, server
address, hostname, database settings, and logging options, providing a flexible
and declarative way to tailor the proxy’s behavior to your environment.

Let's create the file `~/.config/containers/systemd/ZabbixProxy.env` and add
the following content.

```ini
# Zabbix proxy hostname as it appears in the Zabbix frontend
ZBX_HOSTNAME=ProxyA

# IP address or DNS name of the Zabbix server
ZBX_SERVER_HOST=<DNS or IP>

# Proxy mode: 0 = active, 1 = passive
ZBX_PROXYMODE=0
```

With our configuration complete, the final step is to reload the systemd user daemon
so it recognizes the new Quadlet unit. This can be done using the following command:

```bash
systemctl --user daemon-reload
```

If everything is set up correctly, systemd will automatically generate a service
unit for the container based on the `.container` file. You can verify that the
unit has been registered by running:

```bash
systemctl --user list-unit-files | grep zabbix
```

You should see output similar to:

```
zabbix-proxy-sqlite.service             generated
```

To start the container, use the following command (replacing the service name if
you used a different one):

```bash
systemctl --user start zabbix-proxy-sqlite.service
```

To verify that the container started correctly, you can inspect the running containers
with:

```bash
podman ps
```

This will return output like the example below:

```bash
CONTAINER ID  IMAGE                                               COMMAND               CREATED       STATUS       PORTS                     NAMES
b5716f8f379d  docker.io/zabbix/zabbix-proxy-sqlite3:trunk-centos  /usr/sbin/zabbix_...  2 hours ago   Up 2 hours   0.0.0.0:10051->10051/tcp  ZabbixProxySqlite-Quadlet
```

Take note of the `CONTAINER ID`—in this example, it is `b5716f8f379d`. You can
then retrieve the container's logs using:

```bash
podman logs b5716f8f379d
```

This command will return the startup and runtime logs for the container, which
are helpful for troubleshooting and verifying that the Zabbix proxy has started
correctly.

---

## Conclusion

In this chapter, we deployed a Zabbix active proxy using Podman and systemd Quadlets
on a Red Hat-based system. We configured SELinux, enabled user lingering, and created
both `.container` and `.env` files to define proxy behavior. Using Podman in rootless
mode ensures improved security and system integration. Systemd management makes
the container easy to control and monitor. This setup offers a lightweight, flexible,
and secure approach to deploying Zabbix proxies. It is ideal for modern environments,
especially when using containers or virtualisation. With the proxy running, you're
ready to extend Zabbix monitoring to remote locations efficiently.

## Questions

- What are the main advantages of using Podman over Docker for running containers
  on Red Hat-based systems?
- Why is the loginctl enable-linger command important when using systemd with rootless
  Podman containers?
- What is the purpose of the .env file in the context of a Quadlet-managed container?
- How do SELinux policies affect Podman container execution, and how can you configure
  them correctly?
- How can you verify that your Zabbix proxy container started successfully?
- What is the difference between an active and passive Zabbix proxy?

## Useful URLs

- [https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3](https://hub.docker.com/r/zabbix/zabbix-proxy-sqlite3)
- [https://podman.io/](https://podman.io/)
- [https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)
