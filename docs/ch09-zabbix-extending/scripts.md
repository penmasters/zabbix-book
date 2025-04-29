# Frontend Scripts

So, you're diving into the world of Zabbix frontend scripts, and you're in for 
a treat! These little powerhouses unlock a whole new level of flexibility within
your Zabbix environment. Imagine being able to trigger custom actions directly from
your Zabbix interface – whether it's as an action operation responding to an alert,
a manual intervention on a host, or a targeted response to a specific event.

What's truly exciting is *where* you can weave these scripts into your daily Zabbix
workflow. Picture adding custom menu items right within your **Hosts**, **Problems**,
**Dashboards**, and even your **Maps** sections. This means the information and
tools you need are always at your fingertips.

Ultimately, frontend scripts empower you to extend Zabbix far beyond it's out-of-the-box
capabilities. They provide that crucial extra layer of customization, allowing you
to seamlessly integrate your own scripts and workflows directly into the Zabbix
frontend. Get ready to harness this power and tailor Zabbix precisely to your needs!

## Creating a frontend scripts

For this example we will make use of a frontend script I made to put hosts in
maintenance mode. This allow us with frontend scripts to create an option to execute
this script from our GUI and place the host in maintenance. it can be downloaded
from my GitHub page here :
[https://github.com/Trikke76/Zabbix/blob/master/maintenance/zabbix-maintenance.py](https://github.com/Trikke76/Zabbix/blob/master/maintenance/zabbix-maintenance.py)

!!! info "Download this script and place it in `/usr/bin/` "
    ```
    cd /usr/bin/
    dnf install wget -y
    wget https://raw.githubusercontent.com/Trikke76/Zabbix/refs/heads/master/maintenance/zabbix-maintenance.py -P /usr/bin/
    dnf install python3-requests
    chmod +x /usr/bin/zabbix-maintenance.py
    ```
The next step is to edit our script and change some of the variable:

!!! info "Replace variables"
    ```
    vi /usr/bin/zabbix-maintenance.py
    
    ZABBIX_API_URL = "https://zabbix-url.be/api_jsonrpc.php"
    ZABBIX_API_TOKEN = "API TOKEN"
    ```
???+ note
    For the user you can use the user `Admin` or you can create a new user. but
    make sure this user has enough permissions to create a maintenance mode.
    It's best practice to create a dedicated user for this in production.





## Conclusion

## Questions

## Useful URLs


