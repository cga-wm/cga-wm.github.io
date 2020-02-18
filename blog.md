---
title: "Blog"
layout: default
navigation_weight: 4
---

{% for post in site.posts %}
# {{post.title}}
{{post.date | date: '%B %d, %Y'}}

{{post.content}}
{% endfor %}
