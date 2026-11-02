(function () {
  "use strict";

  var tagPage = document.querySelector(".tag-page");
  if (!tagPage) return;

  var indexUrl = tagPage.dataset.indexUrl;
  var baseurl = tagPage.dataset.baseurl || "";
  var resultTitle = document.getElementById("tag-result-title");
  var resultCount = document.getElementById("tag-result-count");
  var resultSection = document.getElementById("tag-results");
  var resultList = document.getElementById("tag-result-list");
  var emptyState = document.getElementById("tag-empty-state");
  var loadStatus = document.getElementById("tag-load-status");
  var retryButton = document.getElementById("tag-retry");
  var filter = document.getElementById("tag-filter");
  var filterClear = document.getElementById("tag-filter-clear");
  var filterStatus = document.getElementById("tag-filter-status");
  var filterEmpty = document.getElementById("tag-filter-empty");
  var buttons = Array.prototype.slice.call(document.querySelectorAll(".tag-cloud-button"));
  var activeTag = null;
  var indexPromise = null;
  var renderVersion = 0;

  function normalize(value) {
    return (value || "").toLowerCase().trim();
  }

  function getHashTag() {
    try {
      return normalize(decodeURIComponent(window.location.hash.substring(1)));
    } catch (error) {
      return "";
    }
  }

  function setHashTag(tagName) {
    var hash = tagName ? ("#" + encodeURIComponent(tagName)) : "";
    if (window.location.hash === hash) return;
    window.history.pushState(null, "", window.location.pathname + window.location.search + hash);
  }

  function getButton(tagName) {
    return buttons.find(function (button) { return button.dataset.tagName === tagName; });
  }

  function loadIndex() {
    if (!indexPromise) {
      var controller = new AbortController();
      var timeout = window.setTimeout(function () { controller.abort(); }, 15000);
      indexPromise = fetch(indexUrl, { signal: controller.signal }).then(function (response) {
        if (!response.ok) throw new Error("Tag index request failed");
        return response.json();
      }).catch(function (error) {
        // Failed requests must not poison subsequent selections and retries.
        indexPromise = null;
        throw error;
      }).finally(function () {
        window.clearTimeout(timeout);
      });
    }
    return indexPromise;
  }

  function syncButtonState() {
    buttons.forEach(function (button) {
      var isActive = button.dataset.tagName === activeTag;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
  }

  function announce(message) {
    if (loadStatus) loadStatus.textContent = message;
  }

  function showMessage(message, state) {
    tagPage.dataset.state = state;
    resultSection.hidden = true;
    resultList.replaceChildren();
    emptyState.textContent = message;
    emptyState.hidden = false;
    retryButton.hidden = state !== "error";
    announce(message);
  }

  function renderPosts(posts) {
    resultList.replaceChildren();
    var fragment = document.createDocumentFragment();
    posts.forEach(function (post) {
      var item = document.createElement("li");
      var date = document.createElement("time");
      var link = document.createElement("a");
      date.className = "post-date";
      date.dateTime = post.date;
      date.textContent = post.date;
      link.href = baseurl + post.url;
      link.textContent = post.title;
      item.append(date, link);
      fragment.appendChild(item);
    });
    resultList.appendChild(fragment);
    resultSection.hidden = false;
    emptyState.hidden = true;
    retryButton.hidden = true;
    tagPage.dataset.state = "ready";
  }

  function revealResults(keyboard) {
    if (keyboard) resultTitle.focus({ preventScroll: true });
    var rect = resultTitle.getBoundingClientRect();
    // Mouse focus stays on the chosen tag; move the viewport only when needed.
    if (rect.top < 80 || rect.bottom > window.innerHeight - 80) {
      resultTitle.scrollIntoView({ block: "start", behavior: "instant" });
    }
  }

  async function render(options) {
    options = options || {};
    var version = ++renderVersion;
    var button = activeTag ? getButton(activeTag) : null;
    if (!button) {
      resultTitle.textContent = "태그별 글";
      resultCount.textContent = "";
      showMessage(getHashTag() ? "해당 태그를 찾을 수 없습니다. 다른 태그를 선택해 주세요." : "태그를 선택하면 관련 글을 볼 수 있습니다.", "idle");
      return;
    }

    resultTitle.textContent = "#" + button.dataset.tagLabel;
    resultCount.textContent = "";
    showMessage("글을 불러오는 중입니다.", "loading");
    try {
      var index = await loadIndex();
      if (version !== renderVersion) return;
      var posts = index[activeTag] || [];
      resultCount.textContent = posts.length + "개";
      if (posts.length) {
        renderPosts(posts);
        announce(button.dataset.tagLabel + " 태그의 글 " + posts.length + "개를 찾았습니다.");
      } else {
        showMessage("이 태그에 등록된 글이 없습니다. 다른 태그를 선택해 주세요.", "empty");
      }
    } catch (error) {
      if (version !== renderVersion) return;
      showMessage("글을 불러오지 못했습니다. 연결을 확인하고 다시 시도해 주세요.", "error");
    }
    if (version === renderVersion && options.reveal) revealResults(options.keyboard);
  }

  function filterTags() {
    var query = normalize(filter.value);
    var visible = 0;
    buttons.forEach(function (button) {
      var matches = normalize(button.dataset.tagLabel).includes(query);
      button.hidden = !matches;
      if (matches) visible += 1;
    });
    filterClear.hidden = !query;
    filterEmpty.hidden = visible !== 0;
    filterStatus.textContent = query ? "태그 " + visible + "개가 일치합니다." : buttons.length + "개의 태그";
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function (event) {
      activeTag = button.dataset.tagName;
      setHashTag(activeTag);
      syncButtonState();
      render({ reveal: true, keyboard: event.detail === 0 });
    });
  });

  retryButton.addEventListener("click", function () {
    render({ reveal: true, keyboard: true });
  });
  filter.addEventListener("input", filterTags);
  document.getElementById("skip-tag-list").addEventListener("click", function () {
    revealResults(true);
  });
  filterClear.addEventListener("click", function () {
    filter.value = "";
    filterTags();
    filter.focus();
  });

  function restoreTag() {
    var nextTag = getHashTag();
    var nextActive = getButton(nextTag) ? nextTag : null;
    if (nextActive === activeTag && tagPage.dataset.state) return;
    activeTag = nextActive;
    syncButtonState();
    render();
  }
  window.addEventListener("hashchange", restoreTag);
  window.addEventListener("popstate", restoreTag);

  var hashTag = getHashTag();
  activeTag = getButton(hashTag) ? hashTag : null;
  document.querySelector(".tag-static-list").hidden = true;
  tagPage.hidden = false;
  syncButtonState();
  render({ reveal: Boolean(activeTag) });
})();
