---
description: |
    Test website performance with Zabbix browser items. Automate real browser
    checks to measure load times, content accuracy, and user experience.
tags: [advanced, expert]
---

# Browser item

## Foundational Concepts and Synthetic Monitoring Architecture
The introduction of the Browser Item (Item Type 19) in Zabbix 7.x marked a significant
expansion of monitoring capabilities, allowing Zabbix to serve not only as a traditional
IT infrastructure monitoring tool but also as a powerful resource for monitoring
strategic web-based information. This item type enables synthetic monitoring a
method that simulates the behavior of a real user, including multi-step journeys
(user journeys) such as logging in, navigating through menus, or completing a checkout
process.

### What is the Zabbix Browser Item?
In essence, the Browser Item collects data by executing user-defined JavaScript code
in an automated browser environment via HTTP/HTTPS. Unlike simple HTTP requests,
this item simulates complex actions like clicks, text input, and dynamic navigation
within web applications. The ability to simulate the website in this manner, including
capturing screenshots and measuring performance, enables organizations to ensure
the availability and integrity of both internal websites and external strategic
information sources (such as government portals for tenders).

### The Technological Foundation: WebDriver API
The functioning of the Browser Item relies on a crucial architectural dependency:
**the WebDriver API** (based on the W3C WebDriver standard). This is an established
framework, often implemented by solutions such as Selenium Server or a headless
WebDriver (e.g., ChromeDriver), which acts as the web testing endpoint. The Zabbix
Server or Proxy functions as the client; it sends the defined JavaScript commands
to this external endpoint, where the actual browser (usually Chrome in a standalone
container) is controlled. The results of the simulated session, including metrics
and error information, are then returned to Zabbix as a structured JSON object.

![Architecture design](ch03_xx_architecture.png)
_CH03.xx Architecture Overview_

### Browser Item vs. Classic Web Scenarios: The Strategic Choice

Before implementing the Browser Item, it is crucial to understand the difference
between it and the older, classic Web Scenarios. Classic web scenarios are based
on the HTTP Agent and execute steps sequentially, collecting only protocol-level
metrics such as download speed, response time, and the HTTP response code. They
check whether a predefined string is present in the HTML response and can perform
a simulated login, but they do not render the full Document Object Model (DOM)
of the page.

The Browser Item, conversely, simulates the entire browser stack. This is indispensable
for monitoring modern, complex JavaScript-based Single Page Applications (SPAs) or
other web pages where content is loaded asynchronously. Where classic scenarios fail
due to the lack of JavaScript execution, the Browser Item ensures the reliability of
synthetic checks by using a real browser engine. Furthermore, the Browser Item is the
only method within Zabbix that can capture visual snapshots (screenshots), which is
invaluable for troubleshooting. The implication of this superior functionality is that
Browser Items require significantly more CPU and memory on the WebDriver host and on
the Zabbix processes performing the polling.

## Architectural Requirements: Setting up the WebDriver Endpoint

A successful implementation of the Browser Item requires careful configuration of the
external web testing endpoint. The recommended and most robust method is to use Docker
containers to create an isolated, scalable Selenium Server environment.

#### Implementing Selenium Standalone Chrome via Docker

The Zabbix system is designed to communicate robustly with a Selenium Standalone
Server using a Chrome browser engine. It is essential to launch the container with
the correct flags to enable stability and debugging.

The following docker run command is used to start the Selenium Server with Chrome
in detached mode (-d), allocating the necessary ports and memory :

```
docker run --name browser \
-p 4444:4444 \
-p 7900:7900 \
--shm-size="2g" \
-d selenium/standalone-chrome:latest
```

**The parameters in this command serve specific, critical purposes :**

1. **`docker run --name browser`:** This initiates a new Docker container named "browser"
2. **`-p 4444:4444`:** This is the primary communication port. It maps port 4444
   on the host machine to the container port. This is the port the Selenium Server
   uses to accept WebDriver commands from the Zabbix Browser Pollers.
3. **`-p 7900:7900`:** This port is optional but highly recommended for diagnostics.
   It maps the Virtual Network Computing (VNC) server port of the container,
   allowing an administrator to visually observe the automated browser in real
   time remotely (via a VNC client). This is crucial for debugging complex JavaScript
   scripts and unexpected web interactions.
4. **`--shm-size="2g"`:** This is a critical stability parameter. It allocates 2GB
   of shared memory to the container. Chrome requires a significant amount of
   shared memory (/dev/shm) to function correctly and stably under automation.
   Failing to set this can lead to unpredictable browser crashes or slow execution
   times that are difficult to diagnose from Zabbix.
5. **`-d`**: Runs the container in detached mode, meaning it will run in the background.
6. **`selenium/standalone-chrome:latest`:** Specifies the Docker image to use.

#### Validation of the Connectivity

Before configuring the Zabbix Server, the accessibility and functionality of the
WebDriver Endpoint must be validated. This eliminates network or container issues
as potential causes of subsequent Zabbix errors.

The validation steps are as follows :

1. **Determine IP Address:** Identify the IP address of the Docker interface
   (e.g., 192.0.2.1).
2. **Test Port Connectivity:** Use nc (Ncat) to verify the connection to the
   WebDriver port:

   ```bash
   nc -zv 192.0.2.1 4444
   # Expected output: Connection to 192.0.2.1 4444 port [tcp/*] succeeded!
   ```
3. Test Selenium Server Response: Use curl to confirm that the Selenium Server
   is serving a valid HTML response:

   ```bash
   curl -L 192.0.2.1:4444
   # Expected output: HTML content, often starting with <!DOCTYPE html>...<title>
   Selenium Grid</title>
   ```
If these steps succeed, the external dependency is correctly configured, and it is
time to configure the Zabbix components themselves.

## Zabbix Server/Proxy Configuration and Scalability

Browser Items are executed by specific Zabbix processes called browser pollers.
These must be correctly configured on the Zabbix Server or Proxy responsible for
executing the synthetic checks.

### Server Configuration Parameters (zabbix_server.conf)

Two parameters in the Zabbix server configuration file (/etc/zabbix/zabbix_server.conf
or zabbix_proxy.conf) are essential: WebDriverURL and StartBrowserPollers.

**WebDriverURL (Mandatory)**
This parameter must specify the web testing endpoint configured before (our container).
This is a mandatory parameter, as the default value is empty. Without a valid URL,
Zabbix cannot initialize the WebDriver sessions.

`Example: WebDriverURL=http://192.0.2.1:4444`

**StartBrowserPollers (Scalability)**
This controls the number of pre-forked Zabbix processes dedicated to executing and
processing Browser Item checks. The default value is 1, and the range is 0 to 1000.

Since browser automation is a CPU-intensive and time-consuming task, Browser Items
are inherently high-latency items. The number of pollers set N<sub>Pollers</sub>
determines how many synthetic checks Zabbix can initiate concurrently. It is a
common mistake to increase this number without increasing the capacity of the
WebDriver Endpoint (the number of simultaneous browser sessions Selenium can handle).
An imbalance here causes the Zabbix Queue Overview to grow, indicating that values
are taking too long to update.10 To optimize monitoring performance, the
N<sub>Pollers</sub> in Zabbix must be balanced with the actual parallel execution
capacity of the WebDriver host.

After modifying the configuration files, the service must be restarted:
`systemctl restart zabbix-server` (or `zabbix-proxy`).

### Scalability and Isolation with Zabbix Proxies

For large-scale monitoring or monitoring remote locations, using Zabbix Proxies
is highly recommended. The Browser Item functionality is available on both the
Server and the Proxy, meaning the CPU-intensive rendering and script execution
can be isolated to a dedicated Proxy environment.

The advantage of isolating synthetic checks on a Proxy is twofold: firstly, the
load on the central Zabbix Server is reduced, and secondly, the risk is avoided
that the high-resource-consuming browser automation interferes with the performance
of regular, critical infrastructure checks.

The table below summarizes the essential configuration parameters.

| Parameter | Purpose | Recommended Action |
|:---       |:---     |:---                |
| `WebDriverURL` | URL/IP of the WebDriver Endpoint (e.g., Selenium Server) | Mandatory to set. Format: http://<IP>:<Port>. |
| `StartBrowserPollers` | Number of pre-forked processes for Browser Item checks| Increase this in line with the parallel capacity of the WebDriver host.|

### Host Configuration and the Master Item

The following steps describe the necessary configuration in the Zabbix Frontend
to set up website monitoring.

#### Host and Template Configuration

1. **`Host Creation`:** Create a new host representing the web application to be
   monitored (e.g., "Production Web Portal").
2. **`Template Link`:** Link the out-of-the-box template "Website by Browser"
   to this host. This template is designed for complex web applications and includes
   standard Master Items, Dependent Items, Triggers, and Dashboards.

### Host Macro Definitions

The linked template typically uses User Macros to set dynamic parameters, keeping
the template reusable. These macros must be set at the Host level (via the Macros
tab -> Inherited and host macros) :

- {$WEBSITE.DOMAIN}: Define the target URL or domain name to be monitored
  (e.g., git.zabbix.com/projects/ZBX/repos/zabbix/browse).
- {$WEBSITE.GET.DATA.INTERVAL}: The update interval for the Master Item. Due to
  the high resource cost of a full browser check, a longer interval is often used
  (e.g., 15m).

### Master Browser Item Configuration

The Browser Item itself acts as the Master Item that returns a large, structured
JSON data set. Configuration at the item level is crucial for functionality :

- **Type:** Select Browser.
- **Key:** Enter a unique key (e.g., web.browser.scenario[login_check]).
- **Parameters:** This is a list of name/value pairs passed as variables to the
  JavaScript script. This is the ideal place to define non-sensitive parameters
  (URLs, viewport sizes) and, using User Macros, sensitive credentials (usernames,
  passwords).
- **Script:** This is the central component where the JavaScript code for browser
  interaction is entered.
- **Timeout:** Set the maximum execution time of the JavaScript (range: 1–600 seconds).
  Exceeding this time results in an error. Since synthetic checks are inherently
  time-consuming, this value should be set generously, but not excessively, to
  prevent long-running checks from blocking the poller queues.

### Scripting Advanced Browser Interactions (JavaScript API)

The power of the Browser Item lies in the specialized JavaScript environment provided
by Zabbix. The JavaScript script directs the entire browser interaction and data
collection.

#### The Zabbix JavaScript Context and the Browser Object

The script has access to Zabbix's additions to the JavaScript language, particularly
the **Browser objects**. The central `Browser` object manages the WebDriver session;
it is initialized upon creation and terminated upon destruction. A single script
can support up to four `Browser` objects.

**The basic workflow of any script includes :**

- Initialization of a `Browser` session, optionally with custom `chromeOptions`
  (e.g., --headless=new for performance).
- Navigation to the starting URL (`browser.navigate(url)`).
- Execution of the defined interactions.
- Data collection via `browser.collectPerfEntries()` at crucial points.
- Returning the results as a JSON string via `JSON.stringify(browser.getResult()`).

### Essential Methods for Interaction and Timing

For executing complex interactions, the following methods of the `Browser` object
are crucial :

- `navigate(url)`: Navigates the browser to the specified URL.
- `findElement(strategy, selector)`: Finds a single element on the page (e.g., an
  input field or button) using a location strategy (CSS selector, XPath, link text,
  etc.).
- `sendKeys(text)/click()`: Methods of the returned Element object to enter text
  or click buttons.
- `setElementWaitTimeout(timeout)`: Sets the implicit wait time (in milliseconds)
  the browser uses when searching for elements. This is a critical method for
  making scripts robust against variable web page load times.
- `collectPerfEntries(mark)`: Collects performance data from the browser (based
  on the browser's Performance API). The optional mark parameter labels this
  snapshot, which is essential for measuring the duration of specific steps in
  a transaction (e.g., "open page" or "login").

### Case Study: Implementing a Multi-Step Login


## Conclusion

## Questions

## Useful URLs
