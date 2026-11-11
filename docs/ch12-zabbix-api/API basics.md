---
description: |
    Learn the fundamentals of the Zabbix 8.0 API, including authentication,
    API requests, permissions, and automating common monitoring tasks.
tags: [beginner]
---

# API basics


The Zabbix API lets us do from a script or an application almost everything we
normally do in the frontend: read and change the configuration, and read history
and trend data. It is not the usual way to send monitoring values to Zabbix;
for that we typically use Zabbix sender with trapper items, agents or other data
collection methods. It is widely used to build new applications on top of Zabbix,
to integrate Zabbix with third-party software and to automate routine tasks.

In this section we cover the basics:
what the API is, how to connect, how to authenticate, the calls we need every
day and what changed in Zabbix 8.0. The use cases in the next section build on this.

## What is the Zabbix API

The Zabbix API is an HTTP-based API that ships as part of the web frontend. There
is nothing extra to install: if the frontend works, the API works. It uses the
JSON-RPC 2.0 protocol, which means two things:

!!! info ""

    - The API is a set of separate methods that we call by name.
    - Requests and responses are encoded in JSON.

Methods are grouped into APIs. In `host.get`, `host` is the API and `get` is the
method. Most APIs offer `get`, `create`, `update` and `delete`, but some have a
different set of methods, for example `user.login` or `event.acknowledge`.

What we can see or change through the API depends on the user type, the user role
and the user group permissions of the user making the call. These are the same
rules as in the frontend.

## Anatomy of a request

Every call is an HTTP POST request to the file `api_jsonrpc.php` in the frontend
directory. The `Content-Type` header must be one of `application/json-rpc`,
`application/json` or `application/jsonrequest`.

The body of the request contains four properties:

| Property | Description |
| --- | --- |
| `jsonrpc` | The protocol version. Always `"2.0"`. |
| `method` | The method we call, for example `host.get`. |
| `params` | The parameters we pass to the method. |
| `id` | An identifier of our choice. The response returns the same value. When it is left out, the API treats the request as a notification. |

The response contains `jsonrpc`, `id` and either a `result` or, when something went wrong, an `error`.

### Check the version first

The simplest call is `apiinfo.version`. It is a good first test because the example
in the official documentation calls it without any authentication:

!!! example "Example"

    ```bash
    ZABBIX_URL="https://zabbix.book.the/api_jsonrpc.php"
 
    curl --request POST \
      --header 'Content-Type: application/json-rpc' \
      --data '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}' \
      $ZABBIX_URL
    ```

The response returns the version of our Zabbix server:

!!! example "Example response"

    ```
    {
        "jsonrpc": "2.0",
        "result": "8.0.0",
        "id": 1
    }
    ```

Since Zabbix 2.0.4 the API version is the same as the Zabbix version. That makes
`apiinfo.version` useful in scripts that must behave differently on different
releases.

!!! tip

    If this call fails, nothing else will work. Check the URL, the web server and the
    TLS certificate first. In a lab with a self-signed certificate `curl --insecure`
    works, but do not use it in production.

## Authentication

All other calls need authentication. There are two common ways to authenticate:

| Method | How | Use it for |
| --- | --- | --- |
| API token | Created in the frontend (`Users` \| `API tokens`) or with the `token` API. Valid until it expires or is disabled. | Scripts, integrations, webhooks and items: everything that runs unattended. |
| Session token | Returned by `user.login` after sending a username and password. | Short-lived interactive scripts. |

For automation we use an API token. A password in a script is one more secret to
protect and rotate. API tokens can be managed and revoked individually; session
tokens are tied to a login session and can be invalidated using `user.logout`.

### Creating an API token

1. Create a dedicated service user for the API and give it a user role. The next section does this step by step.
2. Go to `Users` | `API tokens` and press **Create API token**.
3. Fill in a **Name**, select the **User** and, for anything beyond a lab, set an **Expiry date**.
4. Press **Add** and copy the **Auth token**. It is only shown now. If we lose it, we have to regenerate the token, and the old value stops working.

A token belongs to exactly one user, and that user cannot be changed afterwards.

### Logging in with user.login

If we prefer a session, we call `user.login` with a username and password:

!!! info ""

    ```bash
    curl --request POST \
      --header 'Content-Type: application/json-rpc' \
      --data '{"jsonrpc":"2.0","method":"user.login","params":{"username":"Admin","password":"<password>"},"id":1}' \
      $ZABBIX_URL
    ```

The result is the authentication token for the session:

!!! info ""

    ```json
    {
        "jsonrpc": "2.0",
        "result": "<session token>",
        "id": 1
    }
    ```

### Sending the token

We send the token, API token or session token, in the `Authorization` header of every request:

!!! info ""

    ```
    Authorization: Bearer <token>
    ```

!!! warning

    Header names are case-insensitive, and the header also works in cross-origin (CORS)
    requests. If the API keeps answering that we are not authorised although the token
    is correct, the web server may not forward the header to PHP. See *Authorization
    header forwarding* in the Zabbix known issues: https://www.zabbix.com/documentation/8.0/en/manual/installation/known_issues#authorization-header-forwarding
    Older versions also accepted the token inside the JSON body. The 8.0 documentation
    only describes the `Authorization` header and, for code that runs inside the frontend
    (modules and custom widgets), the `zbx_session` cookie.

### Allow the user to use the API

A valid token is not enough. The role of the user must allow API access:

1. Go to **Users** | **User roles** and open the role.
2. In the section **Access to API** set **Enabled**.
3. Under **API methods** choose an **Allow list** or a **Deny list** and add the
   methods. Wildcards work: `*` is any method, `dashboard.*` is every method of
   the dashboard API and `*.export` is every export method.

Two more details matter:

- In Zabbix 8.0 an **Allow list** without any method denies access to all API
  methods. A **Deny list** without any method allows all methods that are available
  for the user type.
- Switching off an action in the role also switches off the related API methods.
  For example, clearing **Manage API tokens** revokes all `token.*` methods.

!!! warning

    In Zabbix 8.0, API access is disabled by default when creating user roles.
    After upgrading, verify the effective API access settings of existing roles
    used by integrations; do not assume that every existing role has been disabled.
    If a call fails with a permission error while the token is valid, check the
    role of the API user first.

    This is also where we apply the principle of least privilege. A service user
    that only reads hosts does not need `*`. An allow list with `host.get` is enough
    for that method, provided the user also has permission to view the relevant
    hosts.

### API methods versus object permissions

Permission to call an API method is not the same as permission to access the objects
it returns. A role may allow `host.get`, but a user with no read access to the
relevant host groups can still receive an empty result. Likewise, write operations
require the appropriate permissions on the target objects. When troubleshooting
an empty response, check both the API method permissions in the user role and the
user group permissions for the affected hosts or templates.

## Everyday calls

From here on we assume the token is stored in a shell variable:

!!! info ""

    ```text
    ZABBIX_API_TOKEN="<your_api_token>"
    ```

### Reading data with get

Most object APIs have a `get` method, but not all APIs do (for example, `apiinfo`
and session-related methods under `user`). This request returns the ID, the
name and the interfaces of all hosts:

!!! example "Example"

    ```bash
    curl --request POST \
      --header 'Content-Type: application/json-rpc' \
      --header "Authorization: Bearer ${ZABBIX_API_TOKEN}" \
      --data '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid","host"],"selectInterfaces":["interfaceid","ip"]},"id":2}' \
      $ZABBIX_URL
    ```

The `result` is an array with one object per host:

!!! example "Example output"

    ```json
    {
        "jsonrpc": "2.0",
        "result": [
            {
                "hostid": "10084",
                "host": "Zabbix server",
                "interfaces": [
                    {
                        "interfaceid": "1",
                        "ip": "127.0.0.1"
                    }
                ]
            }
        ],
        "id": 2
    }
    ```

Three things to remember:

- **Always list the properties we need in `output`.** The default is `extend`,
  which returns everything. That is slower and returns more data than we need.
- **The ID of the object is always in the response**, even if we do not ask for
  it in `output`.
- “Values are always returned as strings or arrays. A hostid of 10084 is the string
  "10084", and a status of 0 comes back as "0".”

The `select...` parameters, like `selectInterfaces` above, add related objects
to the result in the same call.

These parameters are supported by all `get` methods:

| Parameter | Description |
| --- | --- |
| `output` | The properties to return. |
| `filter` | Returns only exact matches. For example `{"host":["Zabbix server"]}`. |
| `search` | Returns case-insensitive pattern matches, a `LIKE "%...%"` search by default. |
| `searchByAny` | Matches any of the supplied search criteria rather than requiring all of them. |
| `searchWildcardsEnabled` | Allows `*` as a wildcard in search values. |
| `startSearch` | Matches from the start of the field rather than anywhere in it. |
| `excludeSearch` | Returns the results that do not match the `search`. |
| `limit` | Limits the number of records returned. |
| `sortfield`, `sortorder` | Sorts the result. |
| `countOutput` | Returns the number of records instead of the data. |
| `editable` | Returns only objects the user has write permissions to. |
| `preservekeys` | Returns a JSON object keyed by object IDs instead of a JSON array. |

`filter` does not support properties of the `text` type, and `search` only works on `string` and `text` properties.

!!! note 

    The ID `0` is reserved. It is used to filter on and to remove references.
    To remove the proxy from a host, set `proxyid` to `"0"`.

### Creating objects

The `create` methods return the IDs of the new objects. This request creates an
item on the host with ID 10084, using the host and interface IDs from the
previous result:

!!! example "Example"

    ```json
    {
        "jsonrpc": "2.0",
        "method": "item.create",
        "params": {
            "name": "Free disk space on /",
            "key_": "vfs.fs.size[/,free]",
            "hostid": "10084",
            "type": 0,
            "value_type": 3,
            "interfaceid": "1",
            "delay": 30
        },
        "id": 3
    }
    ```

The response contains the ID of the new item:

!!! example "Example output"

    ```json
    {
        "jsonrpc": "2.0",
        "result": {
            "itemids": [
                "24759"
            ]
        },
        "id": 3
    }
    ```

`create` and `update` methods also accept an array of objects, so one call can
create or update many items, triggers or hosts. Fewer calls means less load
on the frontend and the database.

### Updating and deleting objects

An `update` call needs the ID of the object and the properties to change. This
request enables an item by setting its status to `0`:

!!! example

    ```json
    {
        "jsonrpc": "2.0",
        "method": "item.update",
        "params": {
            "itemid": "24759",
            "status": 0
        },
        "id": 4
    }
    ```

The `delete` methods take an array of IDs. Be careful with them: there is no
confirmation dialog and no undo.

### Error handling

When a call is wrong, the response has an `error` instead of a `result`. This is
what happens when we create a host without the mandatory `groups` parameter:

!!! example "Example output"

    ```json
    {
        "jsonrpc": "2.0",
        "error": {
            "code": -32602,
            "message": "Invalid params.",
            "data": "No groups for host \"Linux server\"."
        },
        "id": 7
    }
    ```

The `error` object has a `code`, a short `message` and a more detailed `data`
text. Errors also happen on a session timeout and when we use an object that does
not exist, so every script must check for `error` and not only read `result`.

### Troubleshooting common API errors

| Symptom | What to check |
| --- | --- |
| `Not authorized` | Token validity and whether the web server forwards the `Authorization` header to PHP. |
| Permission error for a method | API access and the method allow/deny list in the user role. |
| Empty `host.get` result | Host group permissions and any filters in the request. |
| `Invalid params.` | Required properties, parameter names and accepted values for the method. |
| HTTP 404 | Frontend URL and the path to `api_jsonrpc.php`. |
| HTTP 500 | Web server and PHP logs; the request may not have reached the API successfully. |

A JSON-RPC error can be returned with an HTTP success status. Always inspect the
JSON response for an `error` object rather than relying only on the HTTP status code.

## Good practice

- **Use a dedicated service user** with a role that allows only the methods the
  script needs.
- **Use API tokens with an expiry date** and rotate them. Regenerate a token immediately
  when it may have been exposed.
- **Keep tokens out of scripts and repositories.** For integrations running inside
  Zabbix, use a user macro of the type **Secret text** where supported. For external
  scripts, use a suitable secrets manager or a protected environment variable.
  The shell variable in our examples is for illustration; do not hardcode a
  production token.
- **Use HTTPS.** A token in a header is a password on the wire.
- **Ask only for what we need.** The API is served by the web frontend, so every
  call is handled by the web server, PHP and the database. Use `output`, `filter`,
  `limit` and bulk calls.
- **Check the version** with `apiinfo.version` when a script must run on more
  than one release.

### Compatibility

Zabbix guarantees backward compatibility of the API inside a major version. Between
major versions a feature is usually first marked as deprecated and removed in the
release after that, but sometimes a feature is removed without warning. Never rely
on deprecated features, and read the API changelog before every upgrade.

## What is new in Zabbix 8.0

This is a selection of the changes in the official release notes and in the API
changelog *Changes from 7.4 to 8.0*. Check the full list before you upgrade a
production environment: [https://www.zabbix.com/documentation/8.0/en/manual/api/changes](https://www.zabbix.com/documentation/8.0/en/manual/api/changes)

### Breaking changes

Scripts that use these methods or behaviours need to be changed:

| Change | What to do |
| --- | --- |
| `host.massupdate`, `hostgroup.massupdate`, `template.massupdate` and `templategroup.massupdate` are removed. | Use `update`, and `massadd` or `massremove` where needed. |
| `hostinterface.create`, `update`, `delete`, `massadd` and `massremove` are removed. Only `hostinterface.get` is left. | Manage interfaces through the `host` methods. |
| `history.get` has a new parameter `maxValueSize`. Values are truncated to 64 KiB unless it is set. | For items with a binary value (`history` type 5), set `maxValueSize` to `null`. |
| In a role, an **Allow list** without methods now denies all API methods. new roles have API access disabled by default, and the role action `select_server_for_monitoring` has been added. | Check the roles of every API user after the upgrade. |

### New APIs

| API | Methods | Purpose |
| --- | --- | --- |
| `apmlog`, `apmmetric`, `apmspan`, `apmtrace` | `get` | Read the application performance monitoring (APM) data: logs, metrics, spans and traces. |
| `ceprule` | `create`, `delete`, `get`, `update`, `resettimewindows` | Manage complex event processing rules. |
| `device` | `get`, `offboard` | Work with the devices registered for the Zabbix mobile app. |
| `serverinfo` | `get` | Retrieve Zabbix server information. |

The `proxy` API gets the `selectApm` parameter in `proxy.get` and the `apm` parameter in `proxy.create` and `proxy.update`.

### New and extended objects

- **JSON values.** A new JSON value type (`6`) for `history.get`, for the `value_type`
  of items and item prototypes, and `64` for the `item_value_type` of connectors.
- **Telemetry query items.** The item and item prototype `type` `24` with the new
  properties `query`, `time_shift`, `lookback_limit` and `granularity`. Proxies
  get `timeout_telemetry_query`.
- **Push media type.** A new media type `type` `5`.
- **Maintenance.** New `triggers` and `event_names` properties, new `triggerids`, `selectTriggers`
  and `selectEventNames` parameters in `maintenance.get`, and the operators *Does
  not equal* and *Does not contain* for `problem_tags`.
- **Inherited tags.** New `inheritedTags` and `selectInheritedTags` parameters
  in `item.get` and `httptest.get`, and `selectInheritedTags` in `itemprototype.get`
  and `hostprototype.get`.
- **Host interfaces.** A new `retries` property in the `details` of host interfaces
  and host prototypes, and user macro support for `max_repetitions`.
- **Configuration import and export.** New `returnMissingObjects` parameter and a
  `dashboards` rule in `configuration.import` and `configuration.importcompare`,
  and `global_regexes` for export, import and compare.
- **Acknowledgements.** `selectAcknowledges` in `event.get` and `problem.get` now
  has the property `maintenanceid`.
- **Dashboards.** A new `scatterplot` widget type and new fields for the graph,
  pie chart, top items and geomap widgets.
- **Actions.** The condition type `29` (proxy group) for discovery and
  autoregistration actions.
- The user group API gained filtering on APM resource attributes, and complex
  event processing can now also run its operations when an event is closed.

## Questions

- What protocol does the Zabbix API use, and which HTTP method is required to send API requests?
- What is the difference between authenticating with an API token and using user.login?
- How do user roles and host group permissions affect what a user can access through the Zabbix API?
- What is the purpose of the output, filter, and selectInterfaces parameters in a host.get request?
- What important API changes were introduced in Zabbix 8.0 that could affect existing scripts and integrations?

## Useful URLs

- [https://www.zabbix.com/documentation/8.0/en/manual/api](https://www.zabbix.com/documentation/8.0/en/manual/api)
- [https://www.zabbix.com/documentation/8.0/en/manual/api/reference](https://www.zabbix.com/documentation/8.0/en/manual/api/reference)
- [https://www.zabbix.com/documentation/8.0/en/manual/api/reference_commentary](https://www.zabbix.com/documentation/8.0/en/manual/api/reference_commentary)
- [https://www.zabbix.com/documentation/8.0/en/manual/api/changes](https://www.zabbix.com/documentation/8.0/en/manual/api/changes)
