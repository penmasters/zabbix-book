# Triggers
In the previous chapter we have been hard at work to collect our data from various monitoring targets. Because of that our Zabbix environment is filled with useful and important information about our IT infrastructure. However, when you want to know something about your various different devices and applications you have to go through a mountain of data. This is where triggers come in.

Triggers in Zabbix work as a way for us to collect a mountain worth of data, while being alerted about what's important. It allows us to set our own expressions that will define exactly when Zabbix should log and alert us about something happening with our data. The easiest example being something like a CPU going to 90% utilization.


## Preparing the environment
In the previous chapter we created some hosts to monitor the active Zabbix agent, which are great for some example triggers. We created this host under the hostname `zbx-agent-active-rocky` or `zbx-agent-active-windows`, either should work for the example. We also should already have an item on this host to monitor the `Zabbix agent ping` with item key `agent.ping`. Let's add one item to our `zbx-agent-active-*` host, specifically to monitor the CPU load in percentage. 

![Zabbix Agent active CPU util](ch05.1-cpu-util-item.png){ align=center }

_5.1 Zabbix Agent active CPU util item_

Let's not forget to add the tag.

![Zabbix Agent active CPU util tag](ch05.2-cpu-util-item-tag.png){ align=center }

_5.2 Zabbix Agent active CPU util item tag_

With this item created, we have two great examples on our Zabbix agent active host for creating some basic triggers.


## Trigger creation
Let's now create two very common triggers in our Zabbix environment. Go to `Data collection | Hosts` and navigate to either your Linux or Windows `zbx-agent-active-*` host and click on `Triggers`. In the top right corner you can now click on `Create trigger` to start.

![Empty trigger creation form](ch05.3-trigger-empty-top.png){ align=center }

_5.3 Empty trigger creation form_

To start with the basics we can see the follow information at the top part of our trigger creation form.

- **Name**
- **Event name: The name of the event and problem you will see Monitoring | Problems**
- **Operational data**
- **Severity**
- **Expression**
- **OK event generation**

### Name
The name of the trigger is important as it will be used for the name of our events and problems created from this trigger. For example if you would navigate to `Monitoring | Problems`, the triggers you see here will probably have the same name as a trigger. 

It doesn't have to be unique, meaning we can have multiple triggers with the same name. As long as the combination of `Name` and `Expression` is unique. 

Let's fill in `Zabbix agent not seen for >5m`.

### Event name
The `Event name` is very similar to the `Name` field, as it will be used to name the events and problems created from this trigger. However, when `Event name` is used, the `Name` field will no longer form the name of events and problems. `Event name` serves as an override for the `Name` field. 

The `Event name` field allows us to create longer and used more extensive macro functionality compared to the `Name` field. This is why it can be useful in some scenarios, but it is not mandatory to use it.

Let's leave this empty for now.

### Operational data
Whenever we create a trigger, once the trigger goes into a problem state it will create a problem event in the background within Zabbix. This problem event in term then creates a `Problem` in Zabbix which we can find under `Monitoring | Problems`. It's important to keep in mind that event and problem names are always static. Even when the trigger name or trigger event name is updated later, existing event and problems will not get a new name until they resolve and go into problem state again.

This is where `Operational data` becomes useful. It can be used to show dynamic information next to your problem names. This will allow you to for example use a macro like `{ITEM.LASTVALUE}` to always show the latest item value related to this triggers item(s).

Let's fill in `{ITEM.VALUE}` and `{ITEM.LASTVALUE}`

### Severity
This field is mandatory, as it is a selector we have to pick something with. By default Zabbix sets it to `No classified`, which is a severity rarely used outside of Zabbix internal problems. Instead we often pick one of the other 5 severities to indicate how important a problem created from this trigger is. 

For example, `Informational` is often used to indicate something we just want to log. Specifically, often `Informational` is something we do not necessarily want to see on our dashboards or receive external alerts from. `Disaster` on the other end however is often used to indicate something that requires immediate attention. The `Warning`, `Average` and `High` severities can be used to classify anything in between. My favorite basic setup usually looks like below.

- **Informational: Just for logging and not showing on dashboards**
- **Warning: Requires attention, shown on dashboards**
- **Average: Requires more immediate attention, send out email or Slack/Teams message**
- **High: Requires attention even out of office hours, send SMS or Signal message**
- **Disaster: Problem with severe implications to the business, possible higher SMS or Signal escalation**

This is of course just an example of how you could use the different severities and it will depend on your organisation and setup if this is actually implemented as such. The key here is that the severity can be used later to filter in various locations. Like dashboards for showing problems and actions for sending out alerts.

Let's select `High` for now.

### Expression 
The expression of the trigger is arguably the most important part. This is where we are going to define exactly how our trigger will detect the problem. Zabbix comes with many different functions to detect problems in an almost unlimited number of ways. But the basis is simple. 

We collect values from an `Item` using a `Function` applied to a number of values or time period (namely `Last of (T) Count/Time`). To this collect set of values we set a operator and constant (namely `Result`) to indicate what we want the result of our expression to be. This is in the end a whole lot of words to say, more simply put, we select and item to collect values from and then state what we want those values to look like to show a problem in Zabbix.

Let's click on the `Add` button now an used the expression builder. For `Item` we select `Zabbix agent ping`, for `Function` we select `nodata`, for `Last of (T)` we set `5m` and for `Result` we set `= 1`. Then press `Insert` to automatically create the expression below.

![Example trigger expression](ch05.4-trigger-expression-example.png){ align=center }

_5.4 Example trigger expression_

The expression is now built automatically and we do not need to write the whole syntax correctly ourselves. This trigger will now detect if `nodata` (is true `=1`) has been received on the item `agent.ping` for host `zbx-agent-active-rocky` (or `zbx-agent-active-windows` if you used that instead). It will only detect that however if `nodata` was received for more than 5 minutes (`,5m`).

The `nodata` function used in this trigger is a bit special, as it specifically can trigger if no data was received (true `=1`) or if data was received (false `=0`) over a time period. This is what we call a time based trigger in Zabbix, whereas most other triggers only trigger when an item receives data instead. More on those later.

### OK event generation
In the case of this trigger, `OK event generation` is set to `Expression`. This means that the trigger expression will simply use the existing problem `Expression` to detect when the trigger creates an `OK` event. With our `nodata` trigger this will be whenever data has been received again, as the no data for 5 minutes will no longer be true.

In short:

- **Trigger expression is true: Problem event is created and problem starts**
- **Trigger expression is false: OK event is generated and existing problem resolves**

Our trigger should now look like the image below.

![Zabbix agent not seen for 5m trigger](ch05.5-trigger-01-example.png){ align=center }

_5.5 Zabbix agent not seen for 5m trigger_

Let's not forget to also add a tag to this trigger. On triggers in Zabbix the best practice is to create a `Scope` tag to indicate what the trigger is going to be about. We usually pick on of 5 options. 

- **availability**
- **performance**
- **notification**
- **security**
- **capacity**

![Zabbix agent not seen for 5m trigger tag](ch05.6-trigger-01-example-tag.png){ align=center }

_5.6 Zabbix agent not seen for 5m trigger tag_

We can now click on the `Add` button at the bottom of the form and our trigger is done! If we stop our Zabbix agent with `systemctl stop zabbix-agent2` we should get a new problem after 5 minutes.

## Another trigger
Before we stop our chapter here though, let's go through one more trigger example. We also created a new item to monitor the monitoring target CPU utilization. A perfect example for another trigger. Let's create it like the image below.

![CPU utilization over 90% trigger](ch05.7-trigger-02-example.png){ align=center }

_5.7 CPU utilization over 90% trigger_

Don't forget to add the tag `scope:performance` and then add the trigger by clicking the `Add` button at the bottom of the form. 

Breaking down this expression we can see a very similar setup as the previous trigger. But this is not a time based trigger and it will not trigger based on a simple data being received or not. Instead this trigger uses the function `min` over a time period of 3 minutes (`3m`) and with the operator and constant `=>90`.

Simply put, this trigger will be evaluated every time new data is received on the item `proc.cpu.util`. We created that item earlier, with an update interval of 1 minute (`1m`). In a time period of 3 minutes that means we could have received the following.

- **95%**
- **80%**
- **99%**

In this case, the CPU utilization is spiking shortly over 90%. The problem however will not start, because we used the `min` function. Function `min` and `max` are some of the most useful function in Zabbix, as they can be used to filter spikes and drops respectively. Since we used `min` in our expression, the result will be `80%` as that is the minimum (smallest) value in our 3 minute time period. If our data looked like below however, the result would be different.

- **90%**
- **99%**
- **97%**

In this case our minimum value is `90%`, which is indeed equal to or higher than 90 as stated in the expression with `=>90`.

## Conclusion
Triggers in Zabbix can be used to detect problems and automatically resolved them based on the data received on items in Zabbix. We do not have to create triggers for all of our items in Zabbix (see Zabbix dataflow in the previous chapter), but they can be useful on important data. 

A few more tips to keep in mind when working with triggers. Make sure to keep your severities setup correctly, as this is one of the most important parameters for filtering later. They are very important to create alerting correctly later.

It is also a good idea to keep your trigger names short and descriptive. `CPU utilization >90%` is a lot easier to understand than `CPU utilization on the server has been over 90% for the past three minutes`. People are usually in a rush, especially when there is a problem with IT infrastructure. The more reading you have to do in that situation, the less likely you are to see the issue straight away. 

The best tip regarding triggers? A good trigger shows you the problem. A great trigger instantly makes you think of where to go and what to do to solve it.

## Questions

## Useful URLs
