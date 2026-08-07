---
description: |

tags: [beginner]
---

# Creating automated PDF reports

Scheduled PDF reports allow Zabbix to automatically generate dashboards as PDF documents and distribute them by email. This feature requires the **Zabbix Web Service**, which uses a headless Google Chrome browser to render dashboards before converting them to PDF.

## Installing the Zabbix Web Service

Install the required package.

```bash
sudo apt update
sudo apt install zabbix-web-service
```

---

## Installing Google Chrome

Although Chromium is available on Ubuntu, the Snap version is **not supported** by the Zabbix Web Service.

When using the Snap package, report generation typically fails with errors similar to:

```text
cannot create snap home dir
chrome failed to start
/system.slice/zabbix-web-service.service is not a snap cgroup
```

Install the official Google Chrome package instead.

```bash
cd /tmp

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

sudo apt install ./google-chrome-stable_current_amd64.deb
```

If Chromium was previously installed as a Snap package, remove it.

```bash
sudo snap remove chromium
```

Verify the installation.

```bash
which google-chrome
```

Example output:

```text
/usr/bin/google-chrome
```

---

## Ubuntu 24.04 Home Directory Issue

On Ubuntu 24.04, the **zabbix-web-service** package does not automatically create the home directory for the **zabbix** user.

Without this directory, Google Chrome cannot start and PDF generation will fail.

Create the directory manually.

```bash
sudo install -d -o zabbix -g zabbix -m 0750 /var/lib/zabbix
```

Create the directories required by Google Chrome.

```bash
sudo -u zabbix mkdir -p \
    /var/lib/zabbix/.config \
    /var/lib/zabbix/.cache \
    /var/lib/zabbix/.local/share/applications
```

Verify that the **zabbix** user can write to its home directory.

```bash
sudo -u zabbix touch /var/lib/zabbix/test
sudo -u zabbix rm /var/lib/zabbix/test
```

---

## Configuring the Zabbix Server

Edit the Zabbix Server configuration.

```bash
sudo nano /etc/zabbix/zabbix_server.conf
```

Configure the Web Service URL.

```text
WebServiceURL=http://127.0.0.1:10053/report
```

Enable at least one report writer.

```text
StartReportWriters=1
```

Restart both services.

```bash
sudo systemctl restart zabbix-web-service
sudo systemctl restart zabbix-server
```

---

## Verifying the Installation

Verify that the Web Service is running.

```bash
systemctl status zabbix-web-service
```

You can also test whether the Web Service is listening.

```bash
curl http://127.0.0.1:10053/report
```

Receiving an error indicating that the HTTP method is not supported is expected and confirms that the Web Service is operational.

Once the Web Service is running successfully, scheduled PDF reports can be created directly from the Zabbix frontend.

---

!!! warning

    On Ubuntu 24.04, the Snap version of Chromium is **not compatible** with the
    Zabbix Web Service. Always install the official Google Chrome package and ensure
    that the `/var/lib/zabbix` home directory exists and is writable by the **zabbix**
    user. Otherwise, Chrome will fail to start and automated PDF report generation
    will not work.



## Conclusion

## Questions

## Useful URLs
