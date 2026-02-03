---
layout: null
---
(function () {
	function getQueryVariable(variable) {
		var s = window.location.search.substring(1),
			vars = s.split("&");
		for (var i = 0; i < vars.length; i++) {
			var p = vars[i].split("=");
			if (p[0] === variable) {
				return decodeURIComponent((p[1] || "").replace(/\+/g, "%20")).trim();
			}
		}
		return "";
	}

	function escapeRegex(s) {
		return (s || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
	}

	function getPreview(query, content, previewLength) {
		content = typeof content === "string" ? content : "";
		previewLength = previewLength || 170;
		var parts = query.split(/\s+/).filter(Boolean),
			match = -1, matchLength = 0,
			contentLower = content.toLowerCase(),
			queryLower = query.toLowerCase();
		match = contentLower.indexOf(queryLower);
		if (match >= 0) matchLength = query.length;
		for (var i = 0; i < parts.length && match < 0; i++) {
			match = contentLower.indexOf(parts[i].toLowerCase());
			if (match >= 0) matchLength = parts[i].length;
		}
		var preview;
		if (match >= 0) {
			var start = Math.max(0, match - Math.floor(previewLength / 2)),
				end = Math.min(content.length, match + matchLength + Math.floor(previewLength / 2));
			preview = content.substring(start, end).trim();
			if (start > 0) preview = "..." + preview;
			if (end < content.length) preview = preview + "...";
			try {
				var re = new RegExp("(" + parts.map(escapeRegex).join("|") + ")", "gi");
				preview = preview.replace(re, "<strong>$1</strong>");
			} catch (e) {}
		} else {
			preview = content.substring(0, previewLength).trim() + (content.length > previewLength ? "..." : "");
		}
		return preview;
	}

	function displaySearchResults(keys, query) {
		var searchResultsEl = document.getElementById("search-results"),
			searchProcessEl = document.getElementById("search-process");
		if (!searchResultsEl || !searchProcessEl) return;
		if (keys.length > 0) {
			var html = "";
			keys.forEach(function (key) {
				var item = window.data[key];
				if (!item) return;
				var url = (item.url || "").trim(),
					title = (item.title || "(제목 없음)").toString(),
					content = (item.content || "").toString();
				var contentPreview = getPreview(query, content, 170),
					titlePreview = getPreview(query, title);
				html += "<li><h4><a href='" + (window.baseurl || "") + url + "'>" + titlePreview + "</a></h4><p><small>" + contentPreview + "</small></p></li>";
			});
			searchResultsEl.innerHTML = html;
			searchResultsEl.style.display = "";
			searchProcessEl.textContent = keys.length + "건";
		} else {
			searchResultsEl.innerHTML = "";
			searchResultsEl.style.display = "none";
			searchProcessEl.textContent = "0건";
		}
	}

	function searchByQuery(query) {
		query = (query || "").trim();
		if (!query) return [];
		var q = query.toLowerCase(),
			keys = [];
		for (var key in window.data) {
			if (!Object.prototype.hasOwnProperty.call(window.data, key)) continue;
			var item = window.data[key],
				title = (item.title != null ? item.title : "").toString(),
				content = (item.content != null ? item.content : "").toString();
			if (title.toLowerCase().indexOf(q) !== -1 || content.toLowerCase().indexOf(q) !== -1)
				keys.push(key);
		}
		return keys;
	}

	// JSON 데이터 로드 (한글 등 인코딩 안전)
	var dataEl = document.getElementById("search-data");
	window.data = {};
	if (dataEl && dataEl.textContent) {
		try {
			var arr = JSON.parse(dataEl.textContent);
			if (Array.isArray(arr)) {
				arr.forEach(function (item) {
					if (item && item.id) window.data[item.id] = item;
				});
			}
		} catch (e) {
			console.warn("Search data load failed:", e);
		}
	}

	window.baseurl = window.baseurl || "";

	var query = getQueryVariable("q"),
		searchQueryContainerEl = document.getElementById("search-query-container"),
		searchQueryEl = document.getElementById("search-query"),
		searchInputEl = document.getElementById("search-input");

	if (searchInputEl) searchInputEl.value = query;
	if (searchQueryEl) searchQueryEl.textContent = query;
	if (searchQueryContainerEl) searchQueryContainerEl.style.display = "inline";

	var matchedKeys = searchByQuery(query);
	displaySearchResults(matchedKeys, query);
})();
