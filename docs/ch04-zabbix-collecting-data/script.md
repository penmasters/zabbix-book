---
description: |
    Extend monitoring flexibility with Zabbix item scripts. Run custom scripts to
    collect unique metrics and automate complex data gathering tasks.
tags: [expert]
---

# Script item

Zabbix offers several item types for gathering data, but sometimes you need logic,
multiple API calls, or data manipulation that's too complex for simple preprocessing.
**Script items** fill that gap, they run JavaScript directly on the Zabbix Server
or Proxy and can fetch, process, and return data exactly how you need it.

In this chapter, we'll explore what script items can do through **three working examples**:

1. Checking GitHub repository stars via public API
2. Monitoring SSL certificate expiry using the SSL Labs API
3. Querying the Zabbix API for problem triggers

---

## Understanding Script items

Script items execute JavaScript in the Zabbix backend using the built-in Duktape
engine.

They're ideal when you need:

* HTTP or API calls that return JSON/XML data
* Conditional logic or loops
* Chained API requests (login + data fetch)
* Monitoring without deploying an agent

### Common JavaScript objects

Zabbix provides several JavaScript objects for script items:

| Object                              | Purpose                                    |
| :---------------------------------- | :----------------------------------------- |
| `HttpRequest`                       | Perform HTTP(S) requests                   |
| `Zabbix.log(level, message)`        | Log messages (level 4=debug, 3=info, etc.) |
| `JSON.parse()` / `JSON.stringify()` | Handle JSON data                           |
| `parameters.<name>`                 | Access item parameters defined in the UI   |


**Limits:** up to 10 `HttpRequest` objects per run; typical timeout ≤ 30 seconds (depending on item settings).

[https://www.zabbix.com/documentation/current/en/manual/config/items/preprocessing/javascript/javascript_objects](https://www.zabbix.com/documentation/current/en/manual/config/items/preprocessing/javascript/javascript_objects)

---

## Example 1 – Query a public API (GitHub repository stars)

### Goal

Return the current number of **stars** for a given GitHub repository using the REST API.

---

### Item setup

| Field               | Value                                                                |
| :------------------ | :------------------------------------------------------------------- |
| Type                | Script                                                               |
| Key                 | `github.repo.stars`                                                  |
| Type of information | Numeric (unsigned)                                                   |
| Update interval     | `1h`                                                                 |
| Timeout             | `5s`                                                                 |
| Parameters          | `owner = zabbix`, `repo = zabbix`, `token = <optional GitHub token>` |

> **Note:** GitHub’s API enforces rate limits for unauthenticated requests (≈60/hour per IP).
> Add a personal access token for higher limits.

---

### Script

```js
// Returns stargazers_count from GitHub REST API
// Parameters: owner, repo, token (optional)

var owner = parameters.owner;
var repo  = parameters.repo;
var token = parameters.token;

if (!owner || !repo) {
  throw "Missing 'owner' or 'repo' parameter";
}

var url = "https://api.github.com/repos/" + owner + "/" + repo;

var req = new HttpRequest();
req.addHeader("User-Agent: zabbix-script-item"); // required by GitHub
req.addHeader("Accept: application/vnd.github+json");
if (token) {
  req.addHeader("Authorization: Bearer " + token);
}

var body = req.get(url);
if (req.getStatus() !== 200) {
  throw "GitHub API returned HTTP " + req.getStatus();
}

var data = JSON.parse(body);
if (typeof data.stargazers_count !== "number") {
  throw "Unexpected response: missing stargazers_count";
}

return data.stargazers_count;
```

---

### Example trigger

```text
{<Template/Host>:github.repo.stars.last()}=0
```

**Meaning:** Alert if the script returns 0 (indicating API or auth issue).

---

### Screenshot placeholder

`![Script item - GitHub stars setup](images/scriptitem_github.png)`

---

## Example 2 – SSL certificate expiry (days left)

### Goal

Return how many **days remain** before an HTTPS certificate expires, using the [SSL Labs API](https://api.ssllabs.com/).

This example shows how to call a third-party API, parse a nested JSON response, and return a simple numeric value.

---

### Item setup

| Field               | Value                                                 |
| :------------------ | :---------------------------------------------------- |
| Type                | Script                                                |
| Key                 | `ssl.days_left`                                       |
| Type of information | Numeric (unsigned)                                    |
| Update interval     | `6h`                                                  |
| Timeout             | `10s`                                                 |
| Parameters          | `host = example.com`, `fromCache = on`, `maxAge = 72` |

> **Tip:** Use `fromCache=on` to retrieve cached results (instant).
> A fresh SSL scan can take up to several minutes and exceed timeout limits.

---

### Script

```js
// Returns integer days until SSL expiry using SSL Labs API (cached).
// Parameters: host, fromCache (on/off), maxAge (hours)

var host = parameters.host;
var fromCache = (parameters.fromCache || "on") === "on";
var maxAge = parseInt(parameters.maxAge || "72", 10);

if (!host) throw "Missing 'host' parameter";

var url = "https://api.ssllabs.com/api/v3/analyze?host=" + encodeURIComponent(host);
if (fromCache) url += "&fromCache=on&maxAge=" + maxAge;

var req = new HttpRequest();
req.addHeader("User-Agent: zabbix-script-item");
var resp = req.get(url);
if (req.getStatus() !== 200) {
  throw "SSL Labs API returned HTTP " + req.getStatus();
}

var data = JSON.parse(resp);
if (data.status !== "READY" || !data.endpoints || !data.endpoints.length) {
  throw "No ready result found (try cached mode)";
}

var endpoint = data.endpoints[0];
if (!endpoint.details || !endpoint.details.cert || !endpoint.details.cert.notAfter) {
  throw "No certificate info in response";
}

var notAfterMs = endpoint.details.cert.notAfter;
var nowMs = Date.now();
var daysLeft = Math.floor((notAfterMs - nowMs) / (1000 * 60 * 60 * 24));

return daysLeft;
```

---

### Example triggers

```text
{<Template/Host>:ssl.days_left.min(1d)}<=14    → Warning
{<Template/Host>:ssl.days_left.min(1d)}<=3     → High
```

---

### Screenshot placeholder

`![Script item - SSL expiry](images/scriptitem_ssl.png)`

---

## Example 3 – Zabbix API: count of problem triggers

### Goal

Use the **Zabbix API** to log in and return the number of triggers currently in a **PROBLEM** state.

This is a classic use case for Script items: multiple API calls with logic in between.

---

### Item setup

| Field               | Value                                                                                  |
| :------------------ | :------------------------------------------------------------------------------------- |
| Type                | Script                                                                                 |
| Key                 | `zbx.api.problem.count`                                                                |
| Type of information | Numeric (unsigned)                                                                     |
| Update interval     | `1m`                                                                                   |
| Timeout             | `5s`                                                                                   |
| Parameters          | `api_url = https://your.zabbix/api_jsonrpc.php`, `user = apiuser`, `password = secret` |

---

### Script

```js
// Returns count of PROBLEM triggers via Zabbix API
// Parameters: api_url, user, password

function apiCall(req, url, payload) {
  req.addHeader("Content-Type: application/json");
  var res = req.post(url, JSON.stringify(payload));
  if (req.getStatus() !== 200) {
    throw "API HTTP " + req.getStatus();
  }
  var json = JSON.parse(res);
  if (json.error) throw "API error: " + JSON.stringify(json.error);
  return json.result;
}

var url = parameters.api_url;
var user = parameters.user;
var pass = parameters.password;
if (!url || !user || !pass) throw "Missing parameters";

var req = new HttpRequest();

// 1. Login
var auth = apiCall(req, url, {
  jsonrpc: "2.0",
  method: "user.login",
  params: { user: user, password: pass },
  id: 1
});

// 2. Get PROBLEM triggers
var result = apiCall(req, url, {
  jsonrpc: "2.0",
  method: "trigger.get",
  params: {
    output: "triggerid",
    filter: { value: 1 }, // value=1 means PROBLEM
    countOutput: true
  },
  auth: auth,
  id: 2
});

return parseInt(result, 10);
```

---

### Example trigger

```text
{<Template/Host>:zbx.api.problem.count.last()}>0
```

**Meaning:** Alert if there is at least one problem trigger on the server.

---

### Screenshot placeholder

`![Script item - Zabbix API](images/scriptitem_zabbixapi.png)`

---

## Best practices and troubleshooting

* **Timeouts:** Keep script execution short; APIs may delay.
* **Testing:** Use *“Check now”* in the item to see raw output.
* **Logging:** Use `Zabbix.log(3, "message")` for debug output (appears in server log).
* **Error handling:** Always `throw` errors instead of returning strings; Zabbix will mark the item as unsupported automatically.
* **Object reuse:** Each script can create up to 10 `HttpRequest` objects—reuse one when chaining API calls.
* **Security:** Never hard-code passwords or tokens; use macros or item parameters.

---

## When to use Script items

Use Script items when:

* You need **logic, loops, or multiple API calls**.
* You monitor **remote services** where agents aren’t available.
* You want to prototype an integration before writing a custom plugin.

For simple JSON transformations, preprocessing JavaScript might be enough—but Script items shine when you need full control.

---

## Expert techniques for Script items

### 1. Debugging like a pro

During development, use the internal logging API to trace script behavior:

```js
Zabbix.log(4, "Debug: response body = " + body);
Zabbix.log(3, "Info: token received successfully");
Zabbix.log(2, "Warning: unexpected API reply");
```

**Tip:**

* Log level `4` = debug, visible only if the server log level ≥4.
* Log level `3` = informational.
* The log lines are written to the Zabbix server or proxy log, not the frontend.

When a script throws an error, Zabbix automatically marks the item as *unsupported* and stores the message for inspection.

---

### 2. Using macros and secret parameters

Always move credentials, tokens, and sensitive values to **item parameters** or **macros** rather than hard-coding them.
For example:

| Parameter | Value             |
| :-------- | :---------------- |
| `token`   | `{$GITHUB_TOKEN}` |

Then define `{$GITHUB_TOKEN}` in your host or template with **secret visibility**.
This allows you to reuse the same script safely across environments.

> **Tip:** in large environments, manage secrets via *global macros* for consistency.

---

### 3. Error handling and fallback logic

Production scripts should degrade gracefully.
You can catch and handle network failures, retry, or return a fallback value:

```js
var req = new HttpRequest();
try {
  var data = req.get(parameters.url);
  if (req.getStatus() !== 200)
    throw "HTTP " + req.getStatus();
  return JSON.parse(data).value;
}
catch (e) {
  Zabbix.log(2, "Request failed: " + e);
  return 0;  // Fallback value for triggers
}
```

This prevents temporary API errors from spamming unsupported item events.

---

### 4. Caching between executions

Script items are stateless by default, but you can cache results using **trapper items** or **dependent items**.
Pattern example:

1. A Script item fetches heavy data every 10 minutes and sends it via `zabbix_sender`.
2. Dependent items extract specific fields via preprocessing.

This offloads work and avoids repetitive API calls.

---

### 5. Parallelization and performance considerations

Each Script item consumes one poller slot.
If you have dozens of Script items that do API calls, consider:

* Running them on a **proxy** close to the data source (reduces latency).
* Adjusting `StartPollers` and `Timeout` in `zabbix_server.conf`.
* Avoiding heavy JSON parsing or unnecessary loops.
* Using asynchronous APIs only when truly needed — Duktape executes synchronously.

A single bad Script item can block a poller for its entire timeout period, so always test and tune.

---

### 6. Returning structured data

Script items can return **JSON strings** which can then be used in **dependent items**.
Example: returning a JSON object containing multiple metrics.

```js
return JSON.stringify({
  cpu_usage: 25,
  mem_usage: 67,
  disk_free: 18234
});
```

Then create dependent items with JSONPath like:

```
$.cpu_usage
$.mem_usage
$.disk_free
```

This allows one Script item to feed many dependent metrics — a professional optimization pattern.

---

### 7. Combining script items with preprocessing JavaScript

Advanced users often pair a Script item that performs heavy retrieval with preprocessing JavaScript that performs lightweight normalization.

Example:

* Script item fetches a full JSON payload from an API.
* Dependent item extracts a numeric value using preprocessing JavaScript:

  ```js
  var obj = JSON.parse(value);
  return obj.metrics.cpu;
  ```

This separates responsibilities and makes troubleshooting easier.

---

### 8. Controlling execution context

Script items always run **on the poller process** of either the Zabbix server or proxy.
Understanding this helps when debugging:

* If an item runs on a **proxy**, it has network access only from the proxy’s location.
* You can **force** execution on a proxy by assigning the host to that proxy.
* Logs for script execution appear in the respective poller’s log file.

---

### 9. Integrating with other Zabbix components

You can use Script items as “glue” between Zabbix and external systems:

* **Maintenance automation:** call an external API to disable a host when a maintenance window starts.
* **Custom SLA checks:** query an API that provides service availability stats and visualize them in Zabbix.
* **Hybrid monitoring:** fetch metrics from cloud APIs (AWS, Azure, etc.) where direct agents aren’t feasible.

Each of these scenarios demonstrates how Script items bridge Zabbix with the outside world.

---

### 10. Best practice checklist

✅ Keep scripts short (<200 lines).
✅ Always handle HTTP status codes and JSON errors.
✅ Use parameters or macros for configuration.
✅ Log at `Zabbix.log(3, ...)` for operations and `Zabbix.log(4, ...)` for debugging.
✅ Reuse a single `HttpRequest` object per script.
✅ Test interactively in the frontend with *“Check now”*.
✅ Document the purpose and return type at the top of each script.

---

### 11. Exercises for the reader

1. Extend the GitHub example to also return **open issue count**.
2. Modify the SSL script to alert when certificates use weak cipher suites.
3. Adapt the Zabbix API script to list **unacknowledged problems only**.
4. Create one Script item that returns both Zabbix host count and problem count in JSON, and build dependent items from it.

---

### 12. Summary

By mastering Script items, you’ve reached the **expert level of Zabbix data collection**.
You now understand not just how to fetch and return data, but how to:

* Debug effectively
* Secure your credentials
* Handle API errors gracefully
* Optimize poller usage
* Reuse scripts for multiple metrics

These skills let you integrate Zabbix with virtually any system that exposes an API — a hallmark of an advanced monitoring engineer.

awesome — here’s the **polished, final expert edition** of the DoH example. it adds timing, informational logs, structured JSON output (for dependent items), input validation, and graceful fallback — all in a compact, production-ready script.

---

## Advanced real-world example — DNS over HTTPS health (expert edition)

### Goal

Query **Google DoH** (`https://dns.google/resolve`) to verify a record and measure **latency**.
Return a compact JSON payload for dependent items, so one script can feed multiple metrics.

### Item setup (script)

| Field               | Value                                                                   |
| ------------------- | ----------------------------------------------------------------------- |
| Type                | Script                                                                  |
| Key                 | `doh.resolve.json`                                                      |
| Type of information | **Text** (JSON)                                                         |
| Update interval     | `1m`                                                                    |
| Timeout             | `5s`                                                                    |
| Parameters          | `host = example.com`, `type = A`, `expect = 93.184.216.34` *(optional)* |

> Tip: If you don’t want to enforce an expected value, leave `expect` empty.

### Script (paste as-is)

```js
// DNS over HTTPS (Google) expert check
// Returns JSON: { ok: 0|1, ms: <latency>, answers: <count>, matched: 0|1, status: <rcode>, msg: <string> }
// Params: host (required), type [A|AAAA|CNAME|MX|TXT|NS|SOA], expect (optional exact match)

function normalizeRRData(v) {
  // Normalize trailing dots for names (CNAME/MX/NS/SOA), leave IPs as-is
  return String(v).trim().replace(/\.$/, "");
}

var host = parameters.host;
var rrtype = parameters.type || "A";
var expect = (parameters.expect || "").trim();

// Guard rails
if (!host) throw "Missing 'host' parameter";
var allowed = {A:1, AAAA:1, CNAME:1, MX:1, TXT:1, NS:1, SOA:1};
if (!allowed[rrtype]) rrtype = "A";

var url = "https://dns.google/resolve?name=" + encodeURIComponent(host) +
          "&type=" + encodeURIComponent(rrtype);

var req = new HttpRequest();
req.addHeader("User-Agent: zabbix-script-item");

var t0 = Date.now();
var body = req.get(url);
var ms = Date.now() - t0;

var statusCode = req.getStatus();
if (statusCode !== 200) {
  Zabbix.log(2, "DoH HTTP " + statusCode + " for " + host + " type=" + rrtype);
  return JSON.stringify({ ok: 0, ms: ms, answers: 0, matched: 0, status: -1, msg: "http_" + statusCode });
}

var json;
try {
  json = JSON.parse(body);
} catch (e) {
  Zabbix.log(2, "Invalid JSON from DoH: " + e);
  return JSON.stringify({ ok: 0, ms: ms, answers: 0, matched: 0, status: -2, msg: "invalid_json" });
}

// RFC 1035 RCODE: 0=NOERROR, 3=NXDOMAIN, etc.
var rcode = (typeof json.Status === "number") ? json.Status : -9;
var answers = Array.isArray(json.Answer) ? json.Answer.length : 0;

// Determine ok/matched
var ok = (rcode === 0 && answers > 0) ? 1 : 0;
var matched = 0;

if (ok && expect) {
  var want = normalizeRRData(expect);
  for (var i = 0; i < json.Answer.length; i++) {
    var got = normalizeRRData(json.Answer[i].data);
    if (got === want) { matched = 1; break; }
  }
  // If an expectation is provided, "ok" should mean "we resolved AND matched"
  if (!matched) ok = 0;
}

var msg = (ok ? "ok" : (rcode === 3 ? "nxdomain" : "not_ok"));
Zabbix.log(3, "DoH " + host + " type=" + rrtype + " ok=" + ok + " matched=" + matched + " ms=" + ms);

return JSON.stringify({
  ok: ok,
  ms: ms,
  answers: answers,
  matched: matched,
  status: rcode,
  msg: msg
});
```

### Dependent items (recommended)

Create **dependent** items to parse fields from the JSON so you can alert/graph cleanly:

1. **DoH OK**

* Type: Dependent item
* Key: `doh.resolve.ok`
* Master item: `doh.resolve.json`
* Preprocessing: *JSONPath* → `$.ok`
* Type of information: Numeric (unsigned)

2. **Latency (ms)**

* Key: `doh.resolve.ms`
* JSONPath: `$.ms`
* Type: Numeric (unsigned)

3. **Answers count**

* Key: `doh.resolve.answers`
* JSONPath: `$.answers`
* Type: Numeric (unsigned)

4. **Matched** (only relevant if you use `expect`)

* Key: `doh.resolve.matched`
* JSONPath: `$.matched`
* Type: Numeric (unsigned)

5. **Status/rcode** (optional)

* Key: `doh.resolve.status`
* JSONPath: `$.status`
* Type: Numeric (unsigned)

### Example triggers

* **Broken or mismatched DNS** (fires if resolution fails or doesn’t match `expect`):

  ```text
  {<Template/Host>:doh.resolve.ok.last()}=0
  ```

* **DNS latency high** (e.g., > 500 ms):

  ```text
  {<Template/Host>:doh.resolve.ms.min(5m)}>500
  ```

* **Flapping detection** (intermittent failures):

  ```text
  {<Template/Host>:doh.resolve.ok.count(10m,0,"eq")}>2
  ```

## Conclusion

## Questions

## Useful URLs
