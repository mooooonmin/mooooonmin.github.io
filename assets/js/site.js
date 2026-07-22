(function () {
  "use strict";

  var body = document.body;
  var openNavButton = document.getElementById("open-nav");
  var sidebarToggleButton = document.getElementById("toggle-sidebar");
  var themeToggleButton = document.getElementById("theme-toggle");
  var collapsedClass = "nav-collapsed";
  var sidebarStorageKey = "sidebar-collapsed";

  function setSidebarCollapsed(isCollapsed) {
    body.classList.toggle(collapsedClass, isCollapsed);
    if (!sidebarToggleButton) return;
    sidebarToggleButton.setAttribute("aria-expanded", String(!isCollapsed));
    sidebarToggleButton.setAttribute(
      "aria-label",
      isCollapsed ? "카테고리 패널 펼치기" : "카테고리 패널 접기",
    );
  }

  function setTheme(theme) {
    var nextTheme = theme === "light" ? "light" : "blue";
    document.documentElement.setAttribute("data-theme", nextTheme);
    document.documentElement.style.colorScheme = nextTheme === "blue" ? "dark" : "light";

    if (!themeToggleButton) return;
    var isBlue = nextTheme === "blue";
    var label = themeToggleButton.querySelector(".theme-toggle-label");
    themeToggleButton.setAttribute("aria-pressed", String(isBlue));
    themeToggleButton.setAttribute(
      "aria-label",
      isBlue ? "밝은 테마로 변경" : "파랑 테마로 변경",
    );
    if (label) label.textContent = isBlue ? "MODE : BLUE" : "MODE : LIGHT";
  }

  if (openNavButton) {
    openNavButton.addEventListener("click", function () {
      var isOpen = body.classList.toggle("nav-open");
      openNavButton.setAttribute("aria-expanded", String(isOpen));
      openNavButton.setAttribute("aria-label", isOpen ? "메뉴 닫기" : "메뉴 열기");
    });
  }

  if (sidebarToggleButton) {
    try {
      setSidebarCollapsed(window.localStorage.getItem(sidebarStorageKey) === "true");
    } catch (error) {
      setSidebarCollapsed(false);
    }

    sidebarToggleButton.addEventListener("click", function () {
      var nextState = !body.classList.contains(collapsedClass);
      setSidebarCollapsed(nextState);
      try {
        window.localStorage.setItem(sidebarStorageKey, String(nextState));
      } catch (error) {
        // The UI state still changes when storage is unavailable.
      }
    });
  }

  if (themeToggleButton) {
    setTheme(document.documentElement.getAttribute("data-theme") || "blue");
    themeToggleButton.addEventListener("click", function () {
      var activeTheme = document.documentElement.getAttribute("data-theme") || "blue";
      var nextTheme = activeTheme === "blue" ? "light" : "blue";
      setTheme(nextTheme);
      try {
        window.localStorage.setItem("theme-mode", nextTheme);
      } catch (error) {
        // The active theme still changes when storage is unavailable.
      }
    });
  }
})();
