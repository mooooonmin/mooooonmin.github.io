---
title: 태그
layout: default
permalink: /tags/
---

{% assign sorted_tags = site.tags | sort %}

{% if sorted_tags.size > 0 %}
  <section class="tag-cloud-section" aria-labelledby="tag-cloud-title">
    <h4 id="tag-cloud-title">태그 모음</h4>
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
    <div class="tag-cloud">
      {% for tag in sorted_tags %}
        {% assign tag_name = tag[0] %}
        {% assign tag_posts = tag[1] %}
        <a
          href="#tag-{{ tag_name | slugify }}"
          class="tag-cloud-item"
          style="--tag-count: {{ tag_posts.size }};"`r`n          data-tag-name="{{ tag_name | downcase }}"`r`n          data-count="{{ tag_posts.size }}"
        >
          <span class="tag-cloud-name">{{ tag_name }}</span>
          <span class="tag-cloud-count">{{ tag_posts.size }}</span>
        </a>
      {% endfor %}
    </div>
  </section>

  <section class="tag-sections" aria-label="태그별 글 목록">
    {% for tag in sorted_tags %}
      {% assign tag_name = tag[0] %}
      {% assign tag_posts = tag[1] %}
      <div
        class="tag-section"
        id="tag-{{ tag_name | slugify }}"
        data-tag-name="{{ tag_name | downcase }}"
        data-count="{{ tag_posts.size }}"
      >
        <div class="tag-section-header">
          <h4>#{{ tag_name }}</h4>
          <span class="tag-section-count">{{ tag_posts.size }}개</span>
        </div>
        <ul class="post-list">
          {% for post in tag_posts %}
            <li data-search-text="{{ post.title | downcase | escape }}">
              <span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>
              <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
            </li>
          {% endfor %}
        </ul>
      </div>
    {% endfor %}
  </section>
{% else %}
  <p>등록된 태그가 없습니다.</p>
{% endif %}

<script>
  (function () {
    var cloud = document.querySelector(".tag-cloud");
    var sections = document.querySelector(".tag-sections");
    var searchInput = document.getElementById("tag-search-input");

    function sortByCount(container, selector) {
      if (!container) return;
      var items = Array.prototype.slice.call(container.querySelectorAll(selector));
      items.sort(function (a, b) {
        return Number(b.dataset.count || 0) - Number(a.dataset.count || 0);
      });
      items.forEach(function (item) {
        container.appendChild(item);
      });
    }

    function normalize(value) {
      return (value || "").toLowerCase().trim();
    }

    function applyFilter() {
      var query = normalize(searchInput && searchInput.value);
      var sectionItems = Array.prototype.slice.call(document.querySelectorAll(".tag-section"));
      var cloudItems = Array.prototype.slice.call(document.querySelectorAll(".tag-cloud-item"));

      sectionItems.forEach(function (section) {
        var tagName = normalize(section.dataset.tagName);
        var postItems = Array.prototype.slice.call(section.querySelectorAll("li"));
        var matchedPosts = 0;

        postItems.forEach(function (postItem) {
          var postText = normalize(postItem.dataset.searchText);
          var visible = !query || tagName.indexOf(query) !== -1 || postText.indexOf(query) !== -1;
          postItem.style.display = visible ? "" : "none";
          if (visible) matchedPosts += 1;
        });

        var shouldShowSection = !query || tagName.indexOf(query) !== -1 || matchedPosts > 0;
        section.style.display = shouldShowSection ? "" : "none";
      });

      cloudItems.forEach(function (item) {
        var tagName = normalize(item.dataset.tagName);
        var linkedSection = document.getElementById(item.getAttribute("href").replace("#", ""));
        var visible = !query || tagName.indexOf(query) !== -1 || (linkedSection && linkedSection.style.display !== "none");
        item.style.display = visible ? "inline-flex" : "none";
      });
    }

    sortByCount(cloud, ".tag-cloud-item");
    sortByCount(sections, ".tag-section");

    if (searchInput) {
      searchInput.addEventListener("input", applyFilter);
    }
  })();
</script>