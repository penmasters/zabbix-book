---
description: |
    Test website performance with Zabbix browser items. Automate real browser
    checks to measure load times, content accuracy, and user experience.
tags: [advanced, expert]
---

# Browser item

This section details the critical steps and solutions required to successfully
deploy the Zabbix Browser Item for high-reliability synthetic monitoring.

## Zabbix Browser Item Architecture and Prerequisites

The Zabbix Browser Item is designed for synthetic transaction monitoring using
real browsers. It requires specific external components to function.

- **The Workflow:** The Zabbix Server/Proxy executes a JavaScript script (written in
  ES5 syntax). This script does not launch the browser itself; instead, it sends
  commands via the WebDriver Protocol to an external WebDriver Server (e.g., Selenium
  Standalone or a Grid).

- **Prerequisites:**
    - **WebDriver Server:** A running instance of the Selenium Standalone Server or Grid,
      which includes the necessary Chromedriver or Geckodriver binaries.
    - **Zabbix Configuration:** The Zabbix Server/Proxy must be configured with the
      WebDriverLocation parameter, pointing to the external server's URL (e.g.,
      http://192.168.x.x:4444/).



## Conclusion

## Questions

## Useful URLs
