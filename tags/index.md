---
title: 태그
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
            <li>
              <span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>
              <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
            </li>
          {% endfor %}
        </ul>
      </section>
    {% endfor %}

    <p class="tag-empty-state tag-empty-state-visible" id="tag-empty-state">왼쪽에서 태그를 선택하면 관련 포스트 목록이 표시됩니다.</p>
  </div>
</section>
{% else %}
<p>등록된 태그가 없습니다.</p>
{% endif %}

<script>
  (function () {
    var cloud = document.getElementById("tag-cloud-list");
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
      var nextUrl = window.location.pathname + window.location.search + (tagName ? ("#" + tagName) : "");
      window.history.replaceState(null, "", nextUrl);
    }

    function sortAlphabetically(items) {
      items.sort(function (a, b) {
        return a.dataset.tagName.localeCompare(b.dataset.tagName);
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

    function render() {
      var activeSection = activeTag ? getSection(activeTag) : null;

      sections.forEach(function (section) {
        section.style.display = section === activeSection ? "block" : "none";
      });

      if (activeSection) {
        resultTitle.textContent = "#" + activeSection.dataset.tagLabel;
        resultCount.textContent = activeSection.dataset.count + "개";
        emptyState.style.display = "none";
      } else {
        resultTitle.textContent = "태그를 선택하세요";
        resultCount.textContent = "";
        emptyState.style.display = "block";
      }
    }

    sortAlphabetically(buttons).forEach(function (button) {
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

    window.addEventListener("hashchange", function () {
      var nextTag = getHashTag();
      activeTag = buttons.some(function (button) { return button.dataset.tagName === nextTag; }) ? nextTag : null;
      syncButtonState();
      render();
    });

    var hashTag = getHashTag();
    activeTag = buttons.some(function (button) { return button.dataset.tagName === hashTag; }) ? hashTag : null;

    syncButtonState();
    render();
  })();
</script>