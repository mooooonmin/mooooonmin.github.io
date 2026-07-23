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
  var buttons = Array.prototype.slice.call(document.querySelectorAll(".tag-cloud-button"));
  var activeTag = null;
  var indexPromise = null;

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
    window.history.replaceState(null, "", window.location.pathname + window.location.search + hash);
  }

  function getButton(tagName) {
    return buttons.find(function (button) { return button.dataset.tagName === tagName; });
  }

  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch(indexUrl).then(function (response) {
        if (!response.ok) throw new Error("Tag index request failed");
        return response.json();
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

  function showMessage(message) {
    resultSection.hidden = true;
    resultList.replaceChildren();
    emptyState.textContent = message;
    emptyState.hidden = false;
  }

  function renderPosts(posts) {
    resultList.replaceChildren();
    posts.forEach(function (post) {
      var item = document.createElement("li");
      var date = document.createElement("span");
      var link = document.createElement("a");
      date.className = "post-date";
      date.textContent = post.date;
      link.href = baseurl + post.url;
      link.textContent = post.title;
      item.append(date, link);
      resultList.appendChild(item);
    });
    resultSection.hidden = false;
    emptyState.hidden = true;
  }

  async function render() {
    var button = activeTag ? getButton(activeTag) : null;
    if (!button) {
      resultTitle.textContent = "Select a tag";
      resultCount.textContent = "";
      showMessage("Select a tag on the left to see related posts.");
      return;
    }

    resultTitle.textContent = "#" + button.dataset.tagLabel;
    resultCount.textContent = button.dataset.count + "개";
    showMessage("Loading posts...");
    try {
      var index = await loadIndex();
      if (activeTag !== button.dataset.tagName) return;
      renderPosts(index[activeTag] || []);
    } catch (error) {
      showMessage("Tag posts are temporarily unavailable.");
    }
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      activeTag = button.dataset.tagName;
      setHashTag(activeTag);
      syncButtonState();
      render();
    });
  });

  window.addEventListener("hashchange", function () {
    var nextTag = getHashTag();
    activeTag = getButton(nextTag) ? nextTag : null;
    syncButtonState();
    render();
  });

  var hashTag = getHashTag();
  activeTag = getButton(hashTag) ? hashTag : null;
  syncButtonState();
  render();
})();
