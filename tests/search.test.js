"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");

const search = require("../assets/js/search.js");


test("tokenize normalizes and removes duplicate search terms", () => {
  assert.deepEqual(search.tokenize(" Linux linux 명령어 C++ "), ["linux", "명령어", "c++"]);
  assert.deepEqual(search.tokenize(""), []);
});


test("findDocumentMatches ranks title and tag matches above body matches", () => {
  const index = {
    documents: [
      ["Recent post", "/recent/", "", "A Kafka body match"],
      ["Kafka", "/title/", "", ""],
      ["Other post", "/tag/", "kafka", ""],
    ],
    terms: { kafka: [0, 1, 2] },
  };

  assert.deepEqual(
    search.findDocumentMatches(index, "kafka").map((match) => match.id),
    [1, 2, 0],
  );
});


test("findDocumentMatches keeps partial matching and intersects multiple terms", () => {
  const index = {
    documents: [
      ["Linux overview", "/linux/", "", ""],
      ["Linux command", "/command/", "", ""],
      ["Command overview", "/other/", "", ""],
    ],
    terms: {
      command: [1, 2],
      linux: [0, 1],
    },
  };

  assert.deepEqual(
    search.findDocumentMatches(index, "lin com").map((match) => match.id),
    [1],
  );
});


test("getHighlightedSegments highlights every query token", () => {
  const highlighted = search.getHighlightedSegments(
    "Linux and Docker command examples",
    ["linux", "command"],
    100,
  );

  assert.deepEqual(
    highlighted.segments.filter((segment) => segment.highlighted).map((segment) => segment.text),
    ["Linux", "command"],
  );
});
