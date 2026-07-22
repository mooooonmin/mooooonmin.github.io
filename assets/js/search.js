(function () {
  "use strict";

  var results = document.getElementById("search-results");
  var empty = document.getElementById("search-empty");
  if (!results || !empty) return;

  var searchIndexUrl = results.dataset.indexUrl;
  var baseurl = results.dataset.baseurl || "";

  function getQuery() {
    return new URLSearchParams(window.location.search).get("q") || "";
  }

  function getPreview(text, query, length) {
    text = String(text || "");
    var matchIndex = text.toLowerCase().indexOf(query.toLowerCase());
    var start = matchIndex < 0 ? 0 : Math.max(0, matchIndex - 40);
    var end = matchIndex < 0
      ? Math.min(text.length, length)
      : Math.min(text.length, matchIndex + query.length + 80);
    return {
      text: text.substring(start, end).trim(),
      prefix: start > 0,
      suffix: end < text.length,
    };
  }

  function appendHighlightedText(parent, text, query, length) {
    var preview = getPreview(text, query, length);
    if (preview.prefix) parent.appendChild(document.createTextNode("..."));

    var normalizedQuery = query.toLowerCase();
    var remaining = preview.text;
    while (normalizedQuery && remaining) {
      var matchIndex = remaining.toLowerCase().indexOf(normalizedQuery);
      if (matchIndex < 0) break;
      parent.appendChild(document.createTextNode(remaining.substring(0, matchIndex)));
      var mark = document.createElement("mark");
      mark.textContent = remaining.substring(matchIndex, matchIndex + query.length);
      parent.appendChild(mark);
      remaining = remaining.substring(matchIndex + query.length);
    }

    parent.appendChild(document.createTextNode(remaining));
    if (preview.suffix) parent.appendChild(document.createTextNode("..."));
  }

  function createResult(item, query) {
    var listItem = document.createElement("li");
    var heading = document.createElement("h4");
    var link = document.createElement("a");
    link.href = baseurl + String(item[1] || "").trim();
    appendHighlightedText(link, item[0] || "(제목 없음)", query, 200);
    heading.appendChild(link);
    listItem.appendChild(heading);

    if (item[2]) {
      var tags = document.createElement("span");
      tags.className = "search-result-tags";
      appendHighlightedText(tags, item[2], query, 120);
      listItem.appendChild(tags);
    }

    var paragraph = document.createElement("p");
    var summary = document.createElement("small");
    appendHighlightedText(summary, item[3] || "", query, 170);
    paragraph.appendChild(summary);
    listItem.appendChild(paragraph);
    return listItem;
  }

  function showMessage(message) {
    results.replaceChildren();
    results.style.display = "none";
    empty.textContent = message;
    empty.style.display = "block";
  }

  function tokenize(query) {
    return query.toLowerCase().match(/[0-9A-Za-z가-힣_+#]{2,}/g) || [query.toLowerCase()];
  }

  function findDocumentIds(index, query) {
    var terms = index.terms || {};
    var indexedTerms = Object.keys(terms);
    var candidates = null;

    tokenize(query).forEach(function (queryTerm) {
      var matchingIds = new Set();
      if (terms[queryTerm]) {
        terms[queryTerm].forEach(function (id) { matchingIds.add(id); });
      } else {
        indexedTerms.forEach(function (term) {
          if (term.includes(queryTerm)) {
            terms[term].forEach(function (id) { matchingIds.add(id); });
          }
        });
      }
      candidates = candidates === null
        ? matchingIds
        : new Set(Array.from(candidates).filter(function (id) { return matchingIds.has(id); }));
    });

    return Array.from(candidates || []).sort(function (a, b) { return a - b; });
  }

  async function run() {
    var query = getQuery().trim();
    var input = document.getElementById("search-input");
    if (input) input.value = query;
    if (!query) {
      showMessage("Enter a keyword to search posts.");
      return;
    }

    try {
      var response = await fetch(searchIndexUrl);
      if (!response.ok) throw new Error("Search index request failed");
      var index = await response.json();
      var documents = index.documents || [];
      var matches = findDocumentIds(index, query)
        .map(function (id) { return documents[id]; })
        .filter(Boolean);
      if (!matches.length) {
        showMessage("No results found.");
        return;
      }

      results.replaceChildren();
      matches.forEach(function (item) { results.appendChild(createResult(item, query)); });
      results.style.display = "";
      empty.style.display = "none";
    } catch (error) {
      showMessage("Search is temporarily unavailable.");
    }
  }

  run();
})();
