document.addEventListener("DOMContentLoaded", () => {
  // target ANY md-tag on the page (span OR link)
  document.querySelectorAll(".md-tag").forEach((el) => {
    // derive slug from visible text (beginner → beginner, "Very Hard" → very-hard)
    const slug = el.textContent.trim().toLowerCase().replace(/\s+/g, "-");
    if (!el.hasAttribute("data-tag")) {
      el.setAttribute("data-tag", slug);
    }
  });
});
