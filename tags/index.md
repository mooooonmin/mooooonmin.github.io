---
title: 태그
layout: default
permalink: /tags/
---

{% assign sorted_tags = site.tags | sort %}

{% if sorted_tags.size > 0 %}
<section class="tag-page" aria-labelledby="tag-page-title">
  <div class="tag-pane tag-pane-list">
    <h4 id="tag-page-title">태그</h4>
    <div class="tag-tools">
      <label class="tag-search-label" for="tag-search-input">검색</label>
      <input
        type="search"
        id="tag-search-input"
        class="tag-search-input"
        placeholder="태그 또는 포스트 제목으로 찾기"
        autocomplete="off"
      />
    </div>
    <div class="tag-cloud tag-cloud-split" id="tag-cloud-list">
      {% for tag in sorted_tags %}
        {% assign tag_name = tag[0] %}
        {% assign tag_posts = tag[1] %}
        <button
          type="button"
          class="tag-cloud-item tag-cloud-button"
          data-tag-name="{{ tag_name | downcase }}"
          data-tag-label="{{ tag_name }}"
          data-count="{{ tag_posts.size }}"
          style="--tag-count: {{ tag_posts.size }};"
        >
          <span class="tag-cloud-name">{{ tag_name }}</span>
          <span class="tag-cloud-count">{{ tag_posts.size }}</span>
        </button>
      {% endfor %}
    </div>
  </div>

  <div class="tag-pane tag-pane-posts">
    <div class="tag-result-header">
      <h4 id="tag-result-title">태그를 선택하세요</h4>
      <span class="tag-section-count" id="tag-result-count"></span>
    </div>

    {% for tag in sorted_tags %}
      {% assign tag_name = tag[0] %}
      {% assign tag_posts = tag[1] %}
      <section
        class="tag-section tag-section-panel"
        data-tag-name="{{ tag_name | downcase }}"
        data-tag-label="{{ tag_name }}"
        data-count="{{ tag_posts.size }}"
      >
        <ul class="post-list">
          {% for post in tag_posts %}
            <li data-search-text="{{ post.title | downcase | escape }}">
              <span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>
              <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
            </li>
          {% endfor %}
        </ul>
      </section>
    {% endfor %}

    <p class="tag-empty-state" id="tag-empty-state">검색 결과가 없습니다.</p>
  </div>
</section>
{% else %}
<p>등록된 태그가 없습니다.</p>
{% endif %}

<script>
  (function () {
    var cloud = document.getElementById("tag-cloud-list");
    var searchInput = document.getElementById("tag-search-input");
    var resultTitle = document.getElementById("tag-result-title");
    var resultCount = document.getElementById("tag-result-count");
    var emptyState = document.getElementById("tag-empty-state");
    var buttons = Array.prototype.slice.call(document.querySelectorAll(".tag-cloud-button"));
    var sections = Array.prototype.slice.call(document.querySelectorAll(".tag-section-panel"));
    var activeTag = null;`r`n`r`n    function getHashTag() {`r`n      return normalize(window.location.hash.replace("#", ""));`r`n    }`r`n`r`n    function setHashTag(tagName) {`r`n      if (!tagName) return;`r`n      var nextHash = "#" + tagName;`r`n      if (window.location.hash !== nextHash) {`r`n        window.history.replaceState(null, "", nextHash);`r`n      }`r`n    }

    function normalize(value) {
      return (value || "").toLowerCase().trim();
    }

    function sortByCount(items) {
      items.sort(function (a, b) {
        return Number(b.dataset.count || 0) - Number(a.dataset.count || 0);
      });
      return items;
    }

    function syncButtonState() {
      buttons.forEach(function (button) {
        var isActive = activeTag && button.dataset.tagName === activeTag;
        button.classList.toggle("is-active", Boolean(isActive));
      });
    }

    function render() {
      var query = normalize(searchInput && searchInput.value);
      var visibleTagCount = 0;
      var activeSectionVisible = false;

      buttons.forEach(function (button) {
        var tagName = normalize(button.dataset.tagName);
        var section = sections.find(function (item) {
          return item.dataset.tagName === tagName;
        });
        var postItems = section ? Array.prototype.slice.call(section.querySelectorAll("li")) : [];
        var matchedPosts = 0;

        postItems.forEach(function (postItem) {
          var postText = normalize(postItem.dataset.searchText);
          var visible = !query || tagName.indexOf(query) !== -1 || postText.indexOf(query) !== -1;
          postItem.style.display = visible ? "" : "none";
          if (visible) matchedPosts += 1;
        });

        var visibleTag = !query || tagName.indexOf(query) !== -1 || matchedPosts > 0;
        button.style.display = visibleTag ? "inline-flex" : "none";
        if (visibleTag) visibleTagCount += 1;

        if (section) {
          var active = activeTag === tagName;
          section.style.display = active && visibleTag ? "block" : "none";
          if (active && visibleTag) {
            activeSectionVisible = true;
            resultTitle.textContent = "#" + section.dataset.tagLabel;
            resultCount.textContent = matchedPosts + "개";
          }
        }
      });

      if (!activeTag || !activeSectionVisible) {
        var firstVisible = buttons.find(function (button) {
          return button.style.display !== "none";
        });

        if (firstVisible) {
          activeTag = firstVisible.dataset.tagName;
          syncButtonState();
          render();
          return;
        }

        resultTitle.textContent = "태그를 선택하세요";
        resultCount.textContent = "";
      }

      emptyState.style.display = visibleTagCount === 0 ? "block" : "none";
    }

    sortByCount(buttons).forEach(function (button) {
      cloud.appendChild(button);
    });

    sortByCount(sections).forEach(function (section) {
      section.parentNode.appendChild(section);
    });

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        activeTag = button.dataset.tagName;
        syncButtonState();
        render();
      });
    });

    if (searchInput) {
      searchInput.addEventListener("input", function () {
        render();
      });
    }

    if (buttons.length > 0) {
      activeTag = buttons[0].dataset.tagName;
      syncButtonState();
    }

    render();
  })();
</script>