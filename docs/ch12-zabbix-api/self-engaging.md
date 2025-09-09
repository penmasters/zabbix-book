# Self-engaging

Welcome to Zabbix API self engaging methods. All upcoming chapters will address the tools available to allow software to re-engage with itself. It is like developing a small service(s) which runs on the top of Zabbix and do exactly the tasks we told to do. This is like simulating an extra employee in the company.

## API variables

To start to engage with Zabbix API:

Create a dedicated service user. Go to "Users" => "Users", click "Create user", set username "api", groups "No access to the frontend", Assign user role "Super admin role" which will automatically give user type "Super admin".

![Create API user](ch12-create-api-user.png)

Permissions tab:

![API user permissions](ch12-api-user-permissions.png) 


Under "Users" => "API tokens" press "New API token", assign user "api", can uncheck "Set expiration date and time", press "Add". Copy macro to clipboard.

![Add token to user object](ch12-token-added-to-user.png) 


Visit "Administration" => "Macros" and install macro. To simulate all upcoming chapters faster, consider running token in plain text:

```yaml
{$ZABBIX.API.TOKEN}
```
value: dafa06e74403ca317112cf5ddd3357b2ad2a2c5cb348665f294a53b4058cfbcf


Install address of the frontend by using:

```yaml
{$ZABBIX.URL}
```
value: https://zabbix.book.the

Later throughout chapters, we will use a reference on the API endpoint in a format of:

```yaml
{$ZABBIX.URL}/api_jsonrpc.php
```

All 3 variables together:

![User macros](ch12-user-macro-global.png) 

## First API call

If you feel new to Zabbix API, try this curl example from Zabbix frontend server:

```bash
ZABBIX_API_TOKEN="dafa06e74403ca317112cf5ddd3357b2ad2a2c5cb348665f294a53b4058cfbcf"
ZABBIX_URL="https://zabbix.book.the/api_jsonrpc.php"
curl --insecure --insecure --request POST \
--header 'Content-Type: application/json-rpc' \
--header 'Authorization: Bearer '$ZABBIX_API_TOKEN \
--data '{"jsonrpc":"2.0","method":"proxy.get","params":{"output":["name"]},"id":1}' \
$ZABBIX_URL
```

Setting Bearer token in header is available and recommended since 7.0.
This API example is tested and works with Zabbix 7.0 versions.

Setting a static token is available since 6.0. In version 6.0, the auth token is not in header, but inside body like this:
```bash
ZABBIX_API_TOKEN="976e481c235563359418200cc6e24b6c49d8470d6653fd1b2cc1a0395077a938"
ZABBIX_URL="https://zabbix.book.the/api_jsonrpc.php"
curl --insecure --insecure --request POST \
--header 'Content-Type: application/json-rpc' \
--data '{"jsonrpc":"2.0","method":"proxy.get","params":{"output":["host"]},"auth":"'"$ZABBIX_API_TOKEN"'","id":1}' \
$ZABBIX_URL
```

## HTTP agent

An item type "HTTP agent" is fastest way to run a single Zabbix API call and retrieve back result. This is possible since Zabbix 6.0 where configuring a static session token comes possible. Upcoming example is reproducible 1:1 on version 7.0.

!!! info "Use case"

    Every time an email arrives user would love to see all host groups the host belongs.

---

!!! note "Implementation"

    Use {HOST.HOST} as an input for Zabbix API call.
    Use "host.get" method to find out about membership.
    Format reply in one line, store it in inventory.

---

Create new HTTP agent item. Set URL:

```yaml
{$ZABBIX.URL}/api_jsonrpc.php
```

```json
{
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {
        "output": ["hostgroups"],
        "selectHostGroups": "extend",
        "filter": {
            "host": [
                "{HOST.HOST}"
            ]
        }
    },
    "id": 1
}
```

![User macros](ch12-host-get.png) 

Preprocessing

JSONPath:
```yaml
$.result[0].hostgroups[*].name
```

JavaScript:
```javascript
return JSON.parse(value).join(',');
```

![User macros](ch12-host-get-preprocessing.png) 


!!! warning "Warning"

    If data collection is done on Zabbix proxy, it is possible the proxy is incapable to reach Zabbix frontend server due to limitation in firewall. 

---

Here is how to check if frontend is available:

```bash
curl -kL "https://zabbix.book.the"
curl -kL "https://zabbix.book.the" | grep Zabbix
```

## Action operation webhook

This web hook is intended to run in automated fashion.

!!! info "Use case"

    Due to reason of impossible to find a recovery expression for trigger, need to close the event automatically after certain minutes/hours.

---

To implement, visit "Alerts" => "Scripts"

Set name:

```yaml
Automatically close problem
```

Scope: "Action operation", Type: "Webhook"

Parameters:
```yaml
eventid = {EVENT.ID}
msg = Auto closed by API
api = {$ZABBIX.API.TOKEN}
url = {$ZABBIX.URL}/api_jsonrpc.php
```

Script:
```javascript
var params = JSON.parse(value);

var request = new HttpRequest();
request.addHeader('Content-Type: application/json');
request.addHeader('Authorization: Bearer ' + params.token);

var allGlobalMacrosBefore = JSON.parse(request.post(params.url,
    '{"jsonrpc":"2.0","method":"event.acknowledge","params":{"eventids":"'+params.eventid+'","action":1,"message":"'+params.msg+'"},"id":1}'
)).result;

return params.eventid;
```

![Auto close problem](ch12-zabbix-api-auto-close-problem-webhook.png) 



This Webhook has been tested with 7.0


## Preprocessing

After collecting data it's possible to create dependent item, use a JavaScript preprocessing step and utilize Zabbix API call to rename field(s).

!!! info "Use case"

    Replace host "Visible name" with a data currently received by item

---

!!! note "Implementation"

    Upon data receival, run a single Zabbix API call to forward and replace the value of host visible name

---

P.S. As a proof of concept this sequence sounds exciting and useful.

However the intention here is only to show possibilities.

It's generally not good to run this solution on more than 9 hosts. There are many drawback:

1) Proxies need to access Zabbix frontend

2) Even if we would use item throttling "Discard unchanged", the restarts of data collector components (zabbix-proxy, zabbix-server) will clear up throttling cache and trigger an execution of API call.

The next chapter will present same use case and better solution.

## Script item

The "Script" item is handy to take data from step 1 and use it as an input for step 2.

Configuration-wise, the "Script" item will give an elegant looking solution where all base variables are kept outside the script.

!!! info "Use case"

    Replace host "Visible name" with a data coming to an item

---

!!! note "Implementation"

    Every host, by default, will store the intended host visible name inside inventory.
    The "Script" item (without running extra API calls) will compare inventory with host visible name.
    If inventory field is empty, the visible field will not be replaced.

---

This is maximum efficiency to run a single API call once per day. If nothing needs to be done, API calls will not be wasted. No SQL UPDATE operations for the Zabbix database :)

```javascript
// load all parameters in memory
var params = JSON.parse(value);

// new API call
var request = new HttpRequest();
request.addHeader('Content-Type: application/json');
request.addHeader('Authorization: Bearer ' + params.token);

// obtain Bare minimum fields: host "Visible name" and inventory "Name"
var hostData = JSON.parse(request.post(params.url,
    '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid","inventory","name","host"],"selectInventory":["name"]},"id":1}'
)).result;

var listOfErrors = [];
var listOfSuccess = [];

// iterate through host list
for (var h = 0; h < hostData.length; h++) {

    // validate if inventory "name" element exists
    if (typeof hostData[h].inventory.name !== 'undefined') {

        // if "name" field is not empty
        if (hostData[h].inventory.name.length > 0) {

            // compare if inventory name is not the same as host visible name
            if (hostData[h].inventory.name !== hostData[h].name) {

                Zabbix.Log(params.debug, 'Host visible name field, host: ' + hostData[h].name + ' need to reinstall visible name');

                // formulate payload for easy printing for troubleshoting
                payload = '{"jsonrpc":"2.0","method":"host.update","params":' + JSON.stringify({
                    'hostid':hostData[h].hostid,
                    'name':hostData[h].inventory.name
                    }) + ',"id":1}';

                Zabbix.Log(params.debug, 'Host visible name field, payload: ' + payload);

                try {
                    hostUpdate = JSON.parse(request.post(params.url, payload));

                    // save API errors, like name already exists:
                    if (typeof hostUpdate.error !== 'undefined') { listOfErrors.push({'error':hostUpdate.error,'origin':hostData[h].host}) }

                    // save successfull operation:
                    if (typeof hostUpdate.result !== 'undefined') { listOfSuccess.push(hostUpdate.result) }

                }
                catch (error) {
                    throw 'noo';
                }

            }

        }

    }

}

return JSON.stringify({ 'listOfSuccess': listOfSuccess, 'errors': listOfErrors });
```

The chances of having duplicate host names are still possible. In this case, the script will continue to parse all hosts and will retry update operation. Ensure $.listOfErrors in output is an empty list.

This is tested and works with Zabbix 7.0
