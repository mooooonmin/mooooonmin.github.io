---
title: 태그
layout: default
permalink: /tags/
---

{% assign sorted_tags = site.tags | sort %}

{% if sorted_tags.size > 0 %}
<section class="tag-page" aria-labelledby="tag-page-title">
  <div class="tag-pane tag-pane-list">
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
    var activeTag = null;

    function normalize(value) {
      return (value || "").toLowerCase().trim();
    }

    function getHashTag() {
      return normalize(window.location.hash.replace("#", ""));
    }

    function setHashTag(tagName) {
      if (!tagName) return;
      var nextHash = "#" + tagName;
      if (window.location.hash !== nextHash) {
        window.history.replaceState(null, "", nextHash);
      }
    }

    function sortByCount(items) {
      items.sort(function (a, b) {
        return Number(b.dataset.count || 0) - Number(a.dataset.count || 0);
      });
      return items;
    }

    function getSection(tagName) {
      return sections.find(function (section) {
        return section.dataset.tagName === tagName;
      });
    }

    function syncButtonState() {
      buttons.forEach(function (button) {
        button.classList.toggle("is-active", button.dataset.tagName === activeTag);
      });
    }

    function showSection(section, visibleCount) {
      sections.forEach(function (item) {
        item.style.display = item === section ? "block" : "none";
      });

      if (section) {
        resultTitle.textContent = "#" + section.dataset.tagLabel;
        resultCount.textContent = visibleCount + "개";
        emptyState.style.display = visibleCount === 0 ? "block" : "none";
      } else {
        resultTitle.textContent = "태그를 선택하세요";
        resultCount.textContent = "";
        emptyState.style.display = "block";
      }
    }

    function render() {
      var query = normalize(searchInput && searchInput.value);
      var visibleButtons = [];

      buttons.forEach(function (button) {
        var tagName = normalize(button.dataset.tagName);
        var section = getSection(tagName);
        var postItems = section ? Array.prototype.slice.call(section.querySelectorAll("li")) : [];
        var matchedPosts = 0;

        postItems.forEach(function (postItem) {
          var postText = normalize(postItem.dataset.searchText);
          var visiblePost = !query || tagName.indexOf(query) !== -1 || postText.indexOf(query) !== -1;
          postItem.style.display = visiblePost ? "" : "none";
          if (visiblePost) matchedPosts += 1;
        });

        var visibleTag = !query || tagName.indexOf(query) !== -1 || matchedPosts > 0;
        button.style.display = visibleTag ? "inline-flex" : "none";
        button.dataset.visiblePosts = String(matchedPosts);

        if (visibleTag) {
          visibleButtons.push(button);
        }
      });

      if (!activeTag || !visibleButtons.some(function (button) { return button.dataset.tagName === activeTag; })) {
        activeTag = visibleButtons.length > 0 ? visibleButtons[0].dataset.tagName : null;
        if (activeTag) {
          setHashTag(activeTag);
        }
      }

      syncButtonState();

      if (activeTag) {
        var activeButton = buttons.find(function (button) {
          return button.dataset.tagName === activeTag;
        });
        var activeSection = getSection(activeTag);
        var visibleCount = activeButton ? Number(activeButton.dataset.visiblePosts || 0) : 0;
        showSection(activeSection, visibleCount);
      } else {
        showSection(null, 0);
      }
    }

    sortByCount(buttons).forEach(function (button) {
      cloud.appendChild(button);
    });

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        activeTag = button.dataset.tagName;
        setHashTag(activeTag);
        syncButtonState();
        render();
      });
    });

    if (searchInput) {
      searchInput.addEventListener("input", render);
    }

    window.addEventListener("hashchange", function () {
      var nextTag = getHashTag();
      if (nextTag && buttons.some(function (button) { return button.dataset.tagName === nextTag; })) {
        activeTag = nextTag;
        syncButtonState();
        render();
      }
    });

    var hashTag = getHashTag();
    if (hashTag && buttons.some(function (button) { return button.dataset.tagName === hashTag; })) {
      activeTag = hashTag;
    } else if (buttons.length > 0) {
      activeTag = buttons[0].dataset.tagName;
      setHashTag(activeTag);
    }

    syncButtonState();
    render();
  })();
</script>