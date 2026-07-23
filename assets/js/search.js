(function () {
  "use strict";

  var TOKEN_PATTERN = /[0-9A-Za-z가-힣_+#]{2,}/g;

  function tokenize(query) {
    var normalized = String(query || "").toLowerCase().trim();
    if (!normalized) return [];
    var matches = normalized.match(TOKEN_PATTERN) || [normalized];
    return Array.from(new Set(matches));
  }

  function findNextMatch(text, tokens, start) {
    var normalized = text.toLowerCase();
    var bestMatch = null;

    tokens.forEach(function (token) {
      var index = normalized.indexOf(token, start);
      if (index < 0) return;
      if (
        bestMatch === null
        || index < bestMatch.index
        || (index === bestMatch.index && token.length > bestMatch.length)
      ) {
        bestMatch = { index: index, length: token.length };
      }
    });

    return bestMatch;
  }

  function getPreview(text, tokens, length) {
    var value = String(text || "");
    var firstMatch = findNextMatch(value, tokens, 0);
    var start = firstMatch ? Math.max(0, firstMatch.index - 40) : 0;
    var end = Math.min(value.length, start + length);
    if (firstMatch && end < firstMatch.index + firstMatch.length) {
      end = Math.min(value.length, firstMatch.index + firstMatch.length);
    }

    return {
      text: value.substring(start, end).trim(),
      prefix: start > 0,
      suffix: end < value.length,
    };
  }

  function getHighlightedSegments(text, tokens, length) {
    var preview = getPreview(text, tokens, length);
    var segments = [];
    var position = 0;
    var match = findNextMatch(preview.text, tokens, position);

    while (match) {
      if (match.index > position) {
        segments.push({ text: preview.text.substring(position, match.index), highlighted: false });
      }
      segments.push({
        text: preview.text.substring(match.index, match.index + match.length),
        highlighted: true,
      });
      position = match.index + match.length;
      match = findNextMatch(preview.text, tokens, position);
    }

    if (position < preview.text.length) {
      segments.push({ text: preview.text.substring(position), highlighted: false });
    }

    return {
      prefix: preview.prefix,
      suffix: preview.suffix,
      segments: segments,
    };
  }

  function resolveTermMatches(terms, indexedTerms, queryTerm) {
    var matches = new Map();
    if (Object.prototype.hasOwnProperty.call(terms, queryTerm)) {
      terms[queryTerm].forEach(function (id) { matches.set(id, 30); });
      return matches;
    }

    indexedTerms.forEach(function (term) {
      if (!term.includes(queryTerm)) return;
      var quality = term.startsWith(queryTerm) ? 12 : 6;
      terms[term].forEach(function (id) {
        matches.set(id, Math.max(matches.get(id) || 0, quality));
      });
    });
    return matches;
  }

  function scoreDocument(item, tokens, query) {
    var title = String(item[0] || "").toLowerCase();
    var tags = String(item[2] || "").toLowerCase();
    var summary = String(item[3] || "").toLowerCase();
    var tagTerms = new Set(tokenize(tags));
    var normalizedQuery = String(query || "").toLowerCase().trim();
    var score = 0;

    if (title === normalizedQuery) score += 300;
    else if (normalizedQuery && title.includes(normalizedQuery)) score += 140;

    tokens.forEach(function (token) {
      if (title === token) score += 120;
      else if (title.startsWith(token)) score += 80;
      else if (title.includes(token)) score += 60;

      if (tagTerms.has(token)) score += 50;
      else if (tags.includes(token)) score += 25;

      if (summary.includes(token)) score += 8;
    });

    return score;
  }

  function findDocumentMatches(index, query) {
    var terms = index.terms || {};
    var documents = index.documents || [];
    var tokens = tokenize(query);
    var indexedTerms = null;
    var candidates = null;

    tokens.forEach(function (queryTerm) {
      var needsPartialLookup = !Object.prototype.hasOwnProperty.call(terms, queryTerm);
      if (needsPartialLookup && indexedTerms === null) indexedTerms = Object.keys(terms);
      var termMatches = resolveTermMatches(terms, indexedTerms || [], queryTerm);

      if (candidates === null) {
        candidates = new Map(termMatches);
        return;
      }

      Array.from(candidates.keys()).forEach(function (id) {
        if (!termMatches.has(id)) candidates.delete(id);
        else candidates.set(id, candidates.get(id) + termMatches.get(id));
      });
    });

    return Array.from(candidates || [])
      .filter(function (entry) { return Boolean(documents[entry[0]]); })
      .map(function (entry) {
        return {
          id: entry[0],
          score: entry[1] + scoreDocument(documents[entry[0]], tokens, query),
        };
      })
      .sort(function (left, right) {
        return right.score - left.score || left.id - right.id;
      });
  }

  function appendHighlightedText(parent, text, tokens, length) {
    var highlighted = getHighlightedSegments(text, tokens, length);
    if (highlighted.prefix) parent.appendChild(document.createTextNode("..."));

    highlighted.segments.forEach(function (segment) {
      if (!segment.highlighted) {
        parent.appendChild(document.createTextNode(segment.text));
        return;
      }
      var mark = document.createElement("mark");
      mark.textContent = segment.text;
      parent.appendChild(mark);
    });

    if (highlighted.suffix) parent.appendChild(document.createTextNode("..."));
  }

  var api = {
    findDocumentMatches: findDocumentMatches,
    getHighlightedSegments: getHighlightedSegments,
    scoreDocument: scoreDocument,
    tokenize: tokenize,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof document === "undefined") return;

  var results = document.getElementById("search-results");
  var empty = document.getElementById("search-empty");
  if (!results || !empty) return;

  var searchIndexUrl = results.dataset.indexUrl;
  var baseurl = results.dataset.baseurl || "";

  function getQuery() {
    return new URLSearchParams(window.location.search).get("q") || "";
  }

  function createResult(item, tokens) {
    var listItem = document.createElement("li");
    var heading = document.createElement("h4");
    var link = document.createElement("a");
    link.href = baseurl + String(item[1] || "").trim();
    appendHighlightedText(link, item[0] || "(제목 없음)", tokens, 200);
    heading.appendChild(link);
    listItem.appendChild(heading);

    if (item[2]) {
      var tags = document.createElement("span");
      tags.className = "search-result-tags";
      appendHighlightedText(tags, item[2], tokens, 120);
      listItem.appendChild(tags);
    }

    var paragraph = document.createElement("p");
    var summary = document.createElement("small");
    appendHighlightedText(summary, item[3] || "", tokens, 170);
    paragraph.appendChild(summary);
    listItem.appendChild(paragraph);
    return listItem;
  }

  function showMessage(message) {
    results.replaceChildren();
    results.hidden = true;
    empty.textContent = message;
    empty.hidden = false;
  }

  async function run() {
    var query = getQuery().trim();
    var tokens = tokenize(query);
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
      var matches = findDocumentMatches(index, query)
        .map(function (match) { return documents[match.id]; });
      if (!matches.length) {
        showMessage("No results found.");
        return;
      }

      results.replaceChildren();
      matches.forEach(function (item) { results.appendChild(createResult(item, tokens)); });
      results.hidden = false;
      empty.hidden = true;
    } catch (error) {
      showMessage("Search is temporarily unavailable.");
    }
  }

  run();
})();
