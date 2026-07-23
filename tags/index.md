---
title: Tags
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
>
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
    <p class="tag-empty-state" id="tag-empty-state">Select a tag on the left to see related posts.</p>
  </div>
</section>
{% else %}
<p>No tags have been added.</p>
{% endif %}

<script src="{{ '/assets/js/tags.js' | relative_url }}" defer></script>
