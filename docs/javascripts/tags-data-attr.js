document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".md-tags .md-tag").forEach((el) => {
    const slug = el.textContent.trim().toLowerCase().replace(/\s+/g, "-");
    el.setAttribute("data-tag", slug);
  });
});
