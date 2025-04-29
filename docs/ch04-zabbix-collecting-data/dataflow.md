# Dataflow
The Zabbix dataflow is a concept that is meant to guide us through the various different
stages of building up our monitoring system. In the end, when building a Zabbix
environment we want to achieve a few things:

- **Collected metrics** are stored, can be easily found and are visualised
- **Problems** are created from our data and shown in the frontend
- **We take action** on important problems by sending a message or executing commands

Those three parts of the Zabbix dataflow in our Zabbix environment can be easily
identified as:

- **Items** 
- **Triggers**
- **Actions**

But when we look at `Items` specifically, it's also possible to alter our data before
storing the metrics in Zabbix. This is something we do with a process called pre-processing,
which will take the collected data and change it before storing it in the Zabbix database.
Our dataflow in the end then looks as such:

![Basic dataflow](ch04.1-dataflow-basic.png){ align=left }
*4.1 Zabbix basic dataflow*

This gives us a very basic understanding of what steps we have to go through in
Zabbix to get from data being collected to alerts being sent out. Very important
to us Zabbix administrators, as we need to go through these steps each time we want
to end up with a certain type of monitoring.

But, now that we have identified what parts to look at, let's dive a bit deeper
into what each of those parts does. Logically, that would start with `Items` looking
at the image above. But before we can start discussing `Items` there is another 
concept we need to understand.

## Hosts
To create `Items` in Zabbix, we first need to create `Hosts`. A `host` is nothing
more than a container (not the Docker kind), it's something that contains `Items`,
`Triggers`, `graphs`, `Low Level Discovery` rules and `Web scenarios`. All of these
various different entities are contained within our **Hosts**.

Often times, Zabbix users and administrators make the misconception here that a
*`host`* always represents a physical or virtualised host. But in the end, hosts
are nothing more than a representation of a `monitoring target`. A monitoring
target is something we want to monitor. This can be a server in your datacenter,
a virtual machine on your hypervisor, a Docker container or even just a website.
Everything you want to monitor in Zabbix will need a host and the host will then
contain your monitoring configuration on its entities.

## Items
`Items` in Zabbix are Metrics. One `Item` is usually a single metric we'd like to
collect, with the exception being bulk metric collection which we will discuss
later on in the book. When we want to create our `Items` we can do this on a host
and we can actually create an unlimited amount of `Items` on a host.

### Preprocessing
But we cannot stop there with `Items` just yet, as we also mentioned an additional
part of our dataflow. It is possible to change the collected metric on an item before
storing it into the Zabbix database. We do this with a process called preprocessing. 

Preprocessing is something we add onto our items when creating the configuration
of such items. It is a part of the item, but not mandatory on every single item.

General rule:

- Collect metric and store as-is in the database? **No preprocessing**
- Collect metric and change before storing in the database? **Add preprocessing**

We will discuss this in more detail later on in the book as well.

## Triggers
With all of the collected metrics, we can now also start to create triggers if we
would want to. A trigger is Zabbix is nothing more than a bit of configuration on
our host, which we will use to define thresholds using metrics collected on items. 

A trigger can be setup to use the data collected on an item in a logical expression.
This logical expression will define the threshold and when data is received on the
item(s) used in the logical expression the trigger can go or stay in on of two states:

- **PROBLEM**: When the logical expression is TRUE
- **OK**: When the logical expression is FALSE

This is how we define if our data is in a good or a bad state.

### Events
When we discuss triggers however, we cannot skip past the Events. Whenever a trigger
changes state, for example it was in OK state and goes into the PROBLEM state, then
Zabbix will create a new Event. There's three types of these events created by our
triggers:

- **Problem event**: When the trigger goes from OK to PROBLEM
- **Problem resolution event**: When the trigger goes from PROBLEM to OK
- **Problem update event**: When someone manually updates a problem

These problem events are what you will see in the frontend when you navigate to
`Monitoring` | `Problems`, but they are also very important in the next step in
the Zabbix dataflow `Actions`.

## Actions
Actions are the last step in our Zabbix dataflow and they are kind of split into
two parts. An action consists of `Conditions` and `Operations`. This is going to
be important in making sure the action executes on the right time (conditions)
and executes the right activity (operations). 

What happens is, whenever a problem event in Zabbix is created it is sent to every
single problem action in our Zabbix environment. All of these action will then
check the event details like what host did it come from, with which severity, when
did it start, which tags are present. These event details are then checked against
the action conditions and only when the conditions match will the operations be executed.
The operation can then be something like, send a message to Microsoft Teams or
Telegram. But an operation could also be, execute the reboot command on this host.

As you can imagine, the conditions will be very important to make sure that operation
on that action are only executed when we specifically want it to. We do not want to
for example reboot a host without the right problem being first detected.

## Conclusion

To summarize, all the steps in the dataflow work together to make sure that you can
build the perfect Zabbix environment. When we put the entire dataflow together it
looks like the image below.

![Detailed dataflow](ch04.2-dataflow-detailed.png){ align=left }
*4.2 Zabbix detailed dataflow*

Here we can see the various steps coming together.

- We have our `Hosts` container our `Items` and `Triggers`. 
- Our `Items` are collecting metrics
- The `Triggers` are using data from `Items` to detected problems and create problem `Events`.
- If a problem `Event` matches the *Conditions* on an `Action` the *Operations* can be executed

Important to note here is that if an item is collecting metrics, it doesn't necessarily
need to have a trigger attached to it. The trigger expression is a separate configuration
where we can choose which items we want to define thresholds on. In the end, not
ever item needs to start creating problems. We can also see that we can use several
items or event several items from different hosts in a single trigger.

The same is the case for our events. Not every event will match the conditions on
an action. In practice, this means that some problems will only show up in your
Zabbix frontend, while other might go on to send you an alert message or even execute
commands or scripts. A single event can also match the conditions on multiple actions,
since we mentioned that all events are always send to all action for evaluation.
This can be useful, for example if you want to split you messaging and your script
execution in different action to keep things organised.

Now that we understand the various parts of our Zabbix dataflow we can dive deeper into creating the configuration for the steps in the dataflow.


## Questions

## Useful URLs
