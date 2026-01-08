---
description: |
    Monitor websites and APIs with Zabbix HTTP checks. Track uptime, response codes,
    and content to ensure web services perform reliably and stay online.
tags: [advanced]
---

# HTTP Items

In modern environments, monitoring stops being useful the moment you only check whether a port is open. Applications, platforms, and integrations increasingly communicate over HTTP-based APIs, and if you want to understand whether something is actually working, you need to monitor it at that level.

The HTTP agent item allows Zabbix to act as a native HTTP client. It can send HTTP or HTTPS requests, authenticate, include custom headers, send payloads, and process responses as structured monitoring data. This makes it possible to monitor REST APIs, web services, internal microservices, SaaS integrations, and even the Zabbix API itself — without external scripts or custom agents.

At a beginner level, the HTTP agent answers the question “does this endpoint respond?”.
At an expert level, it answers “is this application behaving correctly, securely, and predictably under real conditions?”.

### How the HTTP Agent Item Works

An HTTP agent item is executed by the Zabbix server or a Zabbix proxy. For each execution, Zabbix performs exactly one HTTP request based on the configured parameters and stores a result derived from the response.

Zabbix does not decide whether a response is “good” or “bad”. It records facts: response codes, headers, and body content. Interpretation is left entirely to preprocessing and triggers. This design makes the HTTP agent item flexible enough to support both simple availability checks and advanced API monitoring.

Internally, Zabbix uses libcurl to perform HTTP and HTTPS requests. This is an important implementation detail. Redirect handling, TLS negotiation, proxy behavior, timeout semantics, and error reporting all follow curl behavior. If a request can be reproduced successfully using the curl command line, it can almost always be made to work in Zabbix with the same parameters.

### Core Request Configuration

Every HTTP agent item starts with a URL. This must be a fully qualified HTTP or HTTPS endpoint, including the scheme and path. Zabbix sends exactly what you configure; it does not infer protocols or rewrite requests.

The **request method** defines how the request is sent. GET is the default and works well for most health checks and read-only API calls. POST, PUT, PATCH, and DELETE are available and commonly required for REST APIs that expect structured input.

When the chosen method supports it, a request body can be defined. The body is sent verbatim. Zabbix does not validate JSON syntax, escape characters, or infer content types. Any formatting errors are passed directly to the remote endpoint.

To ensure the request is interpreted correctly, HTTP headers can be defined explicitly. This is where authentication tokens, API keys, content types, and vendor-specific headers belong. Headers are static per item, which is intentional and has implications for advanced use cases discussed later.

### HTTPS, Certificates, and Trust

HTTPS support for HTTP agent items depends on the environment in which the Zabbix server or proxy runs. HTTP agent items do not maintain their own certificate store. All TLS validation is performed using the system trust store available to the Zabbix process.

If an endpoint uses an internal or private certificate authority, that CA must be trusted by the operating system running Zabbix. Installing a certificate in a browser does nothing for Zabbix.

Disabling certificate verification at the item level may make errors disappear, but it also disables meaningful security checks, including hostname validation. In production environments, this should be treated as a temporary diagnostic step, not a solution.

For APIs that require mutual TLS, Zabbix supports client certificates. The HTTP agent item references the certificate and private key, but the files themselves must exist on disk and be readable by the Zabbix process. Permission issues here often surface as generic TLS failures, so testing with curl using the same certificate and key is strongly recommended.

### Timeouts: What They Really Mean

The timeout parameter of the HTTP agent item is often misunderstood, and the distinction matters in production.

The configured timeout is not a single, shared budget for the entire request. Instead, it is applied to multiple blocking phases of the HTTP transaction, following libcurl behavior.

Conceptually, the timeout applies to:

- DNS resolution
- TCP connection establishment
- TLS handshake (for HTTPS)
- Sending the request
- Waiting for the response
- Receiving the response body

These phases occur sequentially, and each phase can consume up to the configured timeout.

As a result, the total wall-clock execution time can exceed the configured timeout. This is why users sometimes observe behavior that looks like “double timeout”.

For example, with a timeout of 10 seconds:

- Connection and TLS negotiation take 9 seconds
- The server then takes 9 seconds to respond

The request may complete after roughly 18 seconds without violating timeout rules.

This is not a bug. It is a consequence of exposing a single timeout value rather than separate connect and read timeouts.

From an expert perspective, this means the timeout should not be treated as a strict SLA boundary. Always leave margin between expected response time and configured timeout, especially for APIs that perform backend processing.

### What Becomes the Item Value

The HTTP agent item allows you to choose what part of the HTTP response is stored as the item value.

Zabbix can store the response body, the response headers, or the HTTP status code. This choice has architectural implications.

Storing the full response body allows multiple dependent items to extract different values from a single request. Storing only the status code creates a lightweight availability or correctness check with minimal processing overhead.

At scale, choosing the correct retrieval mode reduces API load, minimizes network traffic, and keeps Zabbix performance predictable.

### Preprocessing and Structured Data

Most APIs return structured data, commonly JSON. Preprocessing allows Zabbix to extract specific values using JSONPath expressions, regular expressions, or text transformations.

A common expert pattern is to create one HTTP agent item that retrieves structured data and several dependent items that extract individual metrics. This avoids repeated API calls and ensures consistency between related values.

Preprocessing is performed entirely on the Zabbix side after the request completes and does not affect the request itself.

### Practical Example: Monitoring the Zabbix API

The Zabbix API itself is a good example of HTTP agent usage because it is strict, well-defined, and widely deployed.

#### Authenticating to the API

The Zabbix API uses JSON-RPC over HTTP. Authentication is performed by calling the user.login method.

The endpoint is typically:

```
https://zabbix.example.com/api_jsonrpc.php
```

The HTTP agent item is configured with a POST request and the following body:

```
{
  "jsonrpc": "2.0",
  "method": "user.login",
  "params": {
    "username": "zabbix_monitor",
    "password": "strongpassword"
  },
  "id": 1
}
```

The `Content-Type` header must be set to `application/json`. Without it, the API will reject the request.

The response looks like this:

```
{
  "jsonrpc": "2.0",
  "result": "a1b2c3d4e5f6...",
  "id": 1
}
```

Using JSONPath preprocessing with $.result, the authentication token can be extracted.

#### Retrieving Data

With a valid token, further API calls include the token in the auth field. For example, retrieving the Zabbix version:

```
{
  "jsonrpc": "2.0",
  "method": "apiinfo.version",
  "params": {},
  "auth": "<auth_token>",
  "id": 2
}
```

The returned version string can be stored as a text item or evaluated by triggers. While this example is simple, the same pattern applies to retrieving problem counts, host statistics, or internal API data.

HTTP agent items are best suited for stateless, deterministic API calls. Token reuse and session orchestration are intentionally limited and should be handled externally if required.

### Runtime Debugging and Logging

Debugging HTTP agent items does not require restarting the Zabbix server or proxy. Zabbix supports runtime log level control, including per-process adjustments.

HTTP agent items are executed by HTTP poller processes. To debug HTTP agent behavior specifically, logging should be increased only for those processes.

This is done using runtime control commands:

```
zabbix_server -R log_level_increase=http poller
```

or on a proxy:

```
zabbix_server -R log_level_decrease=http poller
```

This approach allows detailed libcurl-level diagnostics without restarting services or flooding logs from unrelated processes.

When debug logging is enabled, the Zabbix log will show detailed information about DNS resolution, TLS negotiation, certificate validation, proxy usage, and timeout behavior. These messages are the authoritative source of truth when troubleshooting HTTP agent issues.

Always enable debugging on the node that actually executes the item. If a host is monitored via a proxy, increasing logging on the server will show nothing.

### HTTP Agent Item Parameters Reference

The table below summarizes the key HTTP agent parameters and their purpose.

| Parameter           | Description                                                           |
|:---                 |:---                                                                  |
| URL                 | Full HTTP or HTTPS endpoint Zabbix will request.                      |
| Request method      | HTTP method used for the request (GET, POST, PUT, PATCH, DELETE).     |
| Request body        | Optional payload sent verbatim with supported methods.                |
| HTTP headers        | Custom headers such as authentication tokens or content types.        |
| Timeout             | Maximum duration applied per blocking phase of the request lifecycle. |
| Follow redirects    | Enables or disables automatic redirect handling.                      |
| HTTP authentication | Built-in HTTP authentication supported by libcurl.                    |
| Proxy               | Optional HTTP proxy used for the request.                             |
| Retrieve mode       | Determines whether body, headers, or status code is stored.           |
| SSL verify peer     | Enables or disables server certificate validation.                    |
| SSL verify host     | Enables or disables hostname verification.                            |
| Client certificate  | Client certificate for mutual TLS authentication.                     |
| Client key          | Private key associated with the client certificate.                   |
| Preprocessing       | Transforms responses into usable metrics.                             |


## Conclusion

The HTTP agent item is one of the most powerful and misunderstood tools in Zabbix. It allows Zabbix to observe systems the same way applications and users do: through HTTP.

Used casually, it checks availability. Used deliberately, it becomes a precise, scalable, and secure API monitoring mechanism.

Understanding how it behaves internally — how timeouts are applied, how certificates are validated, and how logging really works — is what turns it from a feature into a tool.

Or, as every experienced API engineer eventually learns:

**_“HTTP is simple — until you assume it is.”_**


## Questions

## Useful URLs
