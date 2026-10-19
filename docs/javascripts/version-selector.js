(() => {
  const script = document.currentScript;
  const manifestUrl = new URL(script.dataset.versionManifest, document.baseURI);

  fetch(manifestUrl)
    .then((response) => {
      if (!response.ok) throw new Error(`Version manifest returned ${response.status}`);
      return response.json();
    })
    .then((versions) => {
      const root = new URL(".", manifestUrl);
      const current = versions.find((version) => {
        const path = new URL(version.url, root).pathname;
        return window.location.pathname.startsWith(path);
      }) || versions[0];
      const topic = document.querySelector(".md-header__topic");
      if (!topic || !current) return;

      const selector = document.createElement("div");
      selector.className = "md-version";

      const button = document.createElement("button");
      button.className = "md-version__current";
      button.setAttribute("aria-label", "Select book version");
      button.textContent = current.title;
      selector.appendChild(button);

      const list = document.createElement("ul");
      list.className = "md-version__list";
      for (const version of versions) {
        const item = document.createElement("li");
        item.className = "md-version__item";
        const link = document.createElement("a");
        link.className = "md-version__link";
        link.href = new URL(version.url, root);
        link.textContent = version.title;
        item.appendChild(link);
        list.appendChild(item);
      }
      selector.appendChild(list);
      topic.appendChild(selector);
    })
    .catch((error) => console.error("Unable to load version selector", error));
})();
