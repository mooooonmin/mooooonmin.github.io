---
title: 전체
layout: default
---

<ul class="post-list">
{% for post in paginator.posts %}
	<li>
		<span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>
		<a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
	</li>
{% endfor %}
</ul>

{% if paginator.posts.size == 0 %}
<p>아직 글이 없습니다. <code>_posts</code> 폴더에 마크다운 파일을 추가하면 글이 나타납니다.</p>
{% endif %}

<nav class="pagination" aria-label="글 목록 페이지">
	{% if paginator.previous_page %}
		<a href="{{ site.baseurl }}{{ paginator.previous_page_path }}" class="pagination-prev">← 이전</a>
	{% endif %}
	<span class="pagination-info">{{ paginator.page }} / {{ paginator.total_pages }}</span>
	{% if paginator.next_page %}
		<a href="{{ site.baseurl }}{{ paginator.next_page_path }}" class="pagination-next">다음 →</a>
	{% endif %}
</nav>
