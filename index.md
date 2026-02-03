---
title: 홈
layout: default
---

블로그에 오신 걸 환영합니다.

### 최근 글

<ul>
{% for post in site.posts limit:10 %}
	<li>
		<a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
		<span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>
	</li>
{% endfor %}
</ul>

{% if site.posts.size == 0 %}
<p>아직 글이 없습니다.</p>
{% endif %}

<p><a href="{{ site.baseurl }}/posts/">전체 글 보기</a> · <a href="{{ site.baseurl }}/feed.xml">RSS</a></p>
