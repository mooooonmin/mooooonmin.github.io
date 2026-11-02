(function () {
  "use strict";
  var body = document.body;
  var sidebar = document.getElementById("site-sidebar");
  var main = document.getElementById("main-content");
  var openButton = document.getElementById("open-nav");
  var collapseButton = document.getElementById("toggle-sidebar");
  var themeButton = document.getElementById("theme-toggle");
  var mobile = window.matchMedia("(max-width: 899px)");
  var collapsed = false;
  function store(key, value) { try { localStorage.setItem(key, value); } catch (e) {} }
  function syncNavigation() {
    var opened = body.classList.contains("nav-open");
    sidebar.inert = mobile.matches ? !opened : collapsed;
    main.inert = mobile.matches && opened;
    body.classList.toggle("nav-collapsed", !mobile.matches && collapsed);
    collapseButton.setAttribute("aria-expanded", String(!collapsed));
    collapseButton.setAttribute("aria-label", collapsed ? "카테고리 패널 펼치기" : "카테고리 패널 접기");
    collapseButton.textContent = collapsed ? "목록 열기" : "접기";
    openButton.setAttribute("aria-expanded", String(opened));
    openButton.setAttribute("aria-label", opened ? "메뉴 닫기" : "메뉴 열기");
    openButton.textContent = opened ? "닫기" : "메뉴";
  }
  function closeMenu() {
    body.classList.remove("nav-open");
    syncNavigation();
    openButton.focus();
  }
  openButton.addEventListener("click", function () {
    body.classList.toggle("nav-open");
    syncNavigation();
    if (body.classList.contains("nav-open")) sidebar.querySelector("input").focus();
  });
  collapseButton.addEventListener("click", function () {
    collapsed = !collapsed;
    syncNavigation();
    store("sidebar-collapsed", String(collapsed));
  });
  document.addEventListener("keydown", function (event) {
    if (!mobile.matches || !body.classList.contains("nav-open")) return;
    if (event.key === "Escape") { event.preventDefault(); closeMenu(); return; }
    if (event.key !== "Tab") return;
    var stops = [openButton].concat(Array.from(sidebar.querySelectorAll('a[href], button, input, summary, [tabindex="0"]')).filter(function (el) {
      return !el.disabled && el.getClientRects().length && getComputedStyle(el).visibility !== "hidden";
    }));
    var first = stops[0], last = stops[stops.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  mobile.addEventListener("change", function () {
    body.classList.remove("nav-open");
    syncNavigation();
    if (sidebar.inert && sidebar.contains(document.activeElement)) {
      (mobile.matches ? openButton : collapseButton).focus();
    }
    if (!mobile.matches && document.activeElement === openButton) collapseButton.focus();
  });
  try { collapsed = localStorage.getItem("sidebar-collapsed") === "true"; } catch (e) {}
  syncNavigation();

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
    store("theme-mode", document.documentElement.dataset.theme);
  });

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
      toc.hidden = false;
    }
    post.querySelectorAll("table").forEach(function (table, index) {
      var wrapper = document.createElement("div");
      wrapper.className = "table-scroll";
      wrapper.tabIndex = 0;
      wrapper.setAttribute("role", "region");
      wrapper.setAttribute("aria-label", "표 " + (index + 1) + ", 가로로 스크롤할 수 있습니다");
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    });
  }
})();
