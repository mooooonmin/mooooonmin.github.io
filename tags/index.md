---
title: 태그
layout: default
permalink: /tags/
---

{% assign sorted_tags = site.tags | sort %}

{% if sorted_tags.size > 0 %}
<section
  class="tag-page"
  data-index-url="{{ '/tags.json' | relative_url }}"
  data-baseurl="{{ site.baseurl | escape }}"
  data-dynamic-fragments
  hidden
>
  <div class="tag-pane tag-pane-list">
    <div class="tag-picker-controls">
      <label for="tag-filter">태그 찾기</label>
      <div class="tag-filter-field">
        <input type="search" id="tag-filter" placeholder="태그 입력" autocomplete="off" aria-controls="tag-cloud-list" />
        <button type="button" id="tag-filter-clear" hidden>지우기</button>
      </div>
      <p class="tag-filter-status" id="tag-filter-status" role="status">{{ sorted_tags.size }}개의 태그</p>
      <button type="button" class="skip-link" id="skip-tag-list">태그 목록 건너뛰기</button>
    </div>
    <div class="tag-picker-scroll">
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
          <span class="tag-cloud-count">{{ tag_posts.size }}개</span>
        </button>
      {% endfor %}
      </div>
      <p class="tag-filter-empty" id="tag-filter-empty" hidden>일치하는 태그가 없습니다.</p>
    </div>
  </div>

  <div class="tag-pane tag-pane-posts" aria-labelledby="tag-result-title">
    <div class="tag-result-header">
      <h2 id="tag-result-title" tabindex="-1">태그별 글</h2>
      <span class="tag-section-count" id="tag-result-count"></span>
    </div>
    <p class="visually-hidden" id="tag-load-status" role="status" aria-atomic="true"></p>
    <section class="tag-section tag-section-panel" id="tag-results" hidden>
      <ul class="post-list" id="tag-result-list"></ul>
    </section>
    <p class="tag-empty-state" id="tag-empty-state">태그를 선택하면 관련 글을 볼 수 있습니다.</p>
    <button type="button" class="button" id="tag-retry" hidden>다시 불러오기</button>
  </div>
</section>
  <div class="tag-static-list">
    {% for tag in sorted_tags %}
      <details>
        <summary>{{ tag[0] | escape }} ({{ tag[1].size }}개)</summary>
        <ul>
          {% for post in tag[1] %}
            <li><a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a></li>
          {% endfor %}
        </ul>
      </details>
    {% endfor %}
  </div>
{% else %}
<p>아직 등록된 태그가 없습니다. <a href="{{ '/' | relative_url }}">전체 글 보기</a></p>
{% endif %}

<script src="{{ '/assets/js/tags.js' | relative_url }}" defer></script>
