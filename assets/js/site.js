(function () {
  "use strict";
  var themeButton = document.getElementById("theme-toggle");

  function setTheme(value) {
    var dark = value === "blue" || value === "dark";
    document.documentElement.dataset.theme = dark ? "blue" : "light";
    themeButton.setAttribute("aria-pressed", String(dark));
    themeButton.setAttribute("aria-label", dark ? "밝은 테마로 변경" : "어두운 테마로 변경");
    themeButton.querySelector(".theme-toggle-label").textContent = dark ? "밝은 테마" : "어두운 테마";
  }
  setTheme(document.documentElement.dataset.theme);
  themeButton.addEventListener("click", function () {
    setTheme(document.documentElement.dataset.theme === "blue" ? "light" : "blue");
    try { localStorage.setItem("theme-mode", document.documentElement.dataset.theme); } catch (e) {}
  });
  themeButton.hidden = false;

  var post = document.querySelector(".post-content");
  var toc = document.getElementById("post-toc");
  if (post && toc) {
    var headings = Array.from(post.querySelectorAll("h2"));
    if (headings.length >= 3) {
      var list = toc.querySelector("ol");
      headings.forEach(function (heading, index) {
        if (!heading.id) {
          var id = "post-section-" + (index + 1);
          while (document.getElementById(id)) id += "-section";
          heading.id = id;
        }
        var item = document.createElement("li"), link = document.createElement("a");
        link.href = "#" + encodeURIComponent(heading.id);
        link.textContent = heading.textContent;
        item.appendChild(link); list.appendChild(item);
      });
      var rail = document.getElementById("rail-toc");
      rail.appendChild(list.cloneNode(true));
      rail.hidden = false;
      toc.hidden = false;
    }
    post.querySelectorAll("table").forEach(function (table, index) {
      var wrapper = document.createElement("div");
      wrapper.className = "table-scroll";
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
      function syncTableAccess() {
        if (wrapper.scrollWidth > wrapper.clientWidth) {
          wrapper.tabIndex = 0;
          wrapper.setAttribute("role", "region");
          wrapper.setAttribute("aria-label", "표 " + (index + 1) + ", 가로로 스크롤할 수 있습니다");
        } else {
          wrapper.removeAttribute("tabindex");
          wrapper.removeAttribute("role");
          wrapper.removeAttribute("aria-label");
        }
      }
      syncTableAccess();
      var observer = new ResizeObserver(syncTableAccess);
      observer.observe(wrapper);
      observer.observe(table);
    });
  }
})();
