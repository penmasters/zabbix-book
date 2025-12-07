---
description: |
    Test website performance with Zabbix browser items. Automate real browser
    checks to measure load times, content accuracy, and user experience.
tags: [advanced, expert]
---

# Browser item

# Chapter: Synthetic Web Monitoring with the Zabbix Browser Item

Modern applications require more than simple HTTP availability checks. The **Zabbix Browser item** enables real user simulation by controlling a headless Chrome/Firefox instance through WebDriver. This allows Zabbix to measure real rendering times, validate user flows, capture screenshots, and extract content from web pages.

---

## 1. Architecture Overview

![WebDriver Architecture](image:selenium-webdriver-architecture-diagram)
![Zabbix Browser Monitoring](image:zabbix-browser-monitoring-architecture)

Components involved:

- **Zabbix Server/Proxy:** Executes JavaScript (ES5 only).
- **WebDriver (Selenium/ChromeDriver):** Controls browser operations.
- **Browser (Chrome/Firefox):** Loads content, renders pages, returns metrics & screenshots.

Zabbix uses **Duktape**, an ES5-only JavaScript engine, meaning modern syntax (ES6, async/await) cannot be used.

---

## 2. Running Browsers in Headless Mode

Linux servers typically lack a graphical environment, causing browser startup failures like:

- “Missing X server”
- “No DISPLAY variable set”
- “GPU process initialization failed”

Solution: Run Chrome in **headless** mode.

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
3. Writing Reliable Browser Scripts

A robust synthetic-check script must:

Initialize a stable browser session

Interact with DOM elements

Wait for dynamic content

Collect performance metrics

Always return JSON (never undefined)

Use a try/finally block to guarantee return values.

4. Practical Example: Monitoring https://www.zabbix.com
Actions Performed

Load homepage

Click Download menu link

Wait for navigation

Extract <h1> headline text

Collect metrics + screenshot

Return structured JSON

Screenshot (reference)




4.1 Full Script Example

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
    browser = new Browser(opts);
    browser.setScreenSize(1920, 1080);

    browser.navigate('https://www.zabbix.com/');
    browser.waitForLoad();

    var downloadLink = browser.findElement('a[href="/download"]');
    downloadLink.click();

    browser.waitForLoad(8000);

    var h1 = browser.findElement('h1');
    var headline = h1.getText();

    browser.collectPerfEntries();

    var result = {
        status: 'ok',
        headline: headline,
        url: browser.getUrl(),
        perf: browser.getPerfEntries()
    };

    return JSON.stringify(result);

} finally {
    if (browser && browser.session) {
        return JSON.stringify(browser.getResult());
    }
    return JSON.stringify({ status: 'session_failed' });
}
```
## 5. What the Script Returns

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

### 6.1 Browser Fails to Start

**Symptoms:**
- “Session not created”
- Empty screenshot
- Browser exits immediately

**Common Causes:**
- Missing headless flags
- Required system libraries not installed
- ChromeDriver and Chrome version mismatch

**Fixes:**
1. Ensure_browser arguments include:  
   `--headless`, `--no-sandbox`, `--disable-gpu`, `--window-size=1920,1080`
2. Install required system libraries (example for RHEL-like systems):  
   `libX11`, `libXcomposite`, `libXdamage`, `mesa-libgbm`, `gtk3`
3. Match Chrome/ChromeDriver versions.

---

### 6.2 Script Returns No Value (Unsupported Item)

**Symptoms:**
- Zabbix marks the item as *Unsupported*
- "Cannot evaluate script: no return value"

**Cause:**
- JavaScript error occurs before reaching `return`, leaving the script without output.

**Fix:**
Always wrap your script with:

```js
try {
    // your browser logic
} finally {
    return JSON.stringify(browser.getResult());
}

```

### 6.3 Element Not Found

**Symptoms:**
- “Failed to find element”
- Script stops during `findElement()`, `.click()`, or `.getText()`
- Browser session ends prematurely

**Typical Causes:**
1. **Page not fully loaded yet**  
   The script attempts to interact with elements before the DOM is ready, especially on JavaScript-heavy websites.

2. **Incorrect or unstable selector**  
   CSS selectors or XPath expressions may differ from what the script expects, or may change over time.

3. **Dynamic content / delayed rendering**  
   SPAs (React, Vue, Angular) load content asynchronously. Elements may not exist immediately after navigation.

4. **Element inside an iframe**  
   WebDriver cannot see inside iframes until the script switches context.

5. **Element hidden or not interactable**  
   Sometimes the element exists but is not visible or clickable due to overlays, animations, or cookie banners.

---

**Fixes and Best Practices:**

#### 1. Explicitly wait for the element

Use `waitForElement()` to prevent interacting too early:

```js
browser.waitForElement('#username', 5000);
```

#### 2. Validate the selector manually

```js
document.querySelector('a[href="/download"]')
```



# Conclusion

## Questions

## Useful URLs
