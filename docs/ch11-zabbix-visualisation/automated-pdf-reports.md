---
description: |
    Learn how to configure automated PDF reports in Zabbix using the Zabbix Web Service and Google Chrome.
tags: [beginner]
---

# Creating automated PDF reports

Scheduled PDF reports allow Zabbix to automatically generate dashboards as PDF
documents and distribute them by email. This feature requires the **Zabbix Web Service**,
which uses a headless Google Chrome browser to render dashboards before converting
them to PDF. Refer to [Chapter 3: Web Services](../ch03-zabbix-proxies/web-services.md)
for detailed instructions on installing and configuring the Zabbix Web Service.

---

## Home Directory Issue

The **zabbix-web-service** package does not automatically
create the home directory for the **zabbix** user. Without this directory, Google
Chrome cannot start and PDF generation will fail.

!!! info "Creating the Zabbix home directory"

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

Next we need to configure the Zabbix Server so it knows where to find the
web service and how many report writers to start.

!!! info "Configuring the Zabbix Server"

    Edit the Zabbix Server configuration.

    ```bash
    sudo vi /etc/zabbix/zabbix_server.d/zabbix_web_service.conf
    ```

    Configure the Web Service URL.

    ```ini
    WebServiceURL=http://127.0.0.1:10053/report
    ```

    Enable at least one report writer.

    ```ini
    StartReportWriters=1
    ```

    Restart both services.

    ```bash
    sudo systemctl restart zabbix-web-service
    sudo systemctl restart zabbix-server
    ```

---

## Verifying the Installation

Before creating scheduled PDF reports, verify that the Zabbix Web Service is running
correctly and listening on the expected port.

!!! info "Verifying the Installation"

    Verify that the Web Service is running.

    ```bash
    systemctl status zabbix-web-service
    systemctl enable zabbix-web-service
```

    You can also test whether the Web Service is listening.

    ```bash
    curl http://127.0.0.1:10053/report
    ```

One final step before we can start creating our scheduled reports is
configuration of the frontend URL. Go to Administration -> General -> Other.
Fill in the `Frontend URL` field met the correct url of your frontend. This can
be something like `http://192.168.0.1/` or `https://myzabbixurl/` or even
`https://my_zabbix_domain/zabbix/`. This depends on how you have configured your
frontend.

![ch11.50-frontend-url.png](ch11.37-frontend-url.png)

_11.37 Frontend URL_

Receiving an error indicating that the HTTP method is not supported is expected
and confirms that the Web Service is operational. After configuring the Frontend URL,
scheduled PDF reports can be created directly from the Zabbix frontend.

---

!!! warning

    On Ubuntu 24.04, the Snap version of Chromium is **not compatible** with the
    Zabbix Web Service. Always install the official Google Chrome package and ensure
    that the `/var/lib/zabbix` home directory exists and is writable by the **zabbix**
    user. Otherwise, Chrome will fail to start and automated PDF report generation
    will not work.

## Conclusion

Automated PDF reports make it easy to distribute dashboards to administrators,
managers, and customers without requiring manual intervention.

By installing the Zabbix Web Service, configuring the Zabbix Server, and using
a supported version of Google Chrome, you can automatically generate and email
PDF reports directly from Zabbix.

---

## Questions

1. Which Zabbix component is responsible for generating scheduled PDF reports?
2. Why is the Ubuntu Snap version of Chromium not supported?
3. Which Zabbix Server parameters must be configured to enable PDF report generation?
4. How can you verify that the Zabbix Web Service is running correctly?
5. Which TCP port does the Zabbix Web Service use by default?

---

## Useful URLs

  - [https://www.zabbix.com/documentation/current/en/manual/config/reports](https://www.zabbix.com/documentation/current/en/manual/config/reports)
  - [https://www.zabbix.com/documentation/current/en/manual/appendix/install/web_service](https://www.zabbix.com/documentation/current/en/manual/appendix/install/web_service)
  -[https://www.google.com/chrome/](https://www.google.com/chrome/)
