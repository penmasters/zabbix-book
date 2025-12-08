---
description: |
    Test website performance with Zabbix browser items. Automate real browser
    checks to measure load times, content accuracy, and user experience.
tags: [advanced, expert]
---

# Browser item

## Synthetic Web Monitoring with the Zabbix Browser Item

Modern applications require more than simple HTTP availability checks. While an HTTP
agent can confirm whether a web server responds, it cannot verify whether a page renders
correctly, whether JavaScript loads, or whether a user can interact with key interface
elements.

The Zabbix Browser item solves this by executing real, scriptable, headless browsers
such as Chrome or Firefox through WebDriver, enabling full synthetic user monitoring.

This chapter explains how to configure the Browser item, write reliable scripts, extract
metrics, troubleshoot errors, and avoid common pitfalls.

---

## Architecture Overview

![WebDriver Architecture](ch03_xx_architecture.png)
_Webdriver Architecture_

Synthetic monitoring with Zabbix relies on a three-layer architecture:

- **Zabbix Server/Proxy:**
  Executes JavaScript using an embedded ES5 engine (Duktape).
  Runs your script, processes results, and stores metrics.
- **WebDriver**
  Acts as a bridge between Zabbix and a browser. Example: Selenium Standalone Server,
  Selenium Grid, ChromeDriver, GeckoDriver.

- **Browser (Chrome/Firefox)**
  Performs all real HTML rendering, JavaScript execution, screenshot capture,
  and navigation.

Zabbix does not include a browser internally; it communicates to one externally
through the WebDriver JSON protocol.

???+ info

     Zabbix uses an ES5 JavaScript engine. This means:

     - No async, no await
     - No let, const, arrow functions, Promises
     - Use only ES5 syntax (var, classical functions, synchronous calls)

---

## Running Browsers in Headless Mode

Most Zabbix environments run on Linux servers which do not have a GUI.
A typical browser expects an X11/Wayland display environment. Without one, Chrome
or Firefox fails with errors such as:

- “Missing X server”
- “No DISPLAY variable set”
- “GPU process initialization failed”

The solution is Headless Mode, which allows Chrome/Firefox to run without a graphical environment.

**Recommended Chrome options:**

```js
var opts = Browser.chromeOptions({
    args: [
        '--headless',
        '--no-sandbox',
        '--disable-gpu',
        '--window-size=1920,1080'
    ]
});
```
Why these flags matter:

| Flag            | Purpose                                          |
| --------------- | ------------------------------------------------ |
| `--headless`    | Runs Chrome without GUI. Required.               |
| `--no-sandbox`  | Needed in SELinux/sandboxed server environments. |
| `--disable-gpu` | Prevents GPU-related crashes in headless mode.   |
| `--window-size` | Ensures consistent screenshots and layout.       |

---

## Writing Reliable Browser Scripts

**A robust synthetic-check script must:**

- Create a stable WebDriver session
- Wait for elements and dynamic content
- Perform interactions (navigate, click, fill fields)
- Collect metrics (TTFB, DOM load, full load time)
- Capture screenshots
- Always return JSON, even when errors occur
- Handle crashes gracefully

The most important rule:

Always wrap your script in a try/finally block

The finally block must always return a valid JSON string.
This prevents “Unsupported item key value” errors.

---

## Practical Example: Monitoring https://www.zabbix.com

Scenario

- Navigate to https://www.zabbix.com/
- Click the Download menu link
- Wait for the Download page to load
- Extract the :  headline text
- Collect performance timing
- Return all results as JSON

Screenshot (reference)

zabbix homepage  and download page

### Full Script Example

```
var opts = Browser.chromeOptions({
    args: [
        '--headless',
        '--no-sandbox',
        '--disable-gpu',
        '--window-size=1920,1080'
    ]
});

var browser = null;

try {
    // Initialize browser
    browser = new Browser(opts);
    browser.setScreenSize(1920, 1080);

    // Load homepage
    browser.navigate('https://www.zabbix.com/');
    browser.waitForLoad();

    // Click "Download"
    var downloadLink = browser.findElement('a[href="/download"]');
    downloadLink.click();

    // Wait for Download page
    browser.waitForLoad(8000);

    // Extract headline
    var h1 = browser.findElement('h1');
    var headline = h1.getText();

    // Collect performance metrics
    browser.collectPerfEntries();

    // Build result object
    var result = {
        status: 'ok',
        headline: headline,
        url: browser.getUrl(),
        perf: browser.getPerfEntries()
    };

    return JSON.stringify(result);

} finally {
    // Ensure Zabbix always gets a return value
    if (browser && browser.session) {
        return JSON.stringify(browser.getResult());
    }
    return JSON.stringify({ status: 'session_failed' });
}

```
### What the Script Returns

The Zabbix Browser item returns a JSON structure that includes:

- **Navigation timing metrics** (TTFB, DOM load, full load time)
- **Resource timing metrics** for all loaded assets
- **Final URL** after redirects
- **Screenshot** (Base64-encoded PNG)
- **Extracted text** from elements you queried (e.g. `<h1>`)
- **Error details** if the browser or WebDriver encountered problems

Typical dependent items you can create:

- `perf.navigation.ttfb`
- `perf.navigation.domContentLoadedEventEnd`
- `perf.navigation.loadEventEnd`
- `perf.navigation.duration`
- Extracted headline text
- Final URL
- Screenshot retrieval/decoding

These dependent items transform the Browser item into a full set of synthetic monitoring checks.

---

## 6. Troubleshooting Common Failures

Synthetic monitoring failures fall into predictable categories.
Below are the most common cases and reliable fixes.

### 6.1 Browser Fails to Start

**Symptoms:**
- “Session not created”
- Empty screenshot
- Browser exits immediately

**Common Causes:**
- Missing headless flags
- Required system libraries not installed
- ChromeDriver and Chrome version mismatch
- Sadndbox or SELinux restrictions

**Fixes:**
1. Ensure_browser arguments include:  
   `--headless`, `--no-sandbox`, `--disable-gpu`, `--window-size=1920,1080`
2. Install required system libraries (example for RHEL-like systems):  
   `libX11`, `libXcomposite`, `libXdamage`, `mesa-libgbm`, `gtk3`
3. Match Chrome/ChromeDriver versions.

---

### Script Returns No Value (Unsupported Item)

**Symptoms:**
- Zabbix marks the item as *Unsupported*
- "Cannot evaluate script: no return value"

**Cause:**
- JavaScript error occurs before reaching `return`, leaving the script without output.

**Fix:**
Always wrap your script with try/finally:

```js
try {
    // your browser logic
} finally {
    return JSON.stringify(browser.getResult());
}
```

### Element not found

Symptoms:
- The script reports "Failed to find element".
- The script fails during clicks or text extraction.
- The script stops when calling findElement or similar functions.

Causes:
- The page has not finished loading or rendering.
- The CSS selector or XPath used does not match the actual element.
- The website uses dynamic content that appears after JavaScript executes.
- The target element exists inside an iframe which requires switching context.
- The element exists but is hidden or not interactable due to overlays or animations.

#### Fixes and Best Practices

Explicitly wait for the element before interacting:

``` js
browser.waitForElement('#username', 5000);
```

Validate the selector in your browser console:

``` js
document.querySelector('a[href="/download"]')
```
If this returns null, the script will also fail.

Prefer stable selectors instead of cosmetic ones.

Unstable selectors include classes based on colors, layout, or nth-child logic.
Stable selectors include IDs, attributes, and data-qa markers.

Use XPath when selecting text-based elements:

```
var elem = browser.findElement('//h1[contains(text(),"Zabbix")]');
```

Add controlled waits for dynamic SPA rendering when necessary:

``` js
browser.sleep(1000);
```

If the target element is inside an iframe, switch context first:

```js
var frame = browser.findElement('iframe#iframe_id');
```

browser.switchToFrame(frame);
var innerElem = browser.findElement('#inside-frame');

**Recommended pattern:**

```js
browser.waitForElement('#welcome-message', 5000);
var welcomeElem = browser.findElement('#welcome-message');
var text = welcomeElem.getText();
```

---

### Common Pitfalls (Text Summary)

Here are the most frequent mistakes seen in Browser item implementations:

- Forgetting headless mode, causing browser launch failure
- Forgetting try/finally, resulting in unsupported items
- Using unstable or incorrect selectors
- Using ES6 syntax instead of ES5
- Not calling setScreenSize(), causing unpredictable Chrome behavior
- Running too many sessions on one Selenium node
- Scripts running too long and blocking Zabbix queues
- Returning plain text instead of JSON, breaking dependent items

Avoiding these pitfalls ensures stable and predictable Browser item monitoring.

# Conclusion

## Questions

## Useful URLs
