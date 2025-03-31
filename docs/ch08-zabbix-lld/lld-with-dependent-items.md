# Low Level Discovery with Dependent items.

Low level discovery can also be done using dependent items. Actually it's not very
different from using regular LLD. You might even be surprised how easy it is and
how many times it will be useful to know how to do

???+ note
    For this chapter we start with a working system without Zabbix agent. You can
    always refer to Chapter 01 if you like to know how to setup Zabbix.



In modern IT environments, automation is key to efficient monitoring. Zabbix's
`Low-Level Discovery (LLD)` simplifies the process by automatically detecting
and creating items, triggers, and graphs for dynamic components like network interfaces,
disks, or services.  

It can be a good start to have a look at our previous topic `Custom LLD` to get
a better understanding on how LLD works.

One powerful yet often overlooked optimization is using `dependent items` within
an LLD rule. Instead of polling each discovered item separately leading to unnecessary
load on the system. You can leverage a single master item to collect structured data
and extract relevant values using `preprocessing rules` in Zabbix. This reduces
query overhead, improves performance, and ensures efficient data processing.

In this chapter, we will explore how to configure LLD using dependent items, walking
through a practical example to streamline monitoring while minimizing system impact.  


## Creating our custom data.

Before we can implement our Low-Level Discovery (LLD) rule, we first need relevant
data to work with. Consider a scenario where a print server provides a list of printers
along with their status in JSON format. This structured data will serve as the foundation
for our discovery process.  


!!! info "Example data"

    ``` json
    {
      "data": [
        {
          "name": "Color Printer 1",
          "status": "OK"
        },
        {
          "name": "Color Printer 2",
          "status": "OK"
        },
        {
          "name": "B&W Printer 1",
          "status": "OK"
        },
        {
          "name": "B&W Printer 2",
          "status": "NOK"
        }
      ]
    }
    ```
On your Zabbix server, log in and create a text file containing the example data
that will serve as the master item for our Low-Level Discovery (LLD) rule.

1. **Access the Server**: Log in to your Zabbix server via SSH or directly.
2. **Create the File**: Run the following command to store the JSON data:

!!! info "Run the following command:"
    ```
    echo 
    '{
      "data": [
        {
          "name": "Color Printer 1",
          "status": "OK"
        },
        {
          "name": "Color Printer 2",
          "status": "OK"
        },
        {
          "name": "B&W Printer 1",
          "status": "OK"
        },
        {
          "name": "B&W Printer 2",
          "status": "NOK"
        }
      ]
    }' | sudo tee /home/printer-status.txt > /dev/null
    ```

3. **Verify the File**: Ensure the file is correctly created by running:

!!! info "Test the file"
    ```
    cat /home/printer-status.json
    ```

## Create a master item.

We are now ready to create an item in Zabbix to get the information in to our
master item. But first we need to create a host.

Go to `Data collection | Hosts` and click `Create host`. Fill in the `Host name` 
and the `Host group` and create an `Agent interface`. Those are the only things
we need for our host and press `Add`.

Go to the host and click on `items` the next step will be to create our item so
that we can retrieve the data from our printers.

![Create Host](ch08-dependent-lld-create-host.png)


???+ note
    Remember this is just an example file we made in real life you will use probably
    a `HHTP agent` or a `Zabbix agent` to retrieve real life data.

Click on top right of the page on `Create item` to create a new item so that we
can retrieve our master items data.

Once the `New Item` popup is on the screen fill in the following details:

- **Name** : RAW : Printer status page
- **Type** : Zabbix agent
- **Key** : vfs.file.contents[/home/printer-status.txt\]

![]()
![Create lld item](ch08-dependent-lld-item.png)

Before you press `Add` let's test our item first to see if we can retrieve the
data we need.

Press `Test` at the bottom of the page a popup will come and you can press at the
bottom of the page `Get value and test` or `Get value` just above. Both should work
and return you the information form the txt file. 

???+ note
    When you press `Get value` it
    will show you the value as is retrieved from the host. `Get value and test` on
    the other hand will also try to execute other pre processing steps if there are
    any. So the output of the data could be different. Also if you use secret macros
    Zabbix will not resolve them you will need to fill in the correct information
    first by yourself.

![test lld item](ch08-dependent-lld-test-item.png)

???+ tip
    Keep a copy of the output somewhere you will need it in the following steps
    to create your LLD rule and LLD items etc ... 



## Create LLD Discovery

To create a discovery rule first to go `Discovery rules` on the top next to Items,
Triggers and Graphs and click on `Create discovery rule`.

![Create discovery rule](ch08-dependent-lld-create-discovery.png)

Before configuring our Low-Level Discovery (LLD) rule, we can test our JSON queries
using tools like [JSON Query Tool](https://www.jsonquerytool.com/). If we apply the
query `$..name`, it extracts all printer names, while `$..status` retrieves their statuses.  

However, referring to the [Zabbix documentation](https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery),
we see that starting from **Zabbix 4.2**, the expected JSON format for LLD has changed.
The `data` object is no longer required; instead, LLD now supports a direct JSON
array. This update enables features like **item value preprocessing** and **custom JSONPath queries**
for macro extraction.  

While Zabbix still accepts legacy JSON structures containing a `data` object for
backward compatibility, its use is discouraged. If the JSON consists of a single
object with a `data` array, Zabbix will automatically extract its content using
`$.data`. Additionally, LLD now allows **user-defined macros** with custom JSONPath
expressions.  

Due to these changes, we cannot use the filters `$..name` or `$..status` directly.
Instead, we must use `$.name` and `$.status` for proper extraction. With this
understanding, let's proceed with creating our LLD rule.  









# URLs
https://www.jsonquerytool.com/
