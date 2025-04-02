# Low Level Discovery with Dependent items.

Efficiency in monitoring isn't just about automation it's also about minimizing
resource usage. Low-Level Discovery (LLD) with dependent items in Zabbix offers
a powerful way to reduce agent load and database overhead by collecting data once
and extracting multiple metrics from it.

Instead of creating separate item queries for each discovered entity, dependent
items allow you to process a single data source such as a JSON response, log entry,
or SNMP bulk data and extract relevant metrics dynamically. This approach significantly
optimizes performance while maintaining full automation.

In this chapter, we'll explore how to implement LLD with dependent items, configure
preprocessing rules, and leverage this technique to make your Zabbix monitoring
more efficient, scalable, and resource friendly by using a practical example.

Let’s get started!

---

???+ note
    For this chapter we start with a working system with a passive Zabbix agent. You can
    always refer to Chapter 01 if you like to know how to setup Zabbix.
    It can be a good start to have a look at our previous topic `Custom LLD` to get
    a better understanding on how LLD works.


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
*8.1 Create host*

???+ note
    Remember this is just an example file we made in real life you will use probably
    a `HHTP agent` or a `Zabbix agent` to retrieve real life data.

Click on top right of the page on `Create item` to create a new item so that we
can retrieve our master items data.

Once the `New Item` popup is on the screen fill in the following details:

- **Name** : RAW : Printer status page
- **Type** : Zabbix agent
- **Key** : vfs.file.contents[/home/printer-status.txt\]

![Create lld item](ch08-dependent-lld-item.png)
*8.2 Create a LLD item*

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
*8.3 Test LLD item*

???+ tip
    Keep a copy of the output somewhere you will need it in the following steps
    to create your LLD rule and LLD items etc ... 



## Create LLD Discovery

To create a discovery rule first to go `Discovery rules` on the top next to Items,
Triggers and Graphs and click on `Create discovery rule`.

![Create discovery rule](ch08-dependent-lld-create-discovery.png)
*8.4 Create a discovery rule*

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

Head over to the `LLD macros` tab in our Discovery rule and map the following macros
with our JSONpath filters to extract the needed info so that we can use it later
in our LLD items, triggers, graphs .... .

- **{#PRINTER.NAME}** : Map it with `$.name`.
- **{#PRINTER.STATUS}** : Map it with `$.status`.

![LLD Macros](ch08-dependent-lld-create-lldmacro.png)
*8.5 Create a LLD Macro*

When ready press `Update` at the bottom of the page.

## Creating a Low-Level Discovery (LLD) Item

After defining the discovery rule and mapping the data to the corresponding LLD
macros, the next step is to create an LLD item. This is done through item prototypes.  

1. Navigate to the `Item prototypes` tab.  
2. Click Create `item prototype` in the upper-right corner.  
3. Configure the following parameters:  

   - **Name**: `Status from {#PRINTER.NAME}`  
   - **Type**: `Dependent item`  
   - **Key**: `status.[{{#PRINTER.NAME}}]`  
   - **Type of information**: `Text`  
   - **Master Item**: Select the previously created raw item.  

This setup ensures that the discovered printer statuses are correctly assigned and
processed through the LLD mechanism.  

![LLD Item create](ch08-dependent-lld-create-llditem.png)
*8.6 Create a LLD item*

Before saving the item, navigate to the `Preprocessing` tab to define the necessary
preprocessing steps. These steps will ensure that the extracted data is correctly
formatted for Zabbix. Configure the following preprocessing steps:

1. **JSONPath**: $.data..[?(@.name=='{#PRINTER.NAME}')].status.first()
2. **Replace**:  
   - Convert `NOK` to `false`.  
   - This step is required because Zabbix does not recognize `NOK` as a boolean
     value but does recognize `false`.
3. **Boolean to Decimal**:  
   - This conversion transforms boolean values into numerical representation (`1` for `OK`, `0` for `false`).  
   - Numeric values are more suitable for graphing and analysis in Zabbix.
4. **Type of Information**:  
   - Set to **Numeric** to ensure proper data processing and visualization.

### Understanding the JSONPath Expression

To derive the correct JSONPath query, use a tool such as the `JSON Query Tool`
([https://www.jsonquerytool.com/](https://www.jsonquerytool.com/)). This tool
allows testing and refining JSON queries using real data retrieved from the raw item.

The JSONPath query used in this case is:

!!! info ""
    ```
    $.data..[?(@.name=='{#PRINTER.NAME}')].status.first()
    ```

### Breakdown of the JSONPath Syntax:

- **`$`** → Refers to the root of the JSON document.  
- **`.data`** → Accesses the `data` key within the JSON structure.  
- **`..`** → The recursive descent operator, searching through all nested levels for matching elements.  
- **`[?(@.name=='{#PRINTER.NAME}')]`** → A filter expression that:  
  - Uses `?(@.name=='Color Printer 1')` to match objects where the `name` field equals `"Color Printer 1"`.  
  - `{#PRINTER.NAME}` is a Zabbix macro that dynamically replaces `"Color Printer 1"` with the discovered printer name.  
- **`@`** → Represents the current element being evaluated.  
- **`.status`** → Retrieves the `status` field from the filtered result.  
- **`.first()`** → Returns only the first matching `status` value instead of an array.  
  - Without `.first()`, the result would be `["OK"]` instead of `"OK"`.

By applying these preprocessing steps, we ensure that the extracted printer status
is correctly formatted and can be efficiently used for monitoring and visualization
in Zabbix.

## Optimizing Data Collection and Discovery Performance

Before finalizing our configuration, we need to make an important adjustment.
The current settings may negatively impact system performance due to an overly frequent
update interval.

Navigate to `Data collection`|`Hosts` and click on `Items`. Select the `RAW item`
that was created in the first step.

By default, the update interval is set to `1 minute`. This means the item is
refreshed every minute, and since our LLD rule is based on this item, Zabbix will
rediscover printers every minute as well. While this ensures timely updates, it
is inefficient and can impact performance.

A common best practice is to configure **discovery rules** to run no more than
`once per hour`. However, since our `LLD item` relies on this same RAW item, an
hourly interval would be too infrequent for monitoring printer status updates.
To strike a balance between efficiency and real-time monitoring, we can apply
a `preprocessing trick`.

Go to the `Preprocessing` tab and add the following preprocessing step:

-  **Discard unchanged with heartbeat** → `1h`  

This ensures that the database is updated `only when a status change occurs`. If
no status change is detected, `no new entry is written to the database`, reducing
unnecessary writes and improving performance. However, to ensure some data is
still recorded, the status will be written to the database at least `once per hour`,
even if no changes occur.

Before saving the changes, we can further optimize storage by preventing the
master item from being stored in the database. Navigate back to the `Item` tab and
set `History` to `Do not store`. 

???+ note
    If you change your mind and want to keep the history then our preprocessing step
    will at least not save it every minute but only when there are changes or once
    every hour.

The RAW item is only used to feed data into the **LLD discovery rule** and `LLD items`.
Since we do not need to retain historical data for this master item, `discarding it` 
saves database space and improves efficiency.

By applying these optimizations, we ensure that our monitoring system remains
efficient while still capturing necessary status updates.


## Creating a Low-Level Discovery (LLD) Filter

Now lets have some fun and use a script that generates the output of our text file with random statuses so that we have a more close to real live environment.
Create in the folder where your `printer-status.txt` file is a new file called `printer-demo.py` and paste following content in it.

!!! info "python script"
    ```
    #!/usr/bin/env python3
    
    import json
    import os
    
    STATUS_FILE = "printer-status.txt"
    
    # Define printers
    printers = [
        {"name": "Color Printer 1", "status": "OK"},
        {"name": "Color Printer 2", "status": "OK"},
        {"name": "B&W Printer 1", "status": "OK"},
        {"name": "B&W Printer 2", "status": "NOK"},
        {"name": "This is not a printer", "status": "NOK"}
    ]
    
    # Check if the status file exists
    if os.path.exists(STATUS_FILE):
        # Read the existing status from the file
        with open(STATUS_FILE, "r") as f:
            output = json.load(f)
        printers = output["data"]
    else:
        # If no file, set initial values
        output = {"data": printers}
    
    # Toggle statuses
    for printer in printers:
        printer["status"] = "NOK" if printer["status"] == "OK" else "OK"
    
    # Write the new status to file
    with open(STATUS_FILE, "w") as f:
        json.dump({"data": printers}, f, indent=2)
    
    print(f"Printer status updated and written to {STATUS_FILE}")
    ```

Once you have created the script make it executable with `chmod +x printer-demo.py`
and then run the script with the following command `./printer-demo.py`.

If you cannot run the script then check the python environment or try to run it as `python printer-demo.py`.

This script will change the status of our printers you can verify this in the `Latest data` page.

![Latest data updated](ch08-dependent-lld-create-latestdata-updated.png)
*8.7 Latest data*

But hey wait as we can see there is an extra devices detected with the name `This is not a printer`
and Zabbix hasn't detected any status for it ..... 

That we don't have any status yet is normal remember we did a check only once per
hour with our Preprocessing step so first time the data was changed the new device was detected.
If the status from the device changes again zabbix will create an update for the item and 
a status will be processed.

???+ note
   Low Level will work in 2 steps first step is the detection of the new devices
   and second step is populating the items with the correct data. Remember that
   we did an item interval of 1m so it can take up to 1m before our items gets a
   new value.

Lets see now how we can remove the device `this is not a printer` from our list
since we don't want to monitor this one.

Let's go back to our LLD discovery rule this time to the tab Filters and add the
following to the fields:

- **Label** : {#PRINTER.NAME} `does not match`
- ** regular expression** : `{$PRINTERS.NOT.TO.DETECT}`

![LLD Filters](ch08-dependent-lld-create-filters.png)
*8.8 LLD Filters*

Press update and go to our Host and click on the tab `Macros`. Here we will create
our macro and link it with a regular expression. 
Fill in the following values :

- **Macro**: {$PRINTERS.NOT.TO.DETECT}
- **Value** : ^This is not a printer$

![Filter macros](ch08-dependent-lld-create-filter-macro.png)
*8.9 LLD Filter Macros*

After executing our discovery rule and sending updated values to Zabbix, we can
verify the filter's effectiveness by checking the `Latest data` view, where the
excluded device no longer appears.

When navigating to the `Items` section of our host, we'll observe that the previously
discovered item for the filtered device now displays a `Disabled` status with an
accompanying orange exclamation mark icon. Hovering over this icon reveals the
system notification: `The item is not discovered anymore and has been disabled, will be deleted in 6d 23h 36m.`

This automatic cleanup behavior for undiscovered items follows Zabbix's default
retention policy, which can be customized by modifying the `Keep lost resources period`
parameter in the Discovery rule settings to align with your organization's monitoring
governance requirements.

This concludes our chapter.

# Conclusion

Low-Level Discovery in Zabbix represents a powerful approach to dynamic monitoring
that scales efficiently with your infrastructure. Through this chapter, we've explored
how the combination of LLD with dependent items and discovery filters creates a robust
framework for automated monitoring that remains both comprehensive and manageable.

By implementing dependent items within discovery rules, we've seen how to build
sophisticated monitoring relationships without the performance overhead of multiple
direct checks. This approach not only reduces the load on monitored systems but
also simplifies the overall monitoring architecture by establishing clear parent-child
relationships between metrics.

The strategic application of LLD filters, as demonstrated in our examples, transforms
raw discovery data into precisely targeted monitoring. Instead of drowning in irrelevant
metrics, your Zabbix instance now focuses only on what matters to your organization's
specific needs. Whether filtering by regex patterns, system types, or operational
states, these filters act as the gatekeepers that maintain monitoring relevance
as your environment expands.

Perhaps most importantly, the techniques covered in this chapter enable truly scalable
monitoring that grows automatically with your infrastructure. New servers, applications,
or network devices are seamlessly incorporated into your monitoring framework without
manual intervention, ensuring that visibility expands in lockstep with your environment.

As you implement these concepts in your own Zabbix deployments, remember that effective
monitoring is about balance and capturing sufficient detail while avoiding data overload.
The combination of LLD, dependent items, and thoughtful filtering provides exactly
this balance, giving you the tools to build monitoring systems that scale without
sacrificing depth or precision.

With these techniques at your disposal, your Zabbix implementation can evolve from
a basic monitoring tool to an intelligent system that adapts to your changing infrastructure,
providing actionable insights without constant reconfiguration.

# Questions

- How do LLD filters change the monitoring paradigm from "collect everything" to a more targeted approach?
- How does Zabbix LLD fundamentally differ from traditional static monitoring approaches ?
- Break down the components of the JSONPath expression $.data..[?(@.name=='{#PRINTER.NAME}')].status.first()
  and explain how each part contributes to extracting the correct data.
- How would you modify the example to monitor printer ink levels in addition to printer status?

# Useful URLs

- [https://www.jsonquerytool.com/](https://www.jsonquerytool.com/)
- [https://regex101.com/](https://regex101.com/)
- [https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery#filter](https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery#filter)
- [https://blog.zabbix.com/lld-filtering-with-macros/24959/](https://blog.zabbix.com/lld-filtering-with-macros/24959/)

