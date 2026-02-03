---
title: 글 목록
layout: default
permalink: /posts/
---

<ul class="post-list">
{% for post in site.posts %}
	<li>
		<a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
		<span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>
	</li>
{% endfor %}
</ul>

{% if site.posts.size == 0 %}
<p>아직 글이 없습니다. <code>_posts</code> 폴더에 마크다운 파일을 추가하면 글이 나타납니다.</p>
{% endif %}
