---
title: Tags
layout: default
permalink: /tags/
---

{% assign sorted_tags = site.tags | sort %}

{% if sorted_tags.size > 0 %}
<section class="tag-page">
  <div class="tag-pane tag-pane-list">
    <div class="tag-cloud tag-cloud-split" id="tag-cloud-list">
      {% for tag in sorted_tags %}
        {% assign tag_name = tag[0] %}
        {% assign tag_posts = tag[1] %}
        <button
          type="button"
          class="tag-cloud-item tag-cloud-button"
          data-tag-name="{{ tag_name | downcase | escape }}"
          data-tag-label="{{ tag_name | escape }}"
          data-count="{{ tag_posts.size }}"
          aria-pressed="false"
          aria-controls="tag-result-list"
        >
          <span class="tag-cloud-name">{{ tag_name }}</span>
          <span class="tag-cloud-count">{{ tag_posts.size }}</span>
        </button>
      {% endfor %}
    </div>
  </div>

  <div class="tag-pane tag-pane-posts" aria-live="polite">
    <div class="tag-result-header">
      <h4 id="tag-result-title">Select a tag</h4>
      <span class="tag-section-count" id="tag-result-count"></span>
    </div>

    <section class="tag-section tag-section-panel" id="tag-results" hidden>
      <ul class="post-list" id="tag-result-list"></ul>
    </section>
    <p class="tag-empty-state tag-empty-state-visible" id="tag-empty-state">Select a tag on the left to see related posts.</p>
  </div>
</section>
{% else %}
<p>No tags have been added.</p>
{% endif %}

<script>
  (function () {
    var indexUrl = {{ "/tags.json" | relative_url | jsonify }};
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
      return buttons.find(function (button) {
        return button.dataset.tagName === tagName;
      });
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
      emptyState.style.display = "block";
    }

    function renderPosts(posts) {
      resultList.replaceChildren();
      posts.forEach(function (post) {
        var item = document.createElement("li");
        var date = document.createElement("span");
        var link = document.createElement("a");
        date.className = "post-date";
        date.textContent = post.date;
        link.href = {{ site.baseurl | jsonify }} + post.url;
        link.textContent = post.title;
        item.append(date, link);
        resultList.appendChild(item);
      });
      resultSection.hidden = false;
      emptyState.style.display = "none";
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
</script>
