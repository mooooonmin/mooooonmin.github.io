---
layout: null
---
(function () {
	function getQueryVariable(variable) {
		var query = window.location.search.substring(1),
			vars = query.split("&");
		for (var i = 0; i < vars.length; i++) {
			var pair = vars[i].split("=");
			if (pair[0] === variable) {
				return decodeURIComponent((pair[1] || "").replace(/\+/g, '%20')).trim();
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
			match = -1,
			matchLength = 0,
			preview,
			contentLower = content.toLowerCase(),
			queryLower = query.toLowerCase();

		match = contentLower.indexOf(queryLower);
		if (match >= 0) matchLength = query.length;
		for (var i = 0; i < parts.length && match < 0; i++) {
			match = contentLower.indexOf(parts[i].toLowerCase());
			if (match >= 0) matchLength = parts[i].length;
		}

		if (match >= 0) {
			var start = Math.max(0, match - Math.floor(previewLength / 2)),
				end = Math.min(content.length, match + matchLength + Math.floor(previewLength / 2));
			preview = content.substring(start, end).trim();
			if (start > 0) preview = "..." + preview;
			if (end < content.length) preview = preview + "...";
			var re = new RegExp("(" + parts.map(escapeRegex).join("|") + ")", "gi");
			preview = preview.replace(re, "<strong>$1</strong>");
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
			var resultsHTML = "";
			keys.forEach(function (key) {
				var item = window.data[key];
				if (!item) return;
				var url = (item.url || "").trim(),
					title = item.title || "(제목 없음)",
					content = item.content || "";
				var contentPreview = getPreview(query, content, 170),
					titlePreview = getPreview(query, title);
				resultsHTML += "<li><h4><a href='" + (window.baseurl || "") + url + "'>" + titlePreview + "</a></h4><p><small>" + contentPreview + "</small></p></li>";
			});
			searchResultsEl.innerHTML = resultsHTML;
			searchResultsEl.style.display = "";
			searchProcessEl.innerText = keys.length + "건";
		} else {
			searchResultsEl.innerHTML = "";
			searchResultsEl.style.display = "none";
			searchProcessEl.innerText = "0건";
		}
	}

	// 검색어: 제목 또는 내용에 포함되면 (전체/부분 일치, 한글 지원)
	function searchByQuery(query) {
		query = (query || "").trim();
		if (!query) return [];
		var q = query.toLowerCase(),
			keys = [];
		for (var key in window.data) {
			if (!window.data.hasOwnProperty(key)) continue;
			var item = window.data[key],
				title = (item.title || ""),
				content = (item.content || "");
			if (title.toLowerCase().indexOf(q) !== -1 || content.toLowerCase().indexOf(q) !== -1) {
				keys.push(key);
			}
		}
		return keys;
	}

	var query = getQueryVariable("q"),
		searchQueryContainerEl = document.getElementById("search-query-container"),
		searchQueryEl = document.getElementById("search-query"),
		searchInputEl = document.getElementById("search-input");

	if (searchInputEl) searchInputEl.value = query;
	if (searchQueryEl) searchQueryEl.textContent = query;
	if (searchQueryContainerEl) searchQueryContainerEl.style.display = "inline";

	// baseurl은 검색 페이지에서 전역으로 넣어두거나 빈 문자열
	window.baseurl = window.baseurl || "";

	var matchedKeys = searchByQuery(query);
	displaySearchResults(matchedKeys, query);
})();
