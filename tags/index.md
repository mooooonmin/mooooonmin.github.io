---
title: 태그
layout: default
permalink: /tags/
---

{% assign sorted_tags = site.tags | sort %}

{% if sorted_tags.size > 0 %}
  <section class="tag-cloud-section" aria-labelledby="tag-cloud-title">
    <h4 id="tag-cloud-title">태그 모음</h4>
    <div class="tag-cloud">
      {% for tag in sorted_tags %}
        {% assign tag_name = tag[0] %}
        {% assign tag_posts = tag[1] %}
        <a
          href="#tag-{{ tag_name | slugify }}"
          class="tag-cloud-item"
          style="--tag-count: {{ tag_posts.size }};"
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
      <div class="tag-section" id="tag-{{ tag_name | slugify }}">
        <div class="tag-section-header">
          <h4>#{{ tag_name }}</h4>
          <span class="tag-section-count">{{ tag_posts.size }}개</span>
        </div>
        <ul class="post-list">
          {% for post in tag_posts %}
            <li>
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
